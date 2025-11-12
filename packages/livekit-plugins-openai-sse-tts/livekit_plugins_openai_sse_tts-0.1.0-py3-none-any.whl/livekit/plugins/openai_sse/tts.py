import asyncio
import aiohttp
import logging
import os
from typing import AsyncIterator, Optional
from livekit.agents import tts
from livekit.agents import APIConnectOptions, APIError, APITimeoutError, APIStatusError, APIConnectionError, utils
from livekit.agents.types import DEFAULT_API_CONNECT_OPTIONS
from livekit import rtc
import json
import base64
import io
import wave
import time

logger = logging.getLogger(__name__)


class OpenAIAPIClient:
    """
    Shared OpenAI API client for TTS operations
    
    Handles common functionality like making requests, parsing SSE events,
    and processing audio data to avoid code duplication.
    """
    
    def __init__(self, tts_instance: "TTS"):
        self._tts = tts_instance
        self._session: Optional[aiohttp.ClientSession] = None
        self._buffer = ""
    
    async def _make_request(self, text: str) -> aiohttp.ClientResponse:
        """Make SSE request to OpenAI TTS API with streaming enabled"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
            
        # OpenAI TTS API endpoint with SSE support
        url = "https://api.openai.com/v1/audio/speech"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",  # Required for SSE
            "Cache-Control": "no-cache"
        }
        
        # Request payload - stream_format: "sse" enables Server-Sent Events
        payload = {
            "model": self._tts.model,
            "input": text,
            "voice": self._tts.voice,
            "stream_format": "sse",  # This enables SSE streaming
            "response_format": self._tts.response_format,
            "speed": self._tts.speed
        }
        
        if self._tts.instructions:
            payload["instructions"] = self._tts.instructions
            
        # Create session if it doesn't exist
        if not self._session:
            self._session = aiohttp.ClientSession()
        
        response = await self._session.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response
    
    async def _parse_sse_event(self, line: str) -> Optional[dict]:
        """
        Parse SSE event line - SSE format is:
        data: <json_data>
        event: <event_type>
        id: <event_id>
        """
        line = line.strip()
        if not line:
            return None
            
        if line.startswith("data: "):
            data = line[6:]  # Remove "data: " prefix
            if data == "[DONE]":
                return {"type": "done"}
            try:
                return json.loads(data)  # Parse JSON data from SSE
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse SSE data: {data}")
                return None
        elif line.startswith("event: "):
            event_type = line[7:]
            return {"type": "event", "event": event_type}
        elif line.startswith("id: "):
            event_id = line[4:]
            return {"type": "id", "id": event_id}
        elif line.startswith("retry: "):
            retry_ms = line[7:]
            return {"type": "retry", "retry": int(retry_ms)}
        
        return None
    
    async def _process_audio_data(self, data: dict) -> Optional[bytes]:
        """Decode base64 audio data from SSE event"""
        # OpenAI TTS SSE sends audio data in different possible formats
        # Let's check for common field names
        audio_data = None
        
        if "audio" in data:
            audio_data = data["audio"]
        elif "data" in data:
            audio_data = data["data"]
        elif isinstance(data, str):
            # Sometimes the data itself is the base64 string
            audio_data = data
            
        if audio_data:
            try:
                # OpenAI sends audio as base64-encoded data in SSE events
                audio_bytes = base64.b64decode(audio_data)
                return audio_bytes
            except Exception as e:
                logger.error(f"Failed to decode audio data: {e}")
                return None
        return None
    
    async def close(self):
        """Close the HTTP session"""
        if self._session:
            await self._session.close()
            self._session = None


class TTS(tts.TTS):
    """
    OpenAI TTS using Server-Sent Events for real-time streaming
    
    This implementation provides real-time streaming of audio generation,
    allowing users to hear audio as it's being synthesized instead of waiting
    for the complete file. This significantly reduces perceived latency.
    
    Key differences from regular OpenAI TTS (livekit.plugins.openai):
    - Regular TTS: Returns complete audio file, higher latency
    - SSE TTS: Streams audio chunks in real-time, lower perceived latency
    - Regular TTS: Handles MP3->PCM conversion internally
    - SSE TTS: Receives raw PCM data and creates AudioFrames directly
    
    The current implementation works with PCM data directly, which is more
    efficient than MP3 as it doesn't require decompression and provides
    better real-time performance.
    """
    
    def __init__(
        self,
        *,
        voice: str = "alloy",
        model: str = "gpt-4o-mini-tts",
        speed: float = 1.0,
        response_format: str = "pcm",
        instructions: Optional[str] = None,
        sample_rate: int = 24000,
        num_channels: int = 1,
    ):
        super().__init__(
            capabilities=tts.TTSCapabilities(streaming=True),
            sample_rate=sample_rate,
            num_channels=num_channels
        )
        self._voice = voice
        self._model = "gpt-4o-mini-tts"  # Always use gpt-4o-mini-tts regardless of parameter
        self._speed = speed
        self._response_format = response_format
        self._instructions = instructions
    
    @property
    def voice(self) -> str:
        return self._voice
    
    @property
    def model(self) -> str:
        return self._model
    
    @property
    def speed(self) -> float:
        return self._speed
    
    @property
    def response_format(self) -> str:
        return self._response_format
    
    @property
    def instructions(self) -> Optional[str]:
        return self._instructions
    
    def stream(self, *, conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS) -> "SynthesizeStream":
        """Create a streaming TTS request"""
        return SynthesizeStream(
            tts=self,
            conn_options=conn_options
        )
    
    def synthesize(self, text: str, *, conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS) -> "ChunkedStream":
        """Synthesize complete audio (non-streaming)"""
        return ChunkedStream(
            tts=self,
            input_text=text,
            conn_options=conn_options
        )


class SynthesizeStream(tts.SynthesizeStream):
    """
    OpenAI TTS Stream using Server-Sent Events (SSE)
    
    Implements LiveKit's SynthesizeStream interface for real-time streaming.
    """
    
    def __init__(
        self,
        *,
        tts: TTS,
        conn_options: APIConnectOptions
    ):
        super().__init__(tts=tts, conn_options=conn_options)
        self._tts: TTS = tts
        
        # Shared API client
        self._api_client = OpenAIAPIClient(tts)
        
        # Sentence tokenizer for processing sentences
        self._sentence_tokenizer = self._create_sentence_tokenizer()
        
        # Timing measurements for accurate latency testing
        self._request_start_time = None

        self._first_audio_time = None
        self._first_raw_audio_latency = None

        self._first_processed_audio_time = None
        self._first_processed_audio_latency = None

    
    def _create_sentence_tokenizer(self):
        """Create a simple sentence tokenizer for processing complete sentences"""
        class SimpleSentenceTokenizer:
            def __init__(self):
                self._event_ch = asyncio.Queue()
                self._closed = False
            
            def push_text(self, text: str) -> None:
                if self._closed:
                    return
                # Each text is already a complete sentence, so emit it
                if text.strip():
                    # Filter out single punctuation marks to avoid unnecessary SSE requests
                    stripped_text = text.strip()
                    if self._is_single_punctuation(stripped_text):
                        logger.debug(f"Skipping single punctuation mark: '{stripped_text}'")
                        return
                    self._event_ch.put_nowait(stripped_text)
            
            def _is_single_punctuation(self, text: str) -> bool:
                """Check if text is just a single punctuation mark"""
                if len(text) != 1:
                    return False
                # Common punctuation marks that shouldn't trigger TTS
                punctuation_marks = ".,!?;:()[]{}'\"`~@#$%^&*-_=+|\\<>/"
                return text in punctuation_marks
            
            def flush(self) -> None:
                # No buffering needed since each push_text is a complete sentence
                pass
            
            def end_input(self) -> None:
                self._closed = True
            
            async def aclose(self) -> None:
                self._closed = True
            
            async def __anext__(self):
                if self._closed and self._event_ch.empty():
                    raise StopAsyncIteration
                return await self._event_ch.get()
            
            def __aiter__(self):
                return self
        
        return SimpleSentenceTokenizer()
    
    async def _input_task(self) -> None:
        """Handle input text from the input channel"""
        async for data in self._input_ch:
            logger.info(f"Data received: {data}")
            if isinstance(data, self._FlushSentinel):
                continue
            
            # Push text to sentence tokenizer
            self._sentence_tokenizer.push_text(data)
            logger.info(f"Pushed text to tokenizer: {data}")
        
        # End input when done
        self._sentence_tokenizer.end_input()

    async def _sentence_stream_task(self, output_emitter: tts.AudioEmitter) -> None:
        """Process streaming text and handle SSE response"""
        try:
            # Process sentences as they become available from the tokenizer
            async for sentence in self._sentence_tokenizer:
                if not sentence.strip():
                    continue
                
                logger.info(f"Processing sentence: {sentence}")
                # Make the request with the current sentence
                self._request_start_time = time.perf_counter()
                logger.info(f"Making SSE request to OpenAI for sentence: {sentence}")
                
                response = await self._api_client._make_request(sentence)
                logger.info(f"Response status: {response.status}")
                
                try:
                    # Process SSE stream line by line for this sentence
                    line_count = 0
                    async for line in response.content:
                        line_str = line.decode('utf-8')
                        line_count += 1
                        self._api_client._buffer += line_str
                        
                        # Process complete lines (SSE events end with \n\n)
                        while '\n' in self._api_client._buffer:
                            line, self._api_client._buffer = self._api_client._buffer.split('\n', 1)
                            event = await self._api_client._parse_sse_event(line)
                            
                            if event is None:
                                continue
                                
                            if event.get("type") == "done":
                                logger.debug("SSE stream completed for sentence")
                                break
                                
                            elif event.get("type") == "speech.audio.delta":
                                # Measure first audio latency
                                audio_b64_received = event.get("audio")
                                if isinstance(audio_b64_received, str) and audio_b64_received:
                                    if self._first_audio_time is None:
                                        self._first_audio_time = time.perf_counter()
                                        self._first_raw_audio_latency = self._first_audio_time - self._request_start_time
                                        logger.info(f"⏱️  First audio delta latency: {self._first_raw_audio_latency:.4f} seconds")
                                
                                # Process audio data
                                audio_bytes = await self._api_client._process_audio_data(event)
                                if audio_bytes:
                                    if self._first_processed_audio_time is None:
                                        self._first_processed_audio_time = time.perf_counter()
                                        self._first_processed_audio_latency = self._first_processed_audio_time - self._request_start_time
                                        logger.info(f"⏱️  First processed audio latency: {self._first_processed_audio_latency:.4f} seconds")
                                    logger.debug(f"Successfully decoded audio chunk")
                                    output_emitter.push(audio_bytes)
                                else:
                                    logger.warning(f"No audio data found in SSE event: {event}")
                finally:
                    # Ensure response is properly closed
                    response.close()
        except Exception as e:
            logger.error(f"Error in sentence stream task: {e}")
            raise

    async def _run(self, output_emitter: tts.AudioEmitter) -> None:
        """Main streaming implementation using AudioEmitter"""
        output_emitter.initialize(
            request_id="openai_sse_request",
            sample_rate=self._tts.sample_rate,
            num_channels=self._tts.num_channels,
            mime_type="audio/pcm",
            stream=True,
        )
        output_emitter.start_segment(segment_id="openai_sse_segment")

        try:
            # Create tasks for input and sentence streaming
            input_task = asyncio.create_task(self._input_task())
            stream_task = asyncio.create_task(self._sentence_stream_task(output_emitter))
            
            try:
                await asyncio.gather(input_task, stream_task)
            except Exception as e:
                if isinstance(e, APIStatusError):
                    raise e
                raise APIStatusError("Could not synthesize") from e
            finally:
                await utils.aio.gracefully_cancel(input_task, stream_task)

        except asyncio.TimeoutError:
            raise APITimeoutError() from None
        except aiohttp.ClientResponseError as e:
            raise APIStatusError(
                message=e.message, status_code=e.status, request_id=None, body=None
            ) from None
        except Exception as e:
            raise APIConnectionError() from e
        finally:
            output_emitter.end_segment()
            await self._api_client.close()
    
    def get_first_raw_audio_latency(self) -> Optional[float]:
        """Get the first audio latency measurement (API response time)"""
        return self._first_raw_audio_latency
    
    def get_first_processed_audio_latency(self) -> Optional[float]:
        """Get the first processed audio latency measurement"""
        return self._first_processed_audio_latency


class ChunkedStream(tts.ChunkedStream):
    """
    OpenAI TTS ChunkedStream for non-streaming synthesis
    
    Collects all audio chunks and returns them as a single response.
    """
    
    def __init__(
        self,
        *,
        tts: TTS,
        input_text: str,
        conn_options: APIConnectOptions
    ):
        super().__init__(tts=tts, input_text=input_text, conn_options=conn_options)
        self._tts: TTS = tts
        
        # Shared API client
        self._api_client = OpenAIAPIClient(tts)
        
        # Timing measurements for accurate latency testing
        self._request_start_time = None

        self._first_audio_time = None
        self._first_raw_audio_latency = None

        self._first_processed_audio_time = None
        self._first_processed_audio_latency = None


    async def _run(self, output_emitter: tts.AudioEmitter) -> None:
        """Main chunked streaming implementation using AudioEmitter"""
        output_emitter.initialize(
            request_id="openai_sse_chunked_request",
            sample_rate=self._tts.sample_rate,
            num_channels=self._tts.num_channels,
            mime_type="audio/pcm",
        )

        try:
            # Start timing the request
            self._request_start_time = time.perf_counter()
            logger.info("Making SSE request to OpenAI...")
            
            try:
                response = await self._api_client._make_request(self._input_text)
                logger.info(f"Response status: {response.status}")
                
                # Process SSE stream line by line
                line_count = 0
                async for line in response.content:
                    line_str = line.decode('utf-8')
                    line_count += 1
                    self._api_client._buffer += line_str
                    
                    # Process complete lines (SSE events end with \n\n)
                    while '\n' in self._api_client._buffer:
                        line, self._api_client._buffer = self._api_client._buffer.split('\n', 1)
                        event = await self._api_client._parse_sse_event(line)
                        
                        if event is None:
                            continue
                            
                        if event.get("type") == "done":
                            logger.debug("SSE stream completed")
                            break
                            
                        elif event.get("type") == "speech.audio.delta":
                            # Measure first audio latency
                            audio_b64_received = event.get("audio")
                            if isinstance(audio_b64_received, str) and audio_b64_received:
                                if self._first_audio_time is None:
                                    self._first_audio_time = time.perf_counter()
                                    self._first_raw_audio_latency = self._first_audio_time - self._request_start_time
                                    logger.info(f"⏱️  First audio delta latency: {self._first_raw_audio_latency:.4f} seconds")
                            
                            # Process audio data
                            audio_bytes = await self._api_client._process_audio_data(event)
                            if audio_bytes:
                                if self._first_processed_audio_time is None:
                                    self._first_processed_audio_time = time.perf_counter()
                                    self._first_processed_audio_latency = self._first_processed_audio_time - self._request_start_time
                                    logger.info(f"⏱️  First processed audio latency: {self._first_processed_audio_latency:.4f} seconds")
                                logger.debug(f"Successfully decoded audio chunk")
                                output_emitter.push(audio_bytes)
                            else:
                                logger.warning(f"No audio data found in SSE event: {event}")

            except asyncio.TimeoutError:
                raise APITimeoutError() from None
            except aiohttp.ClientResponseError as e:
                raise APIStatusError(
                    message=e.message, status_code=e.status, request_id=None, body=None
                ) from None
            except Exception as e:
                raise APIConnectionError() from e

        finally:
            output_emitter.flush()
            await self._api_client.close()

    def get_first_raw_audio_latency(self) -> Optional[float]:
        """Get the first audio latency measurement (API response time)"""
        return self._first_raw_audio_latency
    
    def get_first_processed_audio_latency(self) -> Optional[float]:
        """Get the first processed audio latency measurement"""
        return self._first_processed_audio_latency
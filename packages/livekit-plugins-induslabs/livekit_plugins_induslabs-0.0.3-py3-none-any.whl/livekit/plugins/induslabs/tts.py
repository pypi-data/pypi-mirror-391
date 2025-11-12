"""IndusLabs Text‑to‑Speech implementation for LiveKit Agents.

This module exposes a :class:`TTS` class which implements the
``livekit.agents.tts.TTS`` interface on top of the IndusLabs Voice API.
It supports both chunked (non‑streaming) synthesis where an entire
utterance is produced and then emitted, as well as fully streaming
synthesis where audio bytes are yielded as soon as they are received
from the server.  See the accompanying :mod:`stt` module for the
speech‑to‑text implementation.

The API key used to authenticate with IndusLabs can be supplied
explicitly or via the ``INDUSLABS_API_KEY`` environment variable.  You
can further customise the voice, output sample rate and other
properties via keyword arguments.
"""

from __future__ import annotations

import asyncio
import logging
import os
import weakref
from dataclasses import dataclass, replace
from typing import AsyncGenerator

import aiohttp

from livekit import rtc  # imported for type completeness
from livekit.agents import tokenize, tts, utils
from livekit.agents import APIConnectionError, APIConnectOptions
from livekit.agents.types import (
    DEFAULT_API_CONNECT_OPTIONS,
)

from .log import logger as _logger

# Constants for audio formatting
NUM_CHANNELS = 1
DEFAULT_SAMPLE_RATE = 24_000

# Default endpoint and voice.  Users may override these via the
# constructor.
DEFAULT_BASE_URL = "https://voice.induslabs.io"
DEFAULT_VOICE = "Indus-hi-Urvashi"

# Optimal chunk size for streaming.  Smaller chunks yield lower
# latency at the cost of slightly higher overhead.
PCM_CHUNK_SIZE = 4096


@dataclass
class _TTSOptions:
    """Internal dataclass used to collect TTS options.

    Instances of :class:`_TTSOptions` are immutable; a shallow copy is
    made each time a new stream is constructed.  This ensures that
    per‑stream modifications do not leak back into the parent
    :class:`TTS` instance.
    """

    base_url: str
    api_key: str
    voice: str
    speed: float
    pitch_shift: float
    loudness_db: float
    normalize: bool
    sample_rate: int
    word_tokenizer: tokenize.WordTokenizer


class TTS(tts.TTS):
    """Convert text into speech using IndusLabs' API.

    The :class:`TTS` class implements the ``livekit.agents.tts.TTS``
    interface and can be supplied to an :class:`~livekit.agents.session.AgentSession`
    as the speech synthesiser.  It supports streaming and
    non‑streaming modes and yields raw PCM audio suitable for
    immediate playback.  The service supports Hindi and English along
    with a variety of voices—see the IndusLabs documentation for the
    full list.

    Parameters
    ----------
    api_key:
        API key used for authentication.  If omitted the plugin will
        read the key from the ``INDUSLABS_API_KEY`` environment
        variable.  A missing key will result in a :class:`ValueError`.
    base_url:
        Base URL of the IndusLabs Voice API.  Trailing slashes are
        automatically stripped.
    voice:
        Identifier of the voice to synthesise with.  The default voice
        is "Indus-hi-Urvashi" which speaks Hindi with a female voice.
    sample_rate:
        Sample rate of the output PCM.  IndusLabs currently supports
        24 kHz audio; values outside this range may be silently
        resampled.
    speed:
        Playback speed multiplier (1.0 for normal speed).
    pitch_shift:
        Pitch shift in semitones.
    loudness_db:
        Gain adjustment in decibels.
    normalize:
        Whether to normalise punctuation and whitespace in the input
        text before synthesis.
    word_tokenizer:
        Optional custom tokenizer used for streaming segmentation.  A
        basic tokenizer is used if omitted.
    connect_options:
        Options controlling request timeouts and retries when
        communicating with the API.
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        voice: str = DEFAULT_VOICE,
        sample_rate: int = DEFAULT_SAMPLE_RATE,
        speed: float = 1.0,
        pitch_shift: float = 0.0,
        loudness_db: float = 0.0,
        normalize: bool = True,
        word_tokenizer: tokenize.WordTokenizer | None = None,
        connect_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS,
    ) -> None:
        # Call the parent constructor with capabilities and audio format
        super().__init__(
            capabilities=tts.TTSCapabilities(streaming=True, aligned_transcript=False),
            sample_rate=sample_rate,
            num_channels=NUM_CHANNELS,
        )

        # Determine API key
        if api_key is None:
            api_key = os.getenv("INDUSLABS_API_KEY")
            if not api_key:
                raise ValueError(
                    "API key must be provided either as a parameter or through the "
                    "INDUSLABS_API_KEY environment variable"
                )

        # Use a basic word tokenizer if none is provided
        if word_tokenizer is None:
            word_tokenizer = tokenize.basic.WordTokenizer(ignore_punctuation=False)

        self._opts = _TTSOptions(
            base_url=base_url.rstrip("/"),
            api_key=api_key,
            voice=voice,
            speed=speed,
            pitch_shift=pitch_shift,
            loudness_db=loudness_db,
            normalize=normalize,
            sample_rate=sample_rate,
            word_tokenizer=word_tokenizer,
        )

        # Underlying HTTP session reused across requests
        self._session: aiohttp.ClientSession | None = None
        self._connect_options = connect_options
        # Track active streams so they can be closed when the TTS is closed
        self._streams = weakref.WeakSet["SynthesizeStream"]()

    # Public API -----------------------------------------------------------

    def synthesize(
        self,
        text: str,
        *,
        conn_options: APIConnectOptions | None = None,
    ) -> "ChunkedStream":
        """Return a chunked stream that produces audio for the given text.

        In chunked mode the entire response is buffered and emitted
        sequentially.  This mode is simple but incurs additional
        latency before playback starts.  For lower latency consider
        calling :meth:`stream` instead.
        """
        return ChunkedStream(
            tts=self,
            input_text=text,
            conn_options=conn_options or self._connect_options,
        )

    def stream(
        self,
        *,
        conn_options: APIConnectOptions | None = None,
    ) -> "SynthesizeStream":
        """Return a streaming synthesiser for incremental synthesis.

        In streaming mode audio begins playing almost immediately as
        chunks are received from the server.  The returned stream is
        writeable; you can call ``push()`` with strings to enqueue
        additional text.  Each segment of text is synthesised and
        emitted as soon as it completes.
        """
        stream = SynthesizeStream(
            tts=self,
            conn_options=conn_options or self._connect_options,
        )
        self._streams.add(stream)
        return stream

    def prewarm(self) -> None:
        """Warm up a connection to the API.

        This method asynchronously creates the underlying aiohttp session
        so that the first call to the API does not incur the overhead
        of establishing a new connection.
        """
        _logger.info(f"Pre‑warming TTS connection to {self._opts.base_url}")
        if self._session is None:
            asyncio.create_task(self._ensure_session())

    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Ensure an aiohttp client session exists and is alive."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(
                total=self._connect_options.timeout,
                connect=self._connect_options.timeout,
                sock_read=self._connect_options.timeout,
            )
            connector = aiohttp.TCPConnector(
                limit=20,
                limit_per_host=10,
                keepalive_timeout=60,
                enable_cleanup_closed=True,
                force_close=False,
            )
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
            )
        return self._session

    async def _health_check(self) -> bool:
        """Return whether the IndusLabs TTS service is reachable."""
        try:
            session = await self._ensure_session()
            url = f"{self._opts.base_url}/health"
            async with session.get(url) as response:
                return response.status == 200
        except Exception as e:
            _logger.warning(f"Health check failed: {e}")
            return False

    async def aclose(self) -> None:
        """Close all open streams and the underlying HTTP session."""
        streams_to_close = list(self._streams)
        if streams_to_close:
            _logger.info(f"Closing {len(streams_to_close)} active streams")
            await asyncio.gather(
                *[stream.aclose() for stream in streams_to_close],
                return_exceptions=True,
            )

        if self._session and not self._session.closed:
            await self._session.close()
            _logger.info("TTS session closed")


class ChunkedStream(tts.ChunkedStream):
    """Non‑streaming synthesis with immediate emission of audio chunks."""

    def __init__(
        self,
        *,
        tts: TTS,
        input_text: str,
        conn_options: APIConnectOptions,
    ) -> None:
        super().__init__(tts=tts, input_text=input_text, conn_options=conn_options)
        self._tts = tts
        # Make a copy of options to avoid mutating the parent
        self._opts = replace(self._tts._opts)

    async def _run(self, output_emitter: tts.AudioEmitter) -> None:
        """Execute a single synthesis request in chunked mode."""
        request_id = utils.shortuuid()

        # Initialises the emitter.  Because we know the audio format ahead
        # of time we can pass the sample rate and channel count here.
        output_emitter.initialize(
            request_id=request_id,
            sample_rate=self._tts.sample_rate,
            num_channels=self._tts.num_channels,
            mime_type="audio/pcm",
        )
        try:
            total_bytes = 0
            async for audio_bytes in self._fetch_pcm_audio(self._input_text):
                output_emitter.push(audio_bytes)
                total_bytes += len(audio_bytes)

            _logger.debug(
                f"Chunked stream complete: {total_bytes} bytes for request {request_id}"
            )
        except Exception as e:
            _logger.error(f"TTS API error in chunked stream {request_id}: {e}")
            raise tts.APIError(f"Error during chunked TTS synthesis: {e}") from e

    async def _fetch_pcm_audio(self, text: str) -> AsyncGenerator[bytes, None]:
        """Yield PCM audio chunks for the supplied text."""
        session = await self._tts._ensure_session()
        request_data = {
            "text": text,
            "voice": self._opts.voice,
            "output_format": "pcm",
            "stream": False,
            "model": "indus-tts-v1",
            "api_key": self._opts.api_key,
            "normalize": self._opts.normalize,
            "speed": self._opts.speed,
            "pitch_shift": self._opts.pitch_shift,
            "loudness_db": self._opts.loudness_db,
        }
        url = f"{self._opts.base_url}/v1/audio/speech"
        _logger.info(f"Requesting TTS for text: {text[:50]}... (voice: {self._opts.voice})")
        try:
            async with session.post(
                url,
                json=request_data,
                headers={"Content-Type": "application/json"},
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    _logger.error(f"TTS API error response: {error_text}")
                    raise tts.APIError(
                        f"TTS API returned {response.status}: {error_text}"
                    )
                total_bytes = 0
                async for chunk in response.content.iter_chunked(PCM_CHUNK_SIZE):
                    if chunk:
                        total_bytes += len(chunk)
                        yield chunk
                _logger.debug(f"Received {total_bytes} bytes of PCM audio")
        except aiohttp.ClientError as e:
            _logger.error(f"HTTP client error: {e}")
            raise APIConnectionError(f"HTTP client error: {e}") from e
        except Exception as e:
            _logger.error(f"Unexpected error in _fetch_pcm_audio: {e}")
            raise tts.APIError(f"Unexpected error: {e}") from e


class SynthesizeStream(tts.SynthesizeStream):
    """Realtime streaming synthesiser for text input."""

    def __init__(
        self,
        *,
        tts: TTS,
        conn_options: APIConnectOptions,
    ):
        super().__init__(tts=tts, conn_options=conn_options)
        self._tts = tts
        # Copy options for this stream; modifications should not affect the parent
        self._opts = replace(self._tts._opts)
        # Channel used to communicate tokenised segments from the input
        self._segments_ch = utils.aio.Chan[tokenize.WordStream]()

    def _mark_started(self) -> None:
        """Mark the start of synthesis for metrics collection."""
        super()._mark_started()

    async def _run(self, output_emitter: tts.AudioEmitter) -> None:
        """Continuously process tokenised segments and stream audio."""
        request_id = utils.shortuuid()
        output_emitter.initialize(
            request_id=request_id,
            sample_rate=self._tts.sample_rate,
            num_channels=self._tts.num_channels,
            mime_type="audio/pcm",
            stream=True,
        )
        input_task = asyncio.create_task(self._tokenize_input())
        segment_id_counter = 0
        try:
            async for word_stream in self._segments_ch:
                tokens: list[str] = []
                async for ev in word_stream:
                    tokens.append(ev.token)
                segment_text = self._opts.word_tokenizer.format_words(tokens)
                if not segment_text.strip():
                    continue
                self._mark_started()
                segment_id = f"{request_id}-{segment_id_counter}"
                segment_id_counter += 1
                _logger.info(f"Processing segment {segment_id}: {segment_text[:50]}...")
                output_emitter.start_segment(segment_id=segment_id)
                segment_bytes = 0
                async for audio_bytes in self._fetch_pcm_audio(segment_text):
                    output_emitter.push(audio_bytes)
                    segment_bytes += len(audio_bytes)
                output_emitter.end_segment()
                _logger.debug(
                    f"Segment {segment_id} complete: {segment_bytes} bytes"
                )
        except Exception as e:
            _logger.error(f"TTS API error in synthesis stream: {e}")
            raise tts.APIError(f"Error during streaming TTS synthesis: {e}") from e
        finally:
            await utils.aio.gracefully_cancel(input_task)

    @utils.log_exceptions(logger=_logger)
    async def _tokenize_input(self) -> None:
        """Read strings from the input channel and convert to word streams."""
        word_stream: tokenize.WordStream | None = None
        async for data in self._input_ch:
            if isinstance(data, str):
                if word_stream is None:
                    word_stream = self._opts.word_tokenizer.stream()
                    self._segments_ch.send_nowait(word_stream)
                word_stream.push_text(data)
            elif isinstance(data, self._FlushSentinel):
                if word_stream:
                    word_stream.end_input()
                word_stream = None
        if word_stream:
            word_stream.end_input()
        self._segments_ch.close()

    async def _fetch_pcm_audio(self, text: str) -> AsyncGenerator[bytes, None]:
        """Yield audio chunks for the given segment with streaming enabled."""
        session = await self._tts._ensure_session()
        request_data = {
            "text": text,
            "voice": self._opts.voice,
            "output_format": "pcm",
            "stream": True,
            "model": "indus-tts-v1",
            "api_key": self._opts.api_key,
            "normalize": self._opts.normalize,
            "speed": self._opts.speed,
            "pitch_shift": self._opts.pitch_shift,
            "loudness_db": self._opts.loudness_db,
        }
        url = f"{self._opts.base_url}/v1/audio/speech"
        try:
            async with session.post(
                url,
                json=request_data,
                headers={"Content-Type": "application/json"},
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    _logger.error(f"TTS streaming API error: {error_text}")
                    raise tts.APIError(
                        f"TTS API returned {response.status}: {error_text}"
                    )
                total_bytes = 0
                async for chunk in response.content.iter_chunked(PCM_CHUNK_SIZE):
                    if chunk:
                        total_bytes += len(chunk)
                        yield chunk
                _logger.debug(
                    f"Received {total_bytes} bytes of PCM audio for streaming"
                )
        except aiohttp.ClientError as e:
            _logger.error(f"HTTP client error: {e}")
            raise APIConnectionError(f"HTTP client error: {e}") from e
        except Exception as e:
            _logger.error(f"Unexpected error in streaming _fetch_pcm_audio: {e}")
            raise tts.APIError(f"Unexpected error: {e}") from e

    async def aclose(self) -> None:
        """Close the stream and its associated resources."""
        _logger.debug("Closing SynthesizeStream")
        await super().aclose()
        self._segments_ch.close()


# Alias for backwards compatibility.  Older code may import
# ``FastAPITTS`` from this module.
FastAPITTS = TTS
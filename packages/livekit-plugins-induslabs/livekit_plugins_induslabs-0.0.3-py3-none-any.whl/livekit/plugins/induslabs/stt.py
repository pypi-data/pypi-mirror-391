"""IndusLabs Speech-to-text plugin for Livekit Agents.

The plugin monitors incoming audio frames, performs basic energy/VAD gating to
segment utterances, and submits finished utterances to a remote HTTP endpoint
for transcription. Responses are forwarded to the LiveKit agent pipeline as
`SpeechEvent` messages.
"""

import asyncio  # keep event loop helpers available for future extensions
import weakref
import numpy as np
import aiohttp
import tempfile
import os
import wave
import webrtcvad
import json
from typing import Optional

from livekit import rtc
from livekit.agents import (
    DEFAULT_API_CONNECT_OPTIONS,
    APIConnectOptions,
    stt,
)
from livekit.agents.stt import SpeechEvent, SpeechData, SpeechEventType
from livekit.agents.types import NOT_GIVEN, NotGivenOr

import logging
logger = logging.getLogger("pluggin")  # log under the same namespace as other plugins

REMOTE_API_URL = "https://voice.induslabs.io/v1/audio/transcribe"
REMOTE_API_KEY = os.getenv("INDUSLABS_API_KEY")

FRAME_MS = 20                 # VAD supports 10, 20, or 30 ms
VAD_AGGRESSIVENESS = 2        # 0..3 (2 = balanced, minor bg reduction)
SPEECH_START_MS = 250         # ms voiced required to trigger speech
SPEECH_END_MS = 1200           # ms silence required to mark EOU
MAX_UTTERANCE_S = 12.0        # safety cap (cut very long utterances)

ENERGY_THRESHOLD = 0.0012   # RMS gate (~ -52 dBFS), mild filter

class STTOptions:
    def __init__(self, sample_rate=16000, language: Optional[str] = None):
        """Runtime parameters that can be tweaked per stream."""
        self.sample_rate = sample_rate
        self.language = language


class STT(stt.STT):
    def __init__(self, *, sample_rate: int = 16000, language: Optional[str] = None):
        super().__init__(
            capabilities=stt.STTCapabilities(streaming=True, interim_results=True)
        )
        self._opts = STTOptions(sample_rate=sample_rate, language=language)
        self._streams = weakref.WeakSet[SpeechStream]()  # track live streams without hard refs

    @property
    def model(self) -> str:
        return "remote-faster-whisper"

    @property
    def provider(self) -> str:
        return "Remote-API"

    def stream(
        
        self,
        *,
        language: NotGivenOr[str] = NOT_GIVEN,
        conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS,
    ) -> "SpeechStream":
        opts = STTOptions(
            sample_rate=self._opts.sample_rate,
            language=self._opts.language if (language is NOT_GIVEN or not language) else language,
        )
        
        # Each call to `stream` spawns an independent speech stream with its own state.
        stream = SpeechStream(stt=self, opts=opts, conn_options=conn_options)
        self._streams.add(stream)
        return stream

    async def _recognize_impl(self, audio: bytes, *, language: Optional[str] = None):
        raise NotImplementedError("Only streaming mode is supported for this plugin.")


class SpeechStream(stt.SpeechStream):
    def __init__(self, *, stt: STT, opts: STTOptions, conn_options: APIConnectOptions):
        super().__init__(stt=stt, conn_options=conn_options, sample_rate=opts.sample_rate)
        self._opts = opts

        # VAD / EOU state
        self._vad = webrtcvad.Vad(VAD_AGGRESSIVENESS)
        self._in_speech = False
        self._voiced_ms = 0
        self._unvoiced_ms = 0

        # Buffers
        self._utterance_buffer_f32: list[float] = []
        self._seconds_in_utterance = 0.0

        # frame size
        self._frame_samples = int(self._opts.sample_rate * FRAME_MS / 1000)
        self._last_text = None

    def update_options(self, *, language: Optional[str] = None) -> None:
        self._opts.language = language

    # ---------- Helpers ----------
    def _int16_to_float32(self, pcm16: np.ndarray) -> np.ndarray:
        # Normalize 16-bit PCM audio into float32 range [-1.0, 1.0].
        return pcm16.astype(np.float32) / 32768.0

    def _rms_energy(self, pcm_f32: np.ndarray) -> float:
        # Root-mean-square amplitude used as a quick silence detector.
        return np.sqrt(np.mean(pcm_f32 ** 2))

    async def _write_wav(self, pcm_f32: np.ndarray) -> str:
        """Persist the utterance into a temporary WAV file for the remote API."""
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        tmp_path = tmp.name
        tmp.close()

        pcm_clip = np.clip(pcm_f32, -1.0, 1.0)
        pcm16 = (pcm_clip * 32767.0).astype(np.int16)

        with wave.open(tmp_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self._opts.sample_rate)
            wf.writeframes(pcm16.tobytes())

        return tmp_path

    async def _send_utterance(self, pcm_f32: np.ndarray) -> str:
        logger.info(f"Sending utterance with language={self._opts.language}")

        """Send one utterance to remote STT."""
        if pcm_f32.size == 0:
            return ""

        if not REMOTE_API_KEY:
            logger.error("REMOTE_STT_API_KEY not configured; skipping transcription.")
            return ""

        tmp_path = await self._write_wav(pcm_f32)
        try:
            async with aiohttp.ClientSession() as session:
                with open(tmp_path, "rb") as wav_file:
                    file_bytes = wav_file.read()

                form = aiohttp.FormData()
                form.add_field(
                    "file",
                    file_bytes,
                    filename="utterance.wav",
                    content_type="audio/wav",
                )
                form.add_field("api_key", REMOTE_API_KEY)

                # only send language if user specified
                if self._opts.language:
                    form.add_field("language", self._opts.language)

                headers = {"Accept": "text/event-stream"}

                async with session.post(
                    REMOTE_API_URL,
                    data=form,
                    headers=headers,
                ) as resp:
                    if resp.status != 200:
                        logger.error(
                            "Remote STT failed %s: %s",
                            resp.status,
                            await resp.text(),
                        )
                        return ""

                    final_text = ""
                    buffer = ""

                    async for chunk in resp.content.iter_chunked(1024):
                        if not chunk:
                            continue
                        buffer += chunk.decode("utf-8", errors="ignore")

                        while "\n" in buffer:
                            line, buffer = buffer.split("\n", 1)
                            line = line.strip()
                            if not line or line.startswith(":"):
                                continue
                            if not line.startswith("data:"):
                                continue
                            payload = line[5:].strip()
                            if not payload:
                                continue
                            try:
                                msg = json.loads(payload)
                            except json.JSONDecodeError as exc:
                                logger.debug("Failed to decode SSE payload: %s", exc)
                                continue

                            msg_type = msg.get("type")
                            if msg_type == "final":
                                final_text = msg.get("text", "")
                                return final_text
                            if msg_type == "chunk_final" and not final_text:
                                final_text = msg.get("text", "")

                    return final_text
        finally:
            try:
                os.remove(tmp_path)
            except Exception:
                pass

    def _handle_frame_for_eou(self, frame_i16: np.ndarray, frame_f32: np.ndarray) -> Optional[str]:
        """
        Return: None, "START", "END"
        """
        # RMS gate (minor background filter to skip obvious silence before VAD)
        if self._rms_energy(frame_f32) < ENERGY_THRESHOLD:
            is_speech = False
        else:
            is_speech = self._vad.is_speech(frame_i16.tobytes(), self._opts.sample_rate)

        if not self._in_speech:
            if is_speech:
                self._voiced_ms += FRAME_MS
                if self._voiced_ms >= SPEECH_START_MS:
                    self._in_speech = True
                    self._unvoiced_ms = 0
                    return "START"
            else:
                self._voiced_ms = 0
        else:
            if is_speech:
                self._unvoiced_ms = 0
            else:
                self._unvoiced_ms += FRAME_MS
                if self._unvoiced_ms >= SPEECH_END_MS:
                    self._in_speech = False
                    self._voiced_ms = 0
                    self._unvoiced_ms = 0
                    return "END"
        return None

    async def _finalize_and_send_if_any(self):
        if not self._utterance_buffer_f32:
            return
        # When an utterance finishes, convert buffers into a dense array and reset state.
        pcm = np.array(self._utterance_buffer_f32, dtype=np.float32)
        self._utterance_buffer_f32.clear()
        self._seconds_in_utterance = 0.0

        text = await self._send_utterance(pcm)
        if text and text != self._last_text:
            self._last_text = text
            ev = SpeechEvent(
                type=SpeechEventType.FINAL_TRANSCRIPT,
                alternatives=[SpeechData(language=self._opts.language or "auto",
                                         text=text, confidence=1.0)],
            )
            logger.info(f"EOU final transcript: {text}")
            self._event_ch.send_nowait(ev)

    # ---------- Main loop ----------
    async def _run(self) -> None:
        carry_i16 = np.zeros((0,), dtype=np.int16)  # store partial frames until enough samples arrive

        while True:
            try:
                # Pull events from the LiveKit audio channel; audio frames are processed sequentially.
                item = await self._input_ch.recv()

                if isinstance(item, self._FlushSentinel):
                    # Flush signals mark end-of-stream; emit any trailing transcript.
                    await self._finalize_and_send_if_any()
                    break

                if not isinstance(item, rtc.AudioFrame):
                    continue

                chunk_i16 = np.frombuffer(item.data, dtype=np.int16)

                if carry_i16.size > 0:
                    # Prepend leftover samples from the previous iteration.
                    chunk_i16 = np.concatenate([carry_i16, chunk_i16])
                    carry_i16 = np.zeros((0,), dtype=np.int16)

                total = chunk_i16.size
                pos = 0
                while pos + self._frame_samples <= total:
                    frame_i16 = chunk_i16[pos:pos + self._frame_samples]
                    pos += self._frame_samples
                    frame_f32 = self._int16_to_float32(frame_i16)

                    marker = self._handle_frame_for_eou(frame_i16, frame_f32)

                    if self._in_speech or marker == "START":
                        self._utterance_buffer_f32.extend(frame_f32.tolist())
                        self._seconds_in_utterance += FRAME_MS / 1000.0
                        if self._seconds_in_utterance >= MAX_UTTERANCE_S:
                            # Safety: force-send if the utterance grows too long.
                            await self._finalize_and_send_if_any()
                            self._in_speech = False
                            self._voiced_ms = 0
                            self._unvoiced_ms = 0

                    if marker == "END":
                        await self._finalize_and_send_if_any()

                if pos < total:
                    # Keep trailing samples that were not large enough for a full frame.
                    carry_i16 = chunk_i16[pos:]

            except Exception as e:
                logger.exception(f"Error in remote STT stream: {e}")
                try:
                    await self._finalize_and_send_if_any()
                except Exception:
                    pass
                break

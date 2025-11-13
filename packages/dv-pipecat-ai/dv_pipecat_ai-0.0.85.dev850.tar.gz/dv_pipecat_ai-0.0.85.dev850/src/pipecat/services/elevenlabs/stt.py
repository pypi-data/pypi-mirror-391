#
# Copyright (c) 2024–2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

"""ElevenLabs speech-to-text service implementations."""

import asyncio
import base64
import io
import json
import urllib.parse
from typing import Any, AsyncGenerator, Dict, Literal, Optional

import aiohttp
from loguru import logger
from pydantic import BaseModel

from pipecat.frames.frames import (
    CancelFrame,
    EndFrame,
    ErrorFrame,
    Frame,
    InterimTranscriptionFrame,
    StartFrame,
    TranscriptionFrame,
    UserStartedSpeakingFrame,
    UserStoppedSpeakingFrame,
)
from pipecat.processors.frame_processor import FrameDirection
from pipecat.services.stt_service import SegmentedSTTService, WebsocketSTTService
from pipecat.transcriptions.language import Language
from pipecat.utils.time import time_now_iso8601
from pipecat.utils.tracing.service_decorators import traced_stt

try:
    from websockets.asyncio.client import connect as websocket_connect
    from websockets.protocol import State
except ModuleNotFoundError:
    websocket_connect = None  # type: ignore[assignment]
    State = None  # type: ignore[assignment]


def language_to_elevenlabs_language(language: Language) -> Optional[str]:
    """Convert a Language enum to ElevenLabs language code.

    Source:
        https://elevenlabs.io/docs/capabilities/speech-to-text

    Args:
        language: The Language enum value to convert.

    Returns:
        The corresponding ElevenLabs language code, or None if not supported.
    """
    BASE_LANGUAGES = {
        Language.AF: "afr",  # Afrikaans
        Language.AM: "amh",  # Amharic
        Language.AR: "ara",  # Arabic
        Language.HY: "hye",  # Armenian
        Language.AS: "asm",  # Assamese
        Language.AST: "ast",  # Asturian
        Language.AZ: "aze",  # Azerbaijani
        Language.BE: "bel",  # Belarusian
        Language.BN: "ben",  # Bengali
        Language.BS: "bos",  # Bosnian
        Language.BG: "bul",  # Bulgarian
        Language.MY: "mya",  # Burmese
        Language.YUE: "yue",  # Cantonese
        Language.CA: "cat",  # Catalan
        Language.CEB: "ceb",  # Cebuano
        Language.NY: "nya",  # Chichewa
        Language.HR: "hrv",  # Croatian
        Language.CS: "ces",  # Czech
        Language.DA: "dan",  # Danish
        Language.NL: "nld",  # Dutch
        Language.EN: "eng",  # English
        Language.ET: "est",  # Estonian
        Language.FIL: "fil",  # Filipino
        Language.FI: "fin",  # Finnish
        Language.FR: "fra",  # French
        Language.FF: "ful",  # Fulah
        Language.GL: "glg",  # Galician
        Language.LG: "lug",  # Ganda
        Language.KA: "kat",  # Georgian
        Language.DE: "deu",  # German
        Language.EL: "ell",  # Greek
        Language.GU: "guj",  # Gujarati
        Language.HA: "hau",  # Hausa
        Language.HE: "heb",  # Hebrew
        Language.HI: "hin",  # Hindi
        Language.HU: "hun",  # Hungarian
        Language.IS: "isl",  # Icelandic
        Language.IG: "ibo",  # Igbo
        Language.ID: "ind",  # Indonesian
        Language.GA: "gle",  # Irish
        Language.IT: "ita",  # Italian
        Language.JA: "jpn",  # Japanese
        Language.JV: "jav",  # Javanese
        Language.KEA: "kea",  # Kabuverdianu
        Language.KN: "kan",  # Kannada
        Language.KK: "kaz",  # Kazakh
        Language.KM: "khm",  # Khmer
        Language.KO: "kor",  # Korean
        Language.KU: "kur",  # Kurdish
        Language.KY: "kir",  # Kyrgyz
        Language.LO: "lao",  # Lao
        Language.LV: "lav",  # Latvian
        Language.LN: "lin",  # Lingala
        Language.LT: "lit",  # Lithuanian
        Language.LUO: "luo",  # Luo
        Language.LB: "ltz",  # Luxembourgish
        Language.MK: "mkd",  # Macedonian
        Language.MS: "msa",  # Malay
        Language.ML: "mal",  # Malayalam
        Language.MT: "mlt",  # Maltese
        Language.ZH: "zho",  # Mandarin Chinese
        Language.MI: "mri",  # Māori
        Language.MR: "mar",  # Marathi
        Language.MN: "mon",  # Mongolian
        Language.NE: "nep",  # Nepali
        Language.NSO: "nso",  # Northern Sotho
        Language.NO: "nor",  # Norwegian
        Language.OC: "oci",  # Occitan
        Language.OR: "ori",  # Odia
        Language.PS: "pus",  # Pashto
        Language.FA: "fas",  # Persian
        Language.PL: "pol",  # Polish
        Language.PT: "por",  # Portuguese
        Language.PA: "pan",  # Punjabi
        Language.RO: "ron",  # Romanian
        Language.RU: "rus",  # Russian
        Language.SR: "srp",  # Serbian
        Language.SN: "sna",  # Shona
        Language.SD: "snd",  # Sindhi
        Language.SK: "slk",  # Slovak
        Language.SL: "slv",  # Slovenian
        Language.SO: "som",  # Somali
        Language.ES: "spa",  # Spanish
        Language.SW: "swa",  # Swahili
        Language.SV: "swe",  # Swedish
        Language.TA: "tam",  # Tamil
        Language.TG: "tgk",  # Tajik
        Language.TE: "tel",  # Telugu
        Language.TH: "tha",  # Thai
        Language.TR: "tur",  # Turkish
        Language.UK: "ukr",  # Ukrainian
        Language.UMB: "umb",  # Umbundu
        Language.UR: "urd",  # Urdu
        Language.UZ: "uzb",  # Uzbek
        Language.VI: "vie",  # Vietnamese
        Language.CY: "cym",  # Welsh
        Language.WO: "wol",  # Wolof
        Language.XH: "xho",  # Xhosa
        Language.ZU: "zul",  # Zulu
    }

    result = BASE_LANGUAGES.get(language)

    # If not found in base languages, try to find the base language from a variant
    if not result:
        lang_str = str(language.value)
        base_code = lang_str.split("-")[0].lower()
        result = base_code if base_code in BASE_LANGUAGES.values() else None

    return result


def elevenlabs_language_code_to_language(language_code: Optional[str]) -> Optional[Language]:
    """Convert an ElevenLabs language code back to a Language enum value."""
    if not language_code:
        return None

    normalized = language_code.lower()
    for language in Language:
        code = language_to_elevenlabs_language(language)
        if code and code.lower() == normalized:
            return language
    return None


class ElevenLabsSTTService(SegmentedSTTService):
    """Speech-to-text service using ElevenLabs' file-based API.

    This service uses ElevenLabs' Speech-to-Text API to perform transcription on audio
    segments. It inherits from SegmentedSTTService to handle audio buffering and speech detection.
    The service uploads audio files to ElevenLabs and receives transcription results directly.
    """

    class InputParams(BaseModel):
        """Configuration parameters for ElevenLabs STT API.

        Parameters:
            language: Target language for transcription.
            tag_audio_events: Whether to include audio events like (laughter), (coughing), in the transcription.
        """

        language: Optional[Language] = None
        tag_audio_events: bool = True

    def __init__(
        self,
        *,
        api_key: str,
        aiohttp_session: aiohttp.ClientSession,
        base_url: str = "https://api.elevenlabs.io",
        model: str = "scribe_v1",
        sample_rate: Optional[int] = None,
        params: Optional[InputParams] = None,
        **kwargs,
    ):
        """Initialize the ElevenLabs STT service.

        Args:
            api_key: ElevenLabs API key for authentication.
            aiohttp_session: aiohttp ClientSession for HTTP requests.
            base_url: Base URL for ElevenLabs API.
            model: Model ID for transcription. Defaults to "scribe_v1".
            sample_rate: Audio sample rate in Hz. If not provided, uses the pipeline's rate.
            params: Configuration parameters for the STT service.
            **kwargs: Additional arguments passed to SegmentedSTTService.
        """
        super().__init__(
            sample_rate=sample_rate,
            **kwargs,
        )

        params = params or ElevenLabsSTTService.InputParams()

        self._api_key = api_key
        self._base_url = base_url
        self._session = aiohttp_session
        self._model_id = model
        self._tag_audio_events = params.tag_audio_events

        self._settings = {
            "language": self.language_to_service_language(params.language)
            if params.language
            else "eng",
        }

    def can_generate_metrics(self) -> bool:
        """Check if the service can generate processing metrics.

        Returns:
            True, as ElevenLabs STT service supports metrics generation.
        """
        return True

    def language_to_service_language(self, language: Language) -> Optional[str]:
        """Convert a Language enum to ElevenLabs service-specific language code.

        Args:
            language: The language to convert.

        Returns:
            The ElevenLabs-specific language code, or None if not supported.
        """
        return language_to_elevenlabs_language(language)

    async def set_language(self, language: Language):
        """Set the transcription language.

        Args:
            language: The language to use for speech-to-text transcription.
        """
        self.logger.info(f"Switching STT language to: [{language}]")
        self._settings["language"] = self.language_to_service_language(language)

    async def set_model(self, model: str):
        """Set the STT model.

        Args:
            model: The model name to use for transcription.

        Note:
            ElevenLabs STT API does not currently support model selection.
            This method is provided for interface compatibility.
        """
        await super().set_model(model)
        self.logger.info(f"Model setting [{model}] noted, but ElevenLabs STT uses default model")

    async def _transcribe_audio(self, audio_data: bytes) -> dict:
        """Upload audio data to ElevenLabs and get transcription result.

        Args:
            audio_data: Raw audio bytes in WAV format.

        Returns:
            The transcription result data.

        Raises:
            Exception: If transcription fails or returns an error.
        """
        url = f"{self._base_url}/v1/speech-to-text"
        headers = {"xi-api-key": self._api_key}

        # Create form data with the audio file
        data = aiohttp.FormData()
        data.add_field(
            "file",
            io.BytesIO(audio_data),
            filename="audio.wav",
            content_type="audio/x-wav",
        )

        # Add required model_id, language_code, and tag_audio_events
        data.add_field("model_id", self._model_id)
        data.add_field("language_code", self._settings["language"])
        data.add_field("tag_audio_events", str(self._tag_audio_events).lower())

        async with self._session.post(url, data=data, headers=headers) as response:
            if response.status != 200:
                error_text = await response.text()
                self.logger.error(f"ElevenLabs transcription error: {error_text}")
                raise Exception(f"Transcription failed with status {response.status}: {error_text}")

            result = await response.json()
            return result

    @traced_stt
    async def _handle_transcription(
        self, transcript: str, is_final: bool, language: Optional[str] = None
    ):
        """Handle a transcription result with tracing."""
        await self.stop_ttfb_metrics()
        await self.stop_processing_metrics()

    async def run_stt(self, audio: bytes) -> AsyncGenerator[Frame, None]:
        """Transcribe an audio segment using ElevenLabs' STT API.

        Args:
            audio: Raw audio bytes in WAV format (already converted by base class).

        Yields:
            Frame: TranscriptionFrame containing the transcribed text, or ErrorFrame on failure.

        Note:
            The audio is already in WAV format from the SegmentedSTTService.
            Only non-empty transcriptions are yielded.
        """
        try:
            await self.start_processing_metrics()
            await self.start_ttfb_metrics()

            # Upload audio and get transcription result directly
            result = await self._transcribe_audio(audio)

            # Extract transcription text
            text = result.get("text", "").strip()
            if text:
                # Use the language_code returned by the API
                detected_language = result.get("language_code", "eng")

                await self._handle_transcription(text, True, detected_language)
                self.logger.debug(f"Transcription: [{text}]")

                yield TranscriptionFrame(
                    text,
                    self._user_id,
                    time_now_iso8601(),
                    detected_language,
                    result=result,
                )

        except Exception as e:
            self.logger.error(f"ElevenLabs STT error: {e}")
            yield ErrorFrame(f"ElevenLabs STT error: {str(e)}")


class ElevenLabsRealtimeSTTService(WebsocketSTTService):
    """Realtime speech-to-text service using ElevenLabs Scribe v2 WebSocket API."""

    class InputParams(BaseModel):
        """Realtime connection parameters derived from ElevenLabs documentation."""

        language: Optional[Language] = None
        commit_strategy: Literal["manual", "vad"] = "manual"
        vad_silence_threshold_secs: Optional[float] = None
        vad_threshold: Optional[float] = None
        min_speech_duration_ms: Optional[int] = None
        min_silence_duration_ms: Optional[int] = None

    def __init__(
        self,
        *,
        api_key: str,
        sample_rate: Optional[int] = None,
        model: str = "scribe_v2_realtime",
        url: str = "wss://api.elevenlabs.io/v1/speech-to-text/realtime",
        params: Optional["ElevenLabsRealtimeSTTService.InputParams"] = None,
        reconnect_on_error: bool = True,
        **kwargs,
    ):
        """Initialize the realtime STT service.

        Args:
            api_key: ElevenLabs API key for authentication.
            sample_rate: Optional input sample rate. Defaults to pipeline sample rate.
            model: Scribe realtime model identifier.
            url: WebSocket endpoint for realtime transcription.
            params: Optional realtime configuration options.
            reconnect_on_error: Whether to auto-reconnect on transient failures.
            **kwargs: Additional arguments forwarded to WebsocketSTTService.
        """
        if websocket_connect is None or State is None:
            logger.error(
                "In order to use ElevenLabsRealtimeSTTService, you need to "
                "`pip install pipecat-ai[elevenlabs]` (websockets extra)."
            )
            raise ModuleNotFoundError("Missing optional dependency: websockets")

        super().__init__(sample_rate=sample_rate, reconnect_on_error=reconnect_on_error, **kwargs)

        self._api_key = api_key
        self._url = url
        self.set_model_name(model)
        self._model = model
        self._params = params or ElevenLabsRealtimeSTTService.InputParams()
        self._language_override = self._params.language
        self._encoding = None
        self._receive_task: Optional[asyncio.Task] = None
        self._pending_final_message: Optional[Dict[str, Any]] = None
        self._pending_final_task: Optional[asyncio.Task] = None
        self._timestamp_merge_delay_s = 0.25
        self._ttfb_started = False

    @property
    def commit_strategy(self) -> str:
        """Return the configured commit strategy (manual or vad)."""
        return (self._params.commit_strategy or "manual").lower()

    def can_generate_metrics(self) -> bool:
        """Realtime ElevenLabs service supports latency metrics."""
        return True

    async def start(self, frame: StartFrame):
        """Start the realtime STT service and establish WebSocket connection."""
        await super().start(frame)
        self._encoding = self._determine_encoding(self.sample_rate)
        await self._connect()

    async def stop(self, frame: EndFrame):
        """Stop the realtime STT service and close WebSocket connection."""
        await super().stop(frame)
        await self._disconnect()

    async def cancel(self, frame: CancelFrame):
        """Cancel the realtime STT service and close WebSocket connection."""
        await super().cancel(frame)
        await self._disconnect()

    async def set_language(self, language: Language):
        """Update preferred transcription language (requires reconnect)."""
        self._language_override = language
        self._params.language = language
        if self._websocket:
            await self._disconnect()
            await self._connect()

    async def set_model(self, model: str):
        """Set the STT model and reconnect the WebSocket."""
        await super().set_model(model)
        self._model = model
        if self._websocket:
            await self._disconnect()
            await self._connect()

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        """Process frames and handle VAD events for commit strategy."""
        await super().process_frame(frame, direction)

        if isinstance(frame, UserStartedSpeakingFrame):
            if frame.emulated:
                return
            self._ttfb_started = False
            await self.start_processing_metrics()
        elif isinstance(frame, UserStoppedSpeakingFrame):
            if frame.emulated:
                return
            if self.commit_strategy == "manual":
                await self._send_commit()

    async def run_stt(self, audio: bytes) -> AsyncGenerator[Frame, None]:
        """Stream audio chunks over the ElevenLabs realtime WebSocket."""
        if not audio:
            yield None
            return

        await self._ensure_connection()
        await self._send_audio_chunk(audio)
        yield None

    async def _ensure_connection(self):
        if not self._websocket or self._websocket.state is State.CLOSED:
            await self._connect()

    async def _connect(self):
        await self._connect_websocket()
        if self._websocket and not self._receive_task:
            self._receive_task = asyncio.create_task(self._receive_task_handler(self._report_error))

    async def _disconnect(self):
        if self._receive_task:
            await self.cancel_task(self._receive_task)
            self._receive_task = None

        await self._clear_pending_final()
        await self._disconnect_websocket()

    async def _connect_websocket(self):
        try:
            if self._websocket and self._websocket.state is State.OPEN:
                return

            ws_url = self._build_websocket_url()
            headers = {"xi-api-key": self._api_key}
            self.logger.debug(f"Connecting to ElevenLabs realtime STT at {ws_url}")
            self._websocket = await websocket_connect(ws_url, additional_headers=headers)
            await self._call_event_handler("on_connected")
        except Exception as e:
            self.logger.error(f"{self} unable to connect to ElevenLabs realtime STT: {e}")
            self._websocket = None
            await self._call_event_handler("on_connection_error", f"{e}")

    async def _disconnect_websocket(self):
        try:
            await self.stop_all_metrics()
            if self._websocket and self._websocket.state is State.OPEN:
                self.logger.debug("Disconnecting from ElevenLabs realtime STT")
                await self._websocket.close()
        except Exception as e:
            self.logger.error(f"{self} error closing ElevenLabs realtime websocket: {e}")
        finally:
            self._websocket = None
            await self._call_event_handler("on_disconnected")

    async def _receive_messages(self):
        async for message in self._get_websocket():
            await self._process_event(message)

    def _get_websocket(self):
        if not self._websocket:
            raise RuntimeError("ElevenLabs realtime websocket not connected")
        return self._websocket

    async def _process_event(self, message: Any):
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            self.logger.warning(f"ElevenLabs realtime STT sent invalid JSON: {message}")
            return

        message_type = data.get("message_type")

        if message_type == "session_started":
            self.logger.debug("ElevenLabs realtime session started")
            return

        if message_type == "partial_transcript":
            await self._emit_partial_transcript(data)
        elif message_type == "committed_transcript":
            await self._handle_committed_transcript(data)
        elif message_type == "committed_transcript_with_timestamps":
            await self._handle_committed_transcript_with_timestamps(data)
        elif message_type in {
            "auth_error",
            "quota_exceeded",
            "transcriber_error",
            "input_error",
            "error",
        }:
            fatal = message_type in {"auth_error", "quota_exceeded", "error"}
            description = data.get("error", data)
            await self.push_error(
                ErrorFrame(f"ElevenLabs realtime error: {description}", fatal=fatal)
            )
        else:
            self.logger.debug(f"Unhandled ElevenLabs realtime message: {data}")

    async def _emit_partial_transcript(self, data: Dict[str, Any]):
        text = (data.get("text") or data.get("transcript") or "").strip()
        if not text:
            return

        language = (
            elevenlabs_language_code_to_language(data.get("language_code"))
            or self._language_override
        )
        await self.stop_ttfb_metrics()

        await self.push_frame(
            InterimTranscriptionFrame(
                text,
                self._user_id,
                time_now_iso8601(),
                language,
                result=data,
            )
        )

    async def _handle_committed_transcript(self, data: Dict[str, Any]):
        if self._pending_final_message:
            await self._emit_transcription(self._pending_final_message)
            self._pending_final_message = None

        self._pending_final_message = data
        await self._schedule_pending_final_emit()

    async def _handle_committed_transcript_with_timestamps(self, data: Dict[str, Any]):
        if self._pending_final_message:
            merged = {**self._pending_final_message, **data}
            await self._emit_transcription(merged)
            await self._clear_pending_final()
        else:
            await self._emit_transcription(data)

    async def _schedule_pending_final_emit(self):
        await self._clear_pending_final(timer_only=True)
        self._pending_final_task = asyncio.create_task(self._emit_pending_after_delay())

    async def _emit_pending_after_delay(self):
        try:
            await asyncio.sleep(self._timestamp_merge_delay_s)
            if self._pending_final_message:
                await self._emit_transcription(self._pending_final_message)
                self._pending_final_message = None
        except asyncio.CancelledError:
            pass
        finally:
            self._pending_final_task = None

    async def _clear_pending_final(self, timer_only: bool = False):
        if self._pending_final_task:
            await self.cancel_task(self._pending_final_task)
            self._pending_final_task = None

        if not timer_only:
            self._pending_final_message = None

    async def _emit_transcription(self, data: Dict[str, Any]):
        text = (data.get("text") or data.get("transcript") or "").strip()
        if not text:
            return

        language = (
            elevenlabs_language_code_to_language(data.get("language_code"))
            or self._language_override
        )
        await self.stop_ttfb_metrics()

        frame = TranscriptionFrame(
            text,
            self._user_id,
            time_now_iso8601(),
            language,
            result=data,
        )

        await self.push_frame(frame)
        await self._handle_transcription(text, True, language)
        await self.stop_processing_metrics()

    async def _send_audio_chunk(self, audio: bytes):
        if not audio or not self._websocket:
            return

        if not self._ttfb_started:
            await self.start_ttfb_metrics()
            self._ttfb_started = True

        payload = {
            "message_type": "input_audio_chunk",
            "audio_base_64": base64.b64encode(audio).decode("ascii"),
            "commit": False,
            "sample_rate": self.sample_rate,
        }
        await self._websocket.send(json.dumps(payload))

    async def _send_commit(self):
        if not self._websocket:
            return
        payload = {
            "message_type": "input_audio_chunk",
            "audio_base_64": "",
            "commit": True,
            "sample_rate": self.sample_rate,
        }
        await self._websocket.send(json.dumps(payload))

    def _build_websocket_url(self) -> str:
        if not self.sample_rate:
            raise ValueError(
                "ElevenLabs realtime STT requires a valid sample rate (start() must run first)."
            )

        params = {
            "model_id": self._model,
            "encoding": self._encoding or "pcm_16000",
            "sample_rate": str(self.sample_rate),
            "commit_strategy": self.commit_strategy,
        }

        language_code = (
            language_to_elevenlabs_language(self._language_override)
            if self._language_override
            else None
        )
        if language_code:
            params["language_code"] = language_code

        if self._params.vad_silence_threshold_secs is not None:
            params["vad_silence_threshold_secs"] = str(self._params.vad_silence_threshold_secs)
        if self._params.vad_threshold is not None:
            params["vad_threshold"] = str(self._params.vad_threshold)
        if self._params.min_speech_duration_ms is not None:
            params["min_speech_duration_ms"] = str(self._params.min_speech_duration_ms)
        if self._params.min_silence_duration_ms is not None:
            params["min_silence_duration_ms"] = str(self._params.min_silence_duration_ms)

        return f"{self._url}?{urllib.parse.urlencode(params)}"

    def _determine_encoding(self, sample_rate: int) -> str:
        if not sample_rate:
            raise ValueError("ElevenLabs realtime STT requires a valid sample rate.")

        supported_rates = {8000, 16000, 22050, 24000, 44100, 48000}
        if sample_rate not in supported_rates:
            raise ValueError(
                f"ElevenLabs realtime STT supports sample rates {sorted(supported_rates)}. "
                f"Received {sample_rate} Hz."
            )
        return f"pcm_{sample_rate}"

    @traced_stt
    async def _handle_transcription(
        self, transcript: str, is_final: bool, language: Optional[Language] = None
    ):
        """Handle a transcription result with tracing."""
        # Metrics are stopped by the caller when needed.
        return

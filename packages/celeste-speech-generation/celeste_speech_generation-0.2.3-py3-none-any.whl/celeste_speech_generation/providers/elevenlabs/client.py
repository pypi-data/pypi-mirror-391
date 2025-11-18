"""ElevenLabs client implementation for speech generation."""

from collections.abc import AsyncIterator
from typing import Any, Unpack

import httpx

from celeste.artifacts import AudioArtifact
from celeste.mime_types import ApplicationMimeType, AudioMimeType
from celeste.parameters import ParameterMapper
from celeste_speech_generation.client import SpeechGenerationClient
from celeste_speech_generation.io import (
    SpeechGenerationInput,
    SpeechGenerationOutput,
    SpeechGenerationUsage,
)
from celeste_speech_generation.parameters import SpeechGenerationParameters

from . import config
from .parameters import ELEVENLABS_PARAMETER_MAPPERS
from .streaming import ElevenLabsSpeechGenerationStream
from .voices import ELEVENLABS_VOICES


class ElevenLabsSpeechGenerationClient(SpeechGenerationClient):
    """ElevenLabs client for speech generation."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return ELEVENLABS_PARAMETER_MAPPERS

    def _create_inputs(
        self,
        *args: Any,  # noqa: ANN401
        **parameters: Unpack[SpeechGenerationParameters],
    ) -> SpeechGenerationInput:
        """Map positional arguments to Input type."""
        if args:
            return SpeechGenerationInput(prompt=args[0])
        prompt = parameters.get("prompt")
        if prompt is None:
            msg = (
                "prompt is required (either as positional argument or keyword argument)"
            )
            raise ValueError(msg)
        return SpeechGenerationInput(prompt=prompt)

    @classmethod
    def _output_class(cls) -> type[SpeechGenerationOutput]:
        """Return the Output class for this client."""
        return SpeechGenerationOutput

    def _init_request(self, inputs: SpeechGenerationInput) -> dict[str, Any]:
        """Initialize request from ElevenLabs API format."""
        return {"text": inputs.prompt}

    def _parse_usage(self, response_data: dict[str, Any]) -> SpeechGenerationUsage:
        """Parse usage from response.

        ElevenLabs TTS doesn't return usage metrics in response,
        so we calculate characters_synthesized from the input.
        """
        # Usage is calculated in generate() override from input prompt length
        return SpeechGenerationUsage(characters_synthesized=None)

    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[SpeechGenerationParameters],
    ) -> AudioArtifact:
        """Parse content from response.

        Note: This method is not used for ElevenLabs TTS since we override generate()
        to handle binary responses. Kept for interface compliance.
        """
        # This should never be called for ElevenLabs TTS
        msg = "ElevenLabs TTS returns binary responses, use generate() override"
        raise NotImplementedError(msg)

    def _map_output_format_to_mime_type(
        self, output_format: str | None
    ) -> AudioMimeType:
        """Map ElevenLabs output_format string to AudioMimeType."""
        if output_format is None:
            return AudioMimeType.MP3

        # Parse format: {codec}_{sample_rate}_{bitrate}
        # e.g., mp3_44100_128, pcm_22050_16
        parts = output_format.split("_")
        if not parts:
            return AudioMimeType.MP3

        codec = parts[0].lower()
        codec_map: dict[str, AudioMimeType] = {
            "mp3": AudioMimeType.MP3,
            "pcm": AudioMimeType.PCM,
            "aac": AudioMimeType.AAC,
            "flac": AudioMimeType.FLAC,
        }
        return codec_map.get(codec, AudioMimeType.MP3)  # Default to MP3

    async def _make_request(
        self,
        request_body: dict[str, Any],
        **parameters: Unpack[SpeechGenerationParameters],
    ) -> httpx.Response:
        """Make HTTP request(s) and return response object."""
        # Extract voice_id from request_body (set by VoiceMapper)
        voice_id = request_body.pop("_voice_id", None)
        if voice_id is None:
            # Try to get from parameters as fallback
            voice_id = parameters.get("voice")
        if voice_id is None:
            # Use first voice from ELEVENLABS_VOICES as default (Rachel)
            voice_id = ELEVENLABS_VOICES[0].id

        # Set model_id from self.model.id (not from parameters)
        request_body["model_id"] = self.model.id

        # Build URL with voice_id in path
        endpoint = config.ENDPOINT.format(voice_id=voice_id)

        headers = {
            config.AUTH_HEADER_NAME: self.api_key.get_secret_value(),
            "Content-Type": ApplicationMimeType.JSON,
        }

        return await self.http_client.post(
            f"{config.BASE_URL}{endpoint}",
            headers=headers,
            json_body=request_body,
        )

    async def generate(
        self,
        *args: Any,  # noqa: ANN401
        **parameters: Unpack[SpeechGenerationParameters],
    ) -> SpeechGenerationOutput:
        """Generate speech from text.

        Override base generate() to handle binary audio response from ElevenLabs TTS.
        """
        inputs = self._create_inputs(*args, **parameters)
        inputs, parameters = self._validate_artifacts(inputs, **parameters)
        request_body = self._build_request(inputs, **parameters)
        response = await self._make_request(request_body, **parameters)
        self._handle_error_response(response)

        # Handle binary response (ElevenLabs TTS returns raw audio bytes, not JSON)
        audio_bytes = response.content
        if not audio_bytes:
            msg = "No audio data in response"
            raise ValueError(msg)

        # Determine MIME type from output_format parameter
        output_format = parameters.get("response_format") or "mp3_44100_128"
        mime_type = self._map_output_format_to_mime_type(output_format)

        # Calculate usage from input text length
        characters_synthesized = len(inputs.prompt)

        return self._output_class()(
            content=AudioArtifact(data=audio_bytes, mime_type=mime_type),
            usage=SpeechGenerationUsage(characters_synthesized=characters_synthesized),
            metadata={
                "raw_response": {
                    "content_length": len(audio_bytes),
                    "output_format": output_format,
                },
            },
        )

    def _stream_class(self) -> type[ElevenLabsSpeechGenerationStream]:
        """Return the Stream class for this client."""
        return ElevenLabsSpeechGenerationStream

    def _make_stream_request(
        self,
        request_body: dict[str, Any],
        **parameters: Unpack[SpeechGenerationParameters],
    ) -> AsyncIterator[dict[str, Any]]:
        """Make HTTP streaming request and return async iterator of binary audio chunks.

        ElevenLabs streams binary audio data, not JSON SSE events.
        We wrap the binary stream to yield dicts compatible with Stream interface.
        """
        # Extract voice_id from request_body (same as _make_request())
        voice_id = request_body.pop("_voice_id", None)
        if voice_id is None:
            # Try to get from parameters as fallback
            voice_id = parameters.get("voice")
        if voice_id is None:
            # Use first voice from ELEVENLABS_VOICES as default (Rachel)
            voice_id = ELEVENLABS_VOICES[0].id

        # Set model_id from self.model.id (not from parameters)
        request_body["model_id"] = self.model.id

        # Build URL with voice_id in path
        stream_endpoint = config.STREAM_ENDPOINT.format(voice_id=voice_id)

        headers = {
            config.AUTH_HEADER_NAME: self.api_key.get_secret_value(),
            "Content-Type": ApplicationMimeType.JSON,
        }

        # Return async iterator that wraps httpx binary streaming
        return self._stream_binary_audio(
            f"{config.BASE_URL}{stream_endpoint}",
            headers=headers,
            json_body=request_body,
        )

    async def _stream_binary_audio(
        self,
        url: str,
        headers: dict[str, str],
        json_body: dict[str, Any],
    ) -> AsyncIterator[dict[str, Any]]:
        """Stream binary audio data and yield as dict events.

        Wraps httpx streaming to yield dicts compatible with Stream interface.
        """
        client = await self.http_client._get_client()

        async with client.stream(
            "POST",
            url,
            json=json_body,
            headers=headers,
        ) as response:
            # Check for errors
            if not response.is_success:
                error_text = await response.aread()
                msg = f"HTTP {response.status_code}: {error_text.decode('utf-8', errors='ignore')}"
                raise httpx.HTTPStatusError(
                    msg,
                    request=response.request,
                    response=response,
                )

            # Stream binary audio chunks
            async for chunk in response.aiter_bytes():
                if chunk:
                    # Yield as dict to match Stream interface expectation
                    yield {"data": chunk}


__all__ = ["ElevenLabsSpeechGenerationClient"]

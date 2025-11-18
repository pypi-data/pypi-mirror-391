"""Google client implementation for speech generation."""

import base64
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
from .parameters import GOOGLE_PARAMETER_MAPPERS


class GoogleSpeechGenerationClient(SpeechGenerationClient):
    """Google client for speech generation."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return GOOGLE_PARAMETER_MAPPERS

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
        """Initialize request from Google contents array format."""
        contents = [
            {
                "parts": [{"text": inputs.prompt}],
            }
        ]

        generation_config: dict[str, Any] = {
            "responseModalities": ["AUDIO"],
            "speechConfig": {},
        }

        return {
            "contents": contents,
            "generationConfig": generation_config,
        }

    def _parse_usage(self, response_data: dict[str, Any]) -> SpeechGenerationUsage:
        """Parse usage from response.

        Google Gemini doesn't return usage metrics for TTS,
        so we calculate characters_synthesized from the input.
        """
        # Usage must be calculated from input during _build_response
        # This method receives response_data but we need access to inputs
        # For now, return None - the base client will handle this
        return SpeechGenerationUsage(characters_synthesized=None)

    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[SpeechGenerationParameters],
    ) -> AudioArtifact:
        """Parse content from response."""
        candidates = response_data.get("candidates", [])
        if not candidates:
            msg = "No candidates in response"
            raise ValueError(msg)

        candidate = candidates[0]
        content = candidate.get("content", {})
        parts = content.get("parts", [])

        if not parts:
            msg = "No parts in candidate content"
            raise ValueError(msg)

        inline_data = parts[0].get("inlineData", {})
        base64_audio = inline_data.get("data")

        if not base64_audio:
            msg = "No audio data in response"
            raise ValueError(msg)

        # Decode base64 to get raw PCM bytes
        # Google returns PCM audio (24kHz, 16-bit, mono)
        pcm_bytes = base64.b64decode(base64_audio)

        return AudioArtifact(
            data=pcm_bytes,
            mime_type=AudioMimeType.PCM,
            metadata={
                "sample_rate": config.PCM_SAMPLE_RATE,
                "channels": config.PCM_CHANNELS,
                "sample_width": config.PCM_SAMPLE_WIDTH,
            },
        )

    async def _make_request(
        self,
        request_body: dict[str, Any],
        **parameters: Unpack[SpeechGenerationParameters],
    ) -> httpx.Response:
        """Make HTTP request(s) and return response object."""
        endpoint = config.ENDPOINT.format(model_id=self.model.id)

        headers = {
            config.AUTH_HEADER_NAME: f"{config.AUTH_HEADER_PREFIX}{self.api_key.get_secret_value()}",
            "Content-Type": ApplicationMimeType.JSON,
        }

        return await self.http_client.post(
            f"{config.BASE_URL}{endpoint}",
            headers=headers,
            json_body=request_body,
        )


__all__ = ["GoogleSpeechGenerationClient"]

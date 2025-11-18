"""OpenAI client implementation for speech generation."""

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
from .parameters import OPENAI_PARAMETER_MAPPERS


class OpenAISpeechGenerationClient(SpeechGenerationClient):
    """OpenAI client for speech generation."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return OPENAI_PARAMETER_MAPPERS

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
        """Initialize request from OpenAI API format."""
        return {"input": inputs.prompt}

    def _parse_usage(self, response_data: dict[str, Any]) -> SpeechGenerationUsage:
        """Parse usage from response.

        OpenAI TTS doesn't return usage metrics in response,
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

        Note: This method is not used for OpenAI TTS since we override generate()
        to handle binary responses. Kept for interface compliance.
        """
        # This should never be called for OpenAI TTS
        msg = "OpenAI TTS returns binary responses, use generate() override"
        raise NotImplementedError(msg)

    def _map_response_format_to_mime_type(
        self, response_format: str | None
    ) -> AudioMimeType:
        """Map OpenAI response_format to AudioMimeType."""
        format_map: dict[str, AudioMimeType] = {
            "mp3": AudioMimeType.MP3,
            "opus": AudioMimeType.OGG,  # OGG is closest match for Opus
            "aac": AudioMimeType.AAC,
            "flac": AudioMimeType.FLAC,
        }
        return format_map.get(
            response_format or "", AudioMimeType.MP3
        )  # Default to MP3

    async def _make_request(
        self,
        request_body: dict[str, Any],
        **parameters: Unpack[SpeechGenerationParameters],
    ) -> httpx.Response:
        """Make HTTP request(s) and return response object."""
        request_body["model"] = self.model.id

        headers = {
            config.AUTH_HEADER_NAME: f"{config.AUTH_HEADER_PREFIX}{self.api_key.get_secret_value()}",
            "Content-Type": ApplicationMimeType.JSON,
        }

        return await self.http_client.post(
            f"{config.BASE_URL}{config.ENDPOINT}",
            headers=headers,
            json_body=request_body,
        )

    async def generate(
        self,
        *args: Any,  # noqa: ANN401
        **parameters: Unpack[SpeechGenerationParameters],
    ) -> SpeechGenerationOutput:
        """Generate speech from text.

        Override base generate() to handle binary audio response from OpenAI TTS.
        """
        inputs = self._create_inputs(*args, **parameters)
        inputs, parameters = self._validate_artifacts(inputs, **parameters)
        request_body = self._build_request(inputs, **parameters)
        response = await self._make_request(request_body, **parameters)
        self._handle_error_response(response)

        # Handle binary response (OpenAI TTS returns raw audio bytes, not JSON)
        audio_bytes = response.content
        if not audio_bytes:
            msg = "No audio data in response"
            raise ValueError(msg)

        # Determine MIME type from response_format parameter (default to mp3)
        response_format = parameters.get("response_format") or "mp3"
        mime_type = self._map_response_format_to_mime_type(response_format)

        # Calculate usage from input text length
        characters_synthesized = len(inputs.prompt)

        return self._output_class()(
            content=AudioArtifact(data=audio_bytes, mime_type=mime_type),
            usage=SpeechGenerationUsage(characters_synthesized=characters_synthesized),
            metadata={
                "raw_response": {
                    "content_length": len(audio_bytes),
                    "response_format": response_format,
                },
            },
        )


__all__ = ["OpenAISpeechGenerationClient"]

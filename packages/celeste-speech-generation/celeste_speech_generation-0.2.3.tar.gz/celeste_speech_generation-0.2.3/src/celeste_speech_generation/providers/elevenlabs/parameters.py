"""ElevenLabs parameter mappers for speech generation."""

from enum import StrEnum
from typing import Any

from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste_speech_generation.parameters import SpeechGenerationParameter


class VoiceMapper(ParameterMapper):
    """Map voice parameter to ElevenLabs URL path.

    Note: Voice ID goes in URL path, not request body.
    This mapper validates the voice_id but the actual URL construction
    happens in _make_request().
    """

    name: StrEnum = SpeechGenerationParameter.VOICE

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Validate voice_id format."""
        validated_value = self._validate_value(value, model)
        # Voice ID is stored in request for later use in _make_request()
        # but not added to request body
        if validated_value is not None:
            request["_voice_id"] = validated_value
        return request


class OutputFormatMapper(ParameterMapper):
    """Map response_format parameter to ElevenLabs output_format field."""

    name: StrEnum = SpeechGenerationParameter.RESPONSE_FORMAT

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform response_format into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            # Default to mp3_44100_128 if not provided
            request["output_format"] = "mp3_44100_128"
            return request

        request["output_format"] = validated_value
        return request


ELEVENLABS_PARAMETER_MAPPERS: list[ParameterMapper] = [
    VoiceMapper(),
    OutputFormatMapper(),
]

__all__ = ["ELEVENLABS_PARAMETER_MAPPERS"]

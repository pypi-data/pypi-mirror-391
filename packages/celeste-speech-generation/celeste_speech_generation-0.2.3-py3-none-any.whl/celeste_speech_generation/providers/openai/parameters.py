"""OpenAI parameter mappers for speech generation."""

from enum import StrEnum
from typing import Any

from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste_speech_generation.parameters import SpeechGenerationParameter


class VoiceMapper(ParameterMapper):
    """Map voice parameter to OpenAI voice field."""

    name: StrEnum = SpeechGenerationParameter.VOICE

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform voice into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["voice"] = validated_value
        return request


class SpeedMapper(ParameterMapper):
    """Map speed parameter to OpenAI speed field."""

    name: StrEnum = SpeechGenerationParameter.SPEED

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform speed into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["speed"] = validated_value
        return request


class ResponseFormatMapper(ParameterMapper):
    """Map response_format parameter to OpenAI response_format field."""

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
            return request

        request["response_format"] = validated_value
        return request


OPENAI_PARAMETER_MAPPERS: list[ParameterMapper] = [
    VoiceMapper(),
    SpeedMapper(),
    ResponseFormatMapper(),
]

__all__ = ["OPENAI_PARAMETER_MAPPERS"]

"""Google parameter mappers for speech generation."""

from enum import StrEnum
from typing import Any

from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste_speech_generation.parameters import SpeechGenerationParameter


class VoiceMapper(ParameterMapper):
    """Map voice parameter to Google speechConfig.voiceConfig.prebuiltVoiceConfig.voiceName."""

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

        request.setdefault("generationConfig", {}).setdefault(
            "speechConfig", {}
        ).setdefault("voiceConfig", {}).setdefault("prebuiltVoiceConfig", {})[
            "voiceName"
        ] = validated_value
        return request


GOOGLE_PARAMETER_MAPPERS: list[ParameterMapper] = [
    VoiceMapper(),
]

__all__ = ["GOOGLE_PARAMETER_MAPPERS"]

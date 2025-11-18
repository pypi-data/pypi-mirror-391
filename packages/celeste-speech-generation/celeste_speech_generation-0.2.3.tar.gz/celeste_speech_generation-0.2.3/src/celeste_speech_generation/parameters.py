"""Parameters for speech generation."""

from enum import StrEnum

from pydantic import TypeAdapter

from celeste.parameters import Parameters


class SpeechGenerationParameter(StrEnum):
    """Unified parameter names for speech generation capability."""

    VOICE = "voice"
    SPEED = "speed"
    RESPONSE_FORMAT = "response_format"


class SpeechGenerationParameters(Parameters):
    """Parameters for speech generation."""

    voice: str | None = None
    speed: float | None = None
    response_format: str | None = None


# Pydantic validator for runtime validation
_params_validator = TypeAdapter(SpeechGenerationParameters)

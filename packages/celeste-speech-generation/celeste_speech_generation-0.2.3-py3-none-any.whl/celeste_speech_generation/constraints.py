"""Constraint models for speech generation."""

from pydantic import Field

from celeste.constraints import Constraint
from celeste.exceptions import ConstraintViolationError
from celeste_speech_generation.voices import Voice


class VoiceConstraint(Constraint):
    """Voice constraint - value must be a valid voice ID from the provided voices."""

    voices: list[Voice] = Field(min_length=1)

    def __call__(self, value: str) -> str:
        """Validate value is a valid voice ID and return it."""
        if not isinstance(value, str):
            msg = f"Must be string, got {type(value).__name__}"
            raise ConstraintViolationError(msg)

        voice_ids = [v.id for v in self.voices]
        if value not in voice_ids:
            voice_names = [v.name for v in self.voices]
            msg = f"Must be one of {voice_names} (IDs: {voice_ids}), got {value!r}"
            raise ConstraintViolationError(msg)

        return value


__all__ = ["VoiceConstraint"]

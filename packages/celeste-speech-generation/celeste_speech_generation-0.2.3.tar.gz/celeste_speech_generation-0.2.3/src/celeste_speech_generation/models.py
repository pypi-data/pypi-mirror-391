"""Model definitions for speech generation."""

from celeste import Model
from celeste_speech_generation.providers.elevenlabs.models import ELEVENLABS_MODELS
from celeste_speech_generation.providers.google.models import GOOGLE_MODELS
from celeste_speech_generation.providers.openai.models import OPENAI_MODELS

MODELS: list[Model] = [
    *GOOGLE_MODELS,
    *OPENAI_MODELS,
    *ELEVENLABS_MODELS,
]

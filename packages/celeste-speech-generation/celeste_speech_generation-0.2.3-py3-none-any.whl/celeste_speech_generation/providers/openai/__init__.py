"""OpenAI provider."""

from .client import OpenAISpeechGenerationClient
from .models import OPENAI_MODELS

__all__ = ["OPENAI_MODELS", "OpenAISpeechGenerationClient"]

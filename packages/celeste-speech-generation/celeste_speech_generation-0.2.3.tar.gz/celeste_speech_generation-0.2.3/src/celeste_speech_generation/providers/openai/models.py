"""OpenAI model definitions for speech generation."""

from celeste import Model, Provider
from celeste_speech_generation.constraints import VoiceConstraint
from celeste_speech_generation.parameters import SpeechGenerationParameter

from .voices import GPT4O_MINI_TTS_VOICES, TTS1_HD_VOICES, TTS1_VOICES

OPENAI_MODELS = [
    Model(
        id="tts-1",
        provider=Provider.OPENAI,
        display_name="TTS-1",
        streaming=False,
        parameter_constraints={
            SpeechGenerationParameter.VOICE: VoiceConstraint(voices=TTS1_VOICES),
        },
    ),
    Model(
        id="tts-1-hd",
        provider=Provider.OPENAI,
        display_name="TTS-1 HD",
        streaming=False,
        parameter_constraints={
            SpeechGenerationParameter.VOICE: VoiceConstraint(voices=TTS1_HD_VOICES),
        },
    ),
    Model(
        id="gpt-4o-mini-tts",
        provider=Provider.OPENAI,
        display_name="GPT-4o Mini TTS",
        streaming=False,
        parameter_constraints={
            SpeechGenerationParameter.VOICE: VoiceConstraint(
                voices=GPT4O_MINI_TTS_VOICES
            ),
        },
    ),
]

__all__ = ["OPENAI_MODELS"]

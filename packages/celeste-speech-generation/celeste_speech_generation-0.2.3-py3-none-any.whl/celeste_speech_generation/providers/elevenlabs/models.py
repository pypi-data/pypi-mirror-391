"""ElevenLabs model definitions for speech generation."""

from celeste import Model, Provider
from celeste_speech_generation.constraints import VoiceConstraint
from celeste_speech_generation.parameters import SpeechGenerationParameter

from .voices import ELEVENLABS_VOICES

ELEVENLABS_MODELS = [
    Model(
        id="eleven_multilingual_v2",
        provider=Provider.ELEVENLABS,
        display_name="Eleven Multilingual v2",
        streaming=True,
        parameter_constraints={
            SpeechGenerationParameter.VOICE: VoiceConstraint(voices=ELEVENLABS_VOICES),
        },
    ),
    Model(
        id="eleven_turbo_v2",
        provider=Provider.ELEVENLABS,
        display_name="Eleven Turbo v2",
        streaming=True,
        parameter_constraints={
            SpeechGenerationParameter.VOICE: VoiceConstraint(voices=ELEVENLABS_VOICES),
        },
    ),
    Model(
        id="eleven_flash_v2_5",
        provider=Provider.ELEVENLABS,
        display_name="Eleven Flash v2.5",
        streaming=True,
        parameter_constraints={
            SpeechGenerationParameter.VOICE: VoiceConstraint(voices=ELEVENLABS_VOICES),
        },
    ),
    Model(
        id="eleven_monolingual_v1",
        provider=Provider.ELEVENLABS,
        display_name="Eleven Monolingual v1",
        streaming=True,
        parameter_constraints={
            SpeechGenerationParameter.VOICE: VoiceConstraint(voices=ELEVENLABS_VOICES),
        },
    ),
]

__all__ = ["ELEVENLABS_MODELS"]

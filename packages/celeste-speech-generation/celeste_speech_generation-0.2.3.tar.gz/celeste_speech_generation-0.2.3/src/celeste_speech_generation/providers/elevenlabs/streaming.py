"""ElevenLabs streaming for speech generation."""

from typing import Any

from celeste.io import Chunk
from celeste_speech_generation.io import (
    SpeechGenerationChunk,
    SpeechGenerationUsage,
)
from celeste_speech_generation.streaming import SpeechGenerationStream


class ElevenLabsSpeechGenerationStream(SpeechGenerationStream):
    """ElevenLabs streaming for speech generation."""

    def _parse_chunk(self, event: dict[str, Any]) -> Chunk | None:
        """Parse binary audio chunk from event dict.

        Event dict contains {"data": bytes} for binary audio chunks.
        """
        audio_bytes = event.get("data")
        if audio_bytes is None:
            return None

        if not isinstance(audio_bytes, bytes):
            return None

        # Return chunk with binary audio data
        return SpeechGenerationChunk(
            content=audio_bytes,
            usage=None,  # Usage calculated in _parse_usage()
            metadata={"raw_event": {"content_length": len(audio_bytes)}},
        )

    def _parse_usage(
        self, chunks: list[SpeechGenerationChunk]
    ) -> SpeechGenerationUsage:
        """Parse usage from chunks.

        ElevenLabs doesn't return usage in streaming response,
        so we calculate from input text length.
        Note: We need access to the input prompt, which is stored in _parameters.
        """
        # Get prompt from parameters to calculate characters_synthesized
        prompt = self._parameters.get("prompt", "")
        characters_synthesized = len(prompt) if prompt else None

        return SpeechGenerationUsage(characters_synthesized=characters_synthesized)


__all__ = ["ElevenLabsSpeechGenerationStream"]

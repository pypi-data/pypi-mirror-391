"""Input and output types for speech generation."""

from celeste.artifacts import AudioArtifact
from celeste.io import Chunk, Input, Output, Usage


class SpeechGenerationInput(Input):
    """Input for speech generation operations."""

    prompt: str


class SpeechGenerationUsage(Usage):
    """Speech generation usage metrics from cross-provider research.

    All fields optional since providers vary significantly.
    Most providers bill by characters but don't return usage in response.
    """

    characters_synthesized: int | None = None  # Provider-reported character count


class SpeechGenerationOutput(Output[AudioArtifact]):
    """Output with audio artifact content."""


class SpeechGenerationChunk(Chunk[bytes]):
    """Typed chunk for speech generation streaming.

    Speech streaming sends raw bytes without finish_reason.
    """

    usage: SpeechGenerationUsage | None = None  # Final chunk only


__all__ = [
    "SpeechGenerationChunk",
    "SpeechGenerationInput",
    "SpeechGenerationOutput",
    "SpeechGenerationUsage",
]

"""Input and output types for image intelligence."""

from celeste.artifacts import ImageArtifact
from celeste.io import Chunk, FinishReason, Input, Output, Usage


class ImageIntelligenceInput(Input):
    """Input for image intelligence operations.

    Image can be provided as ImageArtifact (supporting path, url, data, or bytes).
    Multiple images can be analyzed together using a list.
    """

    image: ImageArtifact | list[ImageArtifact]
    prompt: str


class ImageIntelligenceFinishReason(FinishReason):
    """Image intelligence finish reason.

    Stores raw provider reason. Providers map their values in implementation.
    """

    reason: str


class ImageIntelligenceUsage(Usage):
    """Image intelligence usage metrics.

    All fields optional since providers vary.
    """

    input_tokens: int | None = None
    output_tokens: int | None = None
    cache_creation_input_tokens: int | None = None  # Anthropic
    cache_read_input_tokens: int | None = None  # Anthropic


class ImageIntelligenceOutput[Content](Output[Content]):
    """Output with text or structured content."""

    pass


class ImageIntelligenceChunk(Chunk[str]):
    """Typed chunk for image intelligence streaming."""

    finish_reason: ImageIntelligenceFinishReason | None = None
    usage: ImageIntelligenceUsage | None = None


__all__ = [
    "ImageIntelligenceChunk",
    "ImageIntelligenceFinishReason",
    "ImageIntelligenceInput",
    "ImageIntelligenceOutput",
    "ImageIntelligenceUsage",
]

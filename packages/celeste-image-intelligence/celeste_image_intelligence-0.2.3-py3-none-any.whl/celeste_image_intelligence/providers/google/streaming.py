"""Google Gemini streaming for image intelligence."""

from collections.abc import Callable
from typing import Any, Unpack

from celeste.io import Chunk
from celeste_image_intelligence.io import (
    ImageIntelligenceChunk,
    ImageIntelligenceFinishReason,
    ImageIntelligenceOutput,
    ImageIntelligenceUsage,
)
from celeste_image_intelligence.parameters import ImageIntelligenceParameters
from celeste_image_intelligence.streaming import ImageIntelligenceStream
from celeste_text_generation.io import TextGenerationChunk
from celeste_text_generation.providers.google.streaming import GoogleTextGenerationStream


class GoogleImageIntelligenceStream(
    GoogleTextGenerationStream,  # Provides chunk parsing logic
    ImageIntelligenceStream,  # Satisfies type requirements
):
    """Google Gemini streaming for image intelligence - reuses text-generation implementation."""

    def __init__(
        self,
        sse_iterator: Any,  # noqa: ANN401
        transform_output: Callable[[object, Any], object],
        **parameters: Unpack[ImageIntelligenceParameters],
    ) -> None:
        """Initialize stream with output transformation support."""
        super().__init__(sse_iterator, transform_output, **parameters)

    def _parse_chunk(self, event: dict[str, Any]) -> Chunk | None:
        """Override: Parse directly into ImageIntelligenceChunk (reusing parent logic)."""
        # Use parent's parsing logic but convert to ImageIntelligenceChunk
        text_chunk = super()._parse_chunk(event)
        if text_chunk is None:
            return None

        # Convert TextGenerationChunk to ImageIntelligenceChunk
        if isinstance(text_chunk, TextGenerationChunk):
            finish_reason = (
                ImageIntelligenceFinishReason(reason=text_chunk.finish_reason.reason)
                if text_chunk.finish_reason
                else None
            )
            usage = (
                ImageIntelligenceUsage(
                    input_tokens=text_chunk.usage.input_tokens if text_chunk.usage else None,
                    output_tokens=text_chunk.usage.output_tokens if text_chunk.usage else None,
                    cache_creation_input_tokens=None,
                    cache_read_input_tokens=None,
                )
                if text_chunk.usage
                else None
            )
            return ImageIntelligenceChunk(
                content=text_chunk.content,
                finish_reason=finish_reason,
                usage=usage,
            )

        return text_chunk

    def _parse_usage(
        self, chunks: list[ImageIntelligenceChunk]
    ) -> ImageIntelligenceUsage:
        """Override: Parse usage from ImageIntelligenceChunks."""
        # Extract usage from chunks (Google provides cumulative usage in final chunk)
        if not chunks:
            return ImageIntelligenceUsage(
                input_tokens=None,
                output_tokens=None,
                cache_creation_input_tokens=None,
                cache_read_input_tokens=None,
            )

        # Find last chunk with usage (Google includes cumulative usage in each chunk)
        for chunk in reversed(chunks):
            if chunk.usage:
                return chunk.usage

        # Fallback: no usage found
        return ImageIntelligenceUsage(
            input_tokens=None,
            output_tokens=None,
            cache_creation_input_tokens=None,
            cache_read_input_tokens=None,
        )

    def _parse_output(
        self,
        chunks: list[ImageIntelligenceChunk],
        **parameters: Unpack[ImageIntelligenceParameters],
    ) -> ImageIntelligenceOutput:
        """Override: Assemble output with structured output support."""
        # Concatenate text chunks
        content = "".join(chunk.content for chunk in chunks if chunk.content)

        # Apply parameter transformations (e.g., JSON → BaseModel if output_schema provided)
        content = self._transform_output(content, **parameters)

        usage = self._parse_usage(chunks)
        finish_reason = chunks[-1].finish_reason if chunks else None

        return ImageIntelligenceOutput(
            content=content,
            usage=usage,
            finish_reason=finish_reason,
            metadata={},
        )


__all__ = ["GoogleImageIntelligenceStream"]

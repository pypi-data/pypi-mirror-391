"""Streaming for image intelligence."""

from abc import abstractmethod
from typing import Unpack

from celeste.streaming import Stream
from celeste_image_intelligence.io import (
    ImageIntelligenceChunk,
    ImageIntelligenceOutput,
    ImageIntelligenceUsage,
)
from celeste_image_intelligence.parameters import ImageIntelligenceParameters


class ImageIntelligenceStream(
    Stream[ImageIntelligenceOutput, ImageIntelligenceParameters]
):
    """Streaming for image intelligence."""

    def _parse_output(
        self,
        chunks: list[ImageIntelligenceChunk],
        **parameters: Unpack[ImageIntelligenceParameters],
    ) -> ImageIntelligenceOutput:
        """Assemble chunks into final output."""
        content = "".join(chunk.content for chunk in chunks if chunk.content)
        usage = self._parse_usage(chunks)
        finish_reason = chunks[-1].finish_reason if chunks else None

        return ImageIntelligenceOutput(
            content=content, usage=usage, finish_reason=finish_reason, metadata={}
        )

    @abstractmethod
    def _parse_usage(
        self, chunks: list[ImageIntelligenceChunk]
    ) -> ImageIntelligenceUsage:
        """Parse usage from chunks (provider-specific)."""


__all__ = ["ImageIntelligenceStream"]

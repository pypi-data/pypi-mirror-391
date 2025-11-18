"""OpenAI streaming for image intelligence."""

from typing import Any

from celeste.io import Chunk
from celeste_image_intelligence.io import (
    ImageIntelligenceChunk,
    ImageIntelligenceFinishReason,
    ImageIntelligenceOutput,
    ImageIntelligenceUsage,
)
from celeste_image_intelligence.streaming import ImageIntelligenceStream


class OpenAIImageIntelligenceStream(ImageIntelligenceStream):
    """OpenAI streaming for image intelligence."""

    def _parse_chunk(self, event: dict[str, Any]) -> Chunk | None:
        """Parse SSE event into Chunk."""
        event_type = event.get("type")
        if not event_type:
            return None

        if event_type == "response.output_text.delta":
            delta = event.get("delta")
            if delta is None:
                return None
            return ImageIntelligenceChunk(
                content=delta,
                finish_reason=None,
                usage=None,
                metadata={"raw_event": event},
            )

        if event_type == "response.output_text.done":
            return None

        if event_type == "response.completed":
            response_data = event.get("response", {})
            usage_data = response_data.get("usage")

            usage: ImageIntelligenceUsage | None = None
            if usage_data:
                input_tokens_details = usage_data.get("input_tokens_details", {})
                usage = ImageIntelligenceUsage(
                    input_tokens=usage_data.get("input_tokens"),
                    output_tokens=usage_data.get("output_tokens"),
                    cache_creation_input_tokens=None,
                    cache_read_input_tokens=input_tokens_details.get("cached_tokens"),
                )

            finish_reason: ImageIntelligenceFinishReason | None = None
            status = response_data.get("status")
            if status == "completed":
                finish_reason = ImageIntelligenceFinishReason(reason="completed")

            return ImageIntelligenceChunk(
                content="",
                finish_reason=finish_reason,
                usage=usage,
                metadata={"raw_event": event},
            )

        return None

    def _parse_usage(self, chunks: list[ImageIntelligenceChunk]) -> ImageIntelligenceUsage:
        """Parse usage from chunks."""
        if not chunks:
            return ImageIntelligenceUsage()

        for chunk in reversed(chunks):
            if chunk.usage:
                return chunk.usage

        return ImageIntelligenceUsage()

    def _parse_output(
        self,
        chunks: list[ImageIntelligenceChunk],
    ) -> ImageIntelligenceOutput:
        """Assemble chunks into final output."""
        content = "".join(chunk.content for chunk in chunks)
        usage = self._parse_usage(chunks)
        finish_reason = chunks[-1].finish_reason if chunks else None

        return ImageIntelligenceOutput(
            content=content,
            usage=usage,
            finish_reason=finish_reason,
            metadata={},
        )


__all__ = ["OpenAIImageIntelligenceStream"]


"""Mistral streaming for image intelligence."""

from typing import Any

from celeste.io import Chunk
from celeste_image_intelligence.io import (
    ImageIntelligenceChunk,
    ImageIntelligenceFinishReason,
    ImageIntelligenceOutput,
    ImageIntelligenceUsage,
)
from celeste_image_intelligence.streaming import ImageIntelligenceStream


class MistralImageIntelligenceStream(ImageIntelligenceStream):
    """Mistral streaming for image intelligence."""

    def _parse_chunk(self, event: dict[str, Any]) -> ImageIntelligenceChunk | None:
        """Parse chunk from SSE event.

        Extract from choices[0].delta.content (content delta events).
        Extract finish_reason and usage from final event when finish_reason is not null.
        Return None if no text delta (filter lifecycle events).
        """
        choices = event.get("choices", [])
        if not choices:
            return None

        first_choice = choices[0]
        if not isinstance(first_choice, dict):
            return None

        delta = first_choice.get("delta", {})
        if not isinstance(delta, dict):
            return None

        # Extract content delta
        content_delta = delta.get("content")
        finish_reason_str = first_choice.get("finish_reason")

        # Extract usage from event if present (in final event)
        usage = None
        usage_dict = event.get("usage")
        if isinstance(usage_dict, dict):
            usage = ImageIntelligenceUsage(
                input_tokens=usage_dict.get("prompt_tokens"),
                output_tokens=usage_dict.get("completion_tokens"),
                cache_creation_input_tokens=None,
                cache_read_input_tokens=None,
            )

        # Create finish reason if present
        finish_reason = (
            ImageIntelligenceFinishReason(reason=finish_reason_str)
            if finish_reason_str
            else None
        )

        # If no content delta and no finish reason, filter this event
        if not content_delta and not finish_reason:
            return None

        return ImageIntelligenceChunk(
            content=content_delta or "",  # Empty string if no content (final event)
            finish_reason=finish_reason,
            usage=usage,
            metadata={"raw_event": event},
        )

    def _parse_usage(
        self, chunks: list[ImageIntelligenceChunk]
    ) -> ImageIntelligenceUsage:
        """Parse usage from chunks.

        Mistral provides usage metadata in the final event (when finish_reason is not null).
        Use the last chunk that has usage metadata.
        """
        if not chunks:
            return ImageIntelligenceUsage(
                input_tokens=None,
                output_tokens=None,
                cache_creation_input_tokens=None,
                cache_read_input_tokens=None,
            )

        # Usage metadata is typically in the final chunk (when finish_reason is set)
        for chunk in reversed(chunks):
            if chunk.usage:
                return chunk.usage

        return ImageIntelligenceUsage(
            input_tokens=None,
            output_tokens=None,
            cache_creation_input_tokens=None,
            cache_read_input_tokens=None,
        )


__all__ = ["MistralImageIntelligenceStream"]


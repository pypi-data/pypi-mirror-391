"""Base client for image intelligence."""

from abc import abstractmethod
from typing import Any, Unpack

import httpx
from pydantic import BaseModel

from celeste.artifacts import ImageArtifact
from celeste.client import Client
from celeste.exceptions import ValidationError
from celeste_image_intelligence.io import (
    ImageIntelligenceFinishReason,
    ImageIntelligenceInput,
    ImageIntelligenceOutput,
    ImageIntelligenceUsage,
)
from celeste_image_intelligence.parameters import ImageIntelligenceParameters


class ImageIntelligenceClient(
    Client[ImageIntelligenceInput, ImageIntelligenceOutput, ImageIntelligenceParameters]
):
    """Client for image intelligence operations."""

    @abstractmethod
    def _init_request(self, inputs: ImageIntelligenceInput) -> dict[str, Any]:
        """Initialize provider-specific request structure."""

    @abstractmethod
    def _parse_usage(self, response_data: dict[str, Any]) -> ImageIntelligenceUsage:
        """Parse usage information from provider response."""

    @abstractmethod
    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[ImageIntelligenceParameters],
    ) -> str | BaseModel:
        """Parse content from provider response."""

    @abstractmethod
    def _parse_finish_reason(
        self, response_data: dict[str, Any]
    ) -> ImageIntelligenceFinishReason | None:
        """Parse finish reason from provider response."""

    def _create_inputs(
        self,
        *args: Any,  # noqa: ANN401
        image: ImageArtifact | list[ImageArtifact] | None = None,
        prompt: str | None = None,
        **parameters: Unpack[ImageIntelligenceParameters],
    ) -> ImageIntelligenceInput:
        """Map positional arguments to Input type."""
        if len(args) == 2:
            return ImageIntelligenceInput(image=args[0], prompt=args[1])
        if len(args) == 1:
            if image is None:
                return ImageIntelligenceInput(image=args[0], prompt=prompt or "")
            return ImageIntelligenceInput(image=image, prompt=args[0])
        if image is None or prompt is None:
            msg = "image and prompt are required (as keyword arguments or positional: image, prompt)"
            raise ValidationError(msg)
        return ImageIntelligenceInput(image=image, prompt=prompt)

    @classmethod
    def _output_class(cls) -> type[ImageIntelligenceOutput]:
        """Return the Output class for this client."""
        return ImageIntelligenceOutput

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Build metadata dictionary from response data."""
        metadata = super()._build_metadata(response_data)
        metadata["raw_response"] = (
            response_data  # Complete raw response (providers filter content fields)
        )
        # Only parse finish_reason if not already set by provider override
        if "finish_reason" not in metadata:
            finish_reason = self._parse_finish_reason(response_data)
            if finish_reason is not None:
                metadata["finish_reason"] = finish_reason
        return metadata

    @abstractmethod
    async def _make_request(
        self,
        request_body: dict[str, Any],
        **parameters: Unpack[ImageIntelligenceParameters],
    ) -> httpx.Response:
        """Make HTTP request(s) and return response object."""

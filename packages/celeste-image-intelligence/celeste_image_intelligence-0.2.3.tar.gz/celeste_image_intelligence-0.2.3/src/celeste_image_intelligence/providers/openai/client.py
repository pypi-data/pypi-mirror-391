"""OpenAI client implementation for image intelligence."""

import base64
import logging
from collections.abc import AsyncIterator
from typing import Any, Unpack

import httpx

from celeste.artifacts import ImageArtifact
from celeste.mime_types import ApplicationMimeType
from celeste.parameters import ParameterMapper
from celeste_image_intelligence.client import ImageIntelligenceClient
from celeste_image_intelligence.io import (
    ImageIntelligenceFinishReason,
    ImageIntelligenceInput,
    ImageIntelligenceUsage,
)
from celeste_image_intelligence.parameters import ImageIntelligenceParameters

from . import config
from .parameters import OPENAI_PARAMETER_MAPPERS
from .streaming import OpenAIImageIntelligenceStream

logger = logging.getLogger(__name__)


class OpenAIImageIntelligenceClient(ImageIntelligenceClient):
    """OpenAI client for image intelligence."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return OPENAI_PARAMETER_MAPPERS

    def _image_to_data_url(self, image: ImageArtifact) -> str:
        """Convert ImageArtifact to data URL format.

        Args:
            image: ImageArtifact with url, data, or path.

        Returns:
            Data URL string in format: data:{mime_type};base64,{base64_data}
        """
        if image.url:
            # If already a data URL, return as-is
            if image.url.startswith("data:image/"):
                return image.url
            # For remote URLs, we need to convert to base64
            # For now, raise error - OpenAI Responses API requires base64 data URLs
            msg = "OpenAI Responses API requires base64 data URLs. Use ImageArtifact with data or path instead."
            raise ValueError(msg)

        # Get image bytes
        if image.data:
            file_data = image.data
        elif image.path:
            with open(image.path, "rb") as f:
                file_data = f.read()
        else:
            msg = "ImageArtifact must have url, data, or path"
            raise ValueError(msg)

        # Encode to base64
        if isinstance(file_data, bytes):
            base64_data = base64.b64encode(file_data).decode("utf-8")
        else:
            base64_data = file_data

        # Get mime type
        mime_type = image.mime_type.value if image.mime_type else "image/jpeg"

        return f"data:{mime_type};base64,{base64_data}"

    def _init_request(self, inputs: ImageIntelligenceInput) -> dict[str, Any]:
        """Initialize request from OpenAI Responses API format.

        Maps ImageIntelligenceInput to OpenAI Responses API input array format
        with multimodal content array.
        """
        content: list[dict[str, Any]] = []

        # Add images first
        images = inputs.image if isinstance(inputs.image, list) else [inputs.image]
        for image in images:
            data_url = self._image_to_data_url(image)
            content.append(
                {
                    "type": "input_image",
                    "image_url": data_url,
                }
            )

        # Add text prompt
        content.append(
            {
                "type": "input_text",
                "text": inputs.prompt,
            }
        )

        return {
            "input": [
                {
                    "role": "user",
                    "content": content,
                }
            ]
        }

    def _parse_usage(self, response_data: dict[str, Any]) -> ImageIntelligenceUsage:
        """Parse usage from response.

        Maps usage fields to ImageIntelligenceUsage schema.
        """
        usage_data = response_data.get("usage", {})
        input_tokens_details = usage_data.get("input_tokens_details", {})
        output_tokens_details = usage_data.get("output_tokens_details", {})

        return ImageIntelligenceUsage(
            input_tokens=usage_data.get("input_tokens"),
            output_tokens=usage_data.get("output_tokens"),
            cache_creation_input_tokens=None,
            cache_read_input_tokens=input_tokens_details.get("cached_tokens"),
        )

    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[ImageIntelligenceParameters],
    ) -> str:
        """Parse content from response."""
        output_items = response_data.get("output", [])
        if not output_items:
            msg = "No output items in response"
            raise ValueError(msg)

        message_item = None
        for item in output_items:
            if item.get("type") == "message":
                message_item = item
                break

        if not message_item:
            msg = "No message item found in output array"
            raise ValueError(msg)

        content_parts = message_item.get("content", [])
        if not content_parts:
            msg = "No content parts in message item"
            raise ValueError(msg)

        text_content = ""
        for content_part in content_parts:
            if content_part.get("type") == "output_text":
                text_content = content_part.get("text") or ""
                break

        return text_content

    def _parse_finish_reason(
        self, response_data: dict[str, Any]
    ) -> ImageIntelligenceFinishReason | None:
        """Parse finish reason from response."""
        status = response_data.get("status")
        if status != "completed":
            return None

        output_items = response_data.get("output", [])
        for item in output_items:
            if item.get("type") == "message":
                item_status = item.get("status")
                if item_status == "completed":
                    return ImageIntelligenceFinishReason(reason="completed")

        return None

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Build metadata dictionary from response data."""
        # Filter content field before calling super
        content_fields = {"output"}
        filtered_data = {
            k: v for k, v in response_data.items() if k not in content_fields
        }
        return super()._build_metadata(filtered_data)

    async def _make_request(
        self,
        request_body: dict[str, Any],
        **parameters: Unpack[ImageIntelligenceParameters],
    ) -> httpx.Response:
        """Make HTTP request(s) and return response object."""
        request_body["model"] = self.model.id

        headers = {
            config.AUTH_HEADER_NAME: f"{config.AUTH_HEADER_PREFIX}{self.api_key.get_secret_value()}",
            "Content-Type": ApplicationMimeType.JSON,
        }

        return await self.http_client.post(
            f"{config.BASE_URL}{config.ENDPOINT}",
            headers=headers,
            json_body=request_body,
        )

    def _stream_class(self) -> type[OpenAIImageIntelligenceStream]:
        """Return the Stream class for this client."""
        return OpenAIImageIntelligenceStream

    def _make_stream_request(
        self,
        request_body: dict[str, Any],
        **parameters: Unpack[ImageIntelligenceParameters],
    ) -> AsyncIterator[dict[str, Any]]:
        """Make HTTP streaming request and return async iterator of events."""
        request_body["model"] = self.model.id
        request_body["stream"] = True

        headers = {
            config.AUTH_HEADER_NAME: f"{config.AUTH_HEADER_PREFIX}{self.api_key.get_secret_value()}",
            "Content-Type": ApplicationMimeType.JSON,
        }

        return self.http_client.stream_post(
            f"{config.BASE_URL}{config.STREAM_ENDPOINT}",
            headers=headers,
            json_body=request_body,
        )


__all__ = ["OpenAIImageIntelligenceClient"]


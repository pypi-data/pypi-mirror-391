"""Mistral client implementation for image intelligence."""

import base64
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
from .parameters import MISTRAL_PARAMETER_MAPPERS
from .streaming import MistralImageIntelligenceStream


class MistralImageIntelligenceClient(ImageIntelligenceClient):
    """Mistral client for image intelligence."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return MISTRAL_PARAMETER_MAPPERS

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
            # For now, raise error - Mistral requires base64 data URLs
            msg = "Mistral requires base64 data URLs. Use ImageArtifact with data or path instead."
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
        """Initialize request from Mistral messages array format.

        Maps ImageIntelligenceInput to Mistral's OpenAI-compatible messages format
        with multimodal content array.
        """
        content: list[dict[str, Any]] = []

        # Add images first
        images = inputs.image if isinstance(inputs.image, list) else [inputs.image]
        for image in images:
            data_url = self._image_to_data_url(image)
            content.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": data_url,
                    },
                }
            )

        # Add text prompt
        content.append(
            {
                "type": "text",
                "text": inputs.prompt,
            }
        )

        return {
            "messages": [
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
        usage_dict = response_data.get("usage", {})

        return ImageIntelligenceUsage(
            input_tokens=usage_dict.get("prompt_tokens"),
            output_tokens=usage_dict.get("completion_tokens"),
            cache_creation_input_tokens=None,
            cache_read_input_tokens=None,
        )

    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[ImageIntelligenceParameters],
    ) -> str:
        """Parse content from response."""
        choices = response_data.get("choices", [])
        if not choices:
            msg = "No choices in response"
            raise ValueError(msg)

        first_choice = choices[0]
        message = first_choice.get("message", {})
        content = message.get("content") or ""

        return content

    def _parse_finish_reason(
        self, response_data: dict[str, Any]
    ) -> ImageIntelligenceFinishReason | None:
        """Parse finish reason from response.

        Used by streaming implementation. Not included in synchronous Output.
        """
        choices = response_data.get("choices", [])
        if not choices:
            return None

        first_choice = choices[0]
        finish_reason_str = first_choice.get("finish_reason")
        return (
            ImageIntelligenceFinishReason(reason=finish_reason_str)
            if finish_reason_str
            else None
        )

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Build metadata dictionary from response data."""
        # Filter content field before calling super
        content_fields = {"choices"}
        filtered_data = {
            k: v for k, v in response_data.items() if k not in content_fields
        }
        return super()._build_metadata(filtered_data)

    async def _make_request(
        self,
        request_body: dict[str, Any],
        **parameters: Unpack[ImageIntelligenceParameters],
    ) -> httpx.Response:
        """Make HTTP request and return response object."""
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

    def _stream_class(self) -> type[MistralImageIntelligenceStream]:
        """Return the Stream class for this client."""
        return MistralImageIntelligenceStream

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


__all__ = ["MistralImageIntelligenceClient"]


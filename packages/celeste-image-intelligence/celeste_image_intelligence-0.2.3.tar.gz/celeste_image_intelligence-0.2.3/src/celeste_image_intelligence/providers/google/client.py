"""Google Gemini client implementation."""

import base64
import logging
from collections.abc import AsyncIterator
from typing import Any, Unpack

import httpx
from pydantic import BaseModel

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
from celeste_text_generation.providers.google.client import GoogleTextGenerationClient
from celeste_text_generation.io import TextGenerationUsage

from . import config
from .parameters import GOOGLE_PARAMETER_MAPPERS
from .streaming import GoogleImageIntelligenceStream

logger = logging.getLogger(__name__)


class GoogleImageIntelligenceClient(
    GoogleTextGenerationClient,  # Provides all methods
    ImageIntelligenceClient,  # Satisfies type requirements
):
    """Google Gemini client for image intelligence - reuses text-generation implementation."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return GOOGLE_PARAMETER_MAPPERS

    def _create_inputs(
        self,
        *args: Any,  # noqa: ANN401
        image: ImageArtifact | list[ImageArtifact] | None = None,
        prompt: str | None = None,
        **parameters: Unpack[ImageIntelligenceParameters],
    ) -> ImageIntelligenceInput:
        """Override: Ensure ImageIntelligenceInput is created (MRO issue fix)."""
        # Explicitly call ImageIntelligenceClient's _create_inputs to avoid MRO resolution issues
        return ImageIntelligenceClient._create_inputs(
            self, *args, image=image, prompt=prompt, **parameters
        )

    def _build_image_parts(self, images: ImageArtifact | list[ImageArtifact]) -> list[dict[str, Any]]:
        """Build Google API parts array from image artifacts."""
        parts: list[dict[str, Any]] = []
        image_list = images if isinstance(images, list) else [images]
        
        for image in image_list:
            if image.url:
                parts.append({"file_data": {"file_uri": image.url}})
            elif image.data:
                base64_data = (
                    base64.b64encode(image.data).decode("utf-8")
                    if isinstance(image.data, bytes)
                    else image.data
                )
                parts.append(
                    {
                        "inline_data": {
                            "mime_type": image.mime_type or "image/jpeg",
                            "data": base64_data,
                        }
                    }
                )
            elif image.path:
                with open(image.path, "rb") as f:
                    image_bytes = f.read()
                base64_data = base64.b64encode(image_bytes).decode("utf-8")
                parts.append(
                    {
                        "inline_data": {
                            "mime_type": image.mime_type or "image/jpeg",
                            "data": base64_data,
                        }
                    }
                )
            else:
                msg = "ImageArtifact must have url, data, or path"
                raise ValueError(msg)
        
        return parts

    def _init_request(self, inputs: ImageIntelligenceInput) -> dict[str, Any]:
        """Override: Add image parts before text, then reuse parent structure."""
        parts = self._build_image_parts(inputs.image)
        parts.append({"text": inputs.prompt})
        return {"contents": [{"role": "user", "parts": parts}]}

    def _parse_usage(self, response_data: dict[str, Any]) -> ImageIntelligenceUsage:
        """Adapt text-generation usage to image intelligence usage."""
        text_usage: TextGenerationUsage = super()._parse_usage(response_data)
        return ImageIntelligenceUsage(
            input_tokens=text_usage.input_tokens,
            output_tokens=text_usage.output_tokens,
            # Google doesn't support cache fields (Anthropic-specific)
            cache_creation_input_tokens=None,
            cache_read_input_tokens=None,
        )

    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[ImageIntelligenceParameters],
    ) -> str | BaseModel:
        """Parse content from response - inherited from text-generation."""
        # Call parent's _parse_content which handles _transform_output
        return super()._parse_content(response_data, **parameters)

    def _parse_finish_reason(
        self, response_data: dict[str, Any]
    ) -> ImageIntelligenceFinishReason | None:
        """Adapt text-generation finish reason to image intelligence finish reason."""
        from celeste_text_generation.io import TextGenerationFinishReason

        text_finish_reason: TextGenerationFinishReason | None = super()._parse_finish_reason(
            response_data
        )
        if text_finish_reason is None:
            return None
        return ImageIntelligenceFinishReason(reason=text_finish_reason.reason)

    async def _make_request(
        self,
        request_body: dict[str, Any],
        **parameters: Unpack[ImageIntelligenceParameters],
    ) -> httpx.Response:
        """Override: Use image intelligence config format."""
        endpoint = config.ENDPOINT.format(model=self.model.id)

        headers = {
            config.AUTH_HEADER_NAME: f"{config.AUTH_HEADER_PREFIX}{self.api_key.get_secret_value()}",
            "Content-Type": ApplicationMimeType.JSON,
        }

        return await self.http_client.post(
            f"{config.BASE_URL}{endpoint}",
            headers=headers,
            json_body=request_body,
        )

    def _stream_class(self) -> type[GoogleImageIntelligenceStream]:
        """Return the Stream class for this client."""
        return GoogleImageIntelligenceStream

    def _make_stream_request(
        self,
        request_body: dict[str, Any],
        **parameters: Unpack[ImageIntelligenceParameters],
    ) -> AsyncIterator[dict[str, Any]]:
        """Override: Use image intelligence config format."""
        endpoint = config.STREAM_ENDPOINT.format(model=self.model.id)

        headers = {
            config.AUTH_HEADER_NAME: f"{config.AUTH_HEADER_PREFIX}{self.api_key.get_secret_value()}",
            "Content-Type": ApplicationMimeType.JSON,
        }

        return self.http_client.stream_post(
            f"{config.BASE_URL}{endpoint}",
            headers=headers,
            json_body=request_body,
        )


__all__ = ["GoogleImageIntelligenceClient"]

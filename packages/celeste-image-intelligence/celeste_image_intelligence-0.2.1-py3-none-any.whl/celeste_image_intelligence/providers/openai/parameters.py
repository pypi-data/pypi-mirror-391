"""OpenAI parameter mappers for image intelligence."""

from enum import StrEnum
from typing import Any

from celeste.core import Parameter
from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste_image_intelligence.parameters import ImageIntelligenceParameters


class TemperatureMapper(ParameterMapper):
    """Map temperature parameter to OpenAI temperature field."""

    name: StrEnum = Parameter.TEMPERATURE

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform temperature into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["temperature"] = validated_value
        return request


class MaxTokensMapper(ParameterMapper):
    """Map max_tokens parameter to OpenAI max_output_tokens field."""

    name: StrEnum = Parameter.MAX_TOKENS

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform max_tokens into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["max_output_tokens"] = validated_value
        return request


OPENAI_PARAMETER_MAPPERS: list[ParameterMapper] = [
    TemperatureMapper(),
    MaxTokensMapper(),
]

__all__ = ["OPENAI_PARAMETER_MAPPERS"]


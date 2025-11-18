"""Mistral parameter mappers for image intelligence."""

from celeste.core import Parameter
from celeste.models import Model
from celeste.parameters import ParameterMapper
from typing import Any


class TemperatureMapper(ParameterMapper):
    """Map temperature parameter to Mistral temperature field."""

    name = Parameter.TEMPERATURE

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
    """Map max_tokens parameter to Mistral max_tokens field."""

    name = Parameter.MAX_TOKENS

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

        request["max_tokens"] = validated_value
        return request


MISTRAL_PARAMETER_MAPPERS: list[ParameterMapper] = [
    TemperatureMapper(),
    MaxTokensMapper(),
]

__all__ = ["MISTRAL_PARAMETER_MAPPERS"]


"""Google Gemini parameter mappers."""

from enum import StrEnum

from celeste.parameters import ParameterMapper
from celeste_image_intelligence.parameters import ImageIntelligenceParameter
from celeste_text_generation.providers.google.parameters import (
    ThinkingBudgetMapper as _TextThinkingBudgetMapper,
    OutputSchemaMapper as _TextOutputSchemaMapper,
)


class ThinkingBudgetMapper(_TextThinkingBudgetMapper):
    """Adapter: Reuse text-generation mapper with image intelligence enum."""

    name: StrEnum = ImageIntelligenceParameter.THINKING_BUDGET


class OutputSchemaMapper(_TextOutputSchemaMapper):
    """Adapter: Reuse text-generation mapper with image intelligence enum."""

    name: StrEnum = ImageIntelligenceParameter.OUTPUT_SCHEMA


GOOGLE_PARAMETER_MAPPERS: list[ParameterMapper] = [
    ThinkingBudgetMapper(),
    OutputSchemaMapper(),
]

__all__ = ["GOOGLE_PARAMETER_MAPPERS"]

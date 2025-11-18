"""Parameters for image intelligence."""

from enum import StrEnum

from pydantic import BaseModel

from celeste.parameters import Parameters


class ImageIntelligenceParameter(StrEnum):
    """Unified parameter names for image intelligence capability."""

    THINKING_BUDGET = "thinking_budget"
    OUTPUT_SCHEMA = "output_schema"


class ImageIntelligenceParameters(Parameters):
    """Parameters for image intelligence generation."""

    thinking_budget: int | None
    output_schema: type[BaseModel] | None

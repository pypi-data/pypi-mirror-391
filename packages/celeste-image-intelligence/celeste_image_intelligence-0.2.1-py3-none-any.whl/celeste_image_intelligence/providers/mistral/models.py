"""Mistral models for image intelligence."""

from celeste import Model, Provider
from celeste.constraints import Range
from celeste.core import Parameter

# Vision-capable models from official Mistral documentation:
# https://docs.mistral.ai/capabilities/vision
#
# Note: Parameter constraints are consistent across all models per Mistral API documentation.
# The API reference (https://docs.mistral.ai/api) does not specify model-specific limits.
# Temperature: API docs recommend 0.0-0.7, but 0.0-2.0 is accepted (consistent with text-generation).
# Max tokens: No explicit limit stated in docs; using 32768 consistent with text-generation models.
MODELS: list[Model] = [
    Model(
        id="pixtral-12b-latest",
        provider=Provider.MISTRAL,
        display_name="Pixtral 12B",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=32768, step=1),
        },
    ),
    Model(
        id="pixtral-large-latest",
        provider=Provider.MISTRAL,
        display_name="Pixtral Large",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=32768, step=1),
        },
    ),
    Model(
        id="mistral-medium-latest",
        provider=Provider.MISTRAL,
        display_name="Mistral Medium 3.1",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=32768, step=1),
        },
    ),
    Model(
        id="mistral-small-latest",
        provider=Provider.MISTRAL,
        display_name="Mistral Small 3.2",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=32768, step=1),
        },
    ),
    Model(
        id="magistral-small-latest",
        provider=Provider.MISTRAL,
        display_name="Magistral Small",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=32768, step=1),
        },
    ),
    Model(
        id="magistral-medium-latest",
        provider=Provider.MISTRAL,
        display_name="Magistral Medium",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=32768, step=1),
        },
    ),
]


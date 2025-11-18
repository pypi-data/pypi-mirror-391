"""Mistral models for image intelligence."""

from celeste import Model, Provider
from celeste.constraints import Range
from celeste.core import Parameter

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
        display_name="Mistral Medium",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=32768, step=1),
        },
    ),
    Model(
        id="mistral-small-latest",
        provider=Provider.MISTRAL,
        display_name="Mistral Small",
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


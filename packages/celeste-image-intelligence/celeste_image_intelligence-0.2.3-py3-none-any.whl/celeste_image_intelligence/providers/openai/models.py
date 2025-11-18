"""OpenAI models for image intelligence."""

from celeste import Model, Provider
from celeste.constraints import Range
from celeste.core import Parameter

MODELS: list[Model] = [
    Model(
        id="gpt-4o",
        provider=Provider.OPENAI,
        display_name="GPT-4o",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0),
            Parameter.MAX_TOKENS: Range(min=1, max=16384),
        },
    ),
    Model(
        id="gpt-4o-mini",
        provider=Provider.OPENAI,
        display_name="GPT-4o Mini",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0),
            Parameter.MAX_TOKENS: Range(min=1, max=16384),
        },
    ),
    Model(
        id="gpt-4-turbo",
        provider=Provider.OPENAI,
        display_name="GPT-4 Turbo",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0),
            Parameter.MAX_TOKENS: Range(min=1, max=4096),
        },
    ),
    Model(
        id="gpt-4",
        provider=Provider.OPENAI,
        display_name="GPT-4",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0),
            Parameter.MAX_TOKENS: Range(min=1, max=8192),
        },
    ),
]


"""Google Gemini models."""

from celeste import Model, Provider
from celeste.constraints import Range, Schema
from celeste_image_intelligence.parameters import ImageIntelligenceParameter

MODELS: list[Model] = [
    Model(
        id="gemini-2.5-pro",
        provider=Provider.GOOGLE,
        display_name="Gemini 2.5 Pro",
        streaming=True,
        parameter_constraints={
            # Pro: allows -1 (dynamic) or >= 128 (cannot use 0)
            ImageIntelligenceParameter.THINKING_BUDGET: Range(
                min=128, max=32768, special_values=[-1]
            ),
            ImageIntelligenceParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="gemini-2.5-flash",
        provider=Provider.GOOGLE,
        display_name="Gemini 2.5 Flash",
        streaming=True,
        parameter_constraints={
            # Flash: allows -1 (dynamic), 0 (disable), or >= 0
            ImageIntelligenceParameter.THINKING_BUDGET: Range(min=-1, max=24576),
            ImageIntelligenceParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="gemini-2.5-flash-lite",
        provider=Provider.GOOGLE,
        display_name="Gemini 2.5 Flash Lite",
        streaming=True,
        parameter_constraints={
            # Flash Lite: allows -1 (dynamic), 0 (disable), or >= 512
            ImageIntelligenceParameter.THINKING_BUDGET: Range(
                min=512, max=24576, special_values=[-1, 0]
            ),
            ImageIntelligenceParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
]

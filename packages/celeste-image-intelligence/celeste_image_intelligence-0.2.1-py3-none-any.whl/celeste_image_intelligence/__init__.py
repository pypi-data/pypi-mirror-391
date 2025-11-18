"""Celeste image intelligence capability."""


def register_package() -> None:
    """Register image intelligence package (client and models)."""
    from celeste.client import register_client
    from celeste.core import Capability
    from celeste.models import register_models
    from celeste_image_intelligence.models import MODELS
    from celeste_image_intelligence.providers import PROVIDERS

    for provider, client_class in PROVIDERS:
        register_client(Capability.IMAGE_INTELLIGENCE, provider, client_class)

    register_models(MODELS, capability=Capability.IMAGE_INTELLIGENCE)


# Import after register_package is defined to avoid circular imports
from celeste_image_intelligence.io import (  # noqa: E402
    ImageIntelligenceChunk,
    ImageIntelligenceFinishReason,
    ImageIntelligenceInput,
    ImageIntelligenceOutput,
    ImageIntelligenceUsage,
)
from celeste_image_intelligence.streaming import ImageIntelligenceStream  # noqa: E402

__all__ = [
    "ImageIntelligenceChunk",
    "ImageIntelligenceFinishReason",
    "ImageIntelligenceInput",
    "ImageIntelligenceOutput",
    "ImageIntelligenceStream",
    "ImageIntelligenceUsage",
    "register_package",
]

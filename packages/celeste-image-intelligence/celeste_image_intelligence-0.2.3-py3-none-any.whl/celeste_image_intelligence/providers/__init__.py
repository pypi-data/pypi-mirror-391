"""Provider implementations for image intelligence."""

from celeste import Client, Provider

__all__ = ["PROVIDERS"]


def _get_providers() -> list[tuple[Provider, type[Client]]]:
    """Lazy-load providers."""
    # Import clients directly from .client modules to avoid __init__.py imports
    from celeste_image_intelligence.providers.google.client import (
        GoogleImageIntelligenceClient,
    )
    from celeste_image_intelligence.providers.mistral.client import (
        MistralImageIntelligenceClient,
    )
    from celeste_image_intelligence.providers.openai.client import (
        OpenAIImageIntelligenceClient,
    )

    return [
        (Provider.GOOGLE, GoogleImageIntelligenceClient),
        (Provider.MISTRAL, MistralImageIntelligenceClient),
        (Provider.OPENAI, OpenAIImageIntelligenceClient),
    ]


PROVIDERS: list[tuple[Provider, type[Client]]] = _get_providers()

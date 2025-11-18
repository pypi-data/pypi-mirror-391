"""Model definitions for image intelligence."""

from celeste import Model
from celeste_image_intelligence.providers.google.models import MODELS as GOOGLE_MODELS
from celeste_image_intelligence.providers.mistral.models import MODELS as MISTRAL_MODELS
from celeste_image_intelligence.providers.openai.models import MODELS as OPENAI_MODELS

MODELS: list[Model] = [
    *GOOGLE_MODELS,
    *MISTRAL_MODELS,
    *OPENAI_MODELS,
]

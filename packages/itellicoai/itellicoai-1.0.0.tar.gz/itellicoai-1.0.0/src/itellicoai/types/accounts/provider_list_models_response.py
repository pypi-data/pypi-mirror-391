# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import TypeAlias

from ..._models import BaseModel
from .model_range import ModelRange
from .model_catalog_provider import ModelCatalogProvider

__all__ = [
    "ProviderListModelsResponse",
    "ProviderListModelsResponseItem",
    "ProviderListModelsResponseItemModel",
    "ProviderListModelsResponseItemModelSettings",
]


class ProviderListModelsResponseItemModelSettings(BaseModel):
    max_tokens: Optional[ModelRange] = None
    """Numeric range with optional default/min/max."""

    temperature: Optional[ModelRange] = None
    """Numeric range with optional default/min/max."""


class ProviderListModelsResponseItemModel(BaseModel):
    id: str
    """Canonical model id without provider prefix"""

    name: str
    """Display name for the model"""

    description: Optional[str] = None
    """Short description or guidance for the model"""

    settings: Optional[ProviderListModelsResponseItemModelSettings] = None
    """Supported configurable ranges for a model (temperature, max_tokens)."""


class ProviderListModelsResponseItem(BaseModel):
    models: List[ProviderListModelsResponseItemModel]

    provider: ModelCatalogProvider
    """Provider metadata for a group of models."""


ProviderListModelsResponse: TypeAlias = List[ProviderListModelsResponseItem]

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import TypeAlias

from ..._models import BaseModel
from .model_catalog_provider import ModelCatalogProvider

__all__ = [
    "ProviderListTranscribersResponse",
    "ProviderListTranscribersResponseItem",
    "ProviderListTranscribersResponseItemModel",
    "ProviderListTranscribersResponseItemModelSupportedLanguage",
]


class ProviderListTranscribersResponseItemModelSupportedLanguage(BaseModel):
    code: str
    """Language code (e.g., de, en-US, multi)"""

    name: str
    """Display label for the language"""

    description: Optional[str] = None
    """Optional description (typically for 'multi')"""

    includes: Optional[List[str]] = None
    """For 'multi', optional list of included languages (codes)"""


class ProviderListTranscribersResponseItemModel(BaseModel):
    id: str
    """Provider-local model id"""

    name: str
    """Display name"""

    description: Optional[str] = None
    """Short description"""

    supported_languages: Optional[List[ProviderListTranscribersResponseItemModelSupportedLanguage]] = None
    """Supported languages"""


class ProviderListTranscribersResponseItem(BaseModel):
    models: List[ProviderListTranscribersResponseItemModel]

    provider: ModelCatalogProvider
    """Provider metadata for a group of models."""


ProviderListTranscribersResponse: TypeAlias = List[ProviderListTranscribersResponseItem]

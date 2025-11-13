# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["ModelCatalogProvider"]


class ModelCatalogProvider(BaseModel):
    code: str
    """Provider code (e.g., azure_openai, openai)"""

    name: str
    """Human-friendly provider name"""

    eu_hosted: Optional[bool] = None
    """Whether the provider is EU-hosted (data residency)"""

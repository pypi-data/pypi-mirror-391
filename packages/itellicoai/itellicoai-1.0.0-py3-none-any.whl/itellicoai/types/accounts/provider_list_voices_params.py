# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

__all__ = ["ProviderListVoicesParams"]


class ProviderListVoicesParams(TypedDict, total=False):
    provider: Required[str]
    """Voice provider (required): elevenlabs, azure, or cartesia"""

    gender: Optional[str]
    """Filter by gender: male, female, or neutral"""

    language: Optional[str]
    """Filter by language code (e.g., 'en-us', 'fr-fr')"""

    limit: Optional[int]
    """Maximum number of voices to return"""

    refresh: bool
    """Clear cache and fetch fresh data from provider"""

    search: Optional[str]
    """Search in voice name or description"""

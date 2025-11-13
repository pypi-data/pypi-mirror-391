# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["SubaccountListParams"]


class SubaccountListParams(TypedDict, total=False):
    is_active: Optional[bool]
    """Filter by active status"""

    limit: int

    offset: int

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

__all__ = ["SubaccountUpdateParams"]


class SubaccountUpdateParams(TypedDict, total=False):
    account_id: Required[str]

    is_active: Optional[bool]
    """Set active state (soft-disable when false)"""

    name: Optional[str]
    """New name for the subaccount"""

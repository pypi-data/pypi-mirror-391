# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["Account"]


class Account(BaseModel):
    id: str
    """Unique identifier for the account"""

    created: str
    """ISO 8601 date-time when the account was created"""

    is_active: bool
    """Whether the account is active"""

    modified: str
    """ISO 8601 date-time when the account was last modified"""

    name: str
    """Account name"""

    parent_account_id: Optional[str] = None
    """Parent account ID (null for root accounts)"""

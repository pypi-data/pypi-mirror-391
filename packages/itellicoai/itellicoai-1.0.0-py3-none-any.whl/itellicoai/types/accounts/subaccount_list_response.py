# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from ..account import Account
from ..._models import BaseModel

__all__ = ["SubaccountListResponse"]


class SubaccountListResponse(BaseModel):
    count: int

    items: List[Account]

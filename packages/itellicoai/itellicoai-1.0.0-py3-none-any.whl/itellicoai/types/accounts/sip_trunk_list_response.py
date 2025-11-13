# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from ..._models import BaseModel
from .sip_trunk import SipTrunk

__all__ = ["SipTrunkListResponse"]


class SipTrunkListResponse(BaseModel):
    count: int

    items: List[SipTrunk]

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

from ..._types import SequenceNotStr

__all__ = ["SipTrunkUpdateParams"]


class SipTrunkUpdateParams(TypedDict, total=False):
    account_id: Required[str]

    allowed_ips: Optional[SequenceNotStr[str]]
    """IPv4/IPv6 or CIDR ranges"""

    name: Optional[str]

    termination_uri: Optional[str]

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

__all__ = ["PhoneNumberCreateParams"]


class PhoneNumberCreateParams(TypedDict, total=False):
    sip_trunk_id: Required[str]
    """SIPTrunk UUID"""

    inbound_agent_id: Optional[str]
    """Inbound Agent UUID"""

    name: Optional[str]
    """Friendly name"""

    number: Optional[str]
    """E.164 phone number"""

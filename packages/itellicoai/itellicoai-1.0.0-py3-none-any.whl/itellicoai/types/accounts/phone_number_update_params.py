# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

__all__ = ["PhoneNumberUpdateParams"]


class PhoneNumberUpdateParams(TypedDict, total=False):
    account_id: Required[str]

    inbound_agent_id: Optional[str]
    """Inbound Agent UUID (set null to unassign)"""

    name: Optional[str]
    """Friendly name"""

    number: Optional[str]
    """E.164 phone number"""

    sip_trunk_id: Optional[str]
    """SIPTrunk UUID (set null to unlink)"""

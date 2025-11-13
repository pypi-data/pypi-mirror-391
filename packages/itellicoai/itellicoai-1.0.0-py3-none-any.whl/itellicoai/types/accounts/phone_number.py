# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from ..._models import BaseModel

__all__ = ["PhoneNumber", "InboundAgent", "SipTrunk"]


class InboundAgent(BaseModel):
    id: str

    name: str

    avatar: Optional[str] = None


class SipTrunk(BaseModel):
    id: str

    name: str
    """Display name for this SIP trunk"""


class PhoneNumber(BaseModel):
    id: str

    friendly_name: Optional[str] = None

    inbound_agent: Optional[InboundAgent] = None

    number: Optional[str] = None

    sip_trunk: Optional[SipTrunk] = None

    spam_data: Optional[Dict[str, object]] = None

    tellows_data: Optional[object] = None
    """
    Tellows spam check data including score, complaints, caller info, and check
    timestamp
    """

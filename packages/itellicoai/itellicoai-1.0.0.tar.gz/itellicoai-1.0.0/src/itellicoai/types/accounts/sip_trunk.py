# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel

__all__ = ["SipTrunk", "PhoneNumber"]


class PhoneNumber(BaseModel):
    id: str

    friendly_name: Optional[str] = None

    number: Optional[str] = None


class SipTrunk(BaseModel):
    id: str

    name: str
    """Display name for this SIP trunk"""

    allowed_ips: Optional[List[str]] = None

    auth_password_length: Optional[int] = None

    has_auth_password: Optional[bool] = None

    phone_numbers: Optional[List[PhoneNumber]] = None

    sip_auth_username: Optional[str] = None

    termination_uri: Optional[str] = None

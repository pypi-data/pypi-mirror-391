# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["Denoising"]


class Denoising(BaseModel):
    telephony: Optional[bool] = None
    """
    Enable enhanced noise cancellation for telephony/SIP calls with optimized phone
    audio processing powered by Krisp.
    """

    web: Optional[bool] = None
    """
    Enable enhanced noise cancellation for web-based calls powered by Krisp
    technology.
    """

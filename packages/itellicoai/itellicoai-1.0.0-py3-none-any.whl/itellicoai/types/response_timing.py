# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["ResponseTiming"]


class ResponseTiming(BaseModel):
    min_endpointing_delay_seconds: Optional[float] = None
    """
    Delay in seconds to wait after user stops speaking before the agent starts
    responding. Prevents the agent from responding too quickly during natural pauses
    in speech. Default is 0.1 seconds.
    """

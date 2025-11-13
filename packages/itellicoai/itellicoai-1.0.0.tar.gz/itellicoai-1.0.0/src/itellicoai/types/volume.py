# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["Volume"]


class Volume(BaseModel):
    allow_adjustment: Optional[bool] = None
    """
    Whether to allow users to adjust volume through voice commands (e.g., 'speak
    louder', 'speak quieter'). When enabled, adds volume control as an available
    tool for the agent.
    """

    telephony: Optional[float] = None
    """Volume level for telephony/SIP calls.

    Range [0.0, 1.0] where 0.0 is muted, 0.5 is normal volume, and 1.0 is maximum
    volume.
    """

    web: Optional[float] = None
    """Volume level for web-based calls.

    Range [0.0, 1.0] where 0.0 is muted, 0.5 is normal volume, and 1.0 is maximum
    volume.
    """

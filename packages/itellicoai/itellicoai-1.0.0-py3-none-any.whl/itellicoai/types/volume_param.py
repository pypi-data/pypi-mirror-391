# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["VolumeParam"]


class VolumeParam(TypedDict, total=False):
    allow_adjustment: bool
    """
    Whether to allow users to adjust volume through voice commands (e.g., 'speak
    louder', 'speak quieter'). When enabled, adds volume control as an available
    tool for the agent.
    """

    telephony: float
    """Volume level for telephony/SIP calls.

    Range [0.0, 1.0] where 0.0 is muted, 0.5 is normal volume, and 1.0 is maximum
    volume.
    """

    web: float
    """Volume level for web-based calls.

    Range [0.0, 1.0] where 0.0 is muted, 0.5 is normal volume, and 1.0 is maximum
    volume.
    """

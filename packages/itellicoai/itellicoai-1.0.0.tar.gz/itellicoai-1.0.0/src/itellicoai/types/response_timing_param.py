# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["ResponseTimingParam"]


class ResponseTimingParam(TypedDict, total=False):
    min_endpointing_delay_seconds: float
    """
    Delay in seconds to wait after user stops speaking before the agent starts
    responding. Prevents the agent from responding too quickly during natural pauses
    in speech. Default is 0.1 seconds.
    """

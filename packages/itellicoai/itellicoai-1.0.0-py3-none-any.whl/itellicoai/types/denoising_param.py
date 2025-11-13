# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["DenoisingParam"]


class DenoisingParam(TypedDict, total=False):
    telephony: bool
    """
    Enable enhanced noise cancellation for telephony/SIP calls with optimized phone
    audio processing powered by Krisp.
    """

    web: bool
    """
    Enable enhanced noise cancellation for web-based calls powered by Krisp
    technology.
    """

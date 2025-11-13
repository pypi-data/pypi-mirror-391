# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["CaptureSettingsParam"]


class CaptureSettingsParam(TypedDict, total=False):
    recording_enabled: Optional[bool]
    """Whether to record the agent's calls. Set to false to disable recording."""

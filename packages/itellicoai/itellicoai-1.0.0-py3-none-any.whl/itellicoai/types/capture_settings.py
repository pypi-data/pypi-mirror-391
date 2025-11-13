# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["CaptureSettings"]


class CaptureSettings(BaseModel):
    recording_enabled: Optional[bool] = None
    """Whether to record the agent's calls. Set to false to disable recording."""

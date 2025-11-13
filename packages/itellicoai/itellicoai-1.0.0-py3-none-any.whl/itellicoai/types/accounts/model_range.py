# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["ModelRange"]


class ModelRange(BaseModel):
    default: Optional[float] = None
    """Default value used when not specified"""

    max: Optional[float] = None
    """Maximum allowed value"""

    min: Optional[float] = None
    """Minimum allowed value"""

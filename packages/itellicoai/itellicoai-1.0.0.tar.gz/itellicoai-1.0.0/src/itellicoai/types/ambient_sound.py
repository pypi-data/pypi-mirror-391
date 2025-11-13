# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["AmbientSound"]


class AmbientSound(BaseModel):
    source: Optional[
        Literal[
            "open_plan_office", "customer_service_center", "internet_cafe", "urban_street", "rural_outdoors", "ac_fan"
        ]
    ] = None
    """Available ambient background sounds to enhance conversation realism"""

    volume: Optional[float] = None
    """Controls the volume of the ambient sound.

    Value ranging from [0.0, 1.0]. 0.0 is muted, 1.0 is maximum volume, and 0.5 is
    normal/default volume.
    """

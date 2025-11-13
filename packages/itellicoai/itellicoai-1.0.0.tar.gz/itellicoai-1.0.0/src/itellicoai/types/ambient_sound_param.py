# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, TypedDict

__all__ = ["AmbientSoundParam"]


class AmbientSoundParam(TypedDict, total=False):
    source: Optional[
        Literal[
            "open_plan_office", "customer_service_center", "internet_cafe", "urban_street", "rural_outdoors", "ac_fan"
        ]
    ]
    """Available ambient background sounds to enhance conversation realism"""

    volume: float
    """Controls the volume of the ambient sound.

    Value ranging from [0.0, 1.0]. 0.0 is muted, 1.0 is maximum volume, and 0.5 is
    normal/default volume.
    """

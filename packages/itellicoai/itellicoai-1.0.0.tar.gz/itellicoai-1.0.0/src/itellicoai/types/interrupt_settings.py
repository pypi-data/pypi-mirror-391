# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["InterruptSettings"]


class InterruptSettings(BaseModel):
    enabled: Optional[bool] = None
    """Whether users can interrupt the agent while it's speaking.

    When true, the agent will stop speaking and listen when the user starts talking.
    """

    min_speech_seconds: Optional[float] = None
    """
    Minimum duration in seconds of continuous speech required to trigger an
    interruption. Helps filter out brief noises.
    """

    min_words: Optional[int] = None
    """Minimum number of words the user must speak to trigger an interruption.

    Helps prevent accidental interruptions from brief sounds.
    """

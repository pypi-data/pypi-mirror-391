# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["InterruptSettingsParam"]


class InterruptSettingsParam(TypedDict, total=False):
    enabled: bool
    """Whether users can interrupt the agent while it's speaking.

    When true, the agent will stop speaking and listen when the user starts talking.
    """

    min_speech_seconds: float
    """
    Minimum duration in seconds of continuous speech required to trigger an
    interruption. Helps filter out brief noises.
    """

    min_words: int
    """Minimum number of words the user must speak to trigger an interruption.

    Helps prevent accidental interruptions from brief sounds.
    """

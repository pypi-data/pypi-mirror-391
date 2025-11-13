# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, TypedDict

__all__ = ["InitialMessageParam"]


class InitialMessageParam(TypedDict, total=False):
    delay_ms: int
    """
    Delay in milliseconds before the agent speaks the initial message, giving users
    time to prepare. Valid range is [0, 5000]. Default is 0 (speak immediately).
    Only applies when mode is 'fixed_message' or 'dynamic_message'.
    """

    interruptible: bool
    """Whether the user can interrupt the agent while it's speaking the initial
    message.

    When false, the agent will complete its initial greeting before listening.
    Default is false for a smoother start to conversations.
    """

    message: Optional[str]
    """The first message that the agent will say when starting a conversation.

    If not set, the agent will wait for the user to speak first. Use this to set a
    friendly greeting like 'Hello! How can I help you today?'. You can add variables
    in double curly brackets, for example: {{customer_name}} or {{company_name}}.
    """

    mode: Literal["fixed_message", "user_first", "dynamic_message"]
    """How the agent should handle the initial message"""

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["InitialMessage"]


class InitialMessage(BaseModel):
    delay_ms: Optional[int] = None
    """
    Delay in milliseconds before the agent speaks the initial message, giving users
    time to prepare. Valid range is [0, 5000]. Default is 0 (speak immediately).
    Only applies when mode is 'fixed_message' or 'dynamic_message'.
    """

    interruptible: Optional[bool] = None
    """Whether the user can interrupt the agent while it's speaking the initial
    message.

    When false, the agent will complete its initial greeting before listening.
    Default is false for a smoother start to conversations.
    """

    message: Optional[str] = None
    """The first message that the agent will say when starting a conversation.

    If not set, the agent will wait for the user to speak first. Use this to set a
    friendly greeting like 'Hello! How can I help you today?'. You can add variables
    in double curly brackets, for example: {{customer_name}} or {{company_name}}.
    """

    mode: Optional[Literal["fixed_message", "user_first", "dynamic_message"]] = None
    """How the agent should handle the initial message"""

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from datetime import datetime
from typing_extensions import Literal, Annotated, TypeAlias

from .._utils import PropertyInfo
from .._models import BaseModel
from .conversation_type import ConversationType
from .conversation_status import ConversationStatus
from .conversation_direction import ConversationDirection

__all__ = [
    "AccountListConversationsResponse",
    "Item",
    "ItemCapture",
    "ItemMessage",
    "ItemMessageUserMessageSchema",
    "ItemMessageAgentMessageSchema",
    "ItemMessageSystemMessageSchema",
    "ItemMessageToolMessageSchema",
    "ItemMessageEventMessageSchema",
]


class ItemCapture(BaseModel):
    recording_url: Optional[str] = None
    """URL or path to the conversation recording, when available."""


class ItemMessageUserMessageSchema(BaseModel):
    message: str

    role: Optional[Literal["user"]] = None

    timestamp: Optional[datetime] = None
    """UTC timestamp when the message was logged."""


class ItemMessageAgentMessageSchema(BaseModel):
    message: str

    role: Optional[Literal["agent"]] = None

    timestamp: Optional[datetime] = None
    """UTC timestamp when the message was logged."""


class ItemMessageSystemMessageSchema(BaseModel):
    message: str

    role: Optional[Literal["system"]] = None

    timestamp: Optional[datetime] = None
    """UTC timestamp when the message was logged."""


class ItemMessageToolMessageSchema(BaseModel):
    message: Optional[str] = None

    name: Optional[str] = None

    result: Optional[object] = None

    role: Optional[Literal["tool"]] = None

    timestamp: Optional[datetime] = None
    """UTC timestamp when the message was logged."""


class ItemMessageEventMessageSchema(BaseModel):
    message: Optional[str] = None

    role: Optional[Literal["event"]] = None

    timestamp: Optional[datetime] = None
    """UTC timestamp when the message was logged."""


ItemMessage: TypeAlias = Annotated[
    Union[
        ItemMessageUserMessageSchema,
        ItemMessageAgentMessageSchema,
        ItemMessageSystemMessageSchema,
        ItemMessageToolMessageSchema,
        ItemMessageEventMessageSchema,
    ],
    PropertyInfo(discriminator="role"),
]


class Item(BaseModel):
    conversation_id: str

    start_timestamp: datetime

    status: ConversationStatus
    """High-level lifecycle statuses reported by the conversations API."""

    type: ConversationType
    """Conversation type classification (phone, web, or test)."""

    agent_id: Optional[str] = None

    agent_name: Optional[str] = None

    capture: Optional[ItemCapture] = None
    """Capture artifacts associated with a conversation."""

    contact_number: Optional[str] = None
    """Contact-side phone number when the type is phone."""

    direction: Optional[ConversationDirection] = None
    """Directionality of a conversation."""

    duration_seconds: Optional[int] = None

    messages: Optional[List[ItemMessage]] = None

    phone_number: Optional[str] = None
    """Agent-side phone number when the type is phone."""

    phone_number_id: Optional[str] = None


class AccountListConversationsResponse(BaseModel):
    count: int

    items: List[Item]

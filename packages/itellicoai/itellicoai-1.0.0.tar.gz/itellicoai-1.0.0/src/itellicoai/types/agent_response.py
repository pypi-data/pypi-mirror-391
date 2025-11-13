# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from datetime import datetime

from .volume import Volume
from .._models import BaseModel
from .denoising import Denoising
from .ambient_sound import AmbientSound
from .initial_message import InitialMessage
from .response_timing import ResponseTiming
from .capture_settings import CaptureSettings
from .interrupt_settings import InterruptSettings
from .inactivity_settings import InactivitySettings

__all__ = ["AgentResponse"]


class AgentResponse(BaseModel):
    id: str
    """Unique identifier for the agent.

    Use this ID to reference the agent in API calls for updates, deletion, or
    starting conversations.
    """

    account_id: str
    """Unique identifier for the account that owns this agent."""

    ambient_sound: AmbientSound
    """Configuration for ambient background sounds during the conversation."""

    inactivity_settings: InactivitySettings
    """Configuration for handling user inactivity and silence during conversations."""

    initial_message: InitialMessage
    """Configuration for the agent's initial message when starting a conversation."""

    name: str
    """The display name of the agent as configured.

    This is for your reference and internal organization.
    """

    response_timing: ResponseTiming
    """Configuration for agent response timing and conversation flow control."""

    capture_settings: Optional[CaptureSettings] = None
    """Agent capture settings configuration."""

    created: Optional[datetime] = None
    """Date-time of when the agent was created (ISO 8601 on output)."""

    denoising: Optional[Denoising] = None
    """Agent denoising/noise cancellation settings for enhanced audio quality."""

    interrupt_settings: Optional[InterruptSettings] = None
    """Configuration for how the agent handles user interruptions during conversation"""

    max_duration_seconds: Optional[int] = None
    """The maximum conversation duration configured for this agent in seconds.

    Maximum allowed is 7200 seconds (2 hours).
    """

    metadata: Optional[Dict[str, object]] = None
    """Custom metadata associated with the agent."""

    model: Optional[Dict[str, object]] = None
    """Language model configuration for the agent."""

    modified: Optional[datetime] = None
    """Date-time of when the agent was last updated (ISO 8601 on output)."""

    note: Optional[str] = None
    """Internal notes about the agent for your team's reference."""

    tags: Optional[List[str]] = None
    """List of tags assigned to this agent for categorization and filtering."""

    transcriber: Optional[Dict[str, object]] = None
    """Speech-to-text configuration for the agent."""

    voice: Optional[Dict[str, object]] = None
    """Text-to-speech configuration for the agent."""

    volume: Optional[Volume] = None
    """Agent volume settings for audio output control."""

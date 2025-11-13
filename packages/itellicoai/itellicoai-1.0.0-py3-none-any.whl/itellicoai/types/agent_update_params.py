# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Optional
from typing_extensions import Required, TypeAlias, TypedDict

from .._types import SequenceNotStr
from .volume_param import VolumeParam
from .denoising_param import DenoisingParam
from .ambient_sound_param import AmbientSoundParam
from .initial_message_param import InitialMessageParam
from .response_timing_param import ResponseTimingParam
from .capture_settings_param import CaptureSettingsParam
from .azure_transcriber_param import AzureTranscriberParam
from .interrupt_settings_param import InterruptSettingsParam
from .inactivity_settings_param import InactivitySettingsParam
from .deepgram_transcriber_param import DeepgramTranscriberParam

__all__ = ["AgentUpdateParams", "Transcriber"]


class AgentUpdateParams(TypedDict, total=False):
    account_id: Required[str]

    ambient_sound: Optional[AmbientSoundParam]
    """Configuration for ambient background sounds during the conversation"""

    capture_settings: Optional[CaptureSettingsParam]
    """Agent capture settings configuration."""

    denoising: Optional[DenoisingParam]
    """Agent denoising/noise cancellation settings for enhanced audio quality."""

    inactivity_settings: Optional[InactivitySettingsParam]
    """Configuration for handling user inactivity during conversations"""

    initial_message: Optional[InitialMessageParam]
    """Configuration for the agent's initial message when starting a conversation"""

    interrupt_settings: Optional[InterruptSettingsParam]
    """Configuration for how the agent handles user interruptions during conversation"""

    max_duration_seconds: Optional[int]
    """Maximum allowed length for the conversation in seconds.

    Maximum is 7200 seconds (2 hours).
    """

    metadata: Optional[Dict[str, object]]
    """Custom metadata for the agent.

    Store any additional key-value pairs that your application needs.
    """

    model: Optional[Dict[str, object]]
    """Language model configuration for the agent. Partial updates allowed."""

    name: Optional[str]
    """The name of the agent. Only used for your own reference."""

    note: Optional[str]
    """Internal notes about the agent."""

    response_timing: Optional[ResponseTimingParam]
    """Configuration for agent response timing and conversation flow control"""

    tags: Optional[SequenceNotStr[str]]
    """List of tags to categorize the agent."""

    transcriber: Optional[Transcriber]
    """Transcriber (speech-to-text) configuration for the agent.

    Partial updates allowed.
    """

    voice: Optional[Dict[str, object]]
    """Text-to-speech configuration for the agent. Partial updates allowed."""

    volume: Optional[VolumeParam]
    """Agent volume settings for audio output control."""


Transcriber: TypeAlias = Union[AzureTranscriberParam, DeepgramTranscriberParam]

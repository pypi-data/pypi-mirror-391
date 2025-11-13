# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

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

__all__ = [
    "AgentCreateParams",
    "Model",
    "ModelOpenAIModelSchema",
    "ModelAzureOpenAIModelSchema",
    "ModelAnthropicModelSchema",
    "Transcriber",
    "Voice",
    "VoiceAzureVoiceSchema",
    "VoiceCartesiaVoiceSchema",
    "VoiceElevenLabsVoiceSchema",
    "VoiceElevenLabsVoiceSchemaSettings",
]


class AgentCreateParams(TypedDict, total=False):
    model: Required[Model]
    """Model configuration for the agent.

    Defines which AI model to use (OpenAI GPT-4, Anthropic Claude, etc.) and its
    parameters like temperature and max tokens.
    """

    transcriber: Required[Transcriber]
    """Transcriber (speech-to-text) configuration for the agent.

    Defines which transcriber provider to use (Azure, Deepgram) and language
    settings.
    """

    voice: Required[Voice]
    """Voice (text-to-speech) configuration for the agent.

    Defines which provider and voice to use (OpenAI, ElevenLabs, Cartesia, Azure)
    with voice-specific settings.
    """

    ambient_sound: AmbientSoundParam
    """Configuration for ambient background sounds during the conversation"""

    capture_settings: Optional[CaptureSettingsParam]
    """Agent capture settings configuration."""

    denoising: Optional[DenoisingParam]
    """Agent denoising/noise cancellation settings for enhanced audio quality."""

    inactivity_settings: InactivitySettingsParam
    """Configuration for handling user inactivity during conversations"""

    initial_message: InitialMessageParam
    """Configuration for the agent's initial message when starting a conversation"""

    interrupt_settings: Optional[InterruptSettingsParam]
    """Configuration for how the agent handles user interruptions during conversation"""

    max_duration_seconds: Optional[int]
    """Maximum allowed length for the conversation in seconds.

    Default is 1200 seconds (20 minutes) if not specified.
    """

    metadata: Optional[Dict[str, object]]
    """Custom metadata for the agent.

    Store any additional key-value pairs that your application needs. This data is
    not used by the agent itself but can be useful for integrations, tracking, or
    custom business logic.
    """

    name: Optional[str]
    """The name of the agent.

    Only used for your own reference to identify and manage agents. Not visible to
    end users during conversations.
    """

    note: Optional[str]
    """Internal notes about the agent.

    These notes are for your team's reference only and are not visible to end users.
    Use this to document agent configuration, purpose, or any special instructions.
    """

    response_timing: ResponseTimingParam
    """Configuration for agent response timing and conversation flow control"""

    tags: Optional[SequenceNotStr[str]]
    """List of tags to categorize and organize your agents.

    Tags help you filter and find agents quickly. Examples: 'sales', 'support',
    'lead-qualification', 'appointment-booking'.
    """

    volume: Optional[VolumeParam]
    """Agent volume settings for audio output control."""


class ModelOpenAIModelSchema(TypedDict, total=False):
    model: Required[
        Literal["gpt-5", "gpt-5-mini", "gpt-5-nano", "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "gpt-4o", "gpt-4o-mini"]
    ]
    """The OpenAI model to use."""

    max_tokens: Optional[int]
    """Max number of tokens the agent will be allowed to generate in each turn.

    Default is 250.
    """

    provider: Literal["openai"]

    temperature: Optional[float]
    """Temperature for the model. Default is 0 to leverage caching for lower latency."""


class ModelAzureOpenAIModelSchema(TypedDict, total=False):
    model: Required[
        Literal[
            "gpt-5-mini",
            "gpt-5-nano",
            "gpt-4.1-2025-04-14",
            "gpt-4.1-mini-2025-04-14",
            "gpt-4.1-nano-2025-04-14",
            "gpt-4o-2024-11-20",
            "gpt-4o-mini-2024-07-18",
        ]
    ]
    """The Azure OpenAI model to use."""

    max_tokens: Optional[int]
    """Max number of tokens the agent will be allowed to generate in each turn.

    Default is 250.
    """

    provider: Literal["azure_openai"]

    temperature: Optional[float]
    """Temperature for the model. Default is 0 to leverage caching for lower latency."""


class ModelAnthropicModelSchema(TypedDict, total=False):
    model: Required[Literal["claude-sonnet-4-20250514", "claude-3-7-sonnet-20250219", "claude-3-5-haiku-20241022"]]
    """The Anthropic model to use."""

    max_tokens: Optional[int]
    """Max number of tokens the agent will be allowed to generate in each turn.

    Default is 250.
    """

    provider: Literal["anthropic"]

    temperature: Optional[float]
    """Temperature for the model. Default is 0 to leverage caching for lower latency."""


Model: TypeAlias = Union[ModelOpenAIModelSchema, ModelAzureOpenAIModelSchema, ModelAnthropicModelSchema]

Transcriber: TypeAlias = Union[AzureTranscriberParam, DeepgramTranscriberParam]


class VoiceAzureVoiceSchema(TypedDict, total=False):
    voice_id: Required[str]
    """Azure voice ID"""

    provider: Literal["azure"]


class VoiceCartesiaVoiceSchema(TypedDict, total=False):
    voice_id: Required[str]
    """The provider-specific voice ID to use"""

    language: Optional[
        Literal["en", "es", "fr", "de", "pt", "zh", "ja", "hi", "it", "ko", "nl", "pl", "ru", "sv", "tr"]
    ]
    """Language to use (defaults to correct language for voiceId)"""

    provider: Literal["cartesia"]


class VoiceElevenLabsVoiceSchemaSettings(TypedDict, total=False):
    optimize_streaming_latency: Optional[float]
    """Optimize streaming latency setting"""

    similarity_boost: Optional[float]
    """Voice similarity boost setting"""

    speed: Optional[float]
    """Voice speed setting"""

    stability: Optional[float]
    """Voice stability setting"""

    style: Optional[float]
    """Voice style setting"""

    use_speaker_boost: Optional[bool]
    """Enable speaker boost"""


class VoiceElevenLabsVoiceSchema(TypedDict, total=False):
    voice_id: Required[str]
    """ElevenLabs voice ID"""

    provider: Literal["elevenlabs"]

    settings: Optional[VoiceElevenLabsVoiceSchemaSettings]
    """ElevenLabs-specific voice settings."""


Voice: TypeAlias = Union[VoiceAzureVoiceSchema, VoiceCartesiaVoiceSchema, VoiceElevenLabsVoiceSchema]

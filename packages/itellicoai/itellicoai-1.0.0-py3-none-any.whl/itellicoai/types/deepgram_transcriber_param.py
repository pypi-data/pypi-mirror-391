# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, TypedDict

from .._types import SequenceNotStr

__all__ = ["DeepgramTranscriberParam"]


class DeepgramTranscriberParam(TypedDict, total=False):
    keywords: Optional[SequenceNotStr[str]]
    """Keywords to help model pick up use-case specific words"""

    language: Optional[
        Literal[
            "bg",
            "ca",
            "cs",
            "da",
            "da-DK",
            "de",
            "de-CH",
            "el",
            "en",
            "en-AU",
            "en-GB",
            "en-IN",
            "en-NZ",
            "en-US",
            "es",
            "es-419",
            "es-LATAM",
            "et",
            "fi",
            "fr",
            "fr-CA",
            "hi",
            "hi-Latn",
            "hu",
            "id",
            "it",
            "ja",
            "ko",
            "ko-KR",
            "lt",
            "lv",
            "ms",
            "multi",
            "nl",
            "nl-BE",
            "no",
            "pl",
            "pt",
            "pt-BR",
            "ro",
            "ru",
            "sk",
            "sv",
            "sv-SE",
            "ta",
            "taq",
            "th",
            "th-TH",
            "tr",
            "uk",
            "vi",
            "zh",
            "zh-CN",
            "zh-Hans",
            "zh-Hant",
            "zh-TW",
        ]
    ]
    """Language for transcription (see Deepgram docs for supported languages)"""

    model: Optional[
        Literal[
            "nova-3:general",
            "nova-3:medical",
            "nova-2:general",
            "nova-2:phonecall",
            "nova-2:meeting",
            "nova-2:conversationalai",
        ]
    ]
    """Deepgram model to use (matches our YAML configuration)"""

    provider: Literal["deepgram"]

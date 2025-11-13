# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from datetime import datetime
from typing_extensions import Annotated, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo

__all__ = ["AgentListParams"]


class AgentListParams(TypedDict, total=False):
    created_ge: Annotated[Union[str, datetime, None], PropertyInfo(format="iso8601")]
    """Filter agents created on or after this datetime (ISO 8601, timezone-aware)."""

    created_gt: Annotated[Union[str, datetime, None], PropertyInfo(format="iso8601")]
    """Filter agents created after this datetime (ISO 8601, timezone-aware)."""

    created_le: Annotated[Union[str, datetime, None], PropertyInfo(format="iso8601")]
    """Filter agents created on or before this datetime (ISO 8601, timezone-aware)."""

    created_lt: Annotated[Union[str, datetime, None], PropertyInfo(format="iso8601")]
    """Filter agents created before this datetime (ISO 8601, timezone-aware)."""

    is_archived: Optional[bool]
    """Filter by archived status. If omitted, archived are excluded by default."""

    limit: int

    modified_ge: Annotated[Union[str, datetime, None], PropertyInfo(format="iso8601")]
    """Filter agents modified on or after this datetime (ISO 8601, timezone-aware)."""

    modified_gt: Annotated[Union[str, datetime, None], PropertyInfo(format="iso8601")]
    """Filter agents modified after this datetime (ISO 8601, timezone-aware)."""

    modified_le: Annotated[Union[str, datetime, None], PropertyInfo(format="iso8601")]
    """Filter agents modified on or before this datetime (ISO 8601, timezone-aware)."""

    modified_lt: Annotated[Union[str, datetime, None], PropertyInfo(format="iso8601")]
    """Filter agents modified before this datetime (ISO 8601, timezone-aware)."""

    name: Optional[str]
    """Case-insensitive partial match on agent name."""

    offset: int

    tags: Optional[SequenceNotStr[str]]
    """Filter by tags. Returns agents that have ALL specified tags."""

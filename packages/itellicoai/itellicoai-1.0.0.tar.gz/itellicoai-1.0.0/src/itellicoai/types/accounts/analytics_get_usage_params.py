# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Optional
from datetime import datetime
from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo
from .usage_group_by import UsageGroupBy

__all__ = ["AnalyticsGetUsageParams"]


class AnalyticsGetUsageParams(TypedDict, total=False):
    end: Annotated[Union[str, datetime, None], PropertyInfo(format="iso8601")]
    """End timestamp (ISO-8601). Defaults to now."""

    granularity: Literal["hour", "day", "month"]
    """Bucket granularity for aggregation."""

    group_by: Optional[List[UsageGroupBy]]
    """Dimensions to break results by (comma separated or repeated query params)."""

    limit: Optional[int]
    """Maximum number of time buckets to return (default 500)."""

    start: Annotated[Union[str, datetime, None], PropertyInfo(format="iso8601")]
    """Start timestamp (ISO-8601). Defaults to 30 days before `end`."""

    tz: Optional[str]
    """IANA timezone name used for bucket boundaries (default UTC)."""

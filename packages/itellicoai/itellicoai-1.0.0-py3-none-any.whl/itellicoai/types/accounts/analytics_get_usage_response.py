# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from datetime import datetime
from typing_extensions import Literal

from ..._models import BaseModel
from .usage_group_by import UsageGroupBy

__all__ = ["AnalyticsGetUsageResponse", "Meta", "Data", "DataValue"]


class Meta(BaseModel):
    account_id: str

    end: datetime

    granularity: Literal["hour", "day", "month"]

    start: datetime

    group_by: Optional[List[UsageGroupBy]] = None
    """Requested grouping dimensions."""

    tz: Optional[str] = None
    """Timezone applied to bucket boundaries."""


class DataValue(BaseModel):
    conversations: int
    """Completed conversations represented by this value."""

    seconds: int
    """Total conversation seconds represented by this value."""

    dimensions: Optional[Dict[str, str]] = None
    """Grouping dimension key/value pairs for this value."""


class Data(BaseModel):
    ts: datetime
    """Bucket start timestamp in the requested timezone."""

    values: Optional[List[DataValue]] = None
    """Metric values for this bucket."""


class AnalyticsGetUsageResponse(BaseModel):
    meta: Meta
    """Metadata describing the usage response."""

    data: Optional[List[Data]] = None

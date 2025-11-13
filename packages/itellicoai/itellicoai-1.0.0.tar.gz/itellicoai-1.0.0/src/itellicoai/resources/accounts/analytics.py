# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Optional
from datetime import datetime
from typing_extensions import Literal

import httpx

from ..._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.accounts import analytics_get_usage_params
from ...types.accounts.usage_group_by import UsageGroupBy
from ...types.accounts.analytics_get_usage_response import AnalyticsGetUsageResponse

__all__ = ["AnalyticsResource", "AsyncAnalyticsResource"]


class AnalyticsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AnalyticsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/itellicoAI/server-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AnalyticsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AnalyticsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/itellicoAI/server-sdk-python#with_streaming_response
        """
        return AnalyticsResourceWithStreamingResponse(self)

    def get_usage(
        self,
        account_id: str,
        *,
        end: Union[str, datetime, None] | Omit = omit,
        granularity: Literal["hour", "day", "month"] | Omit = omit,
        group_by: Optional[List[UsageGroupBy]] | Omit = omit,
        limit: Optional[int] | Omit = omit,
        start: Union[str, datetime, None] | Omit = omit,
        tz: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AnalyticsGetUsageResponse:
        """Aggregate conversation usage for the specified account.

        Supports configurable
        time ranges, bucket granularity, and optional groupings by agent, subaccount, or
        conversation type.

        Args:
          end: End timestamp (ISO-8601). Defaults to now.

          granularity: Bucket granularity for aggregation.

          group_by: Dimensions to break results by (comma separated or repeated query params).

          limit: Maximum number of time buckets to return (default 500).

          start: Start timestamp (ISO-8601). Defaults to 30 days before `end`.

          tz: IANA timezone name used for bucket boundaries (default UTC).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/analytics/usage",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "end": end,
                        "granularity": granularity,
                        "group_by": group_by,
                        "limit": limit,
                        "start": start,
                        "tz": tz,
                    },
                    analytics_get_usage_params.AnalyticsGetUsageParams,
                ),
            ),
            cast_to=AnalyticsGetUsageResponse,
        )


class AsyncAnalyticsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAnalyticsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/itellicoAI/server-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAnalyticsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAnalyticsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/itellicoAI/server-sdk-python#with_streaming_response
        """
        return AsyncAnalyticsResourceWithStreamingResponse(self)

    async def get_usage(
        self,
        account_id: str,
        *,
        end: Union[str, datetime, None] | Omit = omit,
        granularity: Literal["hour", "day", "month"] | Omit = omit,
        group_by: Optional[List[UsageGroupBy]] | Omit = omit,
        limit: Optional[int] | Omit = omit,
        start: Union[str, datetime, None] | Omit = omit,
        tz: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AnalyticsGetUsageResponse:
        """Aggregate conversation usage for the specified account.

        Supports configurable
        time ranges, bucket granularity, and optional groupings by agent, subaccount, or
        conversation type.

        Args:
          end: End timestamp (ISO-8601). Defaults to now.

          granularity: Bucket granularity for aggregation.

          group_by: Dimensions to break results by (comma separated or repeated query params).

          limit: Maximum number of time buckets to return (default 500).

          start: Start timestamp (ISO-8601). Defaults to 30 days before `end`.

          tz: IANA timezone name used for bucket boundaries (default UTC).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/analytics/usage",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "end": end,
                        "granularity": granularity,
                        "group_by": group_by,
                        "limit": limit,
                        "start": start,
                        "tz": tz,
                    },
                    analytics_get_usage_params.AnalyticsGetUsageParams,
                ),
            ),
            cast_to=AnalyticsGetUsageResponse,
        )


class AnalyticsResourceWithRawResponse:
    def __init__(self, analytics: AnalyticsResource) -> None:
        self._analytics = analytics

        self.get_usage = to_raw_response_wrapper(
            analytics.get_usage,
        )


class AsyncAnalyticsResourceWithRawResponse:
    def __init__(self, analytics: AsyncAnalyticsResource) -> None:
        self._analytics = analytics

        self.get_usage = async_to_raw_response_wrapper(
            analytics.get_usage,
        )


class AnalyticsResourceWithStreamingResponse:
    def __init__(self, analytics: AnalyticsResource) -> None:
        self._analytics = analytics

        self.get_usage = to_streamed_response_wrapper(
            analytics.get_usage,
        )


class AsyncAnalyticsResourceWithStreamingResponse:
    def __init__(self, analytics: AsyncAnalyticsResource) -> None:
        self._analytics = analytics

        self.get_usage = async_to_streamed_response_wrapper(
            analytics.get_usage,
        )

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

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
from ...types.account import Account
from ...types.accounts import subaccount_list_params, subaccount_create_params, subaccount_update_params
from ...types.accounts.subaccount_list_response import SubaccountListResponse

__all__ = ["SubaccountsResource", "AsyncSubaccountsResource"]


class SubaccountsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SubaccountsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/itellicoAI/server-sdk-python#accessing-raw-response-data-eg-headers
        """
        return SubaccountsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SubaccountsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/itellicoAI/server-sdk-python#with_streaming_response
        """
        return SubaccountsResourceWithStreamingResponse(self)

    def create(
        self,
        account_id: str,
        *,
        name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Account:
        """Create a new subaccount under the specified parent account.

        The creator becomes
        OWNER of the new subaccount.

        Args:
          name: Name of the subaccount to create

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._post(
            f"/v1/accounts/{account_id}/subaccounts",
            body=maybe_transform({"name": name}, subaccount_create_params.SubaccountCreateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Account,
        )

    def retrieve(
        self,
        subaccount_id: str,
        *,
        account_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Account:
        """
        Fetch a specific subaccount by ID under the specified parent account.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not subaccount_id:
            raise ValueError(f"Expected a non-empty value for `subaccount_id` but received {subaccount_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/subaccounts/{subaccount_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Account,
        )

    def update(
        self,
        subaccount_id: str,
        *,
        account_id: str,
        is_active: Optional[bool] | Omit = omit,
        name: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Account:
        """
        Update subaccount properties such as name.

        Args:
          is_active: Set active state (soft-disable when false)

          name: New name for the subaccount

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not subaccount_id:
            raise ValueError(f"Expected a non-empty value for `subaccount_id` but received {subaccount_id!r}")
        return self._patch(
            f"/v1/accounts/{account_id}/subaccounts/{subaccount_id}",
            body=maybe_transform(
                {
                    "is_active": is_active,
                    "name": name,
                },
                subaccount_update_params.SubaccountUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Account,
        )

    def list(
        self,
        account_id: str,
        *,
        is_active: Optional[bool] | Omit = omit,
        limit: int | Omit = omit,
        offset: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SubaccountListResponse:
        """
        Paginated list of child accounts directly under the specified parent account.

        Args:
          is_active: Filter by active status

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/subaccounts",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "is_active": is_active,
                        "limit": limit,
                        "offset": offset,
                    },
                    subaccount_list_params.SubaccountListParams,
                ),
            ),
            cast_to=SubaccountListResponse,
        )


class AsyncSubaccountsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSubaccountsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/itellicoAI/server-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncSubaccountsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSubaccountsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/itellicoAI/server-sdk-python#with_streaming_response
        """
        return AsyncSubaccountsResourceWithStreamingResponse(self)

    async def create(
        self,
        account_id: str,
        *,
        name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Account:
        """Create a new subaccount under the specified parent account.

        The creator becomes
        OWNER of the new subaccount.

        Args:
          name: Name of the subaccount to create

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._post(
            f"/v1/accounts/{account_id}/subaccounts",
            body=await async_maybe_transform({"name": name}, subaccount_create_params.SubaccountCreateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Account,
        )

    async def retrieve(
        self,
        subaccount_id: str,
        *,
        account_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Account:
        """
        Fetch a specific subaccount by ID under the specified parent account.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not subaccount_id:
            raise ValueError(f"Expected a non-empty value for `subaccount_id` but received {subaccount_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/subaccounts/{subaccount_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Account,
        )

    async def update(
        self,
        subaccount_id: str,
        *,
        account_id: str,
        is_active: Optional[bool] | Omit = omit,
        name: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Account:
        """
        Update subaccount properties such as name.

        Args:
          is_active: Set active state (soft-disable when false)

          name: New name for the subaccount

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not subaccount_id:
            raise ValueError(f"Expected a non-empty value for `subaccount_id` but received {subaccount_id!r}")
        return await self._patch(
            f"/v1/accounts/{account_id}/subaccounts/{subaccount_id}",
            body=await async_maybe_transform(
                {
                    "is_active": is_active,
                    "name": name,
                },
                subaccount_update_params.SubaccountUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Account,
        )

    async def list(
        self,
        account_id: str,
        *,
        is_active: Optional[bool] | Omit = omit,
        limit: int | Omit = omit,
        offset: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SubaccountListResponse:
        """
        Paginated list of child accounts directly under the specified parent account.

        Args:
          is_active: Filter by active status

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/subaccounts",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "is_active": is_active,
                        "limit": limit,
                        "offset": offset,
                    },
                    subaccount_list_params.SubaccountListParams,
                ),
            ),
            cast_to=SubaccountListResponse,
        )


class SubaccountsResourceWithRawResponse:
    def __init__(self, subaccounts: SubaccountsResource) -> None:
        self._subaccounts = subaccounts

        self.create = to_raw_response_wrapper(
            subaccounts.create,
        )
        self.retrieve = to_raw_response_wrapper(
            subaccounts.retrieve,
        )
        self.update = to_raw_response_wrapper(
            subaccounts.update,
        )
        self.list = to_raw_response_wrapper(
            subaccounts.list,
        )


class AsyncSubaccountsResourceWithRawResponse:
    def __init__(self, subaccounts: AsyncSubaccountsResource) -> None:
        self._subaccounts = subaccounts

        self.create = async_to_raw_response_wrapper(
            subaccounts.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            subaccounts.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            subaccounts.update,
        )
        self.list = async_to_raw_response_wrapper(
            subaccounts.list,
        )


class SubaccountsResourceWithStreamingResponse:
    def __init__(self, subaccounts: SubaccountsResource) -> None:
        self._subaccounts = subaccounts

        self.create = to_streamed_response_wrapper(
            subaccounts.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            subaccounts.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            subaccounts.update,
        )
        self.list = to_streamed_response_wrapper(
            subaccounts.list,
        )


class AsyncSubaccountsResourceWithStreamingResponse:
    def __init__(self, subaccounts: AsyncSubaccountsResource) -> None:
        self._subaccounts = subaccounts

        self.create = async_to_streamed_response_wrapper(
            subaccounts.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            subaccounts.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            subaccounts.update,
        )
        self.list = async_to_streamed_response_wrapper(
            subaccounts.list,
        )

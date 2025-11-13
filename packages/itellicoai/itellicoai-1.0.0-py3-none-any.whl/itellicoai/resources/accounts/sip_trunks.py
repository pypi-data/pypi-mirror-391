# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from ..._types import Body, Omit, Query, Headers, NoneType, NotGiven, SequenceNotStr, omit, not_given
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
from ...types.accounts import sip_trunk_list_params, sip_trunk_create_params, sip_trunk_update_params
from ...types.accounts.sip_trunk import SipTrunk
from ...types.accounts.sip_trunk_list_response import SipTrunkListResponse

__all__ = ["SipTrunksResource", "AsyncSipTrunksResource"]


class SipTrunksResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SipTrunksResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/itellicoAI/server-sdk-python#accessing-raw-response-data-eg-headers
        """
        return SipTrunksResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SipTrunksResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/itellicoAI/server-sdk-python#with_streaming_response
        """
        return SipTrunksResourceWithStreamingResponse(self)

    def create(
        self,
        account_id: str,
        *,
        allowed_ips: Optional[SequenceNotStr[str]] | Omit = omit,
        name: Optional[str] | Omit = omit,
        termination_uri: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SipTrunk:
        """Create a Bring-Your-Own-Carrier (BYOC) SIP trunk for inbound/outbound calls.

        For
        trunks that target FusionPBX, provisioning is performed synchronously.

        Args:
          allowed_ips: IPv4/IPv6 or CIDR ranges

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._post(
            f"/v1/accounts/{account_id}/sip-trunks",
            body=maybe_transform(
                {
                    "allowed_ips": allowed_ips,
                    "name": name,
                    "termination_uri": termination_uri,
                },
                sip_trunk_create_params.SipTrunkCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SipTrunk,
        )

    def retrieve(
        self,
        sip_trunk_id: str,
        *,
        account_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SipTrunk:
        """
        Fetch a single SIP trunk by ID for the specified account.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not sip_trunk_id:
            raise ValueError(f"Expected a non-empty value for `sip_trunk_id` but received {sip_trunk_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/sip-trunks/{sip_trunk_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SipTrunk,
        )

    def update(
        self,
        sip_trunk_id: str,
        *,
        account_id: str,
        allowed_ips: Optional[SequenceNotStr[str]] | Omit = omit,
        name: Optional[str] | Omit = omit,
        termination_uri: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SipTrunk:
        """
        Update BYOC SIP trunk properties and allowed IPs.

        Args:
          allowed_ips: IPv4/IPv6 or CIDR ranges

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not sip_trunk_id:
            raise ValueError(f"Expected a non-empty value for `sip_trunk_id` but received {sip_trunk_id!r}")
        return self._patch(
            f"/v1/accounts/{account_id}/sip-trunks/{sip_trunk_id}",
            body=maybe_transform(
                {
                    "allowed_ips": allowed_ips,
                    "name": name,
                    "termination_uri": termination_uri,
                },
                sip_trunk_update_params.SipTrunkUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SipTrunk,
        )

    def list(
        self,
        account_id: str,
        *,
        limit: int | Omit = omit,
        offset: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SipTrunkListResponse:
        """
        Paginated list of SIP trunks for the specified account.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/sip-trunks",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "limit": limit,
                        "offset": offset,
                    },
                    sip_trunk_list_params.SipTrunkListParams,
                ),
            ),
            cast_to=SipTrunkListResponse,
        )

    def delete(
        self,
        sip_trunk_id: str,
        *,
        account_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delete a SIP trunk that has no associated phone numbers.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not sip_trunk_id:
            raise ValueError(f"Expected a non-empty value for `sip_trunk_id` but received {sip_trunk_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/v1/accounts/{account_id}/sip-trunks/{sip_trunk_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncSipTrunksResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSipTrunksResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/itellicoAI/server-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncSipTrunksResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSipTrunksResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/itellicoAI/server-sdk-python#with_streaming_response
        """
        return AsyncSipTrunksResourceWithStreamingResponse(self)

    async def create(
        self,
        account_id: str,
        *,
        allowed_ips: Optional[SequenceNotStr[str]] | Omit = omit,
        name: Optional[str] | Omit = omit,
        termination_uri: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SipTrunk:
        """Create a Bring-Your-Own-Carrier (BYOC) SIP trunk for inbound/outbound calls.

        For
        trunks that target FusionPBX, provisioning is performed synchronously.

        Args:
          allowed_ips: IPv4/IPv6 or CIDR ranges

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._post(
            f"/v1/accounts/{account_id}/sip-trunks",
            body=await async_maybe_transform(
                {
                    "allowed_ips": allowed_ips,
                    "name": name,
                    "termination_uri": termination_uri,
                },
                sip_trunk_create_params.SipTrunkCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SipTrunk,
        )

    async def retrieve(
        self,
        sip_trunk_id: str,
        *,
        account_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SipTrunk:
        """
        Fetch a single SIP trunk by ID for the specified account.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not sip_trunk_id:
            raise ValueError(f"Expected a non-empty value for `sip_trunk_id` but received {sip_trunk_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/sip-trunks/{sip_trunk_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SipTrunk,
        )

    async def update(
        self,
        sip_trunk_id: str,
        *,
        account_id: str,
        allowed_ips: Optional[SequenceNotStr[str]] | Omit = omit,
        name: Optional[str] | Omit = omit,
        termination_uri: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SipTrunk:
        """
        Update BYOC SIP trunk properties and allowed IPs.

        Args:
          allowed_ips: IPv4/IPv6 or CIDR ranges

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not sip_trunk_id:
            raise ValueError(f"Expected a non-empty value for `sip_trunk_id` but received {sip_trunk_id!r}")
        return await self._patch(
            f"/v1/accounts/{account_id}/sip-trunks/{sip_trunk_id}",
            body=await async_maybe_transform(
                {
                    "allowed_ips": allowed_ips,
                    "name": name,
                    "termination_uri": termination_uri,
                },
                sip_trunk_update_params.SipTrunkUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SipTrunk,
        )

    async def list(
        self,
        account_id: str,
        *,
        limit: int | Omit = omit,
        offset: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SipTrunkListResponse:
        """
        Paginated list of SIP trunks for the specified account.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/sip-trunks",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "limit": limit,
                        "offset": offset,
                    },
                    sip_trunk_list_params.SipTrunkListParams,
                ),
            ),
            cast_to=SipTrunkListResponse,
        )

    async def delete(
        self,
        sip_trunk_id: str,
        *,
        account_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delete a SIP trunk that has no associated phone numbers.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        if not sip_trunk_id:
            raise ValueError(f"Expected a non-empty value for `sip_trunk_id` but received {sip_trunk_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/v1/accounts/{account_id}/sip-trunks/{sip_trunk_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class SipTrunksResourceWithRawResponse:
    def __init__(self, sip_trunks: SipTrunksResource) -> None:
        self._sip_trunks = sip_trunks

        self.create = to_raw_response_wrapper(
            sip_trunks.create,
        )
        self.retrieve = to_raw_response_wrapper(
            sip_trunks.retrieve,
        )
        self.update = to_raw_response_wrapper(
            sip_trunks.update,
        )
        self.list = to_raw_response_wrapper(
            sip_trunks.list,
        )
        self.delete = to_raw_response_wrapper(
            sip_trunks.delete,
        )


class AsyncSipTrunksResourceWithRawResponse:
    def __init__(self, sip_trunks: AsyncSipTrunksResource) -> None:
        self._sip_trunks = sip_trunks

        self.create = async_to_raw_response_wrapper(
            sip_trunks.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            sip_trunks.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            sip_trunks.update,
        )
        self.list = async_to_raw_response_wrapper(
            sip_trunks.list,
        )
        self.delete = async_to_raw_response_wrapper(
            sip_trunks.delete,
        )


class SipTrunksResourceWithStreamingResponse:
    def __init__(self, sip_trunks: SipTrunksResource) -> None:
        self._sip_trunks = sip_trunks

        self.create = to_streamed_response_wrapper(
            sip_trunks.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            sip_trunks.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            sip_trunks.update,
        )
        self.list = to_streamed_response_wrapper(
            sip_trunks.list,
        )
        self.delete = to_streamed_response_wrapper(
            sip_trunks.delete,
        )


class AsyncSipTrunksResourceWithStreamingResponse:
    def __init__(self, sip_trunks: AsyncSipTrunksResource) -> None:
        self._sip_trunks = sip_trunks

        self.create = async_to_streamed_response_wrapper(
            sip_trunks.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            sip_trunks.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            sip_trunks.update,
        )
        self.list = async_to_streamed_response_wrapper(
            sip_trunks.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            sip_trunks.delete,
        )

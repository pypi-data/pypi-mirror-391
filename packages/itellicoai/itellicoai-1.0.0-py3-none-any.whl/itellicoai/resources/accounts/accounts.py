# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from datetime import datetime

import httpx

from ...types import ConversationType, ConversationStatus, ConversationDirection, account_list_conversations_params
from ..._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from .analytics import (
    AnalyticsResource,
    AsyncAnalyticsResource,
    AnalyticsResourceWithRawResponse,
    AsyncAnalyticsResourceWithRawResponse,
    AnalyticsResourceWithStreamingResponse,
    AsyncAnalyticsResourceWithStreamingResponse,
)
from .providers import (
    ProvidersResource,
    AsyncProvidersResource,
    ProvidersResourceWithRawResponse,
    AsyncProvidersResourceWithRawResponse,
    ProvidersResourceWithStreamingResponse,
    AsyncProvidersResourceWithStreamingResponse,
)
from .sip_trunks import (
    SipTrunksResource,
    AsyncSipTrunksResource,
    SipTrunksResourceWithRawResponse,
    AsyncSipTrunksResourceWithRawResponse,
    SipTrunksResourceWithStreamingResponse,
    AsyncSipTrunksResourceWithStreamingResponse,
)
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .subaccounts import (
    SubaccountsResource,
    AsyncSubaccountsResource,
    SubaccountsResourceWithRawResponse,
    AsyncSubaccountsResourceWithRawResponse,
    SubaccountsResourceWithStreamingResponse,
    AsyncSubaccountsResourceWithStreamingResponse,
)
from .phone_numbers import (
    PhoneNumbersResource,
    AsyncPhoneNumbersResource,
    PhoneNumbersResourceWithRawResponse,
    AsyncPhoneNumbersResourceWithRawResponse,
    PhoneNumbersResourceWithStreamingResponse,
    AsyncPhoneNumbersResourceWithStreamingResponse,
)
from ..._base_client import make_request_options
from ...types.account import Account
from ...types.conversation_type import ConversationType
from ...types.conversation_status import ConversationStatus
from ...types.conversation_direction import ConversationDirection
from ...types.account_list_conversations_response import AccountListConversationsResponse

__all__ = ["AccountsResource", "AsyncAccountsResource"]


class AccountsResource(SyncAPIResource):
    @cached_property
    def subaccounts(self) -> SubaccountsResource:
        return SubaccountsResource(self._client)

    @cached_property
    def providers(self) -> ProvidersResource:
        return ProvidersResource(self._client)

    @cached_property
    def phone_numbers(self) -> PhoneNumbersResource:
        return PhoneNumbersResource(self._client)

    @cached_property
    def sip_trunks(self) -> SipTrunksResource:
        return SipTrunksResource(self._client)

    @cached_property
    def analytics(self) -> AnalyticsResource:
        return AnalyticsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AccountsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/itellicoAI/server-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AccountsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AccountsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/itellicoAI/server-sdk-python#with_streaming_response
        """
        return AccountsResourceWithStreamingResponse(self)

    def list_conversations(
        self,
        account_id: str,
        *,
        agent_id: Optional[str] | Omit = omit,
        conversation_id: Optional[str] | Omit = omit,
        created_after: Union[str, datetime, None] | Omit = omit,
        created_before: Union[str, datetime, None] | Omit = omit,
        direction: Optional[ConversationDirection] | Omit = omit,
        status: Optional[ConversationStatus] | Omit = omit,
        type: Optional[ConversationType] | Omit = omit,
        updated_after: Union[str, datetime, None] | Omit = omit,
        updated_before: Union[str, datetime, None] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AccountListConversationsResponse:
        """
        Paginated list of conversations for the specified account and its subaccounts.

        Args:
          agent_id: Filter by agent UUID.

          conversation_id: Filter by conversation identifier.

          created_after: Return conversations created on/after this timestamp.

          created_before: Return conversations created before this timestamp.

          direction: Directionality of a conversation.

          status: High-level lifecycle statuses reported by the conversations API.

          type: High-level conversation types exposed via the v1 API.

          updated_after: Return conversations updated on/after this timestamp.

          updated_before: Return conversations updated before this timestamp.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/conversations",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "agent_id": agent_id,
                        "conversation_id": conversation_id,
                        "created_after": created_after,
                        "created_before": created_before,
                        "direction": direction,
                        "status": status,
                        "type": type,
                        "updated_after": updated_after,
                        "updated_before": updated_before,
                    },
                    account_list_conversations_params.AccountListConversationsParams,
                ),
            ),
            cast_to=AccountListConversationsResponse,
        )

    def retrieve_current(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Account:
        """Return the authenticated account for the provided API key."""
        return self._get(
            "/v1/accounts/current",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Account,
        )


class AsyncAccountsResource(AsyncAPIResource):
    @cached_property
    def subaccounts(self) -> AsyncSubaccountsResource:
        return AsyncSubaccountsResource(self._client)

    @cached_property
    def providers(self) -> AsyncProvidersResource:
        return AsyncProvidersResource(self._client)

    @cached_property
    def phone_numbers(self) -> AsyncPhoneNumbersResource:
        return AsyncPhoneNumbersResource(self._client)

    @cached_property
    def sip_trunks(self) -> AsyncSipTrunksResource:
        return AsyncSipTrunksResource(self._client)

    @cached_property
    def analytics(self) -> AsyncAnalyticsResource:
        return AsyncAnalyticsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncAccountsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/itellicoAI/server-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAccountsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAccountsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/itellicoAI/server-sdk-python#with_streaming_response
        """
        return AsyncAccountsResourceWithStreamingResponse(self)

    async def list_conversations(
        self,
        account_id: str,
        *,
        agent_id: Optional[str] | Omit = omit,
        conversation_id: Optional[str] | Omit = omit,
        created_after: Union[str, datetime, None] | Omit = omit,
        created_before: Union[str, datetime, None] | Omit = omit,
        direction: Optional[ConversationDirection] | Omit = omit,
        status: Optional[ConversationStatus] | Omit = omit,
        type: Optional[ConversationType] | Omit = omit,
        updated_after: Union[str, datetime, None] | Omit = omit,
        updated_before: Union[str, datetime, None] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AccountListConversationsResponse:
        """
        Paginated list of conversations for the specified account and its subaccounts.

        Args:
          agent_id: Filter by agent UUID.

          conversation_id: Filter by conversation identifier.

          created_after: Return conversations created on/after this timestamp.

          created_before: Return conversations created before this timestamp.

          direction: Directionality of a conversation.

          status: High-level lifecycle statuses reported by the conversations API.

          type: High-level conversation types exposed via the v1 API.

          updated_after: Return conversations updated on/after this timestamp.

          updated_before: Return conversations updated before this timestamp.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/conversations",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "agent_id": agent_id,
                        "conversation_id": conversation_id,
                        "created_after": created_after,
                        "created_before": created_before,
                        "direction": direction,
                        "status": status,
                        "type": type,
                        "updated_after": updated_after,
                        "updated_before": updated_before,
                    },
                    account_list_conversations_params.AccountListConversationsParams,
                ),
            ),
            cast_to=AccountListConversationsResponse,
        )

    async def retrieve_current(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Account:
        """Return the authenticated account for the provided API key."""
        return await self._get(
            "/v1/accounts/current",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Account,
        )


class AccountsResourceWithRawResponse:
    def __init__(self, accounts: AccountsResource) -> None:
        self._accounts = accounts

        self.list_conversations = to_raw_response_wrapper(
            accounts.list_conversations,
        )
        self.retrieve_current = to_raw_response_wrapper(
            accounts.retrieve_current,
        )

    @cached_property
    def subaccounts(self) -> SubaccountsResourceWithRawResponse:
        return SubaccountsResourceWithRawResponse(self._accounts.subaccounts)

    @cached_property
    def providers(self) -> ProvidersResourceWithRawResponse:
        return ProvidersResourceWithRawResponse(self._accounts.providers)

    @cached_property
    def phone_numbers(self) -> PhoneNumbersResourceWithRawResponse:
        return PhoneNumbersResourceWithRawResponse(self._accounts.phone_numbers)

    @cached_property
    def sip_trunks(self) -> SipTrunksResourceWithRawResponse:
        return SipTrunksResourceWithRawResponse(self._accounts.sip_trunks)

    @cached_property
    def analytics(self) -> AnalyticsResourceWithRawResponse:
        return AnalyticsResourceWithRawResponse(self._accounts.analytics)


class AsyncAccountsResourceWithRawResponse:
    def __init__(self, accounts: AsyncAccountsResource) -> None:
        self._accounts = accounts

        self.list_conversations = async_to_raw_response_wrapper(
            accounts.list_conversations,
        )
        self.retrieve_current = async_to_raw_response_wrapper(
            accounts.retrieve_current,
        )

    @cached_property
    def subaccounts(self) -> AsyncSubaccountsResourceWithRawResponse:
        return AsyncSubaccountsResourceWithRawResponse(self._accounts.subaccounts)

    @cached_property
    def providers(self) -> AsyncProvidersResourceWithRawResponse:
        return AsyncProvidersResourceWithRawResponse(self._accounts.providers)

    @cached_property
    def phone_numbers(self) -> AsyncPhoneNumbersResourceWithRawResponse:
        return AsyncPhoneNumbersResourceWithRawResponse(self._accounts.phone_numbers)

    @cached_property
    def sip_trunks(self) -> AsyncSipTrunksResourceWithRawResponse:
        return AsyncSipTrunksResourceWithRawResponse(self._accounts.sip_trunks)

    @cached_property
    def analytics(self) -> AsyncAnalyticsResourceWithRawResponse:
        return AsyncAnalyticsResourceWithRawResponse(self._accounts.analytics)


class AccountsResourceWithStreamingResponse:
    def __init__(self, accounts: AccountsResource) -> None:
        self._accounts = accounts

        self.list_conversations = to_streamed_response_wrapper(
            accounts.list_conversations,
        )
        self.retrieve_current = to_streamed_response_wrapper(
            accounts.retrieve_current,
        )

    @cached_property
    def subaccounts(self) -> SubaccountsResourceWithStreamingResponse:
        return SubaccountsResourceWithStreamingResponse(self._accounts.subaccounts)

    @cached_property
    def providers(self) -> ProvidersResourceWithStreamingResponse:
        return ProvidersResourceWithStreamingResponse(self._accounts.providers)

    @cached_property
    def phone_numbers(self) -> PhoneNumbersResourceWithStreamingResponse:
        return PhoneNumbersResourceWithStreamingResponse(self._accounts.phone_numbers)

    @cached_property
    def sip_trunks(self) -> SipTrunksResourceWithStreamingResponse:
        return SipTrunksResourceWithStreamingResponse(self._accounts.sip_trunks)

    @cached_property
    def analytics(self) -> AnalyticsResourceWithStreamingResponse:
        return AnalyticsResourceWithStreamingResponse(self._accounts.analytics)


class AsyncAccountsResourceWithStreamingResponse:
    def __init__(self, accounts: AsyncAccountsResource) -> None:
        self._accounts = accounts

        self.list_conversations = async_to_streamed_response_wrapper(
            accounts.list_conversations,
        )
        self.retrieve_current = async_to_streamed_response_wrapper(
            accounts.retrieve_current,
        )

    @cached_property
    def subaccounts(self) -> AsyncSubaccountsResourceWithStreamingResponse:
        return AsyncSubaccountsResourceWithStreamingResponse(self._accounts.subaccounts)

    @cached_property
    def providers(self) -> AsyncProvidersResourceWithStreamingResponse:
        return AsyncProvidersResourceWithStreamingResponse(self._accounts.providers)

    @cached_property
    def phone_numbers(self) -> AsyncPhoneNumbersResourceWithStreamingResponse:
        return AsyncPhoneNumbersResourceWithStreamingResponse(self._accounts.phone_numbers)

    @cached_property
    def sip_trunks(self) -> AsyncSipTrunksResourceWithStreamingResponse:
        return AsyncSipTrunksResourceWithStreamingResponse(self._accounts.sip_trunks)

    @cached_property
    def analytics(self) -> AsyncAnalyticsResourceWithStreamingResponse:
        return AsyncAnalyticsResourceWithStreamingResponse(self._accounts.analytics)

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
from ...types.accounts import provider_list_voices_params
from ...types.accounts.provider_list_models_response import ProviderListModelsResponse
from ...types.accounts.provider_list_voices_response import ProviderListVoicesResponse
from ...types.accounts.provider_list_transcribers_response import ProviderListTranscribersResponse

__all__ = ["ProvidersResource", "AsyncProvidersResource"]


class ProvidersResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ProvidersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/itellicoAI/server-sdk-python#accessing-raw-response-data-eg-headers
        """
        return ProvidersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ProvidersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/itellicoAI/server-sdk-python#with_streaming_response
        """
        return ProvidersResourceWithStreamingResponse(self)

    def list_models(
        self,
        account_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProviderListModelsResponse:
        """List available models grouped by provider.

        Each provider entry includes its
        code, name, an EU-hosted flag, and a list of models with id, name, description,
        and supported configuration ranges (temperature, max_tokens).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/providers/models",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProviderListModelsResponse,
        )

    def list_transcribers(
        self,
        account_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProviderListTranscribersResponse:
        """List available transcriber models grouped by provider.

        Each provider entry
        includes its code, name, EU-hosted flag, and models with id, name, description,
        and supported_languages (code/name).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/providers/transcribers",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProviderListTranscribersResponse,
        )

    def list_voices(
        self,
        account_id: str,
        *,
        provider: str,
        gender: Optional[str] | Omit = omit,
        language: Optional[str] | Omit = omit,
        limit: Optional[int] | Omit = omit,
        refresh: bool | Omit = omit,
        search: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProviderListVoicesResponse:
        """
        List actual voice models from a specific provider with optional filters
        (language, gender, search). Returns live data from voice providers like
        ElevenLabs, Azure Speech, and Cartesia.

        Args:
          provider: Voice provider (required): elevenlabs, azure, or cartesia

          gender: Filter by gender: male, female, or neutral

          language: Filter by language code (e.g., 'en-us', 'fr-fr')

          limit: Maximum number of voices to return

          refresh: Clear cache and fetch fresh data from provider

          search: Search in voice name or description

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._get(
            f"/v1/accounts/{account_id}/providers/voices",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "provider": provider,
                        "gender": gender,
                        "language": language,
                        "limit": limit,
                        "refresh": refresh,
                        "search": search,
                    },
                    provider_list_voices_params.ProviderListVoicesParams,
                ),
            ),
            cast_to=ProviderListVoicesResponse,
        )


class AsyncProvidersResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncProvidersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/itellicoAI/server-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncProvidersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncProvidersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/itellicoAI/server-sdk-python#with_streaming_response
        """
        return AsyncProvidersResourceWithStreamingResponse(self)

    async def list_models(
        self,
        account_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProviderListModelsResponse:
        """List available models grouped by provider.

        Each provider entry includes its
        code, name, an EU-hosted flag, and a list of models with id, name, description,
        and supported configuration ranges (temperature, max_tokens).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/providers/models",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProviderListModelsResponse,
        )

    async def list_transcribers(
        self,
        account_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProviderListTranscribersResponse:
        """List available transcriber models grouped by provider.

        Each provider entry
        includes its code, name, EU-hosted flag, and models with id, name, description,
        and supported_languages (code/name).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/providers/transcribers",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProviderListTranscribersResponse,
        )

    async def list_voices(
        self,
        account_id: str,
        *,
        provider: str,
        gender: Optional[str] | Omit = omit,
        language: Optional[str] | Omit = omit,
        limit: Optional[int] | Omit = omit,
        refresh: bool | Omit = omit,
        search: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProviderListVoicesResponse:
        """
        List actual voice models from a specific provider with optional filters
        (language, gender, search). Returns live data from voice providers like
        ElevenLabs, Azure Speech, and Cartesia.

        Args:
          provider: Voice provider (required): elevenlabs, azure, or cartesia

          gender: Filter by gender: male, female, or neutral

          language: Filter by language code (e.g., 'en-us', 'fr-fr')

          limit: Maximum number of voices to return

          refresh: Clear cache and fetch fresh data from provider

          search: Search in voice name or description

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._get(
            f"/v1/accounts/{account_id}/providers/voices",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "provider": provider,
                        "gender": gender,
                        "language": language,
                        "limit": limit,
                        "refresh": refresh,
                        "search": search,
                    },
                    provider_list_voices_params.ProviderListVoicesParams,
                ),
            ),
            cast_to=ProviderListVoicesResponse,
        )


class ProvidersResourceWithRawResponse:
    def __init__(self, providers: ProvidersResource) -> None:
        self._providers = providers

        self.list_models = to_raw_response_wrapper(
            providers.list_models,
        )
        self.list_transcribers = to_raw_response_wrapper(
            providers.list_transcribers,
        )
        self.list_voices = to_raw_response_wrapper(
            providers.list_voices,
        )


class AsyncProvidersResourceWithRawResponse:
    def __init__(self, providers: AsyncProvidersResource) -> None:
        self._providers = providers

        self.list_models = async_to_raw_response_wrapper(
            providers.list_models,
        )
        self.list_transcribers = async_to_raw_response_wrapper(
            providers.list_transcribers,
        )
        self.list_voices = async_to_raw_response_wrapper(
            providers.list_voices,
        )


class ProvidersResourceWithStreamingResponse:
    def __init__(self, providers: ProvidersResource) -> None:
        self._providers = providers

        self.list_models = to_streamed_response_wrapper(
            providers.list_models,
        )
        self.list_transcribers = to_streamed_response_wrapper(
            providers.list_transcribers,
        )
        self.list_voices = to_streamed_response_wrapper(
            providers.list_voices,
        )


class AsyncProvidersResourceWithStreamingResponse:
    def __init__(self, providers: AsyncProvidersResource) -> None:
        self._providers = providers

        self.list_models = async_to_streamed_response_wrapper(
            providers.list_models,
        )
        self.list_transcribers = async_to_streamed_response_wrapper(
            providers.list_transcribers,
        )
        self.list_voices = async_to_streamed_response_wrapper(
            providers.list_voices,
        )

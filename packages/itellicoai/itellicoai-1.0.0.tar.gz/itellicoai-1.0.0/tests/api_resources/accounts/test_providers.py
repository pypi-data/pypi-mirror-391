# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from itellicoai import Itellicoai, AsyncItellicoai
from tests.utils import assert_matches_type
from itellicoai.types.accounts import (
    ProviderListModelsResponse,
    ProviderListVoicesResponse,
    ProviderListTranscribersResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestProviders:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_models(self, client: Itellicoai) -> None:
        provider = client.accounts.providers.list_models(
            "account_id",
        )
        assert_matches_type(ProviderListModelsResponse, provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_models(self, client: Itellicoai) -> None:
        response = client.accounts.providers.with_raw_response.list_models(
            "account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        provider = response.parse()
        assert_matches_type(ProviderListModelsResponse, provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_models(self, client: Itellicoai) -> None:
        with client.accounts.providers.with_streaming_response.list_models(
            "account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            provider = response.parse()
            assert_matches_type(ProviderListModelsResponse, provider, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list_models(self, client: Itellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.providers.with_raw_response.list_models(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_transcribers(self, client: Itellicoai) -> None:
        provider = client.accounts.providers.list_transcribers(
            "account_id",
        )
        assert_matches_type(ProviderListTranscribersResponse, provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_transcribers(self, client: Itellicoai) -> None:
        response = client.accounts.providers.with_raw_response.list_transcribers(
            "account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        provider = response.parse()
        assert_matches_type(ProviderListTranscribersResponse, provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_transcribers(self, client: Itellicoai) -> None:
        with client.accounts.providers.with_streaming_response.list_transcribers(
            "account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            provider = response.parse()
            assert_matches_type(ProviderListTranscribersResponse, provider, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list_transcribers(self, client: Itellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.providers.with_raw_response.list_transcribers(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_voices(self, client: Itellicoai) -> None:
        provider = client.accounts.providers.list_voices(
            account_id="account_id",
            provider="provider",
        )
        assert_matches_type(ProviderListVoicesResponse, provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_voices_with_all_params(self, client: Itellicoai) -> None:
        provider = client.accounts.providers.list_voices(
            account_id="account_id",
            provider="provider",
            gender="gender",
            language="language",
            limit=0,
            refresh=True,
            search="search",
        )
        assert_matches_type(ProviderListVoicesResponse, provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_voices(self, client: Itellicoai) -> None:
        response = client.accounts.providers.with_raw_response.list_voices(
            account_id="account_id",
            provider="provider",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        provider = response.parse()
        assert_matches_type(ProviderListVoicesResponse, provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_voices(self, client: Itellicoai) -> None:
        with client.accounts.providers.with_streaming_response.list_voices(
            account_id="account_id",
            provider="provider",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            provider = response.parse()
            assert_matches_type(ProviderListVoicesResponse, provider, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list_voices(self, client: Itellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.providers.with_raw_response.list_voices(
                account_id="",
                provider="provider",
            )


class TestAsyncProviders:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_models(self, async_client: AsyncItellicoai) -> None:
        provider = await async_client.accounts.providers.list_models(
            "account_id",
        )
        assert_matches_type(ProviderListModelsResponse, provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_models(self, async_client: AsyncItellicoai) -> None:
        response = await async_client.accounts.providers.with_raw_response.list_models(
            "account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        provider = await response.parse()
        assert_matches_type(ProviderListModelsResponse, provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_models(self, async_client: AsyncItellicoai) -> None:
        async with async_client.accounts.providers.with_streaming_response.list_models(
            "account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            provider = await response.parse()
            assert_matches_type(ProviderListModelsResponse, provider, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list_models(self, async_client: AsyncItellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.providers.with_raw_response.list_models(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_transcribers(self, async_client: AsyncItellicoai) -> None:
        provider = await async_client.accounts.providers.list_transcribers(
            "account_id",
        )
        assert_matches_type(ProviderListTranscribersResponse, provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_transcribers(self, async_client: AsyncItellicoai) -> None:
        response = await async_client.accounts.providers.with_raw_response.list_transcribers(
            "account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        provider = await response.parse()
        assert_matches_type(ProviderListTranscribersResponse, provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_transcribers(self, async_client: AsyncItellicoai) -> None:
        async with async_client.accounts.providers.with_streaming_response.list_transcribers(
            "account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            provider = await response.parse()
            assert_matches_type(ProviderListTranscribersResponse, provider, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list_transcribers(self, async_client: AsyncItellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.providers.with_raw_response.list_transcribers(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_voices(self, async_client: AsyncItellicoai) -> None:
        provider = await async_client.accounts.providers.list_voices(
            account_id="account_id",
            provider="provider",
        )
        assert_matches_type(ProviderListVoicesResponse, provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_voices_with_all_params(self, async_client: AsyncItellicoai) -> None:
        provider = await async_client.accounts.providers.list_voices(
            account_id="account_id",
            provider="provider",
            gender="gender",
            language="language",
            limit=0,
            refresh=True,
            search="search",
        )
        assert_matches_type(ProviderListVoicesResponse, provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_voices(self, async_client: AsyncItellicoai) -> None:
        response = await async_client.accounts.providers.with_raw_response.list_voices(
            account_id="account_id",
            provider="provider",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        provider = await response.parse()
        assert_matches_type(ProviderListVoicesResponse, provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_voices(self, async_client: AsyncItellicoai) -> None:
        async with async_client.accounts.providers.with_streaming_response.list_voices(
            account_id="account_id",
            provider="provider",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            provider = await response.parse()
            assert_matches_type(ProviderListVoicesResponse, provider, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list_voices(self, async_client: AsyncItellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.providers.with_raw_response.list_voices(
                account_id="",
                provider="provider",
            )

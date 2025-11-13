# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from itellicoai import Itellicoai, AsyncItellicoai
from tests.utils import assert_matches_type
from itellicoai.types import Account
from itellicoai.types.accounts import (
    SubaccountListResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSubaccounts:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Itellicoai) -> None:
        subaccount = client.accounts.subaccounts.create(
            account_id="account_id",
            name="name",
        )
        assert_matches_type(Account, subaccount, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Itellicoai) -> None:
        response = client.accounts.subaccounts.with_raw_response.create(
            account_id="account_id",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        subaccount = response.parse()
        assert_matches_type(Account, subaccount, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Itellicoai) -> None:
        with client.accounts.subaccounts.with_streaming_response.create(
            account_id="account_id",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            subaccount = response.parse()
            assert_matches_type(Account, subaccount, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: Itellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.subaccounts.with_raw_response.create(
                account_id="",
                name="name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: Itellicoai) -> None:
        subaccount = client.accounts.subaccounts.retrieve(
            subaccount_id="subaccount_id",
            account_id="account_id",
        )
        assert_matches_type(Account, subaccount, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: Itellicoai) -> None:
        response = client.accounts.subaccounts.with_raw_response.retrieve(
            subaccount_id="subaccount_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        subaccount = response.parse()
        assert_matches_type(Account, subaccount, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: Itellicoai) -> None:
        with client.accounts.subaccounts.with_streaming_response.retrieve(
            subaccount_id="subaccount_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            subaccount = response.parse()
            assert_matches_type(Account, subaccount, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: Itellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.subaccounts.with_raw_response.retrieve(
                subaccount_id="subaccount_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `subaccount_id` but received ''"):
            client.accounts.subaccounts.with_raw_response.retrieve(
                subaccount_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: Itellicoai) -> None:
        subaccount = client.accounts.subaccounts.update(
            subaccount_id="subaccount_id",
            account_id="account_id",
        )
        assert_matches_type(Account, subaccount, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: Itellicoai) -> None:
        subaccount = client.accounts.subaccounts.update(
            subaccount_id="subaccount_id",
            account_id="account_id",
            is_active=True,
            name="name",
        )
        assert_matches_type(Account, subaccount, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: Itellicoai) -> None:
        response = client.accounts.subaccounts.with_raw_response.update(
            subaccount_id="subaccount_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        subaccount = response.parse()
        assert_matches_type(Account, subaccount, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: Itellicoai) -> None:
        with client.accounts.subaccounts.with_streaming_response.update(
            subaccount_id="subaccount_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            subaccount = response.parse()
            assert_matches_type(Account, subaccount, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: Itellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.subaccounts.with_raw_response.update(
                subaccount_id="subaccount_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `subaccount_id` but received ''"):
            client.accounts.subaccounts.with_raw_response.update(
                subaccount_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Itellicoai) -> None:
        subaccount = client.accounts.subaccounts.list(
            account_id="account_id",
        )
        assert_matches_type(SubaccountListResponse, subaccount, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Itellicoai) -> None:
        subaccount = client.accounts.subaccounts.list(
            account_id="account_id",
            is_active=True,
            limit=1,
            offset=0,
        )
        assert_matches_type(SubaccountListResponse, subaccount, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Itellicoai) -> None:
        response = client.accounts.subaccounts.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        subaccount = response.parse()
        assert_matches_type(SubaccountListResponse, subaccount, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Itellicoai) -> None:
        with client.accounts.subaccounts.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            subaccount = response.parse()
            assert_matches_type(SubaccountListResponse, subaccount, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: Itellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.subaccounts.with_raw_response.list(
                account_id="",
            )


class TestAsyncSubaccounts:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncItellicoai) -> None:
        subaccount = await async_client.accounts.subaccounts.create(
            account_id="account_id",
            name="name",
        )
        assert_matches_type(Account, subaccount, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncItellicoai) -> None:
        response = await async_client.accounts.subaccounts.with_raw_response.create(
            account_id="account_id",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        subaccount = await response.parse()
        assert_matches_type(Account, subaccount, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncItellicoai) -> None:
        async with async_client.accounts.subaccounts.with_streaming_response.create(
            account_id="account_id",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            subaccount = await response.parse()
            assert_matches_type(Account, subaccount, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncItellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.subaccounts.with_raw_response.create(
                account_id="",
                name="name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncItellicoai) -> None:
        subaccount = await async_client.accounts.subaccounts.retrieve(
            subaccount_id="subaccount_id",
            account_id="account_id",
        )
        assert_matches_type(Account, subaccount, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncItellicoai) -> None:
        response = await async_client.accounts.subaccounts.with_raw_response.retrieve(
            subaccount_id="subaccount_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        subaccount = await response.parse()
        assert_matches_type(Account, subaccount, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncItellicoai) -> None:
        async with async_client.accounts.subaccounts.with_streaming_response.retrieve(
            subaccount_id="subaccount_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            subaccount = await response.parse()
            assert_matches_type(Account, subaccount, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncItellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.subaccounts.with_raw_response.retrieve(
                subaccount_id="subaccount_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `subaccount_id` but received ''"):
            await async_client.accounts.subaccounts.with_raw_response.retrieve(
                subaccount_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncItellicoai) -> None:
        subaccount = await async_client.accounts.subaccounts.update(
            subaccount_id="subaccount_id",
            account_id="account_id",
        )
        assert_matches_type(Account, subaccount, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncItellicoai) -> None:
        subaccount = await async_client.accounts.subaccounts.update(
            subaccount_id="subaccount_id",
            account_id="account_id",
            is_active=True,
            name="name",
        )
        assert_matches_type(Account, subaccount, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncItellicoai) -> None:
        response = await async_client.accounts.subaccounts.with_raw_response.update(
            subaccount_id="subaccount_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        subaccount = await response.parse()
        assert_matches_type(Account, subaccount, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncItellicoai) -> None:
        async with async_client.accounts.subaccounts.with_streaming_response.update(
            subaccount_id="subaccount_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            subaccount = await response.parse()
            assert_matches_type(Account, subaccount, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncItellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.subaccounts.with_raw_response.update(
                subaccount_id="subaccount_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `subaccount_id` but received ''"):
            await async_client.accounts.subaccounts.with_raw_response.update(
                subaccount_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncItellicoai) -> None:
        subaccount = await async_client.accounts.subaccounts.list(
            account_id="account_id",
        )
        assert_matches_type(SubaccountListResponse, subaccount, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncItellicoai) -> None:
        subaccount = await async_client.accounts.subaccounts.list(
            account_id="account_id",
            is_active=True,
            limit=1,
            offset=0,
        )
        assert_matches_type(SubaccountListResponse, subaccount, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncItellicoai) -> None:
        response = await async_client.accounts.subaccounts.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        subaccount = await response.parse()
        assert_matches_type(SubaccountListResponse, subaccount, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncItellicoai) -> None:
        async with async_client.accounts.subaccounts.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            subaccount = await response.parse()
            assert_matches_type(SubaccountListResponse, subaccount, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncItellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.subaccounts.with_raw_response.list(
                account_id="",
            )

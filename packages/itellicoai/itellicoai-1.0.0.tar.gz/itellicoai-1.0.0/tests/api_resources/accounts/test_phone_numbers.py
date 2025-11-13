# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from itellicoai import Itellicoai, AsyncItellicoai
from tests.utils import assert_matches_type
from itellicoai.types.accounts import (
    PhoneNumber,
    PhoneNumberListResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPhoneNumbers:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Itellicoai) -> None:
        phone_number = client.accounts.phone_numbers.create(
            account_id="account_id",
            sip_trunk_id="sip_trunk_id",
        )
        assert_matches_type(PhoneNumber, phone_number, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Itellicoai) -> None:
        phone_number = client.accounts.phone_numbers.create(
            account_id="account_id",
            sip_trunk_id="sip_trunk_id",
            inbound_agent_id="inbound_agent_id",
            name="name",
            number="number",
        )
        assert_matches_type(PhoneNumber, phone_number, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Itellicoai) -> None:
        response = client.accounts.phone_numbers.with_raw_response.create(
            account_id="account_id",
            sip_trunk_id="sip_trunk_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        phone_number = response.parse()
        assert_matches_type(PhoneNumber, phone_number, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Itellicoai) -> None:
        with client.accounts.phone_numbers.with_streaming_response.create(
            account_id="account_id",
            sip_trunk_id="sip_trunk_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            phone_number = response.parse()
            assert_matches_type(PhoneNumber, phone_number, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: Itellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.phone_numbers.with_raw_response.create(
                account_id="",
                sip_trunk_id="sip_trunk_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: Itellicoai) -> None:
        phone_number = client.accounts.phone_numbers.retrieve(
            phone_number_id="phone_number_id",
            account_id="account_id",
        )
        assert_matches_type(PhoneNumber, phone_number, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: Itellicoai) -> None:
        response = client.accounts.phone_numbers.with_raw_response.retrieve(
            phone_number_id="phone_number_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        phone_number = response.parse()
        assert_matches_type(PhoneNumber, phone_number, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: Itellicoai) -> None:
        with client.accounts.phone_numbers.with_streaming_response.retrieve(
            phone_number_id="phone_number_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            phone_number = response.parse()
            assert_matches_type(PhoneNumber, phone_number, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: Itellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.phone_numbers.with_raw_response.retrieve(
                phone_number_id="phone_number_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `phone_number_id` but received ''"):
            client.accounts.phone_numbers.with_raw_response.retrieve(
                phone_number_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: Itellicoai) -> None:
        phone_number = client.accounts.phone_numbers.update(
            phone_number_id="phone_number_id",
            account_id="account_id",
        )
        assert_matches_type(PhoneNumber, phone_number, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: Itellicoai) -> None:
        phone_number = client.accounts.phone_numbers.update(
            phone_number_id="phone_number_id",
            account_id="account_id",
            inbound_agent_id="inbound_agent_id",
            name="name",
            number="number",
            sip_trunk_id="sip_trunk_id",
        )
        assert_matches_type(PhoneNumber, phone_number, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: Itellicoai) -> None:
        response = client.accounts.phone_numbers.with_raw_response.update(
            phone_number_id="phone_number_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        phone_number = response.parse()
        assert_matches_type(PhoneNumber, phone_number, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: Itellicoai) -> None:
        with client.accounts.phone_numbers.with_streaming_response.update(
            phone_number_id="phone_number_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            phone_number = response.parse()
            assert_matches_type(PhoneNumber, phone_number, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: Itellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.phone_numbers.with_raw_response.update(
                phone_number_id="phone_number_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `phone_number_id` but received ''"):
            client.accounts.phone_numbers.with_raw_response.update(
                phone_number_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Itellicoai) -> None:
        phone_number = client.accounts.phone_numbers.list(
            account_id="account_id",
        )
        assert_matches_type(PhoneNumberListResponse, phone_number, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Itellicoai) -> None:
        phone_number = client.accounts.phone_numbers.list(
            account_id="account_id",
            limit=1,
            offset=0,
        )
        assert_matches_type(PhoneNumberListResponse, phone_number, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Itellicoai) -> None:
        response = client.accounts.phone_numbers.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        phone_number = response.parse()
        assert_matches_type(PhoneNumberListResponse, phone_number, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Itellicoai) -> None:
        with client.accounts.phone_numbers.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            phone_number = response.parse()
            assert_matches_type(PhoneNumberListResponse, phone_number, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: Itellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.phone_numbers.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: Itellicoai) -> None:
        phone_number = client.accounts.phone_numbers.delete(
            phone_number_id="phone_number_id",
            account_id="account_id",
        )
        assert phone_number is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Itellicoai) -> None:
        response = client.accounts.phone_numbers.with_raw_response.delete(
            phone_number_id="phone_number_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        phone_number = response.parse()
        assert phone_number is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: Itellicoai) -> None:
        with client.accounts.phone_numbers.with_streaming_response.delete(
            phone_number_id="phone_number_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            phone_number = response.parse()
            assert phone_number is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: Itellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.phone_numbers.with_raw_response.delete(
                phone_number_id="phone_number_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `phone_number_id` but received ''"):
            client.accounts.phone_numbers.with_raw_response.delete(
                phone_number_id="",
                account_id="account_id",
            )


class TestAsyncPhoneNumbers:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncItellicoai) -> None:
        phone_number = await async_client.accounts.phone_numbers.create(
            account_id="account_id",
            sip_trunk_id="sip_trunk_id",
        )
        assert_matches_type(PhoneNumber, phone_number, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncItellicoai) -> None:
        phone_number = await async_client.accounts.phone_numbers.create(
            account_id="account_id",
            sip_trunk_id="sip_trunk_id",
            inbound_agent_id="inbound_agent_id",
            name="name",
            number="number",
        )
        assert_matches_type(PhoneNumber, phone_number, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncItellicoai) -> None:
        response = await async_client.accounts.phone_numbers.with_raw_response.create(
            account_id="account_id",
            sip_trunk_id="sip_trunk_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        phone_number = await response.parse()
        assert_matches_type(PhoneNumber, phone_number, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncItellicoai) -> None:
        async with async_client.accounts.phone_numbers.with_streaming_response.create(
            account_id="account_id",
            sip_trunk_id="sip_trunk_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            phone_number = await response.parse()
            assert_matches_type(PhoneNumber, phone_number, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncItellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.phone_numbers.with_raw_response.create(
                account_id="",
                sip_trunk_id="sip_trunk_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncItellicoai) -> None:
        phone_number = await async_client.accounts.phone_numbers.retrieve(
            phone_number_id="phone_number_id",
            account_id="account_id",
        )
        assert_matches_type(PhoneNumber, phone_number, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncItellicoai) -> None:
        response = await async_client.accounts.phone_numbers.with_raw_response.retrieve(
            phone_number_id="phone_number_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        phone_number = await response.parse()
        assert_matches_type(PhoneNumber, phone_number, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncItellicoai) -> None:
        async with async_client.accounts.phone_numbers.with_streaming_response.retrieve(
            phone_number_id="phone_number_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            phone_number = await response.parse()
            assert_matches_type(PhoneNumber, phone_number, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncItellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.phone_numbers.with_raw_response.retrieve(
                phone_number_id="phone_number_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `phone_number_id` but received ''"):
            await async_client.accounts.phone_numbers.with_raw_response.retrieve(
                phone_number_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncItellicoai) -> None:
        phone_number = await async_client.accounts.phone_numbers.update(
            phone_number_id="phone_number_id",
            account_id="account_id",
        )
        assert_matches_type(PhoneNumber, phone_number, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncItellicoai) -> None:
        phone_number = await async_client.accounts.phone_numbers.update(
            phone_number_id="phone_number_id",
            account_id="account_id",
            inbound_agent_id="inbound_agent_id",
            name="name",
            number="number",
            sip_trunk_id="sip_trunk_id",
        )
        assert_matches_type(PhoneNumber, phone_number, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncItellicoai) -> None:
        response = await async_client.accounts.phone_numbers.with_raw_response.update(
            phone_number_id="phone_number_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        phone_number = await response.parse()
        assert_matches_type(PhoneNumber, phone_number, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncItellicoai) -> None:
        async with async_client.accounts.phone_numbers.with_streaming_response.update(
            phone_number_id="phone_number_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            phone_number = await response.parse()
            assert_matches_type(PhoneNumber, phone_number, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncItellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.phone_numbers.with_raw_response.update(
                phone_number_id="phone_number_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `phone_number_id` but received ''"):
            await async_client.accounts.phone_numbers.with_raw_response.update(
                phone_number_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncItellicoai) -> None:
        phone_number = await async_client.accounts.phone_numbers.list(
            account_id="account_id",
        )
        assert_matches_type(PhoneNumberListResponse, phone_number, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncItellicoai) -> None:
        phone_number = await async_client.accounts.phone_numbers.list(
            account_id="account_id",
            limit=1,
            offset=0,
        )
        assert_matches_type(PhoneNumberListResponse, phone_number, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncItellicoai) -> None:
        response = await async_client.accounts.phone_numbers.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        phone_number = await response.parse()
        assert_matches_type(PhoneNumberListResponse, phone_number, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncItellicoai) -> None:
        async with async_client.accounts.phone_numbers.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            phone_number = await response.parse()
            assert_matches_type(PhoneNumberListResponse, phone_number, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncItellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.phone_numbers.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncItellicoai) -> None:
        phone_number = await async_client.accounts.phone_numbers.delete(
            phone_number_id="phone_number_id",
            account_id="account_id",
        )
        assert phone_number is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncItellicoai) -> None:
        response = await async_client.accounts.phone_numbers.with_raw_response.delete(
            phone_number_id="phone_number_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        phone_number = await response.parse()
        assert phone_number is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncItellicoai) -> None:
        async with async_client.accounts.phone_numbers.with_streaming_response.delete(
            phone_number_id="phone_number_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            phone_number = await response.parse()
            assert phone_number is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncItellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.phone_numbers.with_raw_response.delete(
                phone_number_id="phone_number_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `phone_number_id` but received ''"):
            await async_client.accounts.phone_numbers.with_raw_response.delete(
                phone_number_id="",
                account_id="account_id",
            )

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from itellicoai import Itellicoai, AsyncItellicoai
from tests.utils import assert_matches_type
from itellicoai.types.accounts import (
    SipTrunk,
    SipTrunkListResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSipTrunks:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Itellicoai) -> None:
        sip_trunk = client.accounts.sip_trunks.create(
            account_id="account_id",
        )
        assert_matches_type(SipTrunk, sip_trunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Itellicoai) -> None:
        sip_trunk = client.accounts.sip_trunks.create(
            account_id="account_id",
            allowed_ips=["string"],
            name="name",
            termination_uri="termination_uri",
        )
        assert_matches_type(SipTrunk, sip_trunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Itellicoai) -> None:
        response = client.accounts.sip_trunks.with_raw_response.create(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sip_trunk = response.parse()
        assert_matches_type(SipTrunk, sip_trunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Itellicoai) -> None:
        with client.accounts.sip_trunks.with_streaming_response.create(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sip_trunk = response.parse()
            assert_matches_type(SipTrunk, sip_trunk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: Itellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.sip_trunks.with_raw_response.create(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: Itellicoai) -> None:
        sip_trunk = client.accounts.sip_trunks.retrieve(
            sip_trunk_id="sip_trunk_id",
            account_id="account_id",
        )
        assert_matches_type(SipTrunk, sip_trunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: Itellicoai) -> None:
        response = client.accounts.sip_trunks.with_raw_response.retrieve(
            sip_trunk_id="sip_trunk_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sip_trunk = response.parse()
        assert_matches_type(SipTrunk, sip_trunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: Itellicoai) -> None:
        with client.accounts.sip_trunks.with_streaming_response.retrieve(
            sip_trunk_id="sip_trunk_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sip_trunk = response.parse()
            assert_matches_type(SipTrunk, sip_trunk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: Itellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.sip_trunks.with_raw_response.retrieve(
                sip_trunk_id="sip_trunk_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `sip_trunk_id` but received ''"):
            client.accounts.sip_trunks.with_raw_response.retrieve(
                sip_trunk_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: Itellicoai) -> None:
        sip_trunk = client.accounts.sip_trunks.update(
            sip_trunk_id="sip_trunk_id",
            account_id="account_id",
        )
        assert_matches_type(SipTrunk, sip_trunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: Itellicoai) -> None:
        sip_trunk = client.accounts.sip_trunks.update(
            sip_trunk_id="sip_trunk_id",
            account_id="account_id",
            allowed_ips=["string"],
            name="name",
            termination_uri="termination_uri",
        )
        assert_matches_type(SipTrunk, sip_trunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: Itellicoai) -> None:
        response = client.accounts.sip_trunks.with_raw_response.update(
            sip_trunk_id="sip_trunk_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sip_trunk = response.parse()
        assert_matches_type(SipTrunk, sip_trunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: Itellicoai) -> None:
        with client.accounts.sip_trunks.with_streaming_response.update(
            sip_trunk_id="sip_trunk_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sip_trunk = response.parse()
            assert_matches_type(SipTrunk, sip_trunk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: Itellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.sip_trunks.with_raw_response.update(
                sip_trunk_id="sip_trunk_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `sip_trunk_id` but received ''"):
            client.accounts.sip_trunks.with_raw_response.update(
                sip_trunk_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Itellicoai) -> None:
        sip_trunk = client.accounts.sip_trunks.list(
            account_id="account_id",
        )
        assert_matches_type(SipTrunkListResponse, sip_trunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Itellicoai) -> None:
        sip_trunk = client.accounts.sip_trunks.list(
            account_id="account_id",
            limit=1,
            offset=0,
        )
        assert_matches_type(SipTrunkListResponse, sip_trunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Itellicoai) -> None:
        response = client.accounts.sip_trunks.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sip_trunk = response.parse()
        assert_matches_type(SipTrunkListResponse, sip_trunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Itellicoai) -> None:
        with client.accounts.sip_trunks.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sip_trunk = response.parse()
            assert_matches_type(SipTrunkListResponse, sip_trunk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: Itellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.sip_trunks.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: Itellicoai) -> None:
        sip_trunk = client.accounts.sip_trunks.delete(
            sip_trunk_id="sip_trunk_id",
            account_id="account_id",
        )
        assert sip_trunk is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Itellicoai) -> None:
        response = client.accounts.sip_trunks.with_raw_response.delete(
            sip_trunk_id="sip_trunk_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sip_trunk = response.parse()
        assert sip_trunk is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: Itellicoai) -> None:
        with client.accounts.sip_trunks.with_streaming_response.delete(
            sip_trunk_id="sip_trunk_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sip_trunk = response.parse()
            assert sip_trunk is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: Itellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.sip_trunks.with_raw_response.delete(
                sip_trunk_id="sip_trunk_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `sip_trunk_id` but received ''"):
            client.accounts.sip_trunks.with_raw_response.delete(
                sip_trunk_id="",
                account_id="account_id",
            )


class TestAsyncSipTrunks:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncItellicoai) -> None:
        sip_trunk = await async_client.accounts.sip_trunks.create(
            account_id="account_id",
        )
        assert_matches_type(SipTrunk, sip_trunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncItellicoai) -> None:
        sip_trunk = await async_client.accounts.sip_trunks.create(
            account_id="account_id",
            allowed_ips=["string"],
            name="name",
            termination_uri="termination_uri",
        )
        assert_matches_type(SipTrunk, sip_trunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncItellicoai) -> None:
        response = await async_client.accounts.sip_trunks.with_raw_response.create(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sip_trunk = await response.parse()
        assert_matches_type(SipTrunk, sip_trunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncItellicoai) -> None:
        async with async_client.accounts.sip_trunks.with_streaming_response.create(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sip_trunk = await response.parse()
            assert_matches_type(SipTrunk, sip_trunk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncItellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.sip_trunks.with_raw_response.create(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncItellicoai) -> None:
        sip_trunk = await async_client.accounts.sip_trunks.retrieve(
            sip_trunk_id="sip_trunk_id",
            account_id="account_id",
        )
        assert_matches_type(SipTrunk, sip_trunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncItellicoai) -> None:
        response = await async_client.accounts.sip_trunks.with_raw_response.retrieve(
            sip_trunk_id="sip_trunk_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sip_trunk = await response.parse()
        assert_matches_type(SipTrunk, sip_trunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncItellicoai) -> None:
        async with async_client.accounts.sip_trunks.with_streaming_response.retrieve(
            sip_trunk_id="sip_trunk_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sip_trunk = await response.parse()
            assert_matches_type(SipTrunk, sip_trunk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncItellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.sip_trunks.with_raw_response.retrieve(
                sip_trunk_id="sip_trunk_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `sip_trunk_id` but received ''"):
            await async_client.accounts.sip_trunks.with_raw_response.retrieve(
                sip_trunk_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncItellicoai) -> None:
        sip_trunk = await async_client.accounts.sip_trunks.update(
            sip_trunk_id="sip_trunk_id",
            account_id="account_id",
        )
        assert_matches_type(SipTrunk, sip_trunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncItellicoai) -> None:
        sip_trunk = await async_client.accounts.sip_trunks.update(
            sip_trunk_id="sip_trunk_id",
            account_id="account_id",
            allowed_ips=["string"],
            name="name",
            termination_uri="termination_uri",
        )
        assert_matches_type(SipTrunk, sip_trunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncItellicoai) -> None:
        response = await async_client.accounts.sip_trunks.with_raw_response.update(
            sip_trunk_id="sip_trunk_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sip_trunk = await response.parse()
        assert_matches_type(SipTrunk, sip_trunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncItellicoai) -> None:
        async with async_client.accounts.sip_trunks.with_streaming_response.update(
            sip_trunk_id="sip_trunk_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sip_trunk = await response.parse()
            assert_matches_type(SipTrunk, sip_trunk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncItellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.sip_trunks.with_raw_response.update(
                sip_trunk_id="sip_trunk_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `sip_trunk_id` but received ''"):
            await async_client.accounts.sip_trunks.with_raw_response.update(
                sip_trunk_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncItellicoai) -> None:
        sip_trunk = await async_client.accounts.sip_trunks.list(
            account_id="account_id",
        )
        assert_matches_type(SipTrunkListResponse, sip_trunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncItellicoai) -> None:
        sip_trunk = await async_client.accounts.sip_trunks.list(
            account_id="account_id",
            limit=1,
            offset=0,
        )
        assert_matches_type(SipTrunkListResponse, sip_trunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncItellicoai) -> None:
        response = await async_client.accounts.sip_trunks.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sip_trunk = await response.parse()
        assert_matches_type(SipTrunkListResponse, sip_trunk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncItellicoai) -> None:
        async with async_client.accounts.sip_trunks.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sip_trunk = await response.parse()
            assert_matches_type(SipTrunkListResponse, sip_trunk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncItellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.sip_trunks.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncItellicoai) -> None:
        sip_trunk = await async_client.accounts.sip_trunks.delete(
            sip_trunk_id="sip_trunk_id",
            account_id="account_id",
        )
        assert sip_trunk is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncItellicoai) -> None:
        response = await async_client.accounts.sip_trunks.with_raw_response.delete(
            sip_trunk_id="sip_trunk_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sip_trunk = await response.parse()
        assert sip_trunk is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncItellicoai) -> None:
        async with async_client.accounts.sip_trunks.with_streaming_response.delete(
            sip_trunk_id="sip_trunk_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sip_trunk = await response.parse()
            assert sip_trunk is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncItellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.sip_trunks.with_raw_response.delete(
                sip_trunk_id="sip_trunk_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `sip_trunk_id` but received ''"):
            await async_client.accounts.sip_trunks.with_raw_response.delete(
                sip_trunk_id="",
                account_id="account_id",
            )

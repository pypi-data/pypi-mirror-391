# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from itellicoai import Itellicoai, AsyncItellicoai
from tests.utils import assert_matches_type
from itellicoai._utils import parse_datetime
from itellicoai.types.accounts import AnalyticsGetUsageResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAnalytics:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_usage(self, client: Itellicoai) -> None:
        analytics = client.accounts.analytics.get_usage(
            account_id="account_id",
        )
        assert_matches_type(AnalyticsGetUsageResponse, analytics, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_usage_with_all_params(self, client: Itellicoai) -> None:
        analytics = client.accounts.analytics.get_usage(
            account_id="account_id",
            end=parse_datetime("2019-12-27T18:11:19.117Z"),
            granularity="hour",
            group_by=["agent"],
            limit=1,
            start=parse_datetime("2019-12-27T18:11:19.117Z"),
            tz="tz",
        )
        assert_matches_type(AnalyticsGetUsageResponse, analytics, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_usage(self, client: Itellicoai) -> None:
        response = client.accounts.analytics.with_raw_response.get_usage(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        analytics = response.parse()
        assert_matches_type(AnalyticsGetUsageResponse, analytics, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_usage(self, client: Itellicoai) -> None:
        with client.accounts.analytics.with_streaming_response.get_usage(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            analytics = response.parse()
            assert_matches_type(AnalyticsGetUsageResponse, analytics, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_usage(self, client: Itellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.accounts.analytics.with_raw_response.get_usage(
                account_id="",
            )


class TestAsyncAnalytics:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_usage(self, async_client: AsyncItellicoai) -> None:
        analytics = await async_client.accounts.analytics.get_usage(
            account_id="account_id",
        )
        assert_matches_type(AnalyticsGetUsageResponse, analytics, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_usage_with_all_params(self, async_client: AsyncItellicoai) -> None:
        analytics = await async_client.accounts.analytics.get_usage(
            account_id="account_id",
            end=parse_datetime("2019-12-27T18:11:19.117Z"),
            granularity="hour",
            group_by=["agent"],
            limit=1,
            start=parse_datetime("2019-12-27T18:11:19.117Z"),
            tz="tz",
        )
        assert_matches_type(AnalyticsGetUsageResponse, analytics, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_usage(self, async_client: AsyncItellicoai) -> None:
        response = await async_client.accounts.analytics.with_raw_response.get_usage(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        analytics = await response.parse()
        assert_matches_type(AnalyticsGetUsageResponse, analytics, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_usage(self, async_client: AsyncItellicoai) -> None:
        async with async_client.accounts.analytics.with_streaming_response.get_usage(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            analytics = await response.parse()
            assert_matches_type(AnalyticsGetUsageResponse, analytics, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_usage(self, async_client: AsyncItellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.accounts.analytics.with_raw_response.get_usage(
                account_id="",
            )

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from itellicoai import Itellicoai, AsyncItellicoai
from tests.utils import assert_matches_type
from itellicoai.types import (
    AgentResponse,
    AgentListResponse,
)
from itellicoai._utils import parse_datetime

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAgents:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Itellicoai) -> None:
        agent = client.agents.create(
            account_id="account_id",
            model={
                "model": "gpt-5-mini",
                "provider": "azure_openai",
            },
            transcriber={"provider": "deepgram"},
            voice={
                "voice_id": "pMsXgVXv3BLzUgSXRplE",
                "provider": "elevenlabs",
            },
        )
        assert_matches_type(AgentResponse, agent, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Itellicoai) -> None:
        agent = client.agents.create(
            account_id="account_id",
            model={
                "model": "gpt-5-mini",
                "max_tokens": 1024,
                "provider": "azure_openai",
                "temperature": 0.7,
            },
            transcriber={
                "keywords": ["string"],
                "language": "multi",
                "model": "nova-3:general",
                "provider": "deepgram",
            },
            voice={
                "voice_id": "pMsXgVXv3BLzUgSXRplE",
                "provider": "elevenlabs",
                "settings": {
                    "optimize_streaming_latency": 0,
                    "similarity_boost": 0.7,
                    "speed": 0.7,
                    "stability": 0.7,
                    "style": 0,
                    "use_speaker_boost": True,
                },
            },
            ambient_sound={
                "source": "open_plan_office",
                "volume": 0,
            },
            capture_settings={"recording_enabled": True},
            denoising={
                "telephony": True,
                "web": True,
            },
            inactivity_settings={
                "end_call_timeout_ms": 10000,
                "reminder_max_count": 0,
                "reminder_timeout_ms": 5000,
                "reset_on_activity": True,
            },
            initial_message={
                "delay_ms": 0,
                "interruptible": True,
                "message": "message",
                "mode": "fixed_message",
            },
            interrupt_settings={
                "enabled": True,
                "min_speech_seconds": 0,
                "min_words": 0,
            },
            max_duration_seconds=10,
            metadata={"foo": "bar"},
            name="Customer Support Agent",
            note="note",
            response_timing={"min_endpointing_delay_seconds": 0},
            tags=["string"],
            volume={
                "allow_adjustment": True,
                "telephony": 0,
                "web": 0,
            },
        )
        assert_matches_type(AgentResponse, agent, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Itellicoai) -> None:
        response = client.agents.with_raw_response.create(
            account_id="account_id",
            model={
                "model": "gpt-5-mini",
                "provider": "azure_openai",
            },
            transcriber={"provider": "deepgram"},
            voice={
                "voice_id": "pMsXgVXv3BLzUgSXRplE",
                "provider": "elevenlabs",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        agent = response.parse()
        assert_matches_type(AgentResponse, agent, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Itellicoai) -> None:
        with client.agents.with_streaming_response.create(
            account_id="account_id",
            model={
                "model": "gpt-5-mini",
                "provider": "azure_openai",
            },
            transcriber={"provider": "deepgram"},
            voice={
                "voice_id": "pMsXgVXv3BLzUgSXRplE",
                "provider": "elevenlabs",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            agent = response.parse()
            assert_matches_type(AgentResponse, agent, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: Itellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.agents.with_raw_response.create(
                account_id="",
                model={
                    "model": "gpt-5-mini",
                    "provider": "azure_openai",
                },
                transcriber={"provider": "deepgram"},
                voice={
                    "voice_id": "pMsXgVXv3BLzUgSXRplE",
                    "provider": "elevenlabs",
                },
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: Itellicoai) -> None:
        agent = client.agents.retrieve(
            agent_id="agent_id",
            account_id="account_id",
        )
        assert_matches_type(AgentResponse, agent, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: Itellicoai) -> None:
        response = client.agents.with_raw_response.retrieve(
            agent_id="agent_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        agent = response.parse()
        assert_matches_type(AgentResponse, agent, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: Itellicoai) -> None:
        with client.agents.with_streaming_response.retrieve(
            agent_id="agent_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            agent = response.parse()
            assert_matches_type(AgentResponse, agent, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: Itellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.agents.with_raw_response.retrieve(
                agent_id="agent_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `agent_id` but received ''"):
            client.agents.with_raw_response.retrieve(
                agent_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: Itellicoai) -> None:
        agent = client.agents.update(
            agent_id="agent_id",
            account_id="account_id",
        )
        assert_matches_type(AgentResponse, agent, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: Itellicoai) -> None:
        agent = client.agents.update(
            agent_id="agent_id",
            account_id="account_id",
            ambient_sound={
                "source": "open_plan_office",
                "volume": 0,
            },
            capture_settings={"recording_enabled": True},
            denoising={
                "telephony": True,
                "web": True,
            },
            inactivity_settings={
                "end_call_timeout_ms": 10000,
                "reminder_max_count": 0,
                "reminder_timeout_ms": 5000,
                "reset_on_activity": True,
            },
            initial_message={
                "delay_ms": 0,
                "interruptible": True,
                "message": "message",
                "mode": "fixed_message",
            },
            interrupt_settings={
                "enabled": True,
                "min_speech_seconds": 0,
                "min_words": 0,
            },
            max_duration_seconds=10,
            metadata={"foo": "bar"},
            model={"foo": "bar"},
            name="name",
            note="note",
            response_timing={"min_endpointing_delay_seconds": 0},
            tags=["string"],
            transcriber={
                "language": "af-ZA",
                "provider": "azure",
            },
            voice={"foo": "bar"},
            volume={
                "allow_adjustment": True,
                "telephony": 0,
                "web": 0,
            },
        )
        assert_matches_type(AgentResponse, agent, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: Itellicoai) -> None:
        response = client.agents.with_raw_response.update(
            agent_id="agent_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        agent = response.parse()
        assert_matches_type(AgentResponse, agent, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: Itellicoai) -> None:
        with client.agents.with_streaming_response.update(
            agent_id="agent_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            agent = response.parse()
            assert_matches_type(AgentResponse, agent, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: Itellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.agents.with_raw_response.update(
                agent_id="agent_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `agent_id` but received ''"):
            client.agents.with_raw_response.update(
                agent_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Itellicoai) -> None:
        agent = client.agents.list(
            account_id="account_id",
        )
        assert_matches_type(AgentListResponse, agent, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Itellicoai) -> None:
        agent = client.agents.list(
            account_id="account_id",
            created_ge=parse_datetime("2019-12-27T18:11:19.117Z"),
            created_gt=parse_datetime("2019-12-27T18:11:19.117Z"),
            created_le=parse_datetime("2019-12-27T18:11:19.117Z"),
            created_lt=parse_datetime("2019-12-27T18:11:19.117Z"),
            is_archived=True,
            limit=1,
            modified_ge=parse_datetime("2019-12-27T18:11:19.117Z"),
            modified_gt=parse_datetime("2019-12-27T18:11:19.117Z"),
            modified_le=parse_datetime("2019-12-27T18:11:19.117Z"),
            modified_lt=parse_datetime("2019-12-27T18:11:19.117Z"),
            name="name",
            offset=0,
            tags=["string"],
        )
        assert_matches_type(AgentListResponse, agent, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Itellicoai) -> None:
        response = client.agents.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        agent = response.parse()
        assert_matches_type(AgentListResponse, agent, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Itellicoai) -> None:
        with client.agents.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            agent = response.parse()
            assert_matches_type(AgentListResponse, agent, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: Itellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.agents.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_archive(self, client: Itellicoai) -> None:
        agent = client.agents.archive(
            agent_id="agent_id",
            account_id="account_id",
        )
        assert agent is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_archive(self, client: Itellicoai) -> None:
        response = client.agents.with_raw_response.archive(
            agent_id="agent_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        agent = response.parse()
        assert agent is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_archive(self, client: Itellicoai) -> None:
        with client.agents.with_streaming_response.archive(
            agent_id="agent_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            agent = response.parse()
            assert agent is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_archive(self, client: Itellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            client.agents.with_raw_response.archive(
                agent_id="agent_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `agent_id` but received ''"):
            client.agents.with_raw_response.archive(
                agent_id="",
                account_id="account_id",
            )


class TestAsyncAgents:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncItellicoai) -> None:
        agent = await async_client.agents.create(
            account_id="account_id",
            model={
                "model": "gpt-5-mini",
                "provider": "azure_openai",
            },
            transcriber={"provider": "deepgram"},
            voice={
                "voice_id": "pMsXgVXv3BLzUgSXRplE",
                "provider": "elevenlabs",
            },
        )
        assert_matches_type(AgentResponse, agent, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncItellicoai) -> None:
        agent = await async_client.agents.create(
            account_id="account_id",
            model={
                "model": "gpt-5-mini",
                "max_tokens": 1024,
                "provider": "azure_openai",
                "temperature": 0.7,
            },
            transcriber={
                "keywords": ["string"],
                "language": "multi",
                "model": "nova-3:general",
                "provider": "deepgram",
            },
            voice={
                "voice_id": "pMsXgVXv3BLzUgSXRplE",
                "provider": "elevenlabs",
                "settings": {
                    "optimize_streaming_latency": 0,
                    "similarity_boost": 0.7,
                    "speed": 0.7,
                    "stability": 0.7,
                    "style": 0,
                    "use_speaker_boost": True,
                },
            },
            ambient_sound={
                "source": "open_plan_office",
                "volume": 0,
            },
            capture_settings={"recording_enabled": True},
            denoising={
                "telephony": True,
                "web": True,
            },
            inactivity_settings={
                "end_call_timeout_ms": 10000,
                "reminder_max_count": 0,
                "reminder_timeout_ms": 5000,
                "reset_on_activity": True,
            },
            initial_message={
                "delay_ms": 0,
                "interruptible": True,
                "message": "message",
                "mode": "fixed_message",
            },
            interrupt_settings={
                "enabled": True,
                "min_speech_seconds": 0,
                "min_words": 0,
            },
            max_duration_seconds=10,
            metadata={"foo": "bar"},
            name="Customer Support Agent",
            note="note",
            response_timing={"min_endpointing_delay_seconds": 0},
            tags=["string"],
            volume={
                "allow_adjustment": True,
                "telephony": 0,
                "web": 0,
            },
        )
        assert_matches_type(AgentResponse, agent, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncItellicoai) -> None:
        response = await async_client.agents.with_raw_response.create(
            account_id="account_id",
            model={
                "model": "gpt-5-mini",
                "provider": "azure_openai",
            },
            transcriber={"provider": "deepgram"},
            voice={
                "voice_id": "pMsXgVXv3BLzUgSXRplE",
                "provider": "elevenlabs",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        agent = await response.parse()
        assert_matches_type(AgentResponse, agent, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncItellicoai) -> None:
        async with async_client.agents.with_streaming_response.create(
            account_id="account_id",
            model={
                "model": "gpt-5-mini",
                "provider": "azure_openai",
            },
            transcriber={"provider": "deepgram"},
            voice={
                "voice_id": "pMsXgVXv3BLzUgSXRplE",
                "provider": "elevenlabs",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            agent = await response.parse()
            assert_matches_type(AgentResponse, agent, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncItellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.agents.with_raw_response.create(
                account_id="",
                model={
                    "model": "gpt-5-mini",
                    "provider": "azure_openai",
                },
                transcriber={"provider": "deepgram"},
                voice={
                    "voice_id": "pMsXgVXv3BLzUgSXRplE",
                    "provider": "elevenlabs",
                },
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncItellicoai) -> None:
        agent = await async_client.agents.retrieve(
            agent_id="agent_id",
            account_id="account_id",
        )
        assert_matches_type(AgentResponse, agent, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncItellicoai) -> None:
        response = await async_client.agents.with_raw_response.retrieve(
            agent_id="agent_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        agent = await response.parse()
        assert_matches_type(AgentResponse, agent, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncItellicoai) -> None:
        async with async_client.agents.with_streaming_response.retrieve(
            agent_id="agent_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            agent = await response.parse()
            assert_matches_type(AgentResponse, agent, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncItellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.agents.with_raw_response.retrieve(
                agent_id="agent_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `agent_id` but received ''"):
            await async_client.agents.with_raw_response.retrieve(
                agent_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncItellicoai) -> None:
        agent = await async_client.agents.update(
            agent_id="agent_id",
            account_id="account_id",
        )
        assert_matches_type(AgentResponse, agent, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncItellicoai) -> None:
        agent = await async_client.agents.update(
            agent_id="agent_id",
            account_id="account_id",
            ambient_sound={
                "source": "open_plan_office",
                "volume": 0,
            },
            capture_settings={"recording_enabled": True},
            denoising={
                "telephony": True,
                "web": True,
            },
            inactivity_settings={
                "end_call_timeout_ms": 10000,
                "reminder_max_count": 0,
                "reminder_timeout_ms": 5000,
                "reset_on_activity": True,
            },
            initial_message={
                "delay_ms": 0,
                "interruptible": True,
                "message": "message",
                "mode": "fixed_message",
            },
            interrupt_settings={
                "enabled": True,
                "min_speech_seconds": 0,
                "min_words": 0,
            },
            max_duration_seconds=10,
            metadata={"foo": "bar"},
            model={"foo": "bar"},
            name="name",
            note="note",
            response_timing={"min_endpointing_delay_seconds": 0},
            tags=["string"],
            transcriber={
                "language": "af-ZA",
                "provider": "azure",
            },
            voice={"foo": "bar"},
            volume={
                "allow_adjustment": True,
                "telephony": 0,
                "web": 0,
            },
        )
        assert_matches_type(AgentResponse, agent, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncItellicoai) -> None:
        response = await async_client.agents.with_raw_response.update(
            agent_id="agent_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        agent = await response.parse()
        assert_matches_type(AgentResponse, agent, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncItellicoai) -> None:
        async with async_client.agents.with_streaming_response.update(
            agent_id="agent_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            agent = await response.parse()
            assert_matches_type(AgentResponse, agent, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncItellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.agents.with_raw_response.update(
                agent_id="agent_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `agent_id` but received ''"):
            await async_client.agents.with_raw_response.update(
                agent_id="",
                account_id="account_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncItellicoai) -> None:
        agent = await async_client.agents.list(
            account_id="account_id",
        )
        assert_matches_type(AgentListResponse, agent, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncItellicoai) -> None:
        agent = await async_client.agents.list(
            account_id="account_id",
            created_ge=parse_datetime("2019-12-27T18:11:19.117Z"),
            created_gt=parse_datetime("2019-12-27T18:11:19.117Z"),
            created_le=parse_datetime("2019-12-27T18:11:19.117Z"),
            created_lt=parse_datetime("2019-12-27T18:11:19.117Z"),
            is_archived=True,
            limit=1,
            modified_ge=parse_datetime("2019-12-27T18:11:19.117Z"),
            modified_gt=parse_datetime("2019-12-27T18:11:19.117Z"),
            modified_le=parse_datetime("2019-12-27T18:11:19.117Z"),
            modified_lt=parse_datetime("2019-12-27T18:11:19.117Z"),
            name="name",
            offset=0,
            tags=["string"],
        )
        assert_matches_type(AgentListResponse, agent, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncItellicoai) -> None:
        response = await async_client.agents.with_raw_response.list(
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        agent = await response.parse()
        assert_matches_type(AgentListResponse, agent, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncItellicoai) -> None:
        async with async_client.agents.with_streaming_response.list(
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            agent = await response.parse()
            assert_matches_type(AgentListResponse, agent, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncItellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.agents.with_raw_response.list(
                account_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_archive(self, async_client: AsyncItellicoai) -> None:
        agent = await async_client.agents.archive(
            agent_id="agent_id",
            account_id="account_id",
        )
        assert agent is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_archive(self, async_client: AsyncItellicoai) -> None:
        response = await async_client.agents.with_raw_response.archive(
            agent_id="agent_id",
            account_id="account_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        agent = await response.parse()
        assert agent is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_archive(self, async_client: AsyncItellicoai) -> None:
        async with async_client.agents.with_streaming_response.archive(
            agent_id="agent_id",
            account_id="account_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            agent = await response.parse()
            assert agent is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_archive(self, async_client: AsyncItellicoai) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `account_id` but received ''"):
            await async_client.agents.with_raw_response.archive(
                agent_id="agent_id",
                account_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `agent_id` but received ''"):
            await async_client.agents.with_raw_response.archive(
                agent_id="",
                account_id="account_id",
            )

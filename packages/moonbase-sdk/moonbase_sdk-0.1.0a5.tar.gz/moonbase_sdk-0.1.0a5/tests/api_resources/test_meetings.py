# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from moonbase import Moonbase, AsyncMoonbase
from tests.utils import assert_matches_type
from moonbase.types import Meeting
from moonbase.pagination import SyncCursorPage, AsyncCursorPage

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestMeetings:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_retrieve(self, client: Moonbase) -> None:
        meeting = client.meetings.retrieve(
            id="id",
        )
        assert_matches_type(Meeting, meeting, path=["response"])

    @parametrize
    def test_method_retrieve_with_all_params(self, client: Moonbase) -> None:
        meeting = client.meetings.retrieve(
            id="id",
            include=["organizer"],
        )
        assert_matches_type(Meeting, meeting, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Moonbase) -> None:
        response = client.meetings.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        meeting = response.parse()
        assert_matches_type(Meeting, meeting, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Moonbase) -> None:
        with client.meetings.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            meeting = response.parse()
            assert_matches_type(Meeting, meeting, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Moonbase) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.meetings.with_raw_response.retrieve(
                id="",
            )

    @parametrize
    def test_method_update(self, client: Moonbase) -> None:
        meeting = client.meetings.update(
            id="id",
        )
        assert_matches_type(Meeting, meeting, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: Moonbase) -> None:
        meeting = client.meetings.update(
            id="id",
            recording={
                "content_type": "video/mp4",
                "provider_id": "abc123",
                "url": "https://example.com/recording.mp4",
            },
            transcript={
                "cues": [
                    {
                        "from": 0.71999997,
                        "speaker": "Jony Appleseed",
                        "text": "Hello.",
                        "to": 1.22,
                    },
                    {
                        "from": 1.52,
                        "speaker": "Jane Doe",
                        "text": "Hey! It's been too long.",
                        "to": 3.22,
                    },
                ],
                "provider": "example",
                "provider_id": "def456",
            },
        )
        assert_matches_type(Meeting, meeting, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: Moonbase) -> None:
        response = client.meetings.with_raw_response.update(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        meeting = response.parse()
        assert_matches_type(Meeting, meeting, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: Moonbase) -> None:
        with client.meetings.with_streaming_response.update(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            meeting = response.parse()
            assert_matches_type(Meeting, meeting, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: Moonbase) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.meetings.with_raw_response.update(
                id="",
            )

    @parametrize
    def test_method_list(self, client: Moonbase) -> None:
        meeting = client.meetings.list()
        assert_matches_type(SyncCursorPage[Meeting], meeting, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Moonbase) -> None:
        meeting = client.meetings.list(
            after="after",
            before="before",
            filter={"i_cal_uid": {"eq": "eq"}},
            limit=1,
        )
        assert_matches_type(SyncCursorPage[Meeting], meeting, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Moonbase) -> None:
        response = client.meetings.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        meeting = response.parse()
        assert_matches_type(SyncCursorPage[Meeting], meeting, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Moonbase) -> None:
        with client.meetings.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            meeting = response.parse()
            assert_matches_type(SyncCursorPage[Meeting], meeting, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncMeetings:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncMoonbase) -> None:
        meeting = await async_client.meetings.retrieve(
            id="id",
        )
        assert_matches_type(Meeting, meeting, path=["response"])

    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncMoonbase) -> None:
        meeting = await async_client.meetings.retrieve(
            id="id",
            include=["organizer"],
        )
        assert_matches_type(Meeting, meeting, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncMoonbase) -> None:
        response = await async_client.meetings.with_raw_response.retrieve(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        meeting = await response.parse()
        assert_matches_type(Meeting, meeting, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncMoonbase) -> None:
        async with async_client.meetings.with_streaming_response.retrieve(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            meeting = await response.parse()
            assert_matches_type(Meeting, meeting, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncMoonbase) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.meetings.with_raw_response.retrieve(
                id="",
            )

    @parametrize
    async def test_method_update(self, async_client: AsyncMoonbase) -> None:
        meeting = await async_client.meetings.update(
            id="id",
        )
        assert_matches_type(Meeting, meeting, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncMoonbase) -> None:
        meeting = await async_client.meetings.update(
            id="id",
            recording={
                "content_type": "video/mp4",
                "provider_id": "abc123",
                "url": "https://example.com/recording.mp4",
            },
            transcript={
                "cues": [
                    {
                        "from": 0.71999997,
                        "speaker": "Jony Appleseed",
                        "text": "Hello.",
                        "to": 1.22,
                    },
                    {
                        "from": 1.52,
                        "speaker": "Jane Doe",
                        "text": "Hey! It's been too long.",
                        "to": 3.22,
                    },
                ],
                "provider": "example",
                "provider_id": "def456",
            },
        )
        assert_matches_type(Meeting, meeting, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncMoonbase) -> None:
        response = await async_client.meetings.with_raw_response.update(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        meeting = await response.parse()
        assert_matches_type(Meeting, meeting, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncMoonbase) -> None:
        async with async_client.meetings.with_streaming_response.update(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            meeting = await response.parse()
            assert_matches_type(Meeting, meeting, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncMoonbase) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.meetings.with_raw_response.update(
                id="",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncMoonbase) -> None:
        meeting = await async_client.meetings.list()
        assert_matches_type(AsyncCursorPage[Meeting], meeting, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncMoonbase) -> None:
        meeting = await async_client.meetings.list(
            after="after",
            before="before",
            filter={"i_cal_uid": {"eq": "eq"}},
            limit=1,
        )
        assert_matches_type(AsyncCursorPage[Meeting], meeting, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncMoonbase) -> None:
        response = await async_client.meetings.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        meeting = await response.parse()
        assert_matches_type(AsyncCursorPage[Meeting], meeting, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncMoonbase) -> None:
        async with async_client.meetings.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            meeting = await response.parse()
            assert_matches_type(AsyncCursorPage[Meeting], meeting, path=["response"])

        assert cast(Any, response.is_closed) is True

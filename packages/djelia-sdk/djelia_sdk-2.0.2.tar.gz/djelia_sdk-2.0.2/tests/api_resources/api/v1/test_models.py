# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from djelia_sdk import DjeliaSDK, AsyncDjeliaSDK
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestModels:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_speech(self, client: DjeliaSDK) -> None:
        model = client.api.v1.models.create_speech(
            text="text",
        )
        assert_matches_type(object, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_speech_with_all_params(self, client: DjeliaSDK) -> None:
        model = client.api.v1.models.create_speech(
            text="text",
            speaker=0,
        )
        assert_matches_type(object, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_speech(self, client: DjeliaSDK) -> None:
        response = client.api.v1.models.with_raw_response.create_speech(
            text="text",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = response.parse()
        assert_matches_type(object, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_speech(self, client: DjeliaSDK) -> None:
        with client.api.v1.models.with_streaming_response.create_speech(
            text="text",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = response.parse()
            assert_matches_type(object, model, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncModels:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_speech(self, async_client: AsyncDjeliaSDK) -> None:
        model = await async_client.api.v1.models.create_speech(
            text="text",
        )
        assert_matches_type(object, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_speech_with_all_params(self, async_client: AsyncDjeliaSDK) -> None:
        model = await async_client.api.v1.models.create_speech(
            text="text",
            speaker=0,
        )
        assert_matches_type(object, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_speech(self, async_client: AsyncDjeliaSDK) -> None:
        response = await async_client.api.v1.models.with_raw_response.create_speech(
            text="text",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = await response.parse()
        assert_matches_type(object, model, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_speech(self, async_client: AsyncDjeliaSDK) -> None:
        async with async_client.api.v1.models.with_streaming_response.create_speech(
            text="text",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = await response.parse()
            assert_matches_type(object, model, path=["response"])

        assert cast(Any, response.is_closed) is True

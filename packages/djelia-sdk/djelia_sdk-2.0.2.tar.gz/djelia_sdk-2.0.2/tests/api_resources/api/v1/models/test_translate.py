# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from djelia_sdk import DjeliaSDK, AsyncDjeliaSDK
from tests.utils import assert_matches_type
from djelia_sdk.types.api.v1.models import (
    TranslateCreateTranslationResponse,
    TranslateListSupportedLanguagesResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTranslate:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_translation(self, client: DjeliaSDK) -> None:
        translate = client.api.v1.models.translate.create_translation(
            source="fra_Latn",
            target="fra_Latn",
            text="text",
        )
        assert_matches_type(TranslateCreateTranslationResponse, translate, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_translation(self, client: DjeliaSDK) -> None:
        response = client.api.v1.models.translate.with_raw_response.create_translation(
            source="fra_Latn",
            target="fra_Latn",
            text="text",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        translate = response.parse()
        assert_matches_type(TranslateCreateTranslationResponse, translate, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_translation(self, client: DjeliaSDK) -> None:
        with client.api.v1.models.translate.with_streaming_response.create_translation(
            source="fra_Latn",
            target="fra_Latn",
            text="text",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            translate = response.parse()
            assert_matches_type(TranslateCreateTranslationResponse, translate, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_supported_languages(self, client: DjeliaSDK) -> None:
        translate = client.api.v1.models.translate.list_supported_languages()
        assert_matches_type(TranslateListSupportedLanguagesResponse, translate, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_supported_languages(self, client: DjeliaSDK) -> None:
        response = client.api.v1.models.translate.with_raw_response.list_supported_languages()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        translate = response.parse()
        assert_matches_type(TranslateListSupportedLanguagesResponse, translate, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_supported_languages(self, client: DjeliaSDK) -> None:
        with client.api.v1.models.translate.with_streaming_response.list_supported_languages() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            translate = response.parse()
            assert_matches_type(TranslateListSupportedLanguagesResponse, translate, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncTranslate:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_translation(self, async_client: AsyncDjeliaSDK) -> None:
        translate = await async_client.api.v1.models.translate.create_translation(
            source="fra_Latn",
            target="fra_Latn",
            text="text",
        )
        assert_matches_type(TranslateCreateTranslationResponse, translate, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_translation(self, async_client: AsyncDjeliaSDK) -> None:
        response = await async_client.api.v1.models.translate.with_raw_response.create_translation(
            source="fra_Latn",
            target="fra_Latn",
            text="text",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        translate = await response.parse()
        assert_matches_type(TranslateCreateTranslationResponse, translate, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_translation(self, async_client: AsyncDjeliaSDK) -> None:
        async with async_client.api.v1.models.translate.with_streaming_response.create_translation(
            source="fra_Latn",
            target="fra_Latn",
            text="text",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            translate = await response.parse()
            assert_matches_type(TranslateCreateTranslationResponse, translate, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_supported_languages(self, async_client: AsyncDjeliaSDK) -> None:
        translate = await async_client.api.v1.models.translate.list_supported_languages()
        assert_matches_type(TranslateListSupportedLanguagesResponse, translate, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_supported_languages(self, async_client: AsyncDjeliaSDK) -> None:
        response = await async_client.api.v1.models.translate.with_raw_response.list_supported_languages()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        translate = await response.parse()
        assert_matches_type(TranslateListSupportedLanguagesResponse, translate, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_supported_languages(self, async_client: AsyncDjeliaSDK) -> None:
        async with async_client.api.v1.models.translate.with_streaming_response.list_supported_languages() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            translate = await response.parse()
            assert_matches_type(TranslateListSupportedLanguagesResponse, translate, path=["response"])

        assert cast(Any, response.is_closed) is True

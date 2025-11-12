# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from djelia_sdk import DjeliaSDK, AsyncDjeliaSDK
from tests.utils import assert_matches_type
from djelia_sdk.types.api.v1.models import (
    TranscribeCreateTranscriptionResponse,
    TranscribeStreamTranscriptionResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTranscribe:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_transcription(self, client: DjeliaSDK) -> None:
        transcribe = client.api.v1.models.transcribe.create_transcription(
            file=b"raw file contents",
        )
        assert_matches_type(TranscribeCreateTranscriptionResponse, transcribe, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_transcription_with_all_params(self, client: DjeliaSDK) -> None:
        transcribe = client.api.v1.models.transcribe.create_transcription(
            file=b"raw file contents",
            translate_to_french=True,
        )
        assert_matches_type(TranscribeCreateTranscriptionResponse, transcribe, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_transcription(self, client: DjeliaSDK) -> None:
        response = client.api.v1.models.transcribe.with_raw_response.create_transcription(
            file=b"raw file contents",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        transcribe = response.parse()
        assert_matches_type(TranscribeCreateTranscriptionResponse, transcribe, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_transcription(self, client: DjeliaSDK) -> None:
        with client.api.v1.models.transcribe.with_streaming_response.create_transcription(
            file=b"raw file contents",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            transcribe = response.parse()
            assert_matches_type(TranscribeCreateTranscriptionResponse, transcribe, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_stream_transcription(self, client: DjeliaSDK) -> None:
        transcribe = client.api.v1.models.transcribe.stream_transcription(
            file=b"raw file contents",
        )
        assert_matches_type(TranscribeStreamTranscriptionResponse, transcribe, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_stream_transcription_with_all_params(self, client: DjeliaSDK) -> None:
        transcribe = client.api.v1.models.transcribe.stream_transcription(
            file=b"raw file contents",
            translate_to_french=True,
        )
        assert_matches_type(TranscribeStreamTranscriptionResponse, transcribe, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_stream_transcription(self, client: DjeliaSDK) -> None:
        response = client.api.v1.models.transcribe.with_raw_response.stream_transcription(
            file=b"raw file contents",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        transcribe = response.parse()
        assert_matches_type(TranscribeStreamTranscriptionResponse, transcribe, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_stream_transcription(self, client: DjeliaSDK) -> None:
        with client.api.v1.models.transcribe.with_streaming_response.stream_transcription(
            file=b"raw file contents",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            transcribe = response.parse()
            assert_matches_type(TranscribeStreamTranscriptionResponse, transcribe, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncTranscribe:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_transcription(self, async_client: AsyncDjeliaSDK) -> None:
        transcribe = await async_client.api.v1.models.transcribe.create_transcription(
            file=b"raw file contents",
        )
        assert_matches_type(TranscribeCreateTranscriptionResponse, transcribe, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_transcription_with_all_params(self, async_client: AsyncDjeliaSDK) -> None:
        transcribe = await async_client.api.v1.models.transcribe.create_transcription(
            file=b"raw file contents",
            translate_to_french=True,
        )
        assert_matches_type(TranscribeCreateTranscriptionResponse, transcribe, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_transcription(self, async_client: AsyncDjeliaSDK) -> None:
        response = await async_client.api.v1.models.transcribe.with_raw_response.create_transcription(
            file=b"raw file contents",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        transcribe = await response.parse()
        assert_matches_type(TranscribeCreateTranscriptionResponse, transcribe, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_transcription(self, async_client: AsyncDjeliaSDK) -> None:
        async with async_client.api.v1.models.transcribe.with_streaming_response.create_transcription(
            file=b"raw file contents",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            transcribe = await response.parse()
            assert_matches_type(TranscribeCreateTranscriptionResponse, transcribe, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_stream_transcription(self, async_client: AsyncDjeliaSDK) -> None:
        transcribe = await async_client.api.v1.models.transcribe.stream_transcription(
            file=b"raw file contents",
        )
        assert_matches_type(TranscribeStreamTranscriptionResponse, transcribe, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_stream_transcription_with_all_params(self, async_client: AsyncDjeliaSDK) -> None:
        transcribe = await async_client.api.v1.models.transcribe.stream_transcription(
            file=b"raw file contents",
            translate_to_french=True,
        )
        assert_matches_type(TranscribeStreamTranscriptionResponse, transcribe, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_stream_transcription(self, async_client: AsyncDjeliaSDK) -> None:
        response = await async_client.api.v1.models.transcribe.with_raw_response.stream_transcription(
            file=b"raw file contents",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        transcribe = await response.parse()
        assert_matches_type(TranscribeStreamTranscriptionResponse, transcribe, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_stream_transcription(self, async_client: AsyncDjeliaSDK) -> None:
        async with async_client.api.v1.models.transcribe.with_streaming_response.stream_transcription(
            file=b"raw file contents",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            transcribe = await response.parse()
            assert_matches_type(TranscribeStreamTranscriptionResponse, transcribe, path=["response"])

        assert cast(Any, response.is_closed) is True

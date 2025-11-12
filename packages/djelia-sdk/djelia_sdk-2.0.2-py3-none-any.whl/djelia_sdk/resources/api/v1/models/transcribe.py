# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Any, Mapping, Optional, cast

import httpx

from ....._types import Body, Omit, Query, Headers, NotGiven, FileTypes, omit, not_given
from ....._utils import extract_files, maybe_transform, deepcopy_minimal, async_maybe_transform
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....._base_client import make_request_options
from .....types.api.v1.models import transcribe_create_transcription_params, transcribe_stream_transcription_params
from .....types.api.v1.models.transcribe_create_transcription_response import TranscribeCreateTranscriptionResponse
from .....types.api.v1.models.transcribe_stream_transcription_response import TranscribeStreamTranscriptionResponse

__all__ = ["TranscribeResource", "AsyncTranscribeResource"]


class TranscribeResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> TranscribeResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/sudoping01/djelia-sdk#accessing-raw-response-data-eg-headers
        """
        return TranscribeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TranscribeResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/sudoping01/djelia-sdk#with_streaming_response
        """
        return TranscribeResourceWithStreamingResponse(self)

    def create_transcription(
        self,
        *,
        file: FileTypes,
        translate_to_french: Optional[bool] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TranscribeCreateTranscriptionResponse:
        """
        Perform audio transcription in a synchronous manner, with optional French
        translation.

        **What does this endpoint do?**

        - Transcribes the audio file content into text using Bambara models.
        - Optionally translates the transcribed text into French if
          `translate_to_french` is set to `True`.

        **Behavior Notes:**

        - If `translate_to_french=False` (default):
          - The response contains a list of transcribed segment in Bambara.
        - If `translate_to_french=True`:
          - The response contains the full transcription translated into French.

        **Headers:**

        - `x-api-key`: Your API key for authentication.
        - `Content-Type`: Must be set to `multipart/form-data`.

        **Parameters:**

        - `file` (UploadFile): The audio file to transcribe.
        - `translate_to_french` (bool): Whether to translate the transcription into
          French. Defaults to `False`.

        **Example Request Body:**

        ```text
        file: <binary file>
        translate_to_french: true
        ```

        **Example Response (translate_to_french=False):**

        ```json
        [
          {
            "text": "Aw ni ce i ka kene wa.",
            "start": 0.0,
            "end": 1.0
          }
        ]
        ```

        **Example Response (translate_to_french=True):**

        ```json
        {
          "text": "Bonjour, comment ça va?"
        }
        ```

        **Caution:**

        - Translation introduces additional latency as it processes the full
          transcription for context.

        Returns: FrenchTranscriptionResponse: A dictionary containing the transcribed
        (and optionally translated) text.

        Args:
          file: The uploaded audio file

          translate_to_french: Flag to translate transcriptions into French

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal({"file": file})
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return cast(
            TranscribeCreateTranscriptionResponse,
            self._post(
                "/api/v1/models/transcribe",
                body=maybe_transform(body, transcribe_create_transcription_params.TranscribeCreateTranscriptionParams),
                files=files,
                options=make_request_options(
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout,
                    query=maybe_transform(
                        {"translate_to_french": translate_to_french},
                        transcribe_create_transcription_params.TranscribeCreateTranscriptionParams,
                    ),
                ),
                cast_to=cast(
                    Any, TranscribeCreateTranscriptionResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    def stream_transcription(
        self,
        *,
        file: FileTypes,
        translate_to_french: Optional[bool] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TranscribeStreamTranscriptionResponse:
        """
        Perform streaming transcription of an uploaded audio file, with optional French
        translation.

        **What does this endpoint do?**

        - Transcribes audio content into text in real-time using Bambara models.
        - Optionally translates the transcribed text into French if
          `translate_to_french` is set to `True`.

        **Behavior Notes:**

        - If `translate_to_french=False` (default):
          - Each streamed response represents a **chunk** of the transcribed text.
        - If `translate_to_french=True`:
          - Each streamed response represents the **entire transcription** up to that
            point, translated into French.
          - This is because translation requires full context for accurate results.

        **Headers:**

        - `x-api-key`: Your API key for authentication.

        **Parameters:**

        - `file` (UploadFile): The audio file to transcribe.
        - `translate_to_french` (bool): Whether to translate the transcription into
          French. Defaults to `False`.

        **Example Response (Chunk Mode - translate_to_french=False):**

        ```json
        {"text": "Aw ni ce", "start": 0.0, "end": 0.2}
        {"text": "I ka kene wa?", "start": 0.2, "end": 0.4}
        ```

        **Example Response (Full Text Mode - translate_to_french=True):**

        ```json
        { "text": "Bonjour, comment ça va?" }
        ```

        **Caution:**

        - Translation introduces latency because it requires the full transcription
          context for accuracy. Expect longer delays when `translate_to_french=True`.

        Returns: StreamingResponse: A streaming JSON response containing transcription
        and optional translation.

        Args:
          file: The uploaded audio file

          translate_to_french: Flag to translate transcriptions into French

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal({"file": file})
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return cast(
            TranscribeStreamTranscriptionResponse,
            self._post(
                "/api/v1/models/transcribe/stream",
                body=maybe_transform(body, transcribe_stream_transcription_params.TranscribeStreamTranscriptionParams),
                files=files,
                options=make_request_options(
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout,
                    query=maybe_transform(
                        {"translate_to_french": translate_to_french},
                        transcribe_stream_transcription_params.TranscribeStreamTranscriptionParams,
                    ),
                ),
                cast_to=cast(
                    Any, TranscribeStreamTranscriptionResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )


class AsyncTranscribeResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTranscribeResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/sudoping01/djelia-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncTranscribeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTranscribeResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/sudoping01/djelia-sdk#with_streaming_response
        """
        return AsyncTranscribeResourceWithStreamingResponse(self)

    async def create_transcription(
        self,
        *,
        file: FileTypes,
        translate_to_french: Optional[bool] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TranscribeCreateTranscriptionResponse:
        """
        Perform audio transcription in a synchronous manner, with optional French
        translation.

        **What does this endpoint do?**

        - Transcribes the audio file content into text using Bambara models.
        - Optionally translates the transcribed text into French if
          `translate_to_french` is set to `True`.

        **Behavior Notes:**

        - If `translate_to_french=False` (default):
          - The response contains a list of transcribed segment in Bambara.
        - If `translate_to_french=True`:
          - The response contains the full transcription translated into French.

        **Headers:**

        - `x-api-key`: Your API key for authentication.
        - `Content-Type`: Must be set to `multipart/form-data`.

        **Parameters:**

        - `file` (UploadFile): The audio file to transcribe.
        - `translate_to_french` (bool): Whether to translate the transcription into
          French. Defaults to `False`.

        **Example Request Body:**

        ```text
        file: <binary file>
        translate_to_french: true
        ```

        **Example Response (translate_to_french=False):**

        ```json
        [
          {
            "text": "Aw ni ce i ka kene wa.",
            "start": 0.0,
            "end": 1.0
          }
        ]
        ```

        **Example Response (translate_to_french=True):**

        ```json
        {
          "text": "Bonjour, comment ça va?"
        }
        ```

        **Caution:**

        - Translation introduces additional latency as it processes the full
          transcription for context.

        Returns: FrenchTranscriptionResponse: A dictionary containing the transcribed
        (and optionally translated) text.

        Args:
          file: The uploaded audio file

          translate_to_french: Flag to translate transcriptions into French

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal({"file": file})
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return cast(
            TranscribeCreateTranscriptionResponse,
            await self._post(
                "/api/v1/models/transcribe",
                body=await async_maybe_transform(
                    body, transcribe_create_transcription_params.TranscribeCreateTranscriptionParams
                ),
                files=files,
                options=make_request_options(
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout,
                    query=await async_maybe_transform(
                        {"translate_to_french": translate_to_french},
                        transcribe_create_transcription_params.TranscribeCreateTranscriptionParams,
                    ),
                ),
                cast_to=cast(
                    Any, TranscribeCreateTranscriptionResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    async def stream_transcription(
        self,
        *,
        file: FileTypes,
        translate_to_french: Optional[bool] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TranscribeStreamTranscriptionResponse:
        """
        Perform streaming transcription of an uploaded audio file, with optional French
        translation.

        **What does this endpoint do?**

        - Transcribes audio content into text in real-time using Bambara models.
        - Optionally translates the transcribed text into French if
          `translate_to_french` is set to `True`.

        **Behavior Notes:**

        - If `translate_to_french=False` (default):
          - Each streamed response represents a **chunk** of the transcribed text.
        - If `translate_to_french=True`:
          - Each streamed response represents the **entire transcription** up to that
            point, translated into French.
          - This is because translation requires full context for accurate results.

        **Headers:**

        - `x-api-key`: Your API key for authentication.

        **Parameters:**

        - `file` (UploadFile): The audio file to transcribe.
        - `translate_to_french` (bool): Whether to translate the transcription into
          French. Defaults to `False`.

        **Example Response (Chunk Mode - translate_to_french=False):**

        ```json
        {"text": "Aw ni ce", "start": 0.0, "end": 0.2}
        {"text": "I ka kene wa?", "start": 0.2, "end": 0.4}
        ```

        **Example Response (Full Text Mode - translate_to_french=True):**

        ```json
        { "text": "Bonjour, comment ça va?" }
        ```

        **Caution:**

        - Translation introduces latency because it requires the full transcription
          context for accuracy. Expect longer delays when `translate_to_french=True`.

        Returns: StreamingResponse: A streaming JSON response containing transcription
        and optional translation.

        Args:
          file: The uploaded audio file

          translate_to_french: Flag to translate transcriptions into French

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal({"file": file})
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return cast(
            TranscribeStreamTranscriptionResponse,
            await self._post(
                "/api/v1/models/transcribe/stream",
                body=await async_maybe_transform(
                    body, transcribe_stream_transcription_params.TranscribeStreamTranscriptionParams
                ),
                files=files,
                options=make_request_options(
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout,
                    query=await async_maybe_transform(
                        {"translate_to_french": translate_to_french},
                        transcribe_stream_transcription_params.TranscribeStreamTranscriptionParams,
                    ),
                ),
                cast_to=cast(
                    Any, TranscribeStreamTranscriptionResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )


class TranscribeResourceWithRawResponse:
    def __init__(self, transcribe: TranscribeResource) -> None:
        self._transcribe = transcribe

        self.create_transcription = to_raw_response_wrapper(
            transcribe.create_transcription,
        )
        self.stream_transcription = to_raw_response_wrapper(
            transcribe.stream_transcription,
        )


class AsyncTranscribeResourceWithRawResponse:
    def __init__(self, transcribe: AsyncTranscribeResource) -> None:
        self._transcribe = transcribe

        self.create_transcription = async_to_raw_response_wrapper(
            transcribe.create_transcription,
        )
        self.stream_transcription = async_to_raw_response_wrapper(
            transcribe.stream_transcription,
        )


class TranscribeResourceWithStreamingResponse:
    def __init__(self, transcribe: TranscribeResource) -> None:
        self._transcribe = transcribe

        self.create_transcription = to_streamed_response_wrapper(
            transcribe.create_transcription,
        )
        self.stream_transcription = to_streamed_response_wrapper(
            transcribe.stream_transcription,
        )


class AsyncTranscribeResourceWithStreamingResponse:
    def __init__(self, transcribe: AsyncTranscribeResource) -> None:
        self._transcribe = transcribe

        self.create_transcription = async_to_streamed_response_wrapper(
            transcribe.create_transcription,
        )
        self.stream_transcription = async_to_streamed_response_wrapper(
            transcribe.stream_transcription,
        )

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal

import httpx

from .translate import (
    TranslateResource,
    AsyncTranslateResource,
    TranslateResourceWithRawResponse,
    AsyncTranslateResourceWithRawResponse,
    TranslateResourceWithStreamingResponse,
    AsyncTranslateResourceWithStreamingResponse,
)
from ....._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ....._utils import maybe_transform, async_maybe_transform
from .transcribe import (
    TranscribeResource,
    AsyncTranscribeResource,
    TranscribeResourceWithRawResponse,
    AsyncTranscribeResourceWithRawResponse,
    TranscribeResourceWithStreamingResponse,
    AsyncTranscribeResourceWithStreamingResponse,
)
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....._base_client import make_request_options
from .....types.api.v1 import model_create_speech_params

__all__ = ["ModelsResource", "AsyncModelsResource"]


class ModelsResource(SyncAPIResource):
    @cached_property
    def translate(self) -> TranslateResource:
        return TranslateResource(self._client)

    @cached_property
    def transcribe(self) -> TranscribeResource:
        return TranscribeResource(self._client)

    @cached_property
    def with_raw_response(self) -> ModelsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/sudoping01/djelia-sdk#accessing-raw-response-data-eg-headers
        """
        return ModelsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ModelsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/sudoping01/djelia-sdk#with_streaming_response
        """
        return ModelsResourceWithStreamingResponse(self)

    def create_speech(
        self,
        *,
        text: str,
        speaker: Optional[Literal[0, 1, 2, 3, 4]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Generate speech audio from Bambara text.

        **What does this endpoint do?**

        - Converts text into speech audio using Bambara models.
        - Allows selecting different speaker profiles for synthesized speech.

        **Headers:**

        - `x-api-key`: Your API key for authentication.
        - `Content-Type`: Must be set to `application/json`.

        **Parameters:**

        - `text` (str): The input text to be synthesized into speech.
        - `speaker` (int): The ID of the speaker profile to use for speech synthesis.

        **Example Request Body:**

        ```json
        {
          "text": "Aw ni ce",
          "speaker": 1
        }
        ```

        **Response:**

        - Returns the synthesized audio in WAV format.

        **Example Response Usage:**

        - Save the response content as a `.wav` file to listen to the generated audio.

        **How to use this endpoint?**

        - Provide the text and speaker parameters in the request body.
        - Use the returned WAV file in your applications, or save it for playback.

        **Caution:**

        - The response is a binary stream (audio), so ensure your application can handle
          binary responses.

        Returns: Response: The synthesized audio in WAV format.

        Args:
          text: The bambara text to synthesize

          speaker: The speaker ID to use

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/models/tts",
            body=maybe_transform(
                {
                    "text": text,
                    "speaker": speaker,
                },
                model_create_speech_params.ModelCreateSpeechParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncModelsResource(AsyncAPIResource):
    @cached_property
    def translate(self) -> AsyncTranslateResource:
        return AsyncTranslateResource(self._client)

    @cached_property
    def transcribe(self) -> AsyncTranscribeResource:
        return AsyncTranscribeResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncModelsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/sudoping01/djelia-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncModelsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncModelsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/sudoping01/djelia-sdk#with_streaming_response
        """
        return AsyncModelsResourceWithStreamingResponse(self)

    async def create_speech(
        self,
        *,
        text: str,
        speaker: Optional[Literal[0, 1, 2, 3, 4]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Generate speech audio from Bambara text.

        **What does this endpoint do?**

        - Converts text into speech audio using Bambara models.
        - Allows selecting different speaker profiles for synthesized speech.

        **Headers:**

        - `x-api-key`: Your API key for authentication.
        - `Content-Type`: Must be set to `application/json`.

        **Parameters:**

        - `text` (str): The input text to be synthesized into speech.
        - `speaker` (int): The ID of the speaker profile to use for speech synthesis.

        **Example Request Body:**

        ```json
        {
          "text": "Aw ni ce",
          "speaker": 1
        }
        ```

        **Response:**

        - Returns the synthesized audio in WAV format.

        **Example Response Usage:**

        - Save the response content as a `.wav` file to listen to the generated audio.

        **How to use this endpoint?**

        - Provide the text and speaker parameters in the request body.
        - Use the returned WAV file in your applications, or save it for playback.

        **Caution:**

        - The response is a binary stream (audio), so ensure your application can handle
          binary responses.

        Returns: Response: The synthesized audio in WAV format.

        Args:
          text: The bambara text to synthesize

          speaker: The speaker ID to use

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/models/tts",
            body=await async_maybe_transform(
                {
                    "text": text,
                    "speaker": speaker,
                },
                model_create_speech_params.ModelCreateSpeechParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class ModelsResourceWithRawResponse:
    def __init__(self, models: ModelsResource) -> None:
        self._models = models

        self.create_speech = to_raw_response_wrapper(
            models.create_speech,
        )

    @cached_property
    def translate(self) -> TranslateResourceWithRawResponse:
        return TranslateResourceWithRawResponse(self._models.translate)

    @cached_property
    def transcribe(self) -> TranscribeResourceWithRawResponse:
        return TranscribeResourceWithRawResponse(self._models.transcribe)


class AsyncModelsResourceWithRawResponse:
    def __init__(self, models: AsyncModelsResource) -> None:
        self._models = models

        self.create_speech = async_to_raw_response_wrapper(
            models.create_speech,
        )

    @cached_property
    def translate(self) -> AsyncTranslateResourceWithRawResponse:
        return AsyncTranslateResourceWithRawResponse(self._models.translate)

    @cached_property
    def transcribe(self) -> AsyncTranscribeResourceWithRawResponse:
        return AsyncTranscribeResourceWithRawResponse(self._models.transcribe)


class ModelsResourceWithStreamingResponse:
    def __init__(self, models: ModelsResource) -> None:
        self._models = models

        self.create_speech = to_streamed_response_wrapper(
            models.create_speech,
        )

    @cached_property
    def translate(self) -> TranslateResourceWithStreamingResponse:
        return TranslateResourceWithStreamingResponse(self._models.translate)

    @cached_property
    def transcribe(self) -> TranscribeResourceWithStreamingResponse:
        return TranscribeResourceWithStreamingResponse(self._models.transcribe)


class AsyncModelsResourceWithStreamingResponse:
    def __init__(self, models: AsyncModelsResource) -> None:
        self._models = models

        self.create_speech = async_to_streamed_response_wrapper(
            models.create_speech,
        )

    @cached_property
    def translate(self) -> AsyncTranslateResourceWithStreamingResponse:
        return AsyncTranslateResourceWithStreamingResponse(self._models.translate)

    @cached_property
    def transcribe(self) -> AsyncTranscribeResourceWithStreamingResponse:
        return AsyncTranscribeResourceWithStreamingResponse(self._models.transcribe)

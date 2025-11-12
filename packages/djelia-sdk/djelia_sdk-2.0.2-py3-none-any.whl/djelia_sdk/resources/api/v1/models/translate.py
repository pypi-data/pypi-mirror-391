# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ....._types import Body, Query, Headers, NotGiven, not_given
from ....._utils import maybe_transform, async_maybe_transform
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....._base_client import make_request_options
from .....types.api.v1.models import TranslationLanguage, translate_create_translation_params
from .....types.api.v1.models.translation_language import TranslationLanguage
from .....types.api.v1.models.translate_create_translation_response import TranslateCreateTranslationResponse
from .....types.api.v1.models.translate_list_supported_languages_response import TranslateListSupportedLanguagesResponse

__all__ = ["TranslateResource", "AsyncTranslateResource"]


class TranslateResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> TranslateResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/sudoping01/djelia-sdk#accessing-raw-response-data-eg-headers
        """
        return TranslateResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TranslateResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/sudoping01/djelia-sdk#with_streaming_response
        """
        return TranslateResourceWithStreamingResponse(self)

    def create_translation(
        self,
        *,
        source: TranslationLanguage,
        target: TranslationLanguage,
        text: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TranslateCreateTranslationResponse:
        """
        Translate text between supported languages.

        **What does this endpoint do?**

        - This endpoint translates text from a specified source language to a target
          language.
        - It supports Bambara, French, and English.

        **Request Requirements:**

        - The request body must include:
          - `text` (str): The text to translate.
          - `source` (str): The language code of the source text (e.g., "fra_Latn").
          - `target` (str): The language code of the target language (e.g., "bam_Latn").

        **Headers:**

        - `x-api-key`: Your API key for authentication.
        - `Content-Type`: Must be set to `application/json`.

        **Example Request Body:**

        ```json
        {
          "text": "Bonjour",
          "source": "fra_Latn",
          "target": "bam_Latn"
        }
        ```

        **Example Response:**

        ```json
        {
          "text": "Aw ni ce"
        }
        ```

        **How to use this endpoint?**

        - Use the `/translate/supported-languages` endpoint to get a list of valid
          language codes.
        - Provide the `text`, `source`, and `target` fields in the request body.

        Returns: TranslationResponse: A dictionary containing the translated text.

        Args:
          source: The source language code (eg: eng_Latn)

          target: The target language code (eg: bm_Latn)

          text: The text to translate from source language to target language

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/models/translate",
            body=maybe_transform(
                {
                    "source": source,
                    "target": target,
                    "text": text,
                },
                translate_create_translation_params.TranslateCreateTranslationParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TranslateCreateTranslationResponse,
        )

    def list_supported_languages(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TranslateListSupportedLanguagesResponse:
        """
        Retrieve a list of supported languages for translation.

        **What does this endpoint do?**

        - Returns all languages supported by the Djelia translation API.
        - Each language is represented by:
          - `code`: The language code (e.g., "bam_Latn" for Bambara).
          - `name`: The human-readable name of the language (e.g., "Bambara").

        **How to use this endpoint?**

        - Call this endpoint to get the language codes needed for configuring `source`
          and `target` parameters in translation requests.

        **Example Response**:

        ```json
        [
          { "code": "bam_Latn", "name": "Bambara" },
          { "code": "fra_Latn", "name": "French" },
          { "code": "eng_Latn", "name": "English" }
        ]
        ```

        Returns: List[SupportedLanguageSchema]: A list of supported languages.
        """
        return self._get(
            "/api/v1/models/translate/supported-languages",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TranslateListSupportedLanguagesResponse,
        )


class AsyncTranslateResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTranslateResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/sudoping01/djelia-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncTranslateResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTranslateResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/sudoping01/djelia-sdk#with_streaming_response
        """
        return AsyncTranslateResourceWithStreamingResponse(self)

    async def create_translation(
        self,
        *,
        source: TranslationLanguage,
        target: TranslationLanguage,
        text: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TranslateCreateTranslationResponse:
        """
        Translate text between supported languages.

        **What does this endpoint do?**

        - This endpoint translates text from a specified source language to a target
          language.
        - It supports Bambara, French, and English.

        **Request Requirements:**

        - The request body must include:
          - `text` (str): The text to translate.
          - `source` (str): The language code of the source text (e.g., "fra_Latn").
          - `target` (str): The language code of the target language (e.g., "bam_Latn").

        **Headers:**

        - `x-api-key`: Your API key for authentication.
        - `Content-Type`: Must be set to `application/json`.

        **Example Request Body:**

        ```json
        {
          "text": "Bonjour",
          "source": "fra_Latn",
          "target": "bam_Latn"
        }
        ```

        **Example Response:**

        ```json
        {
          "text": "Aw ni ce"
        }
        ```

        **How to use this endpoint?**

        - Use the `/translate/supported-languages` endpoint to get a list of valid
          language codes.
        - Provide the `text`, `source`, and `target` fields in the request body.

        Returns: TranslationResponse: A dictionary containing the translated text.

        Args:
          source: The source language code (eg: eng_Latn)

          target: The target language code (eg: bm_Latn)

          text: The text to translate from source language to target language

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/models/translate",
            body=await async_maybe_transform(
                {
                    "source": source,
                    "target": target,
                    "text": text,
                },
                translate_create_translation_params.TranslateCreateTranslationParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TranslateCreateTranslationResponse,
        )

    async def list_supported_languages(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TranslateListSupportedLanguagesResponse:
        """
        Retrieve a list of supported languages for translation.

        **What does this endpoint do?**

        - Returns all languages supported by the Djelia translation API.
        - Each language is represented by:
          - `code`: The language code (e.g., "bam_Latn" for Bambara).
          - `name`: The human-readable name of the language (e.g., "Bambara").

        **How to use this endpoint?**

        - Call this endpoint to get the language codes needed for configuring `source`
          and `target` parameters in translation requests.

        **Example Response**:

        ```json
        [
          { "code": "bam_Latn", "name": "Bambara" },
          { "code": "fra_Latn", "name": "French" },
          { "code": "eng_Latn", "name": "English" }
        ]
        ```

        Returns: List[SupportedLanguageSchema]: A list of supported languages.
        """
        return await self._get(
            "/api/v1/models/translate/supported-languages",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TranslateListSupportedLanguagesResponse,
        )


class TranslateResourceWithRawResponse:
    def __init__(self, translate: TranslateResource) -> None:
        self._translate = translate

        self.create_translation = to_raw_response_wrapper(
            translate.create_translation,
        )
        self.list_supported_languages = to_raw_response_wrapper(
            translate.list_supported_languages,
        )


class AsyncTranslateResourceWithRawResponse:
    def __init__(self, translate: AsyncTranslateResource) -> None:
        self._translate = translate

        self.create_translation = async_to_raw_response_wrapper(
            translate.create_translation,
        )
        self.list_supported_languages = async_to_raw_response_wrapper(
            translate.list_supported_languages,
        )


class TranslateResourceWithStreamingResponse:
    def __init__(self, translate: TranslateResource) -> None:
        self._translate = translate

        self.create_translation = to_streamed_response_wrapper(
            translate.create_translation,
        )
        self.list_supported_languages = to_streamed_response_wrapper(
            translate.list_supported_languages,
        )


class AsyncTranslateResourceWithStreamingResponse:
    def __init__(self, translate: AsyncTranslateResource) -> None:
        self._translate = translate

        self.create_translation = async_to_streamed_response_wrapper(
            translate.create_translation,
        )
        self.list_supported_languages = async_to_streamed_response_wrapper(
            translate.list_supported_languages,
        )

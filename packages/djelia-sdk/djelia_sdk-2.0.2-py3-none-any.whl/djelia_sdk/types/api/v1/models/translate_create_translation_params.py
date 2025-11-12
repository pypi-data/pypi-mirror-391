# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .translation_language import TranslationLanguage

__all__ = ["TranslateCreateTranslationParams"]


class TranslateCreateTranslationParams(TypedDict, total=False):
    source: Required[TranslationLanguage]
    """The source language code (eg: eng_Latn)"""

    target: Required[TranslationLanguage]
    """The target language code (eg: bm_Latn)"""

    text: Required[str]
    """The text to translate from source language to target language"""

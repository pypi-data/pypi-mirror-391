# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import TypeAlias

from ....._models import BaseModel

__all__ = ["TranslateListSupportedLanguagesResponse", "TranslateListSupportedLanguagesResponseItem"]


class TranslateListSupportedLanguagesResponseItem(BaseModel):
    code: str
    """The language code."""

    name: str
    """The name of the language."""


TranslateListSupportedLanguagesResponse: TypeAlias = List[TranslateListSupportedLanguagesResponseItem]

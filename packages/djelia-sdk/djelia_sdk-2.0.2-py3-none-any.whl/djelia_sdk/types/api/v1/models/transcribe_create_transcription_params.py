# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

from ....._types import FileTypes

__all__ = ["TranscribeCreateTranscriptionParams"]


class TranscribeCreateTranscriptionParams(TypedDict, total=False):
    file: Required[FileTypes]
    """The uploaded audio file"""

    translate_to_french: Optional[bool]
    """Flag to translate transcriptions into French"""

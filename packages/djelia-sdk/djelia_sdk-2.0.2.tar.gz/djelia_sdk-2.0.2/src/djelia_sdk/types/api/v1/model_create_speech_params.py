# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["ModelCreateSpeechParams"]


class ModelCreateSpeechParams(TypedDict, total=False):
    text: Required[str]
    """The bambara text to synthesize"""

    speaker: Optional[Literal[0, 1, 2, 3, 4]]
    """The speaker ID to use"""

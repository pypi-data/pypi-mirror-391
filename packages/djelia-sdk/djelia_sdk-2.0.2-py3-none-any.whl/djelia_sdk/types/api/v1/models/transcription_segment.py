# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ....._models import BaseModel

__all__ = ["TranscriptionSegment"]


class TranscriptionSegment(BaseModel):
    end: float
    """The end of the segment"""

    start: float
    """The start of the segment"""

    text: str
    """The transcribed text of the segment"""

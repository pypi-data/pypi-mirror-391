# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ....._models import BaseModel

__all__ = ["FrenchTranscriptionResponse"]


class FrenchTranscriptionResponse(BaseModel):
    text: str
    """The transcribed text"""

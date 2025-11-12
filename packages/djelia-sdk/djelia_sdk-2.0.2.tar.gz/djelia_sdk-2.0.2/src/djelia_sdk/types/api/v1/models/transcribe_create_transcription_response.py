# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union
from typing_extensions import TypeAlias

from .transcription_segment import TranscriptionSegment
from .french_transcription_response import FrenchTranscriptionResponse

__all__ = ["TranscribeCreateTranscriptionResponse"]

TranscribeCreateTranscriptionResponse: TypeAlias = Union[FrenchTranscriptionResponse, List[TranscriptionSegment]]

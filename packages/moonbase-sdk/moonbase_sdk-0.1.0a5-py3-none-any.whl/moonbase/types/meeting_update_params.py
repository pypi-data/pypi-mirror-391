# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, TypedDict

__all__ = ["MeetingUpdateParams", "Recording", "Transcript", "TranscriptCue"]


class MeetingUpdateParams(TypedDict, total=False):
    recording: Recording

    transcript: Transcript


class Recording(TypedDict, total=False):
    content_type: Required[str]

    provider_id: Required[str]

    url: Required[str]


_TranscriptCueReservedKeywords = TypedDict(
    "_TranscriptCueReservedKeywords",
    {
        "from": float,
    },
    total=False,
)


class TranscriptCue(_TranscriptCueReservedKeywords, total=False):
    speaker: Required[str]

    text: Required[str]

    to: Required[float]


class Transcript(TypedDict, total=False):
    cues: Required[Iterable[TranscriptCue]]

    provider: Required[str]

    provider_id: Required[str]

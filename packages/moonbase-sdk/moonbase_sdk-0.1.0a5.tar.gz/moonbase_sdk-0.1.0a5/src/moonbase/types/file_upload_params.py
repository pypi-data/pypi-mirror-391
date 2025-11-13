# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, TypedDict

from .._types import FileTypes
from .shared_params.pointer import Pointer

__all__ = ["FileUploadParams"]


class FileUploadParams(TypedDict, total=False):
    file: Required[FileTypes]
    """The File object to be uploaded."""

    associations: Iterable[Pointer]
    """
    Link the File to Moonbase items like a person, organization, deal, task, or an
    item in a custom collection.
    """

    name: str
    """The display name of the file."""

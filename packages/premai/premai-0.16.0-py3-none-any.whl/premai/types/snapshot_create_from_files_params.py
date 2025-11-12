# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .._types import FileTypes

__all__ = ["SnapshotCreateFromFilesParams"]


class SnapshotCreateFromFilesParams(TypedDict, total=False):
    label: Required[str]
    """Snapshot name shown in the dashboard once the snapshot is created."""

    project_id: Required[str]
    """Project ID that will own the generated snapshot.

    Must match an existing project.
    """

    training_file: Required[FileTypes]
    """Required JSONL training file.

    Upload line-delimited messages that will form the training split.
    """

    validation_file: Required[FileTypes]
    """Required JSONL validation file.

    Upload line-delimited messages reserved for validation.
    """

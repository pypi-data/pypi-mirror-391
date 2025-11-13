# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .._types import FileTypes

__all__ = ["DatasetCreateFromJSONLParams"]


class DatasetCreateFromJSONLParams(TypedDict, total=False):
    file: Required[FileTypes]
    """Required JSONL upload.

    Each line should be a JSON object containing a "messages" array
    (system/user/assistant) used to seed the dataset.
    """

    name: Required[str]
    """Human-readable name shown in the dashboard once the dataset is created."""

    project_id: Required[str]
    """Project ID that will own the dataset. Must match a project you created."""

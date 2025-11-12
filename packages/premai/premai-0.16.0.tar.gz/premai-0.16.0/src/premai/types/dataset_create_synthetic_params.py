# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

from .._types import FileTypes, SequenceNotStr

__all__ = ["DatasetCreateSyntheticParams"]


class DatasetCreateSyntheticParams(TypedDict, total=False):
    name: Required[str]

    pairs_to_generate: Required[int]

    project_id: Required[str]

    answer_format: str
    """Answer format template"""

    example_answers: SequenceNotStr[str]
    """Example answers"""

    example_questions: SequenceNotStr[str]
    """Example questions"""

    files: SequenceNotStr[FileTypes]
    """Optional: PDF, DOCX, etc."""

    question_format: str
    """Question format template"""

    rules: SequenceNotStr[str]
    """Array of rules and constraints"""

    temperature: Optional[float]
    """0.0-1.0, controls randomness"""

    website_urls: SequenceNotStr[str]
    """Array of website URLs"""

    youtube_urls: SequenceNotStr[str]
    """Array of YouTube URLs"""

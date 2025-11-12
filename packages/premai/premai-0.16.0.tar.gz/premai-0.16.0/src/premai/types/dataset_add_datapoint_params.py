# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, TypedDict

__all__ = ["DatasetAddDatapointParams", "Message"]


class DatasetAddDatapointParams(TypedDict, total=False):
    messages: Required[Iterable[Message]]

    bucket: Literal["uncategorized", "training", "validation"]


class Message(TypedDict, total=False):
    content: Required[str]

    role: Required[Literal["user", "assistant", "system"]]

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import Required, TypedDict

__all__ = ["FinetuningCreateParams", "Experiment"]


class FinetuningCreateParams(TypedDict, total=False):
    experiments: Required[Iterable[Experiment]]

    name: Required[str]

    snapshot_id: Required[str]


class Experiment(TypedDict, total=False):
    base_model_id: Required[str]

    batch_size: Required[int]

    learning_rate_multiplier: Required[float]

    n_epochs: Required[int]

    lora: Optional[bool]

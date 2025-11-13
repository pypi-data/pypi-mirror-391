# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["FinetuningGetResponse", "Experiment"]


class Experiment(BaseModel):
    id: str

    base_model_id: str

    batch_size: int

    experiment_number: int

    learning_rate_multiplier: float

    lora: bool

    n_epochs: int

    status: Literal["pending", "queued", "running", "deploying", "succeeded", "failed", "deleted"]

    api_model_id: Optional[str] = FieldInfo(alias="model_id", default=None)


class FinetuningGetResponse(BaseModel):
    id: str

    experiments: List[Experiment]

    name: str

    snapshot_id: str

    status: Literal["processing", "completed", "failed"]

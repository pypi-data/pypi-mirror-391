# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = [
    "RecommendationGetResponse",
    "RecommendedExperiment",
    "RecommendedModel",
    "RecommendedModelFullHyperparameters",
    "RecommendedModelLoraHyperparameters",
]


class RecommendedExperiment(BaseModel):
    base_model_id: str

    batch_size: int

    learning_rate_multiplier: float

    lora: bool

    n_epochs: int

    reason_for_recommendation: Optional[str] = None

    recommended: bool


class RecommendedModelFullHyperparameters(BaseModel):
    batch_size: int

    learning_rate_multiplier: float

    n_epochs: int


class RecommendedModelLoraHyperparameters(BaseModel):
    batch_size: int

    learning_rate_multiplier: float

    n_epochs: int


class RecommendedModel(BaseModel):
    base_model_id: str

    full_hyperparameters: Optional[RecommendedModelFullHyperparameters] = None

    lora_hyperparameters: Optional[RecommendedModelLoraHyperparameters] = None

    reason_for_recommendation: Optional[str] = None

    recommended: bool


class RecommendationGetResponse(BaseModel):
    recommended_experiments: Optional[List[RecommendedExperiment]] = None

    recommended_models: Optional[List[RecommendedModel]] = None

    snapshot_id: str

    status: Literal["processing", "completed", "failed"]

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = [
    "RecommendationGetResponse",
    "RecommendedModel",
    "RecommendedModelFullHyperparameters",
    "RecommendedModelLoraHyperparameters",
]


class RecommendedModelFullHyperparameters(BaseModel):
    batch_size: int = FieldInfo(alias="batchSize")

    learning_rate_multiplier: float = FieldInfo(alias="learningRateMultiplier")

    n_epochs: int = FieldInfo(alias="nEpochs")


class RecommendedModelLoraHyperparameters(BaseModel):
    batch_size: int = FieldInfo(alias="batchSize")

    learning_rate_multiplier: float = FieldInfo(alias="learningRateMultiplier")

    n_epochs: int = FieldInfo(alias="nEpochs")


class RecommendedModel(BaseModel):
    base_model_id: str = FieldInfo(alias="baseModelId")

    full_hyperparameters: RecommendedModelFullHyperparameters

    lora_hyperparameters: RecommendedModelLoraHyperparameters

    reason_for_recommendation: Optional[str] = FieldInfo(alias="reasonForRecommendation", default=None)

    recommended: bool


class RecommendationGetResponse(BaseModel):
    recommended_models: Optional[List[RecommendedModel]] = None

    snapshot_id: str

    status: Literal["processing", "completed", "failed"]

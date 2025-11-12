# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = [
    "ProjectGetTreeResponse",
    "Project",
    "ProjectChild",
    "ProjectChildMetadata",
    "ProjectChildChild",
    "ProjectChildChildMetadata",
    "ProjectChildChildChild",
    "ProjectChildChildChildMetadata",
    "ProjectChildChildChildChild",
    "ProjectChildChildChildChildMetadata",
]


class ProjectChildMetadata(BaseModel):
    id: str

    datapoints_count: float


class ProjectChildChildMetadata(BaseModel):
    id: str

    created_at: str

    training_count: float

    validation_count: float


class ProjectChildChildChildMetadata(BaseModel):
    id: str

    reasoning: bool


class ProjectChildChildChildChildMetadata(BaseModel):
    id: str

    base_model_id: str

    experiment_number: float

    api_model_id: Optional[str] = FieldInfo(alias="model_id", default=None)


class ProjectChildChildChildChild(BaseModel):
    id: str

    label: str

    metadata: ProjectChildChildChildChildMetadata

    status: Literal["pending", "queued", "running", "deploying", "succeeded", "failed", "deleted"]

    type: Literal["experiment"]


class ProjectChildChildChild(BaseModel):
    id: str

    label: str

    metadata: ProjectChildChildChildMetadata

    status: Literal["processing", "completed", "failed"]

    type: Literal["finetuning-job"]

    children: Optional[List[ProjectChildChildChildChild]] = None


class ProjectChildChild(BaseModel):
    id: str

    label: str

    metadata: ProjectChildChildMetadata

    type: Literal["snapshot"]

    children: Optional[List[ProjectChildChildChild]] = None


class ProjectChild(BaseModel):
    id: str

    label: str

    metadata: ProjectChildMetadata

    status: Literal["processing", "completed", "failed"]

    type: Literal["dataset"]

    children: Optional[List[ProjectChildChild]] = None


class Project(BaseModel):
    id: str

    name: str

    type: Literal["project"]

    children: Optional[List[ProjectChild]] = None


class ProjectGetTreeResponse(BaseModel):
    project: Project

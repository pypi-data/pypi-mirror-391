# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["DatasetGetResponse"]


class DatasetGetResponse(BaseModel):
    id: str

    created_at: str

    datapoints_count: int

    name: str

    project_id: Optional[str] = None

    status: Literal["processing", "completed", "failed"]

    updated_at: str

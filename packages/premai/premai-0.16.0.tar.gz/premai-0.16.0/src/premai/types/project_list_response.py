# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .._models import BaseModel

__all__ = ["ProjectListResponse", "Project"]


class Project(BaseModel):
    id: str

    created_at: str

    name: str


class ProjectListResponse(BaseModel):
    projects: List[Project]

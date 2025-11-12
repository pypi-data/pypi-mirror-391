# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .._models import BaseModel

__all__ = ["RepoListResponse"]


class RepoListResponse(BaseModel):
    repos: List[str]
    """List of repository names"""

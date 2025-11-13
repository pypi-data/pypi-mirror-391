# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["RepoResponse"]


class RepoResponse(BaseModel):
    base_model: str
    """Base model identifier"""

    repo_name: str
    """Repository name"""

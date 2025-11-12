# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .._models import BaseModel

__all__ = ["TargetListResponse"]


class TargetListResponse(BaseModel):
    targets: List[str]
    """List of target names"""

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["BakeRunResponse"]


class BakeRunResponse(BaseModel):
    message: str
    """Job execution message"""

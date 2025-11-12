# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["Message"]


class Message(BaseModel):
    content: str
    """Content of the message"""

    role: str
    """Role of the message sender"""

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["MessageParam"]


class MessageParam(TypedDict, total=False):
    content: Required[str]
    """Content of the message"""

    role: Required[str]
    """Role of the message sender"""

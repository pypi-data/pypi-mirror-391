# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, TypedDict

from .message_param import MessageParam

__all__ = ["PromptSetParams"]


class PromptSetParams(TypedDict, total=False):
    repo_name: Required[str]

    messages: Required[Iterable[MessageParam]]
    """List of messages in the prompt"""

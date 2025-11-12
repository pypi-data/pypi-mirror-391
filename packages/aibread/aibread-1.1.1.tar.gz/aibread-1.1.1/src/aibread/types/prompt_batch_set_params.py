# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Required, TypedDict

from .message_param import MessageParam

__all__ = ["PromptBatchSetParams"]


class PromptBatchSetParams(TypedDict, total=False):
    prompts: Required[Dict[str, Iterable[MessageParam]]]
    """Dictionary mapping prompt_name to messages list"""

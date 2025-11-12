# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .message import Message
from .._models import BaseModel

__all__ = ["PromptResponse"]


class PromptResponse(BaseModel):
    messages: List[Message]
    """List of messages in the prompt"""

    prompt_name: str
    """Prompt identifier"""

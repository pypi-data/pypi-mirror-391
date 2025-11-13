# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

from .._types import SequenceNotStr

__all__ = ["GeneratorParam"]


class GeneratorParam(TypedDict, total=False):
    type: Required[str]
    """Generator type: oneshot_qs, hardcoded, persona, from_dataset, custom"""

    dataset: Optional[str]
    """Dataset name for from_dataset"""

    model: Optional[str]
    """Model name for oneshot_qs"""

    numq: Optional[int]
    """Number of questions to generate"""

    questions: Optional[SequenceNotStr[str]]
    """Hardcoded questions"""

    seed: Optional[int]
    """Random seed"""

    temperature: Optional[float]
    """Generation temperature (0.0-2.0)"""

    template_path: Optional[str]
    """Custom template path"""

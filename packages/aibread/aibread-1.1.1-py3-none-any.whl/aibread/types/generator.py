# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["Generator"]


class Generator(BaseModel):
    type: str
    """Generator type: oneshot_qs, hardcoded, persona, from_dataset, custom"""

    dataset: Optional[str] = None
    """Dataset name for from_dataset"""

    model: Optional[str] = None
    """Model name for oneshot_qs"""

    numq: Optional[int] = None
    """Number of questions to generate"""

    questions: Optional[List[str]] = None
    """Hardcoded questions"""

    seed: Optional[int] = None
    """Random seed"""

    temperature: Optional[float] = None
    """Generation temperature (0.0-2.0)"""

    template_path: Optional[str] = None
    """Custom template path"""

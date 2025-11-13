# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

__all__ = ["RepoSetParams"]


class RepoSetParams(TypedDict, total=False):
    repo_name: Required[str]
    """Name of the repository"""

    base_model: Optional[str]
    """Base model for the repository (optional)"""

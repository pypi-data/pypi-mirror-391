# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["StimGetOutputParams"]


class StimGetOutputParams(TypedDict, total=False):
    repo_name: Required[str]

    limit: int
    """Number of lines to return (max 1000)"""

    offset: int
    """Starting line number (0-indexed)"""

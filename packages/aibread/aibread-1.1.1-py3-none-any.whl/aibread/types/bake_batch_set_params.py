# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import Required, TypedDict

from .bake_config_base_param import BakeConfigBaseParam

__all__ = ["BakeBatchSetParams", "Bake"]


class BakeBatchSetParams(TypedDict, total=False):
    bakes: Required[Iterable[Bake]]
    """List of bakes to create/update"""


class Bake(TypedDict, total=False):
    bake_name: Required[str]
    """Bake name"""

    template: Required[str]
    """Template: 'default' or existing bake name"""

    overrides: Optional[BakeConfigBaseParam]
    """Base bake configuration fields (for responses - all optional)"""

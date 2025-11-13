# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

from .bake_config_base_param import BakeConfigBaseParam

__all__ = ["BakeSetParams"]


class BakeSetParams(TypedDict, total=False):
    repo_name: Required[str]

    template: Required[str]
    """Template: 'default' or existing bake name"""

    overrides: Optional[BakeConfigBaseParam]
    """Base bake configuration fields (for responses - all optional)"""

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import Required, TypedDict

from .target_config_base_param import TargetConfigBaseParam

__all__ = ["TargetBatchSetParams", "Target"]


class TargetBatchSetParams(TypedDict, total=False):
    targets: Required[Iterable[Target]]
    """List of targets to create/update"""


class Target(TypedDict, total=False):
    target_name: Required[str]
    """Target name"""

    template: Required[str]
    """Template: 'default' or existing target name"""

    overrides: Optional[TargetConfigBaseParam]
    """Target configuration base model"""

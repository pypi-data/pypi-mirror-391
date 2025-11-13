# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

from .target_config_base_param import TargetConfigBaseParam

__all__ = ["TargetSetParams"]


class TargetSetParams(TypedDict, total=False):
    repo_name: Required[str]

    template: Required[str]
    """Template: 'default' or existing target name"""

    overrides: Optional[TargetConfigBaseParam]
    """Target configuration base model"""

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .generator import Generator

__all__ = ["TargetConfigBase"]


class TargetConfigBase(BaseModel):
    extra_kwargs: Optional[Dict[str, object]] = None
    """Additional kwargs passed to chat.completions.create()"""

    generators: Optional[List[Generator]] = None
    """Data generation strategies"""

    max_concurrency: Optional[int] = None
    """Maximum concurrent requests"""

    max_tokens: Optional[int] = None
    """Maximum tokens to generate"""

    api_model_name: Optional[str] = FieldInfo(alias="model_name", default=None)
    """Base model for rollout"""

    num_traj_per_stimulus: Optional[int] = None
    """Number of trajectories per stimulus"""

    temperature: Optional[float] = None
    """Generation temperature (0.0-2.0)"""

    u: Optional[str] = None
    """Unconditioned stimulus prompt name"""

    v: Optional[str] = None
    """Conditioned stimulus prompt name"""

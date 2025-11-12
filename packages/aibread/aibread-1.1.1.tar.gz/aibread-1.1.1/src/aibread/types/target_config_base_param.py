# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable, Optional
from typing_extensions import TypedDict

from .generator_param import GeneratorParam

__all__ = ["TargetConfigBaseParam"]


class TargetConfigBaseParam(TypedDict, total=False):
    extra_kwargs: Optional[Dict[str, object]]
    """Additional kwargs passed to chat.completions.create()"""

    generators: Optional[Iterable[GeneratorParam]]
    """Data generation strategies"""

    max_concurrency: Optional[int]
    """Maximum concurrent requests"""

    max_tokens: Optional[int]
    """Maximum tokens to generate"""

    model_name: Optional[str]
    """Base model for rollout"""

    num_traj_per_stimulus: Optional[int]
    """Number of trajectories per stimulus"""

    temperature: Optional[float]
    """Generation temperature (0.0-2.0)"""

    u: Optional[str]
    """Unconditioned stimulus prompt name"""

    v: Optional[str]
    """Conditioned stimulus prompt name"""

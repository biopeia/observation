"""Conditions the closed studies state for their subjects.

These studies run on a controlled subject: no host discovery (a real host is
not reproducible), the built-in semantic senses instead, and neither sensory
plasticity nor predictor promotion. They are study conditions declared by the
Lab, not an organism profile.
"""

from __future__ import annotations

from typing import Any

CLOSED_STUDY_CONDITIONS: dict[str, Any] = {
    "discover_senses": False,
    "bootstrap_semantic_senses": True,
    "sensory_plasticity": False,
    "auto_promote_predictors": False,
}
# Subjects with a private model also share one symbol policy seed.
CLOSED_MODELED_STUDY_CONDITIONS: dict[str, Any] = {
    **CLOSED_STUDY_CONDITIONS,
    "symbol_policy_seed": 0,
}

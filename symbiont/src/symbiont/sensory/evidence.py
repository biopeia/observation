"""Experiential evidence count typing for Sensory and Epistemic Estimators (T_e).

Subordinate to docs/design/core/temporal-scales-and-clock-separation-v1.md.
Represents discrete counts of empirical observations, transductions, and prediction events.
"""

from __future__ import annotations


class EvidenceCount(int):
    """Discrete count of empirical observations or evidence events (T_e)."""

    def __new__(cls, value: int = 0) -> EvidenceCount:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError("EvidenceCount requires an integer observation count")
        if value < 0:
            raise ValueError(f"EvidenceCount cannot be negative: {value}")
        return super().__new__(cls, value)

    def __repr__(self) -> str:
        return f"EvidenceCount({int(self)})"


SampleCount = EvidenceCount

__all__ = ["EvidenceCount", "SampleCount"]

"""Discrete cycle step typing for Organism Orchestration (T_s).

Subordinate to docs/design/core/temporal-scales-and-clock-separation-v1.md.
Represents discrete scheduler iterations of the organism control loop.
"""

from __future__ import annotations


class CycleStep(int):
    """Discrete integer iteration of the organism control cycle (T_s)."""

    def __new__(cls, value: int = 0) -> CycleStep:
        if not (type(value) is int or isinstance(value, cls)):
            raise TypeError("CycleStep requires a plain integer cycle count")
        if value < 0:
            raise ValueError(f"CycleStep cannot be negative: {value}")
        return super().__new__(cls, value)

    def __repr__(self) -> str:
        return f"CycleStep({int(self)})"


__all__ = ["CycleStep"]

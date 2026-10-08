"""Discrete cycle step typing for Organism Orchestration (T_s).

Subordinate to docs/design/core/temporal-scales-and-clock-separation-v1.md.
Represents discrete scheduler iterations of the organism control loop.
"""

from __future__ import annotations


class CycleStep(int):
    """Discrete integer iteration of the organism control cycle (T_s)."""

    def __new__(cls, value: int | float | str = 0) -> CycleStep:
        val = int(value)
        if val < 0:
            raise ValueError(f"CycleStep cannot be negative: {val}")
        return super().__new__(cls, val)

    def __repr__(self) -> str:
        return f"CycleStep({int(self)})"


__all__ = ["CycleStep"]

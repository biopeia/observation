"""Physical continuous duration typing for Embodiment v2 (T_p).

Subordinate to docs/design/core/temporal-scales-and-clock-separation-v1.md.
Cognition and Foundation must never import or consume this scale.
"""

from __future__ import annotations

import math


class PhysicalDuration(float):
    """Continuous metric physical time elapsed in the physical substrate (T_p) in seconds."""

    def __new__(cls, value: float | int = 0.0) -> PhysicalDuration:
        if not (type(value) in (int, float) or isinstance(value, cls)):
            raise TypeError("PhysicalDuration requires a plain numeric duration")
        val = float(value)
        if not math.isfinite(val):
            raise ValueError(f"PhysicalDuration must be finite: {val}")
        if val < 0.0:
            raise ValueError(f"PhysicalDuration cannot be negative: {val}")
        return super().__new__(cls, val)

    def __repr__(self) -> str:
        return f"PhysicalDuration({float(self)})"


__all__ = ["PhysicalDuration"]

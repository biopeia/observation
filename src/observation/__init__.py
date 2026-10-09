"""Passive, transport-neutral projections for runtime observations."""

from .contracts import ObservedFrame
from .projection import runtime_tick_events

__all__ = ["ObservedFrame", "runtime_tick_events"]

"""Sense sources handed to the organism from outside.

The organism does not need to know where a source comes from. Whoever composes
it supplies the discovery and reading providers and says whether host senses are
available; the organism attaches them.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .discovery import DiscoveryProvider
from .readings import ReadingProvider


class ProcessTelemetryObserver(Protocol):
    """Passive observer hook; telemetry must not become organism perception."""

    def observe_tick(self, latency: float) -> None: ...


@dataclass(frozen=True, slots=True)
class HostSenseSources:
    discovery_providers: tuple[DiscoveryProvider, ...] = ()
    reading_providers: tuple[ReadingProvider, ...] = ()
    # Optional passive observer hook. It may receive timing, but its process
    # measurements are not offered as organism capabilities or readings.
    process_telemetry: ProcessTelemetryObserver | None = None
    # "available" | "unavailable": whether host senses could be offered at all.
    availability: str = "unavailable"

    def __post_init__(self) -> None:
        if self.availability not in {"available", "unavailable"}:
            raise ValueError("availability must be 'available' or 'unavailable'")

"""Structural contracts for modality-owned host channels."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .records import Capability, SensorReading


@runtime_checkable
class HostDiscoveryProvider(Protocol):
    """A modality channel that discovers its offered surfaces."""

    provider_id: str

    def discover(self) -> tuple[Capability, ...]: ...


@runtime_checkable
class HostReadingProvider(Protocol):
    """A modality channel that samples only previously discovered surfaces."""

    provider_id: str

    def sample(self, capabilities: tuple[Capability, ...]) -> tuple[SensorReading, ...]: ...


@runtime_checkable
class HostTickObserver(Protocol):
    """A passive apparatus observer that receives elapsed tick latency."""

    provider_id: str

    def observe_tick(self, latency: float) -> None: ...

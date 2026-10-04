"""Structural contracts for opaque Physics3D apparatus surfaces."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Protocol


class MotorPortPair(Protocol):
    """A body-defined pair of mutually exclusive opaque actuator ports."""

    @property
    def positive_port(self) -> str: ...

    @property
    def negative_port(self) -> str: ...


class Physics3DAppliance(Protocol):
    """Opaque body surface consumed by a runtime composition root."""

    @property
    def receptor_ids(self) -> Sequence[str]: ...

    @property
    def effector_ids(self) -> Sequence[str]: ...

    @property
    def motor_bindings(self) -> Sequence[MotorPortPair]: ...

    def sample_receptors(self) -> Mapping[str, float]: ...

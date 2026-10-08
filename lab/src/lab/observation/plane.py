"""In-memory coordination for semantic observations.

This is the first operational Observation Plane seam. It intentionally provides
only bounded current-state materialization and read access. Live delivery,
history, replay, transport, and wire serialization remain outside this module.
"""

from __future__ import annotations

import threading
from collections import OrderedDict
from dataclasses import dataclass
from typing import Hashable

from lab.observation.semantic import SemanticObservation


@dataclass(frozen=True, slots=True)
class ObservationKey:
    family: str
    subject: Hashable


def observation_key(observation: SemanticObservation[object]) -> ObservationKey:
    subject = observation.claim.subject
    identities = tuple(
        (
            assertion.identity.kind,
            assertion.identity.value,
            assertion.identity.issuer.kind,
            assertion.identity.issuer.identifier,
        )
        for assertion in subject.identities
    )
    participants = tuple(
        (
            assertion.identity.kind,
            assertion.identity.value,
            assertion.identity.issuer.kind,
            assertion.identity.issuer.identifier,
        )
        for assertion in subject.participants
    )
    return ObservationKey(
        family=observation.family.qualified_name,
        subject=(subject.kind, subject.key, identities, participants),
    )


class ObservationPlane:
    """Bounded materialized current state for canonical semantic observations."""

    def __init__(self, *, max_entries: int = 4096) -> None:
        if max_entries < 1:
            raise ValueError("max_entries must be >= 1")
        self._max_entries = int(max_entries)
        self._lock = threading.Lock()
        self._current: OrderedDict[ObservationKey, SemanticObservation[object]] = OrderedDict()

    def publish(self, observation: SemanticObservation[object]) -> None:
        key = observation_key(observation)
        with self._lock:
            self._current[key] = observation
            self._current.move_to_end(key)
            while len(self._current) > self._max_entries:
                self._current.popitem(last=False)

    def current(
        self,
        *,
        family: str | None = None,
    ) -> tuple[SemanticObservation[object], ...]:
        with self._lock:
            values = tuple(self._current.values())
        if family is None:
            return values
        return tuple(
            observation
            for observation in values
            if observation.family.qualified_name == family
        )

    def clear(self) -> None:
        with self._lock:
            self._current.clear()


__all__ = ["ObservationKey", "ObservationPlane", "observation_key"]

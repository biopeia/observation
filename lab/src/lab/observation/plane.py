"""In-memory coordination for semantic observations.

This module owns bounded current-state materialization and bounded live
subscription for the operational Observation Plane. It is deliberately
transport-neutral: HTTP/SSE serialization lives in lab.server.
"""

from __future__ import annotations

import queue
import threading
from collections import OrderedDict
from dataclasses import dataclass
from typing import Hashable

from lab.observation.semantic import SemanticObservation

_DEFAULT_SUBSCRIBER_QUEUE = 512


@dataclass(frozen=True, slots=True)
class ObservationKey:
    family: str
    subject: Hashable


@dataclass(frozen=True, slots=True)
class PlaneMessage:
    sequence: int
    observation: SemanticObservation[object]


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
    """Bounded current state and non-blocking live fan-out.

    Slow consumers can lose intermediate live updates, but they can always
    re-read canonical current state. Source publication never blocks on them.
    """

    def __init__(
        self,
        *,
        max_entries: int = 4096,
        subscriber_queue_size: int = _DEFAULT_SUBSCRIBER_QUEUE,
    ) -> None:
        if max_entries < 1:
            raise ValueError("max_entries must be >= 1")
        if subscriber_queue_size < 1:
            raise ValueError("subscriber_queue_size must be >= 1")
        self._max_entries = int(max_entries)
        self._subscriber_queue_size = int(subscriber_queue_size)
        self._lock = threading.Lock()
        self._current: OrderedDict[ObservationKey, PlaneMessage] = OrderedDict()
        self._subscribers: set[queue.Queue[PlaneMessage]] = set()
        self._sequence = 0
        self._consumer_overflows = 0

    @property
    def latest_sequence(self) -> int:
        with self._lock:
            return self._sequence

    @property
    def consumer_overflows(self) -> int:
        with self._lock:
            return self._consumer_overflows

    def publish(self, observation: SemanticObservation[object]) -> int:
        key = observation_key(observation)
        with self._lock:
            self._sequence += 1
            message = PlaneMessage(self._sequence, observation)
            self._current[key] = message
            self._current.move_to_end(key)
            while len(self._current) > self._max_entries:
                self._current.popitem(last=False)

            for consumer in self._subscribers:
                if consumer.full():
                    while True:
                        try:
                            consumer.get_nowait()
                        except queue.Empty:
                            break
                    self._consumer_overflows += 1
                consumer.put_nowait(message)
            return message.sequence

    def current_messages(
        self,
        *,
        family: str | None = None,
    ) -> tuple[PlaneMessage, ...]:
        with self._lock:
            values = tuple(self._current.values())
        if family is None:
            return values
        return tuple(
            message
            for message in values
            if message.observation.family.qualified_name == family
        )

    def current(
        self,
        *,
        family: str | None = None,
    ) -> tuple[SemanticObservation[object], ...]:
        return tuple(message.observation for message in self.current_messages(family=family))

    def subscribe(
        self,
        *,
        include_current: bool = True,
        family: str | None = None,
    ) -> queue.Queue[PlaneMessage]:
        consumer: queue.Queue[PlaneMessage] = queue.Queue(maxsize=self._subscriber_queue_size)
        with self._lock:
            self._subscribers.add(consumer)
            if include_current:
                current = tuple(self._current.values())
                if family is not None:
                    current = tuple(
                        message
                        for message in current
                        if message.observation.family.qualified_name == family
                    )
                # max_entries can be larger than subscriber_queue_size. Bootstrap
                # only the newest bounded tail rather than blocking or overflowing.
                for message in current[-self._subscriber_queue_size :]:
                    consumer.put_nowait(message)
        return consumer

    def unsubscribe(self, consumer: queue.Queue[PlaneMessage]) -> None:
        with self._lock:
            self._subscribers.discard(consumer)

    def clear(self) -> None:
        with self._lock:
            self._current.clear()


__all__ = [
    "ObservationKey",
    "ObservationPlane",
    "PlaneMessage",
    "observation_key",
]

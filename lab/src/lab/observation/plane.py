"""In-memory coordination for semantic observations.

The operational Observation Plane provides:
- bounded current-state materialization,
- bounded live fan-out,
- bounded in-memory replay by delivery sequence,
- explicit rebase when replay is no longer possible.

It is deliberately transport-neutral. HTTP/SSE serialization lives in lab.server.
"""

from __future__ import annotations

import queue
import threading
from collections import OrderedDict, deque
from dataclasses import dataclass
from typing import Hashable

from lab.observation.semantic import SemanticObservation

_DEFAULT_SUBSCRIBER_QUEUE = 512
_DEFAULT_REPLAY_MESSAGES = 2048


@dataclass(frozen=True, slots=True)
class ObservationKey:
    family: str
    subject: Hashable


@dataclass(frozen=True, slots=True)
class PlaneMessage:
    sequence: int
    observation: SemanticObservation[object]


@dataclass(frozen=True, slots=True)
class PlaneRebaseRequired:
    sequence: int
    reason: str


@dataclass(eq=False, slots=True)
class PlaneStreamSubscription:
    queue: queue.Queue[PlaneMessage | PlaneRebaseRequired]
    family: str | None


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
    """Bounded current state, replay and non-blocking live fan-out."""

    def __init__(
        self,
        *,
        max_entries: int = 4096,
        subscriber_queue_size: int = _DEFAULT_SUBSCRIBER_QUEUE,
        replay_messages: int = _DEFAULT_REPLAY_MESSAGES,
    ) -> None:
        if max_entries < 1:
            raise ValueError("max_entries must be >= 1")
        if subscriber_queue_size < 1:
            raise ValueError("subscriber_queue_size must be >= 1")
        if replay_messages < 1:
            raise ValueError("replay_messages must be >= 1")
        self._max_entries = int(max_entries)
        self._subscriber_queue_size = int(subscriber_queue_size)
        self._lock = threading.Lock()
        self._current: OrderedDict[ObservationKey, PlaneMessage] = OrderedDict()
        self._history: deque[PlaneMessage] = deque(maxlen=int(replay_messages))
        self._subscribers: set[queue.Queue[PlaneMessage]] = set()
        self._stream_subscribers: set[PlaneStreamSubscription] = set()
        self._sequence = 0
        self._consumer_overflows = 0

    @property
    def latest_sequence(self) -> int:
        with self._lock:
            return self._sequence

    @property
    def oldest_replay_sequence(self) -> int | None:
        with self._lock:
            return self._history[0].sequence if self._history else None

    @property
    def consumer_overflows(self) -> int:
        with self._lock:
            return self._consumer_overflows

    @staticmethod
    def _drain(consumer: queue.Queue[object]) -> None:
        while True:
            try:
                consumer.get_nowait()
            except queue.Empty:
                return

    def publish(self, observation: SemanticObservation[object]) -> int:
        key = observation_key(observation)
        with self._lock:
            self._sequence += 1
            message = PlaneMessage(self._sequence, observation)
            self._history.append(message)
            self._current[key] = message
            self._current.move_to_end(key)
            while len(self._current) > self._max_entries:
                self._current.popitem(last=False)

            for consumer in self._subscribers:
                if consumer.full():
                    self._drain(consumer)
                    self._consumer_overflows += 1
                consumer.put_nowait(message)

            for subscription in self._stream_subscribers:
                if (
                    subscription.family is not None
                    and observation.family.qualified_name != subscription.family
                ):
                    continue
                if subscription.queue.full():
                    self._drain(subscription.queue)
                    subscription.queue.put_nowait(
                        PlaneRebaseRequired(
                            sequence=self._sequence,
                            reason="consumer_overflow",
                        )
                    )
                    self._consumer_overflows += 1
                    continue
                subscription.queue.put_nowait(message)
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
            message for message in values if message.observation.family.qualified_name == family
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
        """Compatibility subscription for in-process consumers.

        New transport consumers should use open_stream() for replay/rebase semantics.
        """

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
                for message in current[-self._subscriber_queue_size :]:
                    consumer.put_nowait(message)
        return consumer

    def unsubscribe(self, consumer: queue.Queue[PlaneMessage]) -> None:
        with self._lock:
            self._subscribers.discard(consumer)

    def open_stream(
        self,
        *,
        after_sequence: int | None = None,
        family: str | None = None,
    ) -> PlaneStreamSubscription:
        """Open an atomic bootstrap/replay/live subscription.

        No watermark means bootstrap current materialized state. A retained
        watermark replays messages after it. An expired watermark yields an
        explicit rebase request; the transport can then send current state at
        the returned sequence watermark.
        """

        consumer: queue.Queue[PlaneMessage | PlaneRebaseRequired] = queue.Queue(
            maxsize=self._subscriber_queue_size
        )
        subscription = PlaneStreamSubscription(queue=consumer, family=family)
        with self._lock:
            self._stream_subscribers.add(subscription)
            if after_sequence is None:
                bootstrap = tuple(self._current.values())
                if family is not None:
                    bootstrap = tuple(
                        message
                        for message in bootstrap
                        if message.observation.family.qualified_name == family
                    )
                for message in bootstrap[-self._subscriber_queue_size :]:
                    consumer.put_nowait(message)
                return subscription

            resume = max(0, int(after_sequence))
            oldest = self._history[0].sequence if self._history else None
            if resume > self._sequence:
                consumer.put_nowait(
                    PlaneRebaseRequired(
                        sequence=self._sequence,
                        reason="future_watermark",
                    )
                )
                return subscription
            if oldest is None and resume < self._sequence:
                consumer.put_nowait(
                    PlaneRebaseRequired(
                        sequence=self._sequence,
                        reason="replay_unavailable",
                    )
                )
                return subscription
            if oldest is not None and resume < oldest - 1:
                consumer.put_nowait(
                    PlaneRebaseRequired(
                        sequence=self._sequence,
                        reason="replay_expired",
                    )
                )
                return subscription

            replay = tuple(message for message in self._history if message.sequence > resume)
            if family is not None:
                replay = tuple(
                    message
                    for message in replay
                    if message.observation.family.qualified_name == family
                )
            if len(replay) > self._subscriber_queue_size:
                consumer.put_nowait(
                    PlaneRebaseRequired(
                        sequence=self._sequence,
                        reason="replay_exceeds_subscriber_bound",
                    )
                )
                return subscription
            for message in replay:
                consumer.put_nowait(message)
        return subscription

    def close_stream(self, subscription: PlaneStreamSubscription) -> None:
        with self._lock:
            self._stream_subscribers.discard(subscription)

    def clear(self) -> None:
        with self._lock:
            self._current.clear()
            self._history.clear()
            for consumer in self._subscribers:
                self._drain(consumer)
            for subscription in self._stream_subscribers:
                self._drain(subscription.queue)
                subscription.queue.put_nowait(
                    PlaneRebaseRequired(
                        sequence=self._sequence,
                        reason="run_boundary",
                    )
                )


__all__ = [
    "ObservationKey",
    "ObservationPlane",
    "PlaneMessage",
    "PlaneRebaseRequired",
    "PlaneStreamSubscription",
    "observation_key",
]

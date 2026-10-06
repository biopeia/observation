from __future__ import annotations

import json

from lab.observation.bus import ObservationBus
from lab.observation.contracts import (
    COMPLETED_FRAME_CONTRACT,
    OBSERVATION_IDENTITY_CONTRACT,
    ObservedFrame,
)
from lab.observation.physics3d import Physics3DObservationBridge
from lab.observation.world_scene import SCENE_CONTRACT


class _Sink:
    def __init__(self) -> None:
        self.events: list[dict] = []

    def push(self, event: dict) -> None:
        self.events.append(event)


def _payload(message) -> dict:
    return json.loads(message.data)


def test_coherent_frame_contract_carries_scientific_identity() -> None:
    event = ObservedFrame(
        tick=12,
        source="physics3d",
        run_id="run-12",
        organism_id="organism-1",
        instance_id="instance-1",
        body_id="body-2",
        embodiment_id="embodiment-3",
        topology_revision=9,
        body={"type": "body", "tick": 12},
        cognition={"type": "cognition", "tick": 12},
        vitals={"type": "vitals", "tick": 12},
        mind={"tick": 12},
    ).as_event()

    assert event["run_id"] == "run-12"
    assert event["organism_id"] == "organism-1"
    assert event["instance_id"] == "instance-1"
    assert event["body_id"] == "body-2"
    assert event["embodiment_id"] == "embodiment-3"
    assert event["topology_revision"] == 9
    assert event["provenance"]["contract"] == COMPLETED_FRAME_CONTRACT
    assert COMPLETED_FRAME_CONTRACT == "completed-render-frame-v1"
    assert event["provenance"]["identity_contract"] == OBSERVATION_IDENTITY_CONTRACT
    assert OBSERVATION_IDENTITY_CONTRACT == "observation-identity-v1"


def test_physics3d_bridge_propagates_run_identity_to_all_coherent_components() -> None:
    sink = _Sink()
    bridge = Physics3DObservationBridge(sink, run_id="run-identity")
    bridge.publish(
        {"tick": 5, "alive": True},
        physical_state={
            "body_kind": "anthropomorphic-v6",
            "joints": [],
            "links": [],
            "organism_id": "organism-a",
            "body_id": "body-a",
            "embodiment_id": "embodiment-a",
        },
    )
    bridge.publish_rich_state(
        {
            "tick": 5,
            "organism_id": "organism-a",
            "body_id": "body-a",
            "embodiment_id": "embodiment-a",
            "runtime": {},
            "cognition": {"topology_revision": 4},
        }
    )

    by_type = {event["type"]: event for event in sink.events}
    for kind in ("body", "cognition", "vitals", "mind_snapshot", "observed_frame"):
        assert by_type[kind]["run_id"] == "run-identity"
    frame = by_type["observed_frame"]
    assert frame["organism_id"] == "organism-a"
    assert frame["body_id"] == "body-a"
    assert frame["embodiment_id"] == "embodiment-a"
    assert frame["topology_revision"] == 4
    assert frame["body"]["run_id"] == "run-identity"
    assert frame["cognition"]["run_id"] == "run-identity"
    assert frame["vitals"]["run_id"] == "run-identity"


def test_bridge_uses_lab_known_identity_when_runtime_projection_omits_it() -> None:
    sink = _Sink()
    bridge = Physics3DObservationBridge(
        sink,
        run_id="run-known",
        organism_id="organism-known",
        body_id="body-known",
    )
    bridge.publish(
        {"tick": 3, "alive": True},
        physical_state={
            "body_kind": "anthropomorphic-v6",
            "joints": [],
            "links": [],
        },
    )
    bridge.publish_rich_state({"tick": 3, "runtime": {}, "cognition": {}})

    by_type = {event["type"]: event for event in sink.events}
    frame = by_type["observed_frame"]
    assert frame["run_id"] == "run-known"
    assert frame["organism_id"] == "organism-known"
    assert frame["body_id"] == "body-known"
    assert frame["cognition"]["organism_id"] == "organism-known"
    assert frame["cognition"]["body_id"] == "body-known"
    assert by_type["mind_snapshot"]["organism_id"] == "organism-known"
    assert by_type["mind_snapshot"]["body_id"] == "body-known"


def test_bridge_locks_onto_runtime_symbiont_id_across_components() -> None:
    sink = _Sink()
    bridge = Physics3DObservationBridge(
        sink,
        run_id="run-known",
        organism_id="org-fallback-ref",
        body_id="body-known",
    )
    bridge.publish(
        {"tick": 4, "alive": True, "symbiont_id": "symbiont:3d:canonical-id"},
        physical_state={
            "body_kind": "anthropomorphic-v6",
            "joints": [],
            "links": [],
        },
    )
    bridge.publish_rich_state({"tick": 4, "runtime": {}, "cognition": {}})

    by_type = {event["type"]: event for event in sink.events}
    assert by_type["body"]["organism_id"] == "symbiont:3d:canonical-id"
    assert by_type["cognition"]["organism_id"] == "symbiont:3d:canonical-id"
    assert by_type["vitals"]["organism_id"] == "symbiont:3d:canonical-id"
    assert by_type["mind_snapshot"]["organism_id"] == "symbiont:3d:canonical-id"
    assert by_type["observed_frame"]["organism_id"] == "symbiont:3d:canonical-id"


def test_slow_consumer_rebase_is_visible_and_counted() -> None:
    bus = ObservationBus(queue_size=1, history_size=8, anchor_interval=64)
    consumer = bus.subscribe()
    bus.push({"type": "vitals", "run_id": "r", "tick": 1})
    bus.push({"type": "vitals", "run_id": "r", "tick": 2})

    payload = _payload(consumer.get_nowait())
    assert payload["kind"] == "anchor"
    assert payload["transport"]["rebase"] == "consumer_overflow"
    status = bus.transport_status()
    assert status["consumer_overflows"] == 1
    assert status["subscribers"] == 1
    assert status["queue_capacity"] == 1


def test_world_scene_overflow_rebase_is_visible() -> None:
    bus = ObservationBus(queue_size=1, history_size=8)
    consumer = bus.subscribe()
    bus.push(
        {
            "type": "world_scene",
            "kind": "snapshot",
            "contract": SCENE_CONTRACT,
            "world_id": "world-1",
            "revision": 1,
            "entities": {},
            "run_id": "r",
        }
    )
    bus.push(
        {
            "type": "world_scene",
            "kind": "snapshot",
            "contract": SCENE_CONTRACT,
            "world_id": "world-1",
            "revision": 2,
            "entities": {},
            "run_id": "r",
        }
    )

    payload = _payload(consumer.get_nowait())
    assert payload["type"] == "world_scene"
    assert payload["transport"]["rebase"] == "consumer_overflow"


def test_history_rotation_reconnect_is_materialized_and_visible() -> None:
    bus = ObservationBus(queue_size=8, history_size=2, anchor_interval=64)
    first = bus.push({"type": "vitals", "run_id": "r", "tick": 1})
    for tick in range(2, 7):
        bus.push({"type": "vitals", "run_id": "r", "tick": tick})

    consumer = bus.subscribe(after_sequence=first)
    payload = _payload(consumer.get_nowait())
    assert payload["kind"] == "anchor"
    assert payload["state"]["tick"] == 6
    assert payload["transport"]["rebase"] == "history_rotated"
    assert bus.transport_status()["history_rebases"] == 1

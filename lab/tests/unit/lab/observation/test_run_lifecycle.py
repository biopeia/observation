from __future__ import annotations

import json
import threading
from pathlib import Path

from lab.app.physics3d.session import Physics3DSession
from lab.observation.bus import ObservationBus
from lab.observation.delta import ObservationDeltaDecoder
from lab.observation.development_history import build_development_history


def _payload(message) -> dict:
    return json.loads(message.data)


def _drain(consumer) -> list[dict]:
    items = []
    while not consumer.empty():
        items.append(_payload(consumer.get_nowait()))
    return items


def _decode_anchor(payload: dict) -> dict:
    decoded = ObservationDeltaDecoder().decode(payload)
    assert decoded is not None
    return decoded


def test_begin_run_removes_previous_current_state_from_new_subscribers() -> None:
    bus = ObservationBus(queue_size=16, history_size=16, anchor_interval=64)
    bus.begin_run("run-a")
    bus.push(
        {
            "type": "observed_frame",
            "source": "physics3d",
            "run_id": "run-a",
            "organism_id": "org-a",
            "tick": 10,
        }
    )

    before = _drain(bus.subscribe())
    assert any(
        item.get("type") == "observation_delta"
        and item.get("channel") == "observed_frame"
        and item.get("state", {}).get("run_id") == "run-a"
        for item in before
    )

    boundary_sequence = bus.begin_run("run-b")
    after = _drain(bus.subscribe())

    assert after == [
        {
            "type": "observation_boundary",
            "phase": "begin",
            "run_id": "run-b",
        }
    ]
    assert bus.active_run_id == "run-b"
    assert bus.has_data is False
    assert bus.latest_sequence == boundary_sequence
    assert bus.recent_materialized("observed_frame", limit=16) == []


def test_begin_run_drops_queued_old_run_backlog_for_connected_clients() -> None:
    bus = ObservationBus(queue_size=16, history_size=16, anchor_interval=64)
    bus.begin_run("run-a")
    consumer = bus.subscribe()
    _drain(consumer)

    bus.push({"type": "body", "source": "physics3d", "run_id": "run-a", "tick": 1})
    bus.push({"type": "vitals", "source": "physics3d", "run_id": "run-a", "tick": 1})
    assert consumer.qsize() == 2

    bus.begin_run("run-b")
    assert _drain(consumer) == [
        {
            "type": "observation_boundary",
            "phase": "begin",
            "run_id": "run-b",
        }
    ]

    bus.push({"type": "body", "source": "physics3d", "run_id": "run-b", "tick": 2})
    payload = _payload(consumer.get_nowait())
    assert payload["type"] == "observation_delta"
    assert payload["kind"] == "anchor"
    assert payload["revision"] == 1
    assert _decode_anchor(payload)["run_id"] == "run-b"


def test_run_boundary_resets_delta_bases_without_resetting_transport_sequence() -> None:
    bus = ObservationBus(queue_size=16, history_size=16, anchor_interval=64)
    begin_a = bus.begin_run("run-a")
    first_a = bus.push({"type": "cognition", "run_id": "run-a", "tick": 1, "value": 1})
    second_a = bus.push({"type": "cognition", "run_id": "run-a", "tick": 2, "value": 2})
    begin_b = bus.begin_run("run-b")
    first_b = bus.push({"type": "cognition", "run_id": "run-b", "tick": 3, "value": 3})

    assert [begin_a, first_a, second_a, begin_b, first_b] == sorted(
        {begin_a, first_a, second_a, begin_b, first_b}
    )
    current = _drain(bus.subscribe())
    cognition = next(item for item in current if item.get("channel") == "cognition")
    assert cognition["kind"] == "anchor"
    assert cognition["revision"] == 1
    assert _decode_anchor(cognition) == {
        "type": "cognition",
        "run_id": "run-b",
        "tick": 3,
        "value": 3,
    }


def test_world_materialization_is_invalidated_at_run_boundary() -> None:
    bus = ObservationBus()
    bus.begin_run("run-a")
    bus.push(
        {
            "type": "world_scene",
            "kind": "snapshot",
            "contract": "body-in-world-v1",
            "world_id": "world-a",
            "revision": 1,
            "entities": {},
        }
    )
    assert bus.world_scene() is not None
    assert bus.world_scene()["world_id"] == "world-a"

    bus.begin_run("run-b")
    assert bus.world_scene() is None


def test_end_run_invalidates_current_state_and_emits_terminal_boundary() -> None:
    bus = ObservationBus()
    bus.begin_run("run-a")
    bus.push({"type": "vitals", "run_id": "run-a", "tick": 1})
    consumer = bus.subscribe()
    _drain(consumer)

    end_sequence = bus.end_run("run-a")

    assert bus.active_run_id is None
    assert bus.has_data is False
    assert bus.world_scene() is None
    assert bus.recent_materialized("vitals", limit=8) == []
    assert bus.latest_sequence == end_sequence
    assert _drain(consumer) == [
        {
            "type": "observation_boundary",
            "phase": "end",
            "run_id": "run-a",
        }
    ]


def test_physics3d_session_owns_bus_run_lifecycle() -> None:
    bus = ObservationBus(queue_size=16)
    entered = threading.Event()
    release = threading.Event()

    def runner(**_kwargs) -> int:
        entered.set()
        assert release.wait(timeout=5)
        return 0

    session = Physics3DSession(bus, runner=runner)
    consumer = bus.subscribe()
    assert session.start() is True
    assert entered.wait(timeout=5)

    snapshot = session.snapshot()
    assert snapshot.run_id is not None
    assert snapshot.run_id.startswith("local:")
    assert bus.active_run_id == snapshot.run_id
    assert _drain(consumer) == [
        {
            "type": "observation_boundary",
            "phase": "begin",
            "run_id": snapshot.run_id,
        }
    ]

    release.set()
    thread = session._thread
    assert thread is not None
    thread.join(timeout=5)
    assert not thread.is_alive()
    assert bus.active_run_id is None
    assert _drain(consumer) == [
        {
            "type": "observation_boundary",
            "phase": "end",
            "run_id": snapshot.run_id,
        }
    ]


def test_development_marks_identified_but_unreadable_run_incomplete(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    telemetry = runs / "run-a" / "telemetry"
    telemetry.mkdir(parents=True)
    (runs / "run-a" / "manifest.json").write_text(
        json.dumps({"run_id": "run-a", "started_at": "2026-10-06T10:00:00+00:00"}),
        encoding="utf-8",
    )
    # The persisted telemetry identity is sufficient to attribute the run, but
    # no ticks.ndjson exists, so open_telemetry must fail closed.
    (telemetry / "manifest.json").write_text(
        json.dumps(
            {
                "schema_version": "4.1",
                "organism_id": "symbiont:one",
                "status": "closed",
                "integrity": "sha256:test",
            }
        ),
        encoding="utf-8",
    )

    payload = build_development_history(runs, organism_id="symbiont:one", limit=16)

    assert payload["available"] is True
    assert payload["complete"] is False
    assert payload["points"] == []
    assert payload["snapshots"] == []
    assert payload["coverage"] == [
        {
            "run_id": "run-a",
            "started_at": "2026-10-06T10:00:00+00:00",
            "status": "closed",
            "entries": None,
            "tick_min": None,
            "tick_max": None,
            "integrity": "sha256:test",
            "availability": "unreadable",
        }
    ]


def test_unreadable_run_for_another_organism_does_not_pollute_coverage(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    telemetry = runs / "run-other" / "telemetry"
    telemetry.mkdir(parents=True)
    (telemetry / "manifest.json").write_text(
        json.dumps(
            {
                "schema_version": "4.1",
                "organism_id": "symbiont:other",
                "status": "closed",
            }
        ),
        encoding="utf-8",
    )

    payload = build_development_history(runs, organism_id="symbiont:one", limit=16)

    assert payload["available"] is False
    assert payload["complete"] is False
    assert payload["coverage"] == []

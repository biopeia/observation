from __future__ import annotations

import json

from lab.observation.bus import ObservationBus


def _drain(consumer) -> list[tuple[int, dict]]:
    items: list[tuple[int, dict]] = []
    while not consumer.empty():
        message = consumer.get_nowait()
        items.append((message.stream_id, json.loads(message.data)))
    return items


def test_reconnect_cursor_from_previous_run_cannot_replay_previous_run_state() -> None:
    bus = ObservationBus(queue_size=16, history_size=16, anchor_interval=64)
    bus.begin_run("run-a")
    last_a = bus.push(
        {
            "type": "observed_frame",
            "source": "physics3d",
            "run_id": "run-a",
            "organism_id": "org-a",
            "tick": 10,
        }
    )

    begin_b = bus.begin_run("run-b")
    resumed = _drain(bus.subscribe(after_sequence=last_a))

    assert resumed == [
        (
            begin_b,
            {
                "type": "observation_boundary",
                "phase": "begin",
                "run_id": "run-b",
            },
        )
    ]
    assert all(item.get("run_id") != "run-a" for _, item in resumed)


def test_transport_status_separates_server_sequence_from_active_run_lifecycle() -> None:
    bus = ObservationBus()

    begin_a = bus.begin_run("run-a")
    event_a = bus.push({"type": "vitals", "source": "physics3d", "run_id": "run-a", "tick": 1})
    end_a = bus.end_run("run-a")
    begin_b = bus.begin_run("run-b")

    assert begin_a < event_a < end_a < begin_b
    status = bus.transport_status()
    assert status["active_run_id"] == "run-b"
    assert status["run_boundaries"] == 3
    assert bus.latest_sequence == begin_b
    assert bus.has_data is False

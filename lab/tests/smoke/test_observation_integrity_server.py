from __future__ import annotations

import json
from contextlib import contextmanager
from http.client import HTTPConnection
from threading import Thread
from typing import Iterator

from lab.observation.bus import ObservationBus
from lab.server.server import UnifiedLabServer, make_server


@contextmanager
def _running_server(stream: ObservationBus) -> Iterator[UnifiedLabServer]:
    server = make_server(
        host="127.0.0.1",
        port=0,
        observation_bus=stream,
    )
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2.0)


def _get(server: UnifiedLabServer, path: str) -> tuple[int, dict]:
    host, port = server.server_address[:2]
    connection = HTTPConnection(host, port, timeout=2)
    try:
        connection.request("GET", path)
        response = connection.getresponse()
        return response.status, json.loads(response.read())
    finally:
        connection.close()


def test_history_endpoint_keeps_the_complete_coherent_frame_contract() -> None:
    stream = ObservationBus()
    stream.push(
        {
            "type": "observed_frame",
            "source": "physics3d",
            "run_id": "run-1",
            "organism_id": "organism-1",
            "instance_id": "instance-1",
            "body_id": "body-1",
            "embodiment_id": "embodiment-2",
            "topology_revision": 7,
            "tick": 41,
            "body": {"type": "body", "tick": 41, "base_position": [1, 2, 3]},
            "cognition": {"type": "cognition", "tick": 41, "predictor_count": 2},
            "vitals": {"type": "vitals", "tick": 41, "alive": True},
            "mind": {"tick": 41, "display_id": "symbiont:test"},
            "provenance": {"owner": "observer", "contract": "completed-render-frame-v2"},
        }
    )

    with _running_server(stream) as server:
        status, payload = _get(server, "/api/organism/history?limit=8")

    assert status == 200
    assert len(payload["items"]) == 1
    frame = payload["items"][0]
    assert frame["run_id"] == "run-1"
    assert frame["body_id"] == "body-1"
    assert frame["embodiment_id"] == "embodiment-2"
    assert frame["topology_revision"] == 7
    assert frame["body"]["base_position"] == [1, 2, 3]
    assert frame["cognition"]["predictor_count"] == 2
    assert frame["vitals"]["alive"] is True
    assert frame["provenance"]["contract"] == "completed-render-frame-v2"


def test_api_state_exposes_aggregate_observation_transport_health() -> None:
    stream = ObservationBus(queue_size=1, history_size=4)
    consumer = stream.subscribe()
    stream.push({"type": "vitals", "tick": 1})
    stream.push({"type": "vitals", "tick": 2})  # overflows the slow consumer
    stream.note_client_disconnect()

    with _running_server(stream) as server:
        status, payload = _get(server, "/api/state")

    stream.unsubscribe(consumer)
    assert status == 200
    transport = payload["sources"]["organism_stream"]["transport"]
    assert transport["consumer_overflows"] == 1
    assert transport["client_disconnects"] == 1
    assert transport["queue_capacity"] == 1
    assert transport["history_capacity"] == 4

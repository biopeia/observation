"""End-to-end HTTP/SSE tests for canonical semantic observations."""

from __future__ import annotations

import json
from contextlib import contextmanager
from http.client import HTTPConnection
from threading import Thread

from embodiment.observation import BodyPoseSample
from lab.observation.body_pose import body_pose_observation
from lab.observation.plane import ObservationPlane
from lab.server.server import make_server


@contextmanager
def _server(plane: ObservationPlane):
    server = make_server(host="127.0.0.1", port=0, observation_plane=plane)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2.0)


def _publish(plane: ObservationPlane) -> None:
    plane.publish(
        body_pose_observation(
            BodyPoseSample(
                body_id="body.http.1",
                reference_frame="physics3d.world",
                body_frame="body.root",
                position_m=(1.0, 2.0, 3.0),
                orientation_xyzw=(0.0, 0.0, 0.0, 1.0),
                sample_kind="physics_step",
                sample_value=42,
                sample_time_s=0.21,
            ),
            run_id="run.http.1",
        )
    )


def test_semantic_query_returns_materialized_body_pose() -> None:
    plane = ObservationPlane()
    _publish(plane)

    with _server(plane) as server:
        host, port = server.server_address[:2]
        conn = HTTPConnection(host, port, timeout=2)
        try:
            conn.request("GET", "/api/observations?family=embodiment.body_pose")
            response = conn.getresponse()
            payload = json.loads(response.read())
        finally:
            conn.close()

    assert response.status == 200
    assert payload["wire_contract"] == "observation-semantic-wire-v1"
    assert payload["latest_sequence"] == 1
    assert len(payload["items"]) == 1
    assert payload["items"][0]["family"] == "embodiment.body_pose"
    assert payload["items"][0]["value"]["position_m"] == [1.0, 2.0, 3.0]


def test_semantic_query_filter_does_not_alias_other_families() -> None:
    plane = ObservationPlane()
    _publish(plane)

    with _server(plane) as server:
        host, port = server.server_address[:2]
        conn = HTTPConnection(host, port, timeout=2)
        try:
            conn.request("GET", "/api/observations?family=environment.resource_state")
            response = conn.getresponse()
            payload = json.loads(response.read())
        finally:
            conn.close()

    assert response.status == 200
    assert payload["items"] == []


def test_api_state_reports_semantic_plane_health() -> None:
    plane = ObservationPlane()
    _publish(plane)

    with _server(plane) as server:
        host, port = server.server_address[:2]
        conn = HTTPConnection(host, port, timeout=2)
        try:
            conn.request("GET", "/api/state")
            response = conn.getresponse()
            payload = json.loads(response.read())
        finally:
            conn.close()

    semantic = payload["sources"]["semantic_observations"]
    assert semantic["available"] is True
    assert semantic["current"] == 1
    assert semantic["latest_sequence"] == 1


def test_semantic_sse_bootstraps_current_body_pose() -> None:
    plane = ObservationPlane()
    _publish(plane)

    with _server(plane) as server:
        host, port = server.server_address[:2]
        conn = HTTPConnection(host, port, timeout=2)
        try:
            conn.request(
                "GET",
                "/api/observations/stream?family=embodiment.body_pose",
                headers={"Accept": "text/event-stream"},
            )
            response = conn.getresponse()
            first = response.fp.readline().decode().strip()
            second = response.fp.readline().decode().strip()
        finally:
            conn.close()

    assert response.status == 200
    assert first == "id: 1"
    assert second.startswith("data: ")
    payload = json.loads(second[len("data: ") :])
    assert payload["family"] == "embodiment.body_pose"
    assert payload["orchestration"]["run"]["value"] == "run.http.1"

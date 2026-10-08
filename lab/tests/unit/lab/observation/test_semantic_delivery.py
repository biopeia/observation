"""Delivery tests for the semantic Observation Plane."""

from __future__ import annotations

import queue

from embodiment.observation import BodyPoseSample
from lab.observation.body_pose import body_pose_observation
from lab.observation.plane import ObservationPlane, PlaneRebaseRequired
from lab.observation.wire import plane_message_payload


def _observation(*, body_id: str = "body.1", step: int = 1):
    return body_pose_observation(
        BodyPoseSample(
            body_id=body_id,
            reference_frame="physics3d.world",
            body_frame="body.root",
            position_m=(float(step), 0.0, 0.0),
            orientation_xyzw=(0.0, 0.0, 0.0, 1.0),
            sample_kind="physics_step",
            sample_value=step,
            sample_time_s=step * 0.005,
        ),
        run_id="run.semantic.1",
    )


def test_semantic_plane_bootstraps_current_then_delivers_live_updates() -> None:
    plane = ObservationPlane(subscriber_queue_size=8)
    plane.publish(_observation(step=1))

    consumer = plane.subscribe(family="embodiment.body_pose")
    bootstrap = consumer.get_nowait()
    assert bootstrap.sequence == 1
    assert bootstrap.observation.claim.value.position_m == (1.0, 0.0, 0.0)

    plane.publish(_observation(step=2))
    live = consumer.get_nowait()
    assert live.sequence == 2
    assert live.observation.claim.value.position_m == (2.0, 0.0, 0.0)


def test_semantic_plane_slow_consumer_never_blocks_publication() -> None:
    plane = ObservationPlane(subscriber_queue_size=1)
    consumer = plane.subscribe(include_current=False)

    plane.publish(_observation(step=1))
    plane.publish(_observation(step=2))

    latest = consumer.get_nowait()
    assert latest.sequence == 2
    assert plane.consumer_overflows == 1


def test_run_boundary_clear_removes_current_and_pending_subscriber_backlog() -> None:
    plane = ObservationPlane(subscriber_queue_size=8)
    consumer = plane.subscribe(include_current=False)
    plane.publish(_observation(step=1))

    plane.clear()

    assert plane.current() == ()
    with __import__("pytest").raises(queue.Empty):
        consumer.get_nowait()


def test_wire_projection_preserves_semantics_and_run_context() -> None:
    plane = ObservationPlane()
    plane.publish(_observation(step=7))
    payload = plane_message_payload(plane.current_messages()[0])

    assert payload["type"] == "semantic_observation"
    assert payload["wire_contract"] == "observation-semantic-wire-v1"
    assert payload["family"] == "embodiment.body_pose"
    assert payload["authority"] == "embodiment"
    assert payload["semantic_contract"] == {
        "id": "embodiment.body_pose",
        "revision": "v1",
    }
    assert payload["subject"]["identities"][0]["value"] == "body.1"
    assert payload["value"]["position_m"] == [7.0, 0.0, 0.0]
    assert payload["value"]["orientation_xyzw"] == [0.0, 0.0, 0.0, 1.0]
    assert payload["domain_time"] == [
        {"domain": "embodiment", "kind": "physics_step", "value": 7},
        {"domain": "embodiment", "kind": "simulation_time_s", "value": 0.035},
    ]
    assert payload["orchestration"]["run"]["value"] == "run.semantic.1"



def test_stream_replays_messages_after_retained_watermark() -> None:
    plane = ObservationPlane(subscriber_queue_size=8, replay_messages=8)
    plane.publish(_observation(step=1))
    plane.publish(_observation(step=2))
    plane.publish(_observation(step=3))

    subscription = plane.open_stream(after_sequence=1, family="embodiment.body_pose")
    try:
        first = subscription.queue.get_nowait()
        second = subscription.queue.get_nowait()
    finally:
        plane.close_stream(subscription)

    assert first.sequence == 2
    assert second.sequence == 3


def test_stream_requires_rebase_when_watermark_expired() -> None:
    plane = ObservationPlane(subscriber_queue_size=8, replay_messages=1)
    plane.publish(_observation(step=1))
    plane.publish(_observation(step=2))
    plane.publish(_observation(step=3))

    subscription = plane.open_stream(after_sequence=1)
    try:
        control = subscription.queue.get_nowait()
    finally:
        plane.close_stream(subscription)

    assert isinstance(control, PlaneRebaseRequired)
    assert control.sequence == 3
    assert control.reason == "replay_expired"


def test_stream_requires_rebase_for_future_watermark() -> None:
    plane = ObservationPlane(subscriber_queue_size=8)
    plane.publish(_observation(step=1))

    subscription = plane.open_stream(after_sequence=9)
    try:
        control = subscription.queue.get_nowait()
    finally:
        plane.close_stream(subscription)

    assert isinstance(control, PlaneRebaseRequired)
    assert control.reason == "future_watermark"


def test_stream_overflow_emits_rebase_instead_of_silent_gap() -> None:
    plane = ObservationPlane(subscriber_queue_size=1)
    subscription = plane.open_stream(after_sequence=0)
    try:
        plane.publish(_observation(step=1))
        plane.publish(_observation(step=2))
        control = subscription.queue.get_nowait()
    finally:
        plane.close_stream(subscription)

    assert isinstance(control, PlaneRebaseRequired)
    assert control.sequence == 2
    assert control.reason == "consumer_overflow"


def test_run_boundary_invalidates_stream_state_explicitly() -> None:
    plane = ObservationPlane(subscriber_queue_size=8)
    plane.publish(_observation(step=1))
    subscription = plane.open_stream(after_sequence=1)
    try:
        plane.clear()
        control = subscription.queue.get_nowait()
    finally:
        plane.close_stream(subscription)

    assert isinstance(control, PlaneRebaseRequired)
    assert control.reason == "run_boundary"

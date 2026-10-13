"""Adversarial checks for the bounded Observation plane (not a data lake).

These tests must not be mistaken for an approved browser consumer contract.
"""
from observation import ObservationPlane, PlaneRebaseRequired
from observation.semantic import (
    AcquisitionBasis, ActorRef, AuthorityDomain, SemanticClaim,
    SemanticContractRef, SemanticFamily, SemanticObservation, SubjectScope,
)


def observation(value: int) -> SemanticObservation[object]:
    origin = ActorRef("test", "owner")
    return SemanticObservation(
        claim=SemanticClaim(
            family=SemanticFamily(
                AuthorityDomain.WORLD, ("test",),
                SemanticContractRef("test.world", "1"),
            ),
            subject=SubjectScope("test_subject", key=str(value)),
            epistemic_kind="authoritative_state",
            value={"value": value},
        ),
        acquisition=AcquisitionBasis("test_projection"),
        asserter=origin,
        producer=origin,
    )


def test_bounded_replay_eviction_requires_rebase() -> None:
    plane = ObservationPlane(max_entries=1, replay_messages=1)
    plane.publish(observation(1))
    plane.publish(observation(2))
    assert len(plane.current_messages()) == 1
    assert plane.current_messages()[0].observation.claim.value == {"value": 2}
    assert plane.latest_sequence == 2
    subscription = plane.open_stream(after_sequence=0)
    try:
        notice = subscription.queue.get_nowait()
        assert isinstance(notice, PlaneRebaseRequired)
        assert notice.reason == "replay_expired"
    finally:
        plane.close_stream(subscription)


def test_mutating_read_projection_cannot_rewrite_plane_history() -> None:
    plane = ObservationPlane()
    plane.publish(observation(1))
    read = plane.current_messages()[0]
    read.observation.claim.value["value"] = 999
    assert plane.current_messages()[0].observation.claim.value == {"value": 1}


def test_explicit_clear_rebases_stream_without_causal_context() -> None:
    plane = ObservationPlane()
    plane.publish(observation(1))
    plane.clear()
    plane.publish(observation(2))
    subscription = plane.open_stream(after_sequence=1)
    try:
        event = subscription.queue.get_nowait()
        assert isinstance(event, PlaneRebaseRequired)
        assert event.reason == "run_boundary"
    finally:
        plane.close_stream(subscription)

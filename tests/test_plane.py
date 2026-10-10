"""Passive bounded materialization and delivery for semantic observations."""

import pytest

from observation import ObservationPlane, PlaneRebaseRequired
from observation.semantic import (
    AcquisitionBasis,
    ActorRef,
    AuthorityDomain,
    DomainTimeRef,
    IdentityAssertion,
    IdentityRef,
    SemanticClaim,
    SemanticContractRef,
    SemanticFamily,
    SemanticObservation,
    SubjectScope,
)


def sample(step: int = 1) -> SemanticObservation[object]:
    owner = ActorRef("component", "embodiment.runtime")
    body = IdentityAssertion(IdentityRef("body", "body.1", owner), owner)
    return SemanticObservation(
        claim=SemanticClaim(
            family=SemanticFamily(
                AuthorityDomain.EMBODIMENT,
                ("body_pose",),
                SemanticContractRef("embodiment.body_pose", "v1"),
            ),
            subject=SubjectScope("body", identities=(body,)),
            epistemic_kind="simulated_apparatus_sample",
            value={"step": step},
        ),
        acquisition=AcquisitionBasis("physical_state_sample"),
        asserter=owner,
        producer=ActorRef("component", "observation.adapter"),
        domain_time=(DomainTimeRef(AuthorityDomain.EMBODIMENT, "step", step),),
    )


def with_value(
    original: SemanticObservation[object], value: object
) -> SemanticObservation[object]:
    claim = SemanticClaim(
        family=original.family,
        subject=original.claim.subject,
        epistemic_kind=original.claim.epistemic_kind,
        value=value,
    )
    return SemanticObservation(
        claim=claim,
        acquisition=original.acquisition,
        asserter=original.asserter,
        producer=original.producer,
        domain_time=original.domain_time,
        context_time=original.context_time,
        identity_links=original.identity_links,
        lineage=original.lineage,
        conditions=original.conditions,
        orchestration=original.orchestration,
    )


def test_publish_detaches_nested_aliases_from_family_adapter_and_owner_state() -> None:
    plane = ObservationPlane()
    owner_state = {"pose": {"position": [1.0, 2.0, 3.0]}}
    observation = with_value(sample(), owner_state)
    plane.publish(observation)

    # Later owner mutation cannot rewrite the published value.
    owner_state["pose"]["position"].append(4.0)
    assert plane.current()[0].claim.value == {"pose": {"position": [1.0, 2.0, 3.0]}}

    # A consumer receives a detached mutable projection, not owner state or
    # the plane's retained canonical copy.
    delivered = plane.current_messages()[0]
    delivered.observation.claim.value["pose"]["position"].append(9.0)  # type: ignore[index]
    assert owner_state["pose"]["position"] == [1.0, 2.0, 3.0, 4.0]
    assert plane.current()[0].claim.value == {"pose": {"position": [1.0, 2.0, 3.0]}}


def test_live_subscribers_receive_independent_nested_snapshots() -> None:
    plane = ObservationPlane()
    first = plane.open_stream()
    second = plane.open_stream()
    try:
        plane.publish(with_value(sample(), {"nested": [1]}))
        first_message = first.queue.get_nowait()
        second_message = second.queue.get_nowait()
        assert first_message.sequence == second_message.sequence == 1
        first_message.observation.claim.value["nested"].append(2)  # type: ignore[index]
        assert second_message.observation.claim.value == {"nested": [1]}
        assert plane.current()[0].claim.value == {"nested": [1]}
    finally:
        plane.close_stream(first)
        plane.close_stream(second)


def test_bootstrap_and_replay_deliver_detached_snapshots() -> None:
    plane = ObservationPlane()
    plane.publish(with_value(sample(), {"nested": [1]}))

    bootstrap = plane.open_stream()
    try:
        bootstrap_item = bootstrap.queue.get_nowait()
        bootstrap_item.observation.claim.value["nested"].append(2)  # type: ignore[index]
        assert plane.current()[0].claim.value == {"nested": [1]}
    finally:
        plane.close_stream(bootstrap)

    replay = plane.open_stream(after_sequence=0)
    try:
        replay_item = replay.queue.get_nowait()
        replay_item.observation.claim.value["nested"].append(3)  # type: ignore[index]
        assert plane.current()[0].claim.value == {"nested": [1]}
    finally:
        plane.close_stream(replay)


def test_unsupported_custom_value_fails_before_any_publication_side_effect() -> None:
    class CustomValue:
        pass

    plane = ObservationPlane()
    subscriber = plane.open_stream()
    try:
        with pytest.raises(TypeError, match="family adapters must project custom values"):
            plane.publish(with_value(sample(), {"nested": [CustomValue()]}))

        assert plane.latest_sequence == 0
        assert plane.oldest_replay_sequence is None
        assert plane.current_messages() == ()
        assert subscriber.queue.empty()
    finally:
        plane.close_stream(subscriber)


def test_recursive_claim_value_is_rejected_without_advancing_sequence() -> None:
    plane = ObservationPlane()
    recursive: list[object] = []
    recursive.append(recursive)

    with pytest.raises(TypeError, match="must not contain recursive containers"):
        plane.publish(with_value(sample(), recursive))
    assert plane.latest_sequence == 0
    assert plane.current() == ()


def test_plane_is_bounded_passive_current_and_live_delivery() -> None:
    plane = ObservationPlane(max_entries=1, subscriber_queue_size=2, replay_messages=2)
    subscription = plane.open_stream(family="embodiment.body_pose")
    try:
        plane.publish(sample(1))
        plane.publish(sample(2))
        delivered = subscription.queue.get_nowait()
        assert delivered.sequence == 1
        assert delivered.observation.claim.value == {"step": 1}
        assert [item.claim.value for item in plane.current()] == [{"step": 2}]
        assert plane.latest_sequence == 2
    finally:
        plane.close_stream(subscription)


def test_expired_resume_requires_explicit_rebase() -> None:
    plane = ObservationPlane(replay_messages=1)
    plane.publish(sample(1))
    plane.publish(sample(2))
    sub = plane.open_stream(after_sequence=0)
    try:
        message = sub.queue.get_nowait()
        assert isinstance(message, PlaneRebaseRequired)
        assert message.reason == "replay_expired"
    finally:
        plane.close_stream(sub)


def test_run_boundary_reaches_active_stream_and_reserves_delivery_watermark() -> None:
    plane = ObservationPlane()
    sub = plane.open_stream()
    try:
        plane.publish(sample(1))
        plane.clear()
        boundary = sub.queue.get_nowait()
        assert isinstance(boundary, PlaneRebaseRequired)
        assert boundary.reason == "run_boundary"
        assert boundary.sequence == 2
        assert plane.latest_sequence == 2
    finally:
        plane.close_stream(sub)


def test_late_resume_before_run_boundary_requires_rebase_even_with_new_history() -> None:
    plane = ObservationPlane()
    plane.publish(sample(1))
    plane.publish(sample(2))
    plane.clear()
    boundary_sequence = plane.latest_sequence
    plane.publish(sample(3))

    # Family filtering does not hide a global run boundary.
    sub = plane.open_stream(after_sequence=2, family="embodiment.body_pose")
    try:
        item = sub.queue.get_nowait()
        assert isinstance(item, PlaneRebaseRequired)
        assert item.reason == "run_boundary"
        assert item.sequence == 4
        current = plane.current_messages()
        assert len(current) == 1
        assert current[0].sequence == item.sequence
        assert current[0].observation.claim.value == {"step": 3}

        # Rebase repairs the materialized view, not the skipped event history;
        # this still-open subscription delivers publications after watermark 4.
        plane.publish(sample(4))
        following = sub.queue.get_nowait()
        assert not isinstance(following, PlaneRebaseRequired)
        assert following.sequence == 5
        assert following.observation.claim.value == {"step": 4}
    finally:
        plane.close_stream(sub)

    # A consumer that has acknowledged the boundary can replay later values.
    sub = plane.open_stream(after_sequence=boundary_sequence, family="embodiment.body_pose")
    try:
        item = sub.queue.get_nowait()
        assert not isinstance(item, PlaneRebaseRequired)
        assert item.sequence == 4
        assert item.observation.claim.value == {"step": 3}
    finally:
        plane.close_stream(sub)


def test_each_clear_advances_boundary_and_older_watermark_rebases_at_latest() -> None:
    plane = ObservationPlane()
    plane.publish(sample(1))
    plane.clear()
    first_boundary = plane.latest_sequence
    plane.clear()
    latest_boundary = plane.latest_sequence

    assert latest_boundary == first_boundary + 1
    sub = plane.open_stream(after_sequence=first_boundary)
    try:
        item = sub.queue.get_nowait()
        assert isinstance(item, PlaneRebaseRequired)
        assert item.reason == "run_boundary"
        assert item.sequence == latest_boundary
    finally:
        plane.close_stream(sub)

    # A resume at the latest boundary does not repeat the marker; an empty
    # current view is a projection result, not evidence of source absence.
    sub = plane.open_stream(after_sequence=latest_boundary)
    try:
        assert sub.queue.empty()
        assert plane.current() == ()
    finally:
        plane.close_stream(sub)


@pytest.mark.parametrize("watermark", [True, False, 1.5, "1"])
def test_stream_rejects_non_integer_resume_watermark(watermark: object) -> None:
    plane = ObservationPlane()
    with pytest.raises(TypeError, match="after_sequence must be an integer or None"):
        plane.open_stream(after_sequence=watermark)  # type: ignore[arg-type]


def test_stream_rejects_negative_resume_watermark() -> None:
    plane = ObservationPlane()
    with pytest.raises(ValueError, match="after_sequence must be >= 0"):
        plane.open_stream(after_sequence=-1)


@pytest.mark.parametrize("watermark", [0, 1, 99])
def test_stream_accepts_non_negative_integer_resume_watermark(watermark: int) -> None:
    plane = ObservationPlane()
    subscription = plane.open_stream(after_sequence=watermark)
    plane.close_stream(subscription)


def test_incompatible_semantic_revision_does_not_overwrite_materialization() -> None:
    plane = ObservationPlane()
    original = sample(1)
    revised = SemanticObservation(
        claim=SemanticClaim(
            family=SemanticFamily(
                AuthorityDomain.EMBODIMENT,
                ("body_pose",),
                SemanticContractRef("embodiment.body_pose", "v2"),
            ),
            subject=original.claim.subject,
            epistemic_kind=original.claim.epistemic_kind,
            value={"step": 2},
        ),
        acquisition=original.acquisition,
        asserter=original.asserter,
        producer=original.producer,
    )
    plane.publish(original)
    plane.publish(revised)

    messages = plane.current_messages()
    assert len(messages) == 2
    assert {m.observation.family.contract.revision for m in messages} == {"v1", "v2"}


def test_materialization_key_includes_contract_id_and_identity_scope_and_lifetime() -> None:
    plane = ObservationPlane()
    baseline = sample(1)
    owner = baseline.claim.subject.identities[0].identity.issuer

    scoped_subject = SubjectScope(
        "body",
        identities=(
            IdentityAssertion(
                IdentityRef("body", "body.1", owner, scope="episode-a"),
                owner,
            ),
        ),
    )
    lifetime_subject = SubjectScope(
        "body",
        identities=(
            IdentityAssertion(
                IdentityRef("body", "body.1", owner, lifetime="episode-a"),
                owner,
            ),
        ),
    )

    def with_subject(subject: SubjectScope) -> SemanticObservation[object]:
        return SemanticObservation(
            claim=SemanticClaim(
                family=baseline.family,
                subject=subject,
                epistemic_kind=baseline.claim.epistemic_kind,
                value=baseline.claim.value,
            ),
            acquisition=baseline.acquisition,
            asserter=baseline.asserter,
            producer=baseline.producer,
        )

    different_contract = SemanticObservation(
        claim=SemanticClaim(
            family=SemanticFamily(
                AuthorityDomain.EMBODIMENT,
                ("body_pose",),
                SemanticContractRef("embodiment.body_pose.alternate", "v1"),
            ),
            subject=baseline.claim.subject,
            epistemic_kind=baseline.claim.epistemic_kind,
            value=baseline.claim.value,
        ),
        acquisition=baseline.acquisition,
        asserter=baseline.asserter,
        producer=baseline.producer,
    )

    for observation in (
        baseline,
        with_subject(scoped_subject),
        with_subject(lifetime_subject),
        different_contract,
    ):
        plane.publish(observation)

    assert len(plane.current_messages()) == 4


def test_materialization_key_separates_epistemic_kinds() -> None:
    plane = ObservationPlane()
    authoritative = sample(1)
    estimated = SemanticObservation(
        claim=SemanticClaim(
            family=authoritative.family,
            subject=authoritative.claim.subject,
            epistemic_kind="estimate",
            value=authoritative.claim.value,
        ),
        acquisition=authoritative.acquisition,
        asserter=authoritative.asserter,
        producer=authoritative.producer,
    )
    inferred = SemanticObservation(
        claim=SemanticClaim(
            family=authoritative.family,
            subject=authoritative.claim.subject,
            epistemic_kind="inference",
            value=authoritative.claim.value,
        ),
        acquisition=authoritative.acquisition,
        asserter=authoritative.asserter,
        producer=authoritative.producer,
    )

    for observation in (authoritative, estimated, inferred):
        plane.publish(observation)

    assert len(plane.current_messages()) == 3


def test_current_view_is_a_bounded_subset_not_a_complete_subject_census() -> None:
    plane = ObservationPlane(max_entries=1)
    first = sample(1)
    second = SemanticObservation(
        claim=SemanticClaim(
            family=first.family,
            subject=SubjectScope("body", key="body.2"),
            epistemic_kind=first.claim.epistemic_kind,
            value={"step": 2},
        ),
        acquisition=first.acquisition,
        asserter=first.asserter,
        producer=first.producer,
    )
    plane.publish(first)
    plane.publish(second)

    assert len(plane.current_messages()) == 1
    assert [item.claim.value for item in plane.current()] == [{"step": 2}]


def test_bootstrap_overflow_signals_rebase_instead_of_truncating_materialized_state() -> None:
    plane = ObservationPlane(max_entries=2, subscriber_queue_size=1)
    first = sample(1)
    second = SemanticObservation(
        claim=SemanticClaim(
            family=first.family,
            subject=SubjectScope("body", key="body.2"),
            epistemic_kind=first.claim.epistemic_kind,
            value={"step": 2},
        ),
        acquisition=first.acquisition,
        asserter=first.asserter,
        producer=first.producer,
    )
    plane.publish(first)
    plane.publish(second)

    sub = plane.open_stream()
    try:
        item = sub.queue.get_nowait()
        assert isinstance(item, PlaneRebaseRequired)
        assert item.sequence == 2
        assert item.reason == "bootstrap_exceeds_subscriber_bound"
    finally:
        plane.close_stream(sub)


def test_stream_overflow_signals_rebase_instead_of_silent_loss() -> None:
    plane = ObservationPlane(subscriber_queue_size=1)
    sub = plane.open_stream()
    try:
        # Consume bootstrap (empty), then overflow the bounded live stream.
        plane.publish(sample(1))
        plane.publish(sample(2))
        item = sub.queue.get_nowait()
        assert isinstance(item, PlaneRebaseRequired)
        assert item.reason == "consumer_overflow"
        assert item.sequence == 2
        assert plane.consumer_overflows == 1
    finally:
        plane.close_stream(sub)


def test_future_resume_watermark_requires_rebase_at_current_sequence() -> None:
    plane = ObservationPlane()
    plane.publish(sample(1))
    plane.publish(sample(2))

    sub = plane.open_stream(after_sequence=99)
    try:
        item = sub.queue.get_nowait()
        assert isinstance(item, PlaneRebaseRequired)
        assert item.reason == "future_watermark"
        assert item.sequence == plane.latest_sequence == 2
    finally:
        plane.close_stream(sub)


def test_replay_larger_than_subscriber_bound_requires_rebase() -> None:
    plane = ObservationPlane(subscriber_queue_size=1, replay_messages=4)
    plane.publish(sample(1))
    plane.publish(sample(2))

    sub = plane.open_stream(after_sequence=0)
    try:
        item = sub.queue.get_nowait()
        assert isinstance(item, PlaneRebaseRequired)
        assert item.reason == "replay_exceeds_subscriber_bound"
        assert item.sequence == plane.latest_sequence == 2
        assert sub.queue.empty()
    finally:
        plane.close_stream(sub)


def test_family_filtered_stream_preserves_global_sequence_gaps() -> None:
    plane = ObservationPlane()
    sub = plane.open_stream(family="embodiment.body_pose")
    source = sample(2)
    environment_observation = SemanticObservation(
        claim=SemanticClaim(
            family=SemanticFamily(
                AuthorityDomain.ENVIRONMENT,
                ("field",),
                SemanticContractRef("environment.field", "v1"),
            ),
            subject=source.claim.subject,
            epistemic_kind=source.claim.epistemic_kind,
            value={"step": 2},
        ),
        acquisition=source.acquisition,
        asserter=source.asserter,
        producer=source.producer,
    )
    try:
        plane.publish(sample(1))
        plane.publish(environment_observation)
        plane.publish(sample(3))

        first = sub.queue.get_nowait()
        second = sub.queue.get_nowait()
        assert not isinstance(first, PlaneRebaseRequired)
        assert not isinstance(second, PlaneRebaseRequired)
        assert first.sequence == 1
        assert second.sequence == 3
        assert first.observation.claim.value == {"step": 1}
        assert second.observation.claim.value == {"step": 3}
    finally:
        plane.close_stream(sub)


def test_live_stream_continues_after_overflow_rebase_marker() -> None:
    plane = ObservationPlane(subscriber_queue_size=1)
    sub = plane.open_stream()
    try:
        plane.publish(sample(1))
        plane.publish(sample(2))

        marker = sub.queue.get_nowait()
        assert isinstance(marker, PlaneRebaseRequired)
        assert marker.reason == "consumer_overflow"
        assert marker.sequence == 2

        plane.publish(sample(3))
        following = sub.queue.get_nowait()
        assert not isinstance(following, PlaneRebaseRequired)
        assert following.sequence == 3
        assert following.observation.claim.value == {"step": 3}
    finally:
        plane.close_stream(sub)

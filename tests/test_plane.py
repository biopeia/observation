"""Passive bounded materialization and delivery for semantic observations."""

import queue

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


def test_plane_is_bounded_passive_current_and_live_delivery() -> None:
    plane = ObservationPlane(max_entries=1, subscriber_queue_size=2, replay_messages=2)
    consumer = plane.subscribe(include_current=False, family="embodiment.body_pose")
    plane.publish(sample(1))
    plane.publish(sample(2))
    delivered = consumer.get_nowait()
    assert delivered.sequence == 1
    assert delivered.observation.claim.value == {"step": 1}
    assert [item.claim.value for item in plane.current()] == [{"step": 2}]
    assert plane.latest_sequence == 2


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


def test_publish_never_blocks_slow_compat_consumer() -> None:
    plane = ObservationPlane(subscriber_queue_size=1)
    consumer = plane.subscribe(include_current=False)
    plane.publish(sample(1))
    plane.publish(sample(2))
    assert consumer.get_nowait().sequence == 2
    assert plane.consumer_overflows == 1
    with pytest.raises(queue.Empty):
        consumer.get_nowait()


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
    finally:
        plane.close_stream(sub)

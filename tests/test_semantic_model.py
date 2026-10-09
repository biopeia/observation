"""Tests for the transport-independent semantic observation model."""

from __future__ import annotations

import pytest

from observation.semantic import (
    AcquisitionBasis,
    ActorRef,
    AuthorityDomain,
    ConditionDimension,
    ConditionOrigin,
    DomainTimeRef,
    IdentityAssertion,
    IdentityLink,
    IdentityLinkState,
    IdentityRef,
    Lineage,
    LineageSourceRef,
    ObservationCondition,
    OrchestrationContext,
    SemanticClaim,
    SemanticContractRef,
    SemanticFamily,
    SemanticObservation,
    SubjectScope,
    TransformationRef,
)


LAB = ActorRef("component", "lab")
PHYSICS3D = ActorRef("apparatus", "physics3d.mujoco")
EMBODIMENT_RUNTIME = ActorRef("component", "embodiment.runtime")
ENVIRONMENT_RUNTIME = ActorRef("component", "environment.runtime")
SYMBIONT_RUNTIME = ActorRef("component", "symbiont.runtime")


def family(authority: AuthorityDomain, *path: str, revision: str = "v1") -> SemanticFamily:
    return SemanticFamily(
        authority=authority,
        path=tuple(path),
        contract=SemanticContractRef(
            contract_id=".".join((authority.value, *path)),
            revision=revision,
        ),
    )


def identity(kind: str, value: str, issuer: ActorRef) -> IdentityAssertion:
    return IdentityAssertion(
        identity=IdentityRef(kind=kind, value=value, issuer=issuer),
        asserter=issuer,
    )


def test_body_pose_expresses_embodiment_measurement_without_lab_authority() -> None:
    body = identity("body", "body.42", EMBODIMENT_RUNTIME)
    part = identity("body_part", "pelvis", EMBODIMENT_RUNTIME)
    claim = SemanticClaim(
        family=family(AuthorityDomain.EMBODIMENT, "body_pose"),
        subject=SubjectScope(kind="body_part", identities=(body, part)),
        epistemic_kind="simulated_apparatus_sample",
        value={"position_m": (0.0, 0.0, 1.0), "orientation_xyzw": (0.0, 0.0, 0.0, 1.0)},
    )
    observation = SemanticObservation(
        claim=claim,
        acquisition=AcquisitionBasis(
            method="physical_state_sample",
            measurement_source=PHYSICS3D,
        ),
        asserter=EMBODIMENT_RUNTIME,
        producer=LAB,
        domain_time=(
            DomainTimeRef(
                domain=AuthorityDomain.EMBODIMENT,
                kind="physical_sample",
                value=17,
            ),
        ),
    )

    assert observation.authority is AuthorityDomain.EMBODIMENT
    assert observation.acquisition.measurement_source == PHYSICS3D
    assert observation.producer == LAB


def test_unknown_body_pose_unit_can_be_expressed_as_source_nonconformance() -> None:
    body = identity("body", "body.42", EMBODIMENT_RUNTIME)
    observation = SemanticObservation(
        claim=SemanticClaim(
            family=family(AuthorityDomain.EMBODIMENT, "body_pose"),
            subject=SubjectScope(kind="body", identities=(body,)),
            epistemic_kind="simulated_apparatus_sample",
            value={"position": (1.0, 2.0, 3.0)},
        ),
        acquisition=AcquisitionBasis(
            method="physical_state_sample",
            measurement_source=PHYSICS3D,
        ),
        asserter=EMBODIMENT_RUNTIME,
        producer=LAB,
        conditions=(
            ObservationCondition(
                dimension=ConditionDimension.AVAILABILITY,
                origin=ConditionOrigin.SOURCE,
                kind="nonconforming_capability",
                detail="position unit is implicit",
            ),
        ),
    )

    assert observation.source_conditions()[0].kind == "nonconforming_capability"


def test_environment_resource_scope_does_not_require_durable_resource_entity() -> None:
    environment = identity("environment_instance", "world.7", ENVIRONMENT_RUNTIME)
    claim = SemanticClaim(
        family=family(AuthorityDomain.ENVIRONMENT, "resource_state"),
        subject=SubjectScope(
            kind="environment_location",
            key="cell:4,9/resource:opaque-7",
            identities=(environment,),
        ),
        epistemic_kind="source_owned_state",
        value=0.75,
    )
    observation = SemanticObservation(
        claim=claim,
        acquisition=AcquisitionBasis(method="world_model_state"),
        asserter=ENVIRONMENT_RUNTIME,
        producer=ENVIRONMENT_RUNTIME,
        domain_time=(
            DomainTimeRef(
                domain=AuthorityDomain.ENVIRONMENT,
                kind="world_revision",
                value=31,
            ),
        ),
    )

    assert observation.claim.subject.kind == "environment_location"
    assert observation.claim.subject.participants == ()


def test_body_local_physiology_is_modeled_state_not_measurement() -> None:
    body = identity("body", "body.42", EMBODIMENT_RUNTIME)
    observation = SemanticObservation(
        claim=SemanticClaim(
            family=family(AuthorityDomain.EMBODIMENT, "body_physiology"),
            subject=SubjectScope(kind="body", identities=(body,)),
            epistemic_kind="modeled_body_state",
            value={"fatigue": 0.2},
        ),
        acquisition=AcquisitionBasis(method="canonical_body_state"),
        asserter=EMBODIMENT_RUNTIME,
        producer=EMBODIMENT_RUNTIME,
        domain_time=(
            DomainTimeRef(
                domain=AuthorityDomain.EMBODIMENT,
                kind="embodiment_cycle",
                value=99,
            ),
        ),
    )

    assert observation.acquisition.measurement_source is None
    assert observation.authority is AuthorityDomain.EMBODIMENT


def test_symbiont_affordance_retains_authority_with_cross_domain_lineage() -> None:
    organism = identity("organism", "organism.alpha", SYMBIONT_RUNTIME)
    observation = SemanticObservation(
        claim=SemanticClaim(
            family=family(AuthorityDomain.SYMBIONT, "affordance"),
            subject=SubjectScope(
                kind="organism_in_context",
                identities=(organism,),
                key="current-embodiment",
            ),
            epistemic_kind="domain_derived_state",
            value=("approach", "grasp"),
        ),
        acquisition=AcquisitionBasis(method="action_model_derivation"),
        asserter=SYMBIONT_RUNTIME,
        producer=SYMBIONT_RUNTIME,
        domain_time=(
            DomainTimeRef(
                domain=AuthorityDomain.SYMBIONT,
                kind="organism_cycle",
                value=201,
            ),
        ),
        lineage=Lineage(
            parents=(
                LineageSourceRef("symbiont.competence", "competence:grasp"),
                LineageSourceRef("embodiment.binding", "binding:hand"),
                LineageSourceRef("environment.context", "context:near-resource"),
            ),
            transformation=TransformationRef(
                transformation_id="symbiont.affordance_resolution",
                revision="v1",
            ),
        ),
    )

    assert observation.authority is AuthorityDomain.SYMBIONT
    assert len(observation.lineage.parents) == 3


def test_lab_derived_claim_does_not_take_authority_over_parent() -> None:
    residual = LineageSourceRef("symbiont.prediction_residual", "residual:88")
    observation = SemanticObservation(
        claim=SemanticClaim(
            family=family(AuthorityDomain.LAB, "prediction_error_band"),
            subject=SubjectScope(kind="predictor_target_relation", key="p1->t1"),
            epistemic_kind="lab_derived_claim",
            value="high",
        ),
        acquisition=AcquisitionBasis(method="classification"),
        asserter=LAB,
        producer=LAB,
        domain_time=(
            DomainTimeRef(
                domain=AuthorityDomain.LAB,
                kind="projection_revision",
                value=7,
            ),
        ),
        lineage=Lineage(
            parents=(residual,),
            transformation=TransformationRef(
                transformation_id="lab.prediction_error_classifier",
                revision="legacy-test-only",
            ),
        ),
    )

    assert observation.authority is AuthorityDomain.LAB
    assert observation.lineage.parents == (residual,)


def test_conflicting_identity_link_does_not_invalidate_independent_claim() -> None:
    physical = IdentityRef("body", "body.42", EMBODIMENT_RUNTIME)
    catalog = IdentityRef("lab_body_ref", "body-managed-17", LAB)
    observation = SemanticObservation(
        claim=SemanticClaim(
            family=family(AuthorityDomain.EMBODIMENT, "body_pose"),
            subject=SubjectScope(
                kind="body",
                identities=(IdentityAssertion(physical, EMBODIMENT_RUNTIME),),
            ),
            epistemic_kind="simulated_apparatus_sample",
            value={"position_m": (0.0, 0.0, 0.0)},
        ),
        acquisition=AcquisitionBasis(
            method="physical_state_sample",
            measurement_source=PHYSICS3D,
        ),
        asserter=EMBODIMENT_RUNTIME,
        producer=LAB,
        identity_links=(
            IdentityLink(
                left=physical,
                right=catalog,
                relation="same_subject",
                asserter=LAB,
                state=IdentityLinkState.CONFLICT,
            ),
        ),
    )

    assert observation.has_identity_conflict()
    assert observation.claim.subject.identities[0].identity == physical


def test_run_context_remains_separate_from_source_subject_identity() -> None:
    organism = identity("organism", "organism.alpha", SYMBIONT_RUNTIME)
    run = IdentityAssertion(
        IdentityRef("run", "run.9", LAB),
        asserter=LAB,
    )
    observation = SemanticObservation(
        claim=SemanticClaim(
            family=family(AuthorityDomain.SYMBIONT, "affordance"),
            subject=SubjectScope(kind="organism", identities=(organism,)),
            epistemic_kind="domain_derived_state",
            value=("grasp",),
        ),
        acquisition=AcquisitionBasis(method="action_model_derivation"),
        asserter=SYMBIONT_RUNTIME,
        producer=SYMBIONT_RUNTIME,
        orchestration=OrchestrationContext(run_identity=run),
    )

    assert observation.orchestration is not None
    assert observation.claim.subject.identities == (organism,)


def test_plane_condition_is_distinct_from_source_availability() -> None:
    organism = identity("organism", "organism.alpha", SYMBIONT_RUNTIME)
    observation = SemanticObservation(
        claim=SemanticClaim(
            family=family(AuthorityDomain.SYMBIONT, "affordance"),
            subject=SubjectScope(kind="organism", identities=(organism,)),
            epistemic_kind="domain_derived_state",
            value=(),
        ),
        acquisition=AcquisitionBasis(method="action_model_derivation"),
        asserter=SYMBIONT_RUNTIME,
        producer=LAB,
        conditions=(
            ObservationCondition(
                dimension=ConditionDimension.COMPLETENESS,
                origin=ConditionOrigin.SOURCE,
                kind="partial",
            ),
            ObservationCondition(
                dimension=ConditionDimension.AVAILABILITY,
                origin=ConditionOrigin.PLANE,
                kind="delivery_gap",
            ),
        ),
    )

    assert tuple(condition.kind for condition in observation.source_conditions()) == ("partial",)
    assert tuple(condition.kind for condition in observation.plane_conditions()) == (
        "delivery_gap",
    )


def test_transport_sequence_cannot_be_used_as_domain_time() -> None:
    with pytest.raises(ValueError, match="delivery metadata"):
        DomainTimeRef(
            domain=AuthorityDomain.LAB,
            kind="transport_sequence",
            value=5,
        )


def test_primary_domain_time_must_match_claim_authority() -> None:
    organism = identity("organism", "organism.alpha", SYMBIONT_RUNTIME)
    claim = SemanticClaim(
        family=family(AuthorityDomain.SYMBIONT, "affordance"),
        subject=SubjectScope(kind="organism", identities=(organism,)),
        epistemic_kind="domain_derived_state",
        value=("grasp",),
    )

    with pytest.raises(ValueError, match="claim authority"):
        SemanticObservation(
            claim=claim,
            acquisition=AcquisitionBasis(method="action_model_derivation"),
            asserter=SYMBIONT_RUNTIME,
            producer=SYMBIONT_RUNTIME,
            domain_time=(
                DomainTimeRef(
                    domain=AuthorityDomain.EMBODIMENT,
                    kind="embodiment_cycle",
                    value=2,
                ),
            ),
        )


def test_cross_domain_time_is_allowed_only_as_explicit_context() -> None:
    organism = identity("organism", "organism.alpha", SYMBIONT_RUNTIME)
    observation = SemanticObservation(
        claim=SemanticClaim(
            family=family(AuthorityDomain.SYMBIONT, "affordance"),
            subject=SubjectScope(kind="organism", identities=(organism,)),
            epistemic_kind="domain_derived_state",
            value=("grasp",),
        ),
        acquisition=AcquisitionBasis(method="action_model_derivation"),
        asserter=SYMBIONT_RUNTIME,
        producer=SYMBIONT_RUNTIME,
        domain_time=(
            DomainTimeRef(
                domain=AuthorityDomain.SYMBIONT,
                kind="organism_cycle",
                value=2,
            ),
        ),
        context_time=(
            DomainTimeRef(
                domain=AuthorityDomain.EMBODIMENT,
                kind="embodiment_cycle",
                value=9,
            ),
        ),
    )

    assert observation.context_time[0].domain is AuthorityDomain.EMBODIMENT

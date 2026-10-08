"""Adapt Body-local modeled physiology into the operational Observation Plane."""

from __future__ import annotations

from embodiment.observation import BodyPhysiologySample
from lab.observation.body_pose import (
    EMBODIMENT_AUTHORITY,
    LAB_PRODUCER,
    LAB_RUN_ISSUER,
    PHYSICS3D_RUNTIME,
)
from lab.observation.semantic import (
    AcquisitionBasis,
    ActorRef,
    AuthorityDomain,
    DomainTimeRef,
    IdentityAssertion,
    IdentityRef,
    OrchestrationContext,
    SemanticClaim,
    SemanticContractRef,
    SemanticFamily,
    SemanticObservation,
    SubjectScope,
)

LIVING_BODY_SOURCE = ActorRef("component", "embodiment.living_body_state")


def body_physiology_observation(
    sample: BodyPhysiologySample,
    *,
    organism_tick: int | None = None,
    run_id: str | None = None,
) -> SemanticObservation[BodyPhysiologySample]:
    body_identity = IdentityRef(
        kind="body",
        value=sample.body_id,
        issuer=PHYSICS3D_RUNTIME,
        lifetime="physical_body",
    )
    subject = SubjectScope(
        kind="body",
        identities=(
            IdentityAssertion(
                identity=body_identity,
                asserter=PHYSICS3D_RUNTIME,
            ),
        ),
    )
    family = SemanticFamily(
        authority=AuthorityDomain.EMBODIMENT,
        path=("body_physiology",),
        contract=SemanticContractRef(
            contract_id="embodiment.body_physiology",
            revision=sample.contract_revision,
        ),
    )
    return SemanticObservation(
        claim=SemanticClaim(
            family=family,
            subject=subject,
            epistemic_kind="modeled_body_state",
            value=sample,
        ),
        acquisition=AcquisitionBasis(
            method="living_body_operational_observation",
            measurement_source=LIVING_BODY_SOURCE,
        ),
        asserter=LIVING_BODY_SOURCE,
        producer=LAB_PRODUCER,
        orchestration=(
            OrchestrationContext(
                run_identity=IdentityAssertion(
                    identity=IdentityRef(
                        kind="run",
                        value=run_id,
                        issuer=LAB_RUN_ISSUER,
                        lifetime="lab_run",
                    ),
                    asserter=LAB_RUN_ISSUER,
                )
            )
            if run_id is not None
            else None
        ),
        domain_time=(
            DomainTimeRef(
                domain=AuthorityDomain.EMBODIMENT,
                kind="body_age_tick",
                value=sample.age_ticks,
            ),
        ),
        context_time=(
            (
                DomainTimeRef(
                    domain=AuthorityDomain.SYMBIONT,
                    kind="organism_tick",
                    value=organism_tick,
                ),
            )
            if organism_tick is not None
            else ()
        ),
    )


__all__ = ["body_physiology_observation"]

"""Adapt Embodiment-owned Body Pose samples into the operational Observation Plane model."""

from __future__ import annotations

from embodiment.observation import BodyPoseSample

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

EMBODIMENT_AUTHORITY = ActorRef("domain", "embodiment")
PHYSICS3D_SOURCE = ActorRef("apparatus", "physics3d.mujoco")
PHYSICS3D_RUNTIME = ActorRef("component", "physics3d.embodiment_runtime")
LAB_PRODUCER = ActorRef("component", "lab.observation.physics3d")
LAB_RUN_ISSUER = ActorRef("component", "lab.run_lifecycle")


def body_pose_observation(
    sample: BodyPoseSample,
    *,
    run_id: str | None = None,
) -> SemanticObservation[BodyPoseSample]:
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
        path=("body_pose",),
        contract=SemanticContractRef(
            contract_id="embodiment.body_pose",
            revision=sample.contract_revision,
        ),
    )
    return SemanticObservation(
        claim=SemanticClaim(
            family=family,
            subject=subject,
            epistemic_kind="simulated_apparatus_sample",
            value=sample,
        ),
        acquisition=AcquisitionBasis(
            method="physical_state_sample",
            measurement_source=PHYSICS3D_SOURCE,
        ),
        asserter=PHYSICS3D_RUNTIME,
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
                kind=sample.sample_kind,
                value=sample.sample_value,
            ),
            *(
                (
                    DomainTimeRef(
                        domain=AuthorityDomain.EMBODIMENT,
                        kind="simulation_time_s",
                        value=sample.sample_time_s,
                    ),
                )
                if sample.sample_time_s is not None
                else ()
            ),
        ),
    )


__all__ = ["body_pose_observation"]

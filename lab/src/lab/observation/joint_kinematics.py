"""Adapt Embodiment-owned Joint Kinematics into the operational Observation Plane."""

from __future__ import annotations

from embodiment.observation import JointKinematicsSample
from lab.observation.body_pose import (
    EMBODIMENT_AUTHORITY,
    LAB_PRODUCER,
    LAB_RUN_ISSUER,
    PHYSICS3D_RUNTIME,
    PHYSICS3D_SOURCE,
)
from lab.observation.semantic import (
    AcquisitionBasis,
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


def joint_kinematics_observation(
    sample: JointKinematicsSample,
    *,
    run_id: str | None = None,
) -> SemanticObservation[JointKinematicsSample]:
    body_identity = IdentityRef(
        kind="body",
        value=sample.body_id,
        issuer=PHYSICS3D_RUNTIME,
        lifetime="physical_body",
    )
    subject = SubjectScope(
        kind="body_joint_set",
        identities=(
            IdentityAssertion(
                identity=body_identity,
                asserter=PHYSICS3D_RUNTIME,
            ),
        ),
    )
    family = SemanticFamily(
        authority=AuthorityDomain.EMBODIMENT,
        path=("joint_kinematics",),
        contract=SemanticContractRef(
            contract_id="embodiment.joint_kinematics",
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
            method="physical_joint_state_sample",
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


__all__ = ["joint_kinematics_observation"]

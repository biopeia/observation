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
    SemanticClaim,
    SemanticContractRef,
    SemanticFamily,
    SemanticObservation,
    SubjectScope,
)

EMBODIMENT_AUTHORITY = ActorRef("domain", "embodiment")
PHYSICS3D_SOURCE = ActorRef("apparatus", "physics3d.mujoco")
LAB_PRODUCER = ActorRef("component", "lab.observation.physics3d")


def body_pose_observation(sample: BodyPoseSample) -> SemanticObservation[BodyPoseSample]:
    body_identity = IdentityRef(
        kind="body",
        value=sample.body_id,
        issuer=EMBODIMENT_AUTHORITY,
        lifetime="physical_body",
    )
    subject = SubjectScope(
        kind="body",
        identities=(
            IdentityAssertion(
                identity=body_identity,
                asserter=EMBODIMENT_AUTHORITY,
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
        asserter=EMBODIMENT_AUTHORITY,
        producer=LAB_PRODUCER,
        domain_time=(
            DomainTimeRef(
                domain=AuthorityDomain.EMBODIMENT,
                kind=sample.sample_kind,
                value=sample.sample_value,
            ),
        ),
    )


__all__ = ["body_pose_observation"]

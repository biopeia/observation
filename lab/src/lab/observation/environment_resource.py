"""Adapt Environment logical resource-pool state into the Observation Plane."""

from __future__ import annotations

from environment.observation import ResourcePoolObservation
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

ENVIRONMENT_AUTHORITY = ActorRef("domain", "environment")
WORLD_STATE_ISSUER = ActorRef("component", "environment.world_state")
WORLD_ENVIRONMENT_SOURCE = ActorRef("component", "environment.world_environment")
WORLD_RUNTIME_PRODUCER = ActorRef("component", "lab.world.runtime")


def resource_state_observation(
    sample: ResourcePoolObservation,
    *,
    world_id: str,
) -> SemanticObservation[ResourcePoolObservation]:
    environment_identity = IdentityRef(
        kind="environment_instance",
        value=world_id,
        issuer=WORLD_STATE_ISSUER,
        lifetime="world_runtime",
    )
    subject = SubjectScope(
        kind="environment_cell",
        key=f"hex:{sample.q},{sample.r}",
        identities=(
            IdentityAssertion(
                identity=environment_identity,
                asserter=WORLD_STATE_ISSUER,
            ),
        ),
    )
    family = SemanticFamily(
        authority=AuthorityDomain.ENVIRONMENT,
        path=("resource_state",),
        contract=SemanticContractRef(
            contract_id="environment.resource_state",
            revision=sample.contract_revision,
        ),
    )
    return SemanticObservation(
        claim=SemanticClaim(
            family=family,
            subject=subject,
            epistemic_kind="logical_world_state",
            value=sample,
        ),
        acquisition=AcquisitionBasis(
            method="environment_resource_pool_observation",
            measurement_source=WORLD_ENVIRONMENT_SOURCE,
        ),
        asserter=WORLD_ENVIRONMENT_SOURCE,
        producer=WORLD_RUNTIME_PRODUCER,
        domain_time=(
            DomainTimeRef(
                domain=AuthorityDomain.ENVIRONMENT,
                kind="world_tick",
                value=sample.world_tick,
            ),
        ),
    )


__all__ = ["resource_state_observation"]

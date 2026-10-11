"""Adapters for Environment-owned semantic projections.

Observation maps approved owner projections into its passive common record
model. It does not calculate, reinterpret, or assert Environment state.
"""

from __future__ import annotations

import math
from typing import Protocol

from observation.semantic import (
    AcquisitionBasis,
    ActorRef,
    AuthorityDomain,
    DomainTimeRef,
    IdentityAssertion,
    IdentityRef,
    Lineage,
    LineageSourceRef,
    SemanticClaim,
    SemanticContractRef,
    SemanticFamily,
    SemanticObservation,
    SubjectScope,
    TransformationRef,
)


_FAMILY_ID = "biopeia.environment.finite-scalar-field"
_FAMILY_REVISION = "1"
_AUTHORITY = "ENVIRONMENT"
_EPISTEMIC_BASIS = "DOMAIN_DERIVED"
_ACQUISITION_BASIS = "environment_field_evaluation"
_SUBJECT_TYPE = "environment.finite_resource_field"
_ASSERTER = "environment.identified_finite_scalar_field"
_PRODUCER = "environment.identified_finite_scalar_field.project_observation"


class _FiniteScalarFieldProjection(Protocol):
    """Structural view of the approved Environment projection contract."""

    semantic_family_id: str
    semantic_revision: str
    semantic_authority: str
    epistemic_basis: str
    acquisition_basis: str
    semantic_asserter: str
    semantic_producer: str
    quantity_kind: str
    unit: str
    valid_range: tuple[float, float]
    resource_id: str
    field_revision: str
    environment_id: str
    environment_revision: str
    world_id: str
    source_causal_tick: int
    target_causal_tick: int
    physical_step_id: str
    frame_id: str
    point_m: tuple[float, float, float]
    value: float
    source_owner_checkpoint_sha256: str


def environment_finite_scalar_field_observation(
    projection: _FiniteScalarFieldProjection,
) -> SemanticObservation[dict[str, object]]:
    """Map the approved finite scalar-field owner projection to one claim.

    The accepted input is the Environment-owned
    ``FiniteScalarFieldObservationProjection`` contract. Attribute-based
    access keeps this repository independent of Environment's package
    internals; all contract identity and correlation fields are validated
    before a passive Observation value is created.

    This maps an Environment field projection, not an Embodiment receptor
    signal. It does not prove adoption or World commit; the World publisher
    must validate those independently before publication.
    """

    expected = {
        "semantic_family_id": _FAMILY_ID,
        "semantic_revision": _FAMILY_REVISION,
        "semantic_authority": _AUTHORITY,
        "epistemic_basis": _EPISTEMIC_BASIS,
        "acquisition_basis": _ACQUISITION_BASIS,
        "semantic_asserter": _ASSERTER,
        "semantic_producer": _PRODUCER,
        "quantity_kind": "dimensionless_scalar_field",
        "unit": "1",
        "valid_range": (0.0, 1.0),
    }
    for name, expected_value in expected.items():
        if getattr(projection, name, None) != expected_value:
            raise ValueError(f"Environment projection has invalid {name}")

    resource_id = _required_text(projection, "resource_id")
    field_revision = _required_text(projection, "field_revision")
    environment_id = _required_text(projection, "environment_id")
    environment_revision = _required_text(projection, "environment_revision")
    world_id = _required_text(projection, "world_id")
    physical_step_id = _required_text(projection, "physical_step_id")
    frame_id = _required_text(projection, "frame_id")
    source_tick = _required_tick(projection, "source_causal_tick")
    target_tick = _required_tick(projection, "target_causal_tick")
    if target_tick != source_tick + 1:
        raise ValueError("Environment projection target tick must follow source tick")

    point = getattr(projection, "point_m", None)
    if (
        not isinstance(point, tuple)
        or len(point) != 3
        or any(
            isinstance(component, bool)
            or not isinstance(component, (int, float))
            or not math.isfinite(component)
            for component in point
        )
    ):
        raise ValueError("Environment projection point_m must be three finite metres")
    value = getattr(projection, "value", None)
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or not 0.0 <= value <= 1.0
    ):
        raise ValueError("Environment projection value must be within [0, 1]")

    source_digest = _required_text(projection, "source_owner_checkpoint_sha256")
    if len(source_digest) != 64 or any(char not in "0123456789abcdef" for char in source_digest):
        raise ValueError("Environment owner checkpoint digest must be lowercase SHA-256")

    environment_actor = ActorRef("environment", environment_id)
    family = SemanticFamily(
        authority=AuthorityDomain.ENVIRONMENT,
        path=("finite_scalar_field",),
        contract=SemanticContractRef(_FAMILY_ID, _FAMILY_REVISION),
    )
    subject = SubjectScope(
        kind=_SUBJECT_TYPE,
        identities=(
            IdentityAssertion(
                IdentityRef("environment", environment_id, environment_actor),
                asserter=environment_actor,
            ),
            IdentityAssertion(
                IdentityRef(
                    "environment_resource",
                    resource_id,
                    environment_actor,
                    scope=environment_id,
                ),
                asserter=environment_actor,
            ),
        ),
    )
    claim_value: dict[str, object] = {
        "quantity_kind": "dimensionless_scalar_field",
        "value": float(value),
        "unit": "1",
        "valid_range": (0.0, 1.0),
        "reference_frame": frame_id,
        "point_m": tuple(float(component) for component in point),
    }
    claim = SemanticClaim(
        family=family,
        subject=subject,
        epistemic_kind="domain_derived",
        value=claim_value,
    )
    return SemanticObservation(
        claim=claim,
        acquisition=AcquisitionBasis(method=_ACQUISITION_BASIS),
        asserter=ActorRef("environment_owner_boundary", _ASSERTER),
        producer=ActorRef("environment_projection", _PRODUCER),
        domain_time=(
            DomainTimeRef(AuthorityDomain.ENVIRONMENT, "environment_revision", environment_revision),
            DomainTimeRef(AuthorityDomain.ENVIRONMENT, "field_revision", field_revision),
        ),
        context_time=(
            DomainTimeRef(AuthorityDomain.WORLD, "world_source_causal_tick", source_tick),
            DomainTimeRef(AuthorityDomain.WORLD, "world_target_causal_tick", target_tick),
        ),
        lineage=Lineage(
            parents=(LineageSourceRef("owner_checkpoint_sha256", source_digest),),
            transformation=TransformationRef(
                "environment.finite_scalar_field.project_observation",
                _FAMILY_REVISION,
                effective_configuration=(
                    ("field_revision", field_revision),
                    ("environment_revision", environment_revision),
                    ("frame_id", frame_id),
                    ("physical_step_id", physical_step_id),
                    ("world_id", world_id),
                ),
            ),
        ),
    )


def _required_text(source: _FiniteScalarFieldProjection, name: str) -> str:
    value = getattr(source, name, None)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Environment projection {name} must be non-empty text")
    return value.strip()


def _required_tick(source: _FiniteScalarFieldProjection, name: str) -> int:
    value = getattr(source, name, None)
    if type(value) is not int or value < 0:
        raise ValueError(f"Environment projection {name} must be a non-negative integer")
    return value


__all__ = ["environment_finite_scalar_field_observation"]

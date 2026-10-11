from __future__ import annotations

from types import SimpleNamespace

import pytest

from observation import ObservationPlane, environment_finite_scalar_field_observation
from observation.semantic import AuthorityDomain


def _projection(**overrides: object) -> SimpleNamespace:
    values: dict[str, object] = {
        "semantic_family_id": "biopeia.environment.finite-scalar-field",
        "semantic_revision": "1",
        "semantic_authority": "ENVIRONMENT",
        "epistemic_basis": "DOMAIN_DERIVED",
        "acquisition_basis": "environment_field_evaluation",
        "semantic_asserter": "environment.identified_finite_scalar_field",
        "semantic_producer": (
            "environment.identified_finite_scalar_field.project_observation"
        ),
        "quantity_kind": "dimensionless_scalar_field",
        "unit": "1",
        "valid_range": (0.0, 1.0),
        "resource_id": "resource.1",
        "field_revision": "field.rev-1",
        "environment_id": "environment.1",
        "environment_revision": "environment.rev-4",
        "world_id": "world.1",
        "source_causal_tick": 9,
        "target_causal_tick": 10,
        "physical_step_id": "physical-step.9",
        "frame_id": "environment-local",
        "point_m": (1.0, 2.0, 3.0),
        "value": 0.25,
        "source_owner_checkpoint_sha256": "a" * 64,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_environment_field_projection_maps_to_owner_authorized_claim() -> None:
    observation = environment_finite_scalar_field_observation(_projection())

    assert observation.authority is AuthorityDomain.ENVIRONMENT
    assert observation.family.qualified_name == "environment.finite_scalar_field"
    assert observation.family.contract.contract_id == (
        "biopeia.environment.finite-scalar-field"
    )
    assert observation.family.contract.revision == "1"
    assert observation.claim.epistemic_kind == "domain_derived"
    assert observation.claim.value == {
        "quantity_kind": "dimensionless_scalar_field",
        "value": 0.25,
        "unit": "1",
        "valid_range": (0.0, 1.0),
        "reference_frame": "environment-local",
        "point_m": (1.0, 2.0, 3.0),
    }
    assert observation.domain_time[0].domain is AuthorityDomain.ENVIRONMENT
    assert observation.domain_time[0].value == "environment.rev-4"
    assert observation.domain_time[1].value == "field.rev-1"
    assert [time.kind for time in observation.context_time] == [
        "world_source_causal_tick",
        "world_target_causal_tick",
    ]
    assert [time.value for time in observation.context_time] == [9, 10]
    assert all(time.domain is AuthorityDomain.WORLD for time in observation.context_time)
    resource_identity = observation.claim.subject.identities[1].identity
    assert resource_identity.kind == "environment_resource"
    assert resource_identity.scope == "environment.1"
    assert resource_identity.lifetime is None
    assert observation.lineage.parents[0].reference == "a" * 64
    assert observation.lineage.transformation is not None
    assert observation.lineage.transformation.effective_configuration == (
        ("field_revision", "field.rev-1"),
        ("environment_revision", "environment.rev-4"),
        ("frame_id", "environment-local"),
        ("physical_step_id", "physical-step.9"),
        ("world_id", "world.1"),
    )
    assert observation.asserter.identifier == "environment.identified_finite_scalar_field"
    assert observation.producer.identifier.endswith("project_observation")


def test_environment_field_observation_can_be_delivered_without_changing_authority() -> None:
    plane = ObservationPlane()
    observation = environment_finite_scalar_field_observation(_projection())

    sequence = plane.publish(observation)
    message = plane.current_messages()[0]

    assert sequence == message.sequence
    assert message.observation.authority is AuthorityDomain.ENVIRONMENT
    assert message.observation.claim.subject.identities[1].identity.value == "resource.1"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("semantic_authority", "WORLD"),
        ("semantic_family_id", "unapproved.family"),
        ("unit", "m"),
        ("target_causal_tick", 11),
        ("value", float("nan")),
        ("source_owner_checkpoint_sha256", "not-a-digest"),
    ],
)
def test_environment_projection_rejects_unapproved_or_invalid_contract_data(
    field: str, value: object
) -> None:
    with pytest.raises(ValueError):
        environment_finite_scalar_field_observation(_projection(**{field: value}))

from __future__ import annotations

from types import SimpleNamespace

import pytest

from observation import ObservationPlane, embodiment_body_pose_observation
from observation.semantic import AuthorityDomain


def _projection(**overrides: object) -> SimpleNamespace:
    pose = SimpleNamespace(
        body_id="body.1",
        reference_frame="world",
        body_frame="body.base",
        position_m=(1.0, 2.0, 3.0),
        orientation_xyzw=(0.0, 0.0, 0.0, 1.0),
        sample_kind="initial_state",
        sample_value="genesis",
        contract_revision="v1",
    )
    values: dict[str, object] = {
        "world_id": "world.1",
        "causal_tick": 0,
        "body_id": "body.1",
        "embodiment_episode_id": "episode.1",
        "morphology_revision": "morphology.rev-1",
        "source_state_sha256": "a" * 64,
        "pose": pose,
        "last_physical_step_id": None,
        "last_physical_step_source_tick": None,
        "environment_revision": None,
        "solver_config_revision": None,
        "physical_step_correlation": None,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_body_pose_owner_projection_maps_to_one_authoritative_claim() -> None:
    observation = embodiment_body_pose_observation(_projection())

    assert observation.authority is AuthorityDomain.EMBODIMENT
    assert observation.family.qualified_name == "embodiment.body_pose"
    assert observation.family.contract.contract_id == "embodiment.body_pose"
    assert observation.family.contract.revision == "v1"
    assert observation.claim.epistemic_kind == "authoritative_state"
    assert observation.claim.value == {
        "position": {"value": (1.0, 2.0, 3.0), "unit": "m"},
        "orientation": {
            "value_xyzw": (0.0, 0.0, 0.0, 1.0),
            "representation": "unit_quaternion_xyzw",
            "convention": "right_handed_hamilton_q_v_q_conjugate",
        },
        "reference_frame": "world",
        "body_frame": "body.base",
    }
    assert [item.identity.kind for item in observation.claim.subject.identities] == [
        "body",
        "embodiment_episode",
        "morphology_revision",
    ]
    assert observation.domain_time == ()
    assert [(time.kind, time.value) for time in observation.context_time] == [
        ("world_causal_tick", 0)
    ]
    assert observation.lineage.parents[0].reference == "a" * 64
    assert observation.asserter.identifier == "embodiment_owner_boundary"
    assert observation.producer.identifier == "embodiment_owner_projection"


def test_body_pose_observation_can_be_passively_delivered_without_authority_change() -> None:
    plane = ObservationPlane()
    observation = embodiment_body_pose_observation(_projection())

    sequence = plane.publish(observation)

    assert sequence == plane.current_messages()[0].sequence
    assert plane.current_messages()[0].observation.authority is AuthorityDomain.EMBODIMENT


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("body_id", "body.other"),
        ("embodiment_episode_id", ""),
        ("morphology_revision", ""),
        ("source_state_sha256", "not-a-digest"),
        ("causal_tick", True),
    ],
)
def test_body_pose_projection_rejects_missing_or_invalid_identity_and_provenance(
    field: str, value: object
) -> None:
    with pytest.raises(ValueError):
        embodiment_body_pose_observation(_projection(**{field: value}))


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("reference_frame", ""),
        ("body_frame", ""),
        ("contract_revision", "v2"),
        ("position_m", (1.0, float("nan"), 3.0)),
        ("orientation_xyzw", (0.0, 0.0, 1.0, 1.0)),
    ],
)
def test_body_pose_projection_rejects_invalid_frame_revision_or_pose(
    field: str, value: object
) -> None:
    projection = _projection()
    pose = vars(projection.pose)
    pose[field] = value
    projection.pose = SimpleNamespace(**pose)

    with pytest.raises(ValueError):
        embodiment_body_pose_observation(projection)


def test_physics_step_pose_requires_complete_matching_correlation() -> None:
    projection = _projection()
    projection.pose = SimpleNamespace(
        **{
            **vars(projection.pose),
            "sample_kind": "physics_step",
            "sample_value": "step.0",
        }
    )
    projection.causal_tick = 1
    projection.last_physical_step_id = "step.0"
    projection.last_physical_step_source_tick = 0
    projection.environment_revision = "environment.rev-2"
    projection.solver_config_revision = "solver.rev-3"
    projection.physical_step_correlation = SimpleNamespace(
        world_id="world.1",
        causal_tick=0,
        physical_step_id="step.0",
        body_id="body.1",
        embodiment_episode_id="episode.1",
        morphology_revision="morphology.rev-1",
        environment_revision="environment.rev-2",
        solver_config_revision="solver.rev-3",
    )

    observation = embodiment_body_pose_observation(projection)

    assert observation.context_time[0].value == 1
    assert observation.lineage.transformation is not None
    assert ("physical_step_id", "step.0") in (
        observation.lineage.transformation.effective_configuration
    )

    projection.physical_step_correlation.body_id = "body.other"
    with pytest.raises(ValueError, match="inconsistent body_id"):
        embodiment_body_pose_observation(projection)

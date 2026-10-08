"""First real semantic-observation vertical: Physics3D Body Pose -> plane."""

from __future__ import annotations

from lab.observation.bus import ObservationBus
from lab.observation.physics3d import Physics3DObservationBridge
from lab.observation.plane import ObservationPlane


def _pose_state(*, include_semantics: bool) -> dict[str, object]:
    state: dict[str, object] = {
        "body_kind": "crawler-v1",
        "body_id": "body.test.1",
        "base_position": [1.0, 2.0, 0.5],
        "base_orientation": [0.0, 0.0, 0.0, 1.0],
        "links": [],
        "joints": [],
    }
    if include_semantics:
        state["body_pose_semantics"] = {
            "position_unit": "m",
            "handedness": "right",
            "up_axis": "+z",
            "orientation": "xyzw",
            "reference_frame": "physics3d.world",
            "body_frame": "body.root",
            "contract_revision": "v1",
        }
    return state


def test_conforming_pose_frame_reaches_semantic_observation_plane() -> None:
    plane = ObservationPlane()
    bridge = Physics3DObservationBridge(
        ObservationBus(),
        observation_plane=plane,
    )

    bridge.publish_pose_frame(
        physical_state=_pose_state(include_semantics=True),
        tick=12,
        substep_index=3,
        physics_step=44,
        simulation_time_s=0.22,
        tick_simulation_span_s=0.005,
    )

    current = plane.current(family="embodiment.body_pose")
    assert len(current) == 1

    observation = current[0]
    sample = observation.claim.value
    assert observation.authority.value == "embodiment"
    assert observation.family.qualified_name == "embodiment.body_pose"
    assert sample.body_id == "body.test.1"
    assert sample.position_m == (1.0, 2.0, 0.5)
    assert sample.orientation_xyzw == (0.0, 0.0, 0.0, 1.0)
    assert sample.reference_frame == "physics3d.world"
    assert observation.domain_time[0].kind == "physics_step"
    assert observation.domain_time[0].value == 44
    assert observation.acquisition.measurement_source is not None
    assert observation.acquisition.measurement_source.identifier == "physics3d.mujoco"


def test_implicit_units_fail_closed_and_do_not_enter_semantic_plane() -> None:
    plane = ObservationPlane()
    bridge = Physics3DObservationBridge(
        ObservationBus(),
        observation_plane=plane,
    )

    bridge.publish_pose_frame(
        physical_state=_pose_state(include_semantics=False),
        tick=12,
        substep_index=3,
        physics_step=44,
        simulation_time_s=0.22,
        tick_simulation_span_s=0.005,
    )

    assert plane.current(family="embodiment.body_pose") == ()


def test_noncanonical_unit_fails_closed() -> None:
    plane = ObservationPlane()
    state = _pose_state(include_semantics=True)
    semantics = dict(state["body_pose_semantics"])  # type: ignore[arg-type]
    semantics["position_unit"] = "cm"
    state["body_pose_semantics"] = semantics
    bridge = Physics3DObservationBridge(
        ObservationBus(),
        observation_plane=plane,
    )

    bridge.publish_pose_frame(
        physical_state=state,
        tick=12,
        substep_index=3,
        physics_step=44,
        simulation_time_s=0.22,
        tick_simulation_span_s=0.005,
    )

    assert plane.current(family="embodiment.body_pose") == ()


def test_plane_materializes_latest_pose_per_subject() -> None:
    plane = ObservationPlane()
    bridge = Physics3DObservationBridge(
        ObservationBus(),
        observation_plane=plane,
    )
    state = _pose_state(include_semantics=True)

    bridge.publish_pose_frame(
        physical_state=state,
        tick=12,
        substep_index=3,
        physics_step=44,
        simulation_time_s=0.22,
        tick_simulation_span_s=0.005,
    )
    state["base_position"] = [2.0, 3.0, 0.5]
    bridge.publish_pose_frame(
        physical_state=state,
        tick=13,
        substep_index=3,
        physics_step=45,
        simulation_time_s=0.225,
        tick_simulation_span_s=0.005,
    )

    current = plane.current(family="embodiment.body_pose")
    assert len(current) == 1
    assert current[0].claim.value.position_m == (2.0, 3.0, 0.5)
    assert current[0].domain_time[0].value == 45


def test_plane_is_bounded() -> None:
    from embodiment.observation import BodyPoseSample
    from lab.observation.body_pose import body_pose_observation

    plane = ObservationPlane(max_entries=2)
    for index in range(3):
        plane.publish(
            body_pose_observation(
                BodyPoseSample(
                    body_id=f"body.{index}",
                    reference_frame="physics3d.world",
                    body_frame="body.root",
                    position_m=(float(index), 0.0, 0.0),
                    orientation_xyzw=(0.0, 0.0, 0.0, 1.0),
                    sample_kind="physics_step",
                    sample_value=index,
                )
            )
        )

    current = plane.current(family="embodiment.body_pose")
    assert len(current) == 2
    assert [item.claim.value.body_id for item in current] == ["body.1", "body.2"]

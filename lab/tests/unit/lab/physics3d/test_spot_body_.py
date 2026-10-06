import pytest

from embodiment.physics3d.articulated import build_articulated_urdf
from embodiment.physics3d.bodies import CRAWLER_V1, SPOT_INSPIRED_V1
from embodiment.physics3d.spot import SPOT_INSPIRED_SPEC, SpotInspiredPhysics


def test_spot_inspired_body_is_separate_from_existing_crawler() -> None:
    assert CRAWLER_V1.body_kind == "crawler-v1"
    assert SPOT_INSPIRED_V1.body_kind == "spot-inspired-v1"
    assert SPOT_INSPIRED_V1.motor_dof == 12
    assert SPOT_INSPIRED_V1.effector_count == 24
    assert len(SPOT_INSPIRED_SPEC.contact_link_names) == 16
    assert len(SPOT_INSPIRED_SPEC.fixed_link_topology) == 4
    assert SPOT_INSPIRED_SPEC.spawn_height == 0.59


def test_spot_inspired_body_has_four_three_joint_legs_and_feet() -> None:
    for leg in ("front_left", "front_right", "rear_left", "rear_right"):
        assert {f"{leg}_{joint}" for joint in ("hip_abduction", "hip_pitch", "knee_pitch")} <= {
            joint.name for joint in SPOT_INSPIRED_SPEC.joint_specs
        }
        assert f"{leg}_foot" in SPOT_INSPIRED_SPEC.contact_link_names

    urdf = build_articulated_urdf(SPOT_INSPIRED_SPEC)
    assert urdf.count('type="revolute"') == 12
    assert urdf.count('type="fixed"') == 4


def test_spot_inspired_spawns_upright_with_all_four_feet_on_ground() -> None:
    pytest.importorskip("mujoco")
    from embodiment.physics3d.scene import PhysicsScene

    scene = PhysicsScene(timestep=1.0 / 240.0)
    scene.add_ground()
    SpotInspiredPhysics(scene)

    for leg in ("front_left", "front_right", "rear_left", "rear_right"):
        body_id = scene.name_to_id("body", f"body.{leg}_foot")
        geom_id = next(
            index
            for index, parent_id in enumerate(scene.model.geom_bodyid)
            if int(parent_id) == body_id
        )
        sole_height = scene.data.geom_xpos[geom_id, 2] - scene.model.geom_size[geom_id, 2]
        assert abs(float(sole_height)) < 1e-6
    assert scene.data.ncon > 0


def test_spot_runtime_starts_at_declared_pose_without_passive_settling() -> None:
    pytest.importorskip("mujoco")
    from lab.physics3d.runtime import Physics3DEmbodimentRuntime

    runtime = Physics3DEmbodimentRuntime(
        gui=False,
        body_kind="spot-inspired-v1",
        physics_substeps_per_tick=1,
    )
    try:
        position, orientation = runtime.apparatus.base_pose()
        linear, angular = runtime.apparatus.base_velocity()
        assert position[2] == pytest.approx(SPOT_INSPIRED_SPEC.spawn_height)
        assert orientation == pytest.approx((0.0, 0.0, 0.0, 1.0))
        assert linear == pytest.approx((0.0, 0.0, 0.0))
        assert angular == pytest.approx((0.0, 0.0, 0.0))
        assert runtime._settling_result is None
        runtime.step()
    finally:
        runtime.close()

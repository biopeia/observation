from __future__ import annotations

from embodiment.physics3d.articulated import build_articulated_urdf
from embodiment.physics3d.bodies import HEXAPOD_V1, ROBOTIC_ARM_V1
from embodiment.physics3d.hexapod import HEXAPOD_SPEC
from embodiment.physics3d.robotic_arm import ROBOTIC_ARM_SPEC


def test_hexapod_has_six_three_axis_legs_and_explicit_feet() -> None:
    assert HEXAPOD_SPEC.motor_dof == 18
    assert len(HEXAPOD_SPEC.joint_topology) == 18
    assert len(HEXAPOD_SPEC.contact_link_names) == 24
    for leg in (
        "front_left",
        "middle_left",
        "rear_left",
        "front_right",
        "middle_right",
        "rear_right",
    ):
        assert {f"{leg}_{joint}" for joint in ("coxa_yaw", "femur_pitch", "tibia_pitch")} <= {
            joint.name for joint in HEXAPOD_SPEC.joint_specs
        }
        assert f"{leg}_foot" in HEXAPOD_SPEC.contact_link_names
        assert any(item.child_link == f"{leg}_foot" for item in HEXAPOD_SPEC.fixed_link_topology)
        for segment in ("coxa", "femur", "tibia"):
            assert f"{leg}_{segment}" in HEXAPOD_SPEC.segments
    assert HEXAPOD_V1.motor_dof == 18
    assert len(HEXAPOD_V1.effector_ids) == 36


def test_hexapod_urdf_contains_18_revolute_joints_and_six_passive_feet() -> None:
    urdf = build_articulated_urdf(HEXAPOD_SPEC)
    assert urdf.count('type="revolute"') == 18
    assert urdf.count('type="fixed"') == 6
    assert all(
        f'link name="{name}_foot"' in urdf
        for name in (
            "front_left",
            "middle_left",
            "rear_left",
            "front_right",
            "middle_right",
            "rear_right",
        )
    )


def test_robotic_arm_is_six_axis_with_world_fixed_base_and_flange() -> None:
    assert ROBOTIC_ARM_SPEC.motor_dof == 6
    assert ROBOTIC_ARM_SPEC.fixed_base is True
    assert ROBOTIC_ARM_V1.motor_dof == 6
    assert ROBOTIC_ARM_SPEC.joint_specs[-1].name == "wrist_yaw"
    assert any(item.child_link == "tool_flange" for item in ROBOTIC_ARM_SPEC.fixed_link_topology)
    urdf = build_articulated_urdf(ROBOTIC_ARM_SPEC)
    assert urdf.count('type="revolute"') == 6
    assert 'name="tool_flange_fixed" type="fixed"' in urdf

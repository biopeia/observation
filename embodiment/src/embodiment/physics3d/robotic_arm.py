"""Physics3D constitution for a fixed-base six-axis articulated arm.

All dimensions and actuator values are provisional structural placeholders;
this model is not calibrated and makes no capability claim.
"""

from __future__ import annotations

import math

from embodiment.physics3d.articulated import (
    ArticulatedBodySpec,
    ArticulatedPhysics,
    FixedLinkTopology,
)
from embodiment.physics3d.mechanics import JointSpec, JointTopology, SegmentSpec


def _deg(value: float) -> float:
    return math.radians(value)


ROBOTIC_ARM_JOINT_SPECS = (
    JointSpec("base_yaw", (0, 0, 1), _deg(-170), _deg(170), 25.0, 2.0, 2.5),
    JointSpec("shoulder_pitch", (0, 1, 0), _deg(-120), _deg(120), 35.0, 2.5, 2.0),
    JointSpec("elbow_pitch", (0, 1, 0), _deg(-150), _deg(150), 25.0, 2.0, 2.5),
    JointSpec("wrist_roll", (1, 0, 0), _deg(-180), _deg(180), 8.0, 0.8, 3.0),
    JointSpec("wrist_pitch", (0, 1, 0), _deg(-120), _deg(120), 8.0, 0.8, 3.0),
    JointSpec("wrist_yaw", (1, 0, 0), _deg(-180), _deg(180), 5.0, 0.5, 3.0),
)

ROBOTIC_ARM_SEGMENTS = {
    "arm_base": SegmentSpec(5.0, (0.30, 0.30, 0.50), (0, 0, 0.25), (0.30, 0.42, 0.52, 1)),
    "upper_arm": SegmentSpec(2.0, (0.36, 0.12, 0.12), (0.18, 0, 0), (0.38, 0.62, 0.76, 1)),
    "forearm": SegmentSpec(1.4, (0.32, 0.10, 0.10), (0.16, 0, 0), (0.44, 0.70, 0.82, 1)),
    "wrist_1": SegmentSpec(0.45, (0.09, 0.09, 0.12), (0.06, 0, 0), (0.55, 0.76, 0.84, 1)),
    "wrist_2": SegmentSpec(0.35, (0.08, 0.08, 0.10), (0.05, 0, 0), (0.62, 0.80, 0.86, 1)),
    "wrist_3": SegmentSpec(0.25, (0.07, 0.07, 0.08), (0.04, 0, 0), (0.68, 0.83, 0.88, 1)),
    "tool_flange": SegmentSpec(0.15, (0.10, 0.10, 0.04), (0, 0, 0), (0.76, 0.86, 0.90, 1)),
}

ROBOTIC_ARM_TOPOLOGY = (
    JointTopology("base_yaw", "arm_base", "arm_yaw_carrier", (0, 0, 0.50)),
    JointTopology("shoulder_pitch", "arm_yaw_carrier", "upper_arm", (0, 0, 0)),
    JointTopology("elbow_pitch", "upper_arm", "forearm", (0.36, 0, 0)),
    JointTopology("wrist_roll", "forearm", "wrist_1", (0.32, 0, 0)),
    JointTopology("wrist_pitch", "wrist_1", "wrist_2", (0.12, 0, 0)),
    JointTopology("wrist_yaw", "wrist_2", "wrist_3", (0.10, 0, 0)),
)

ROBOTIC_ARM_SPEC = ArticulatedBodySpec(
    body_kind="robotic-arm-v1",
    state_schema_version=1,
    spawn_height=0.0,
    base_link_name="arm_base",
    joint_specs=ROBOTIC_ARM_JOINT_SPECS,
    joint_topology=ROBOTIC_ARM_TOPOLOGY,
    fixed_link_topology=(FixedLinkTopology("wrist_3", "tool_flange", (0.08, 0, 0)),),
    segments=ROBOTIC_ARM_SEGMENTS,
    contact_link_names=(
        "arm_base",
        "upper_arm",
        "forearm",
        "wrist_1",
        "wrist_2",
        "wrist_3",
        "tool_flange",
    ),
    structural_neighbour_names=(
        ("arm_base", "upper_arm"),
        ("upper_arm", "forearm"),
        ("forearm", "wrist_1"),
        ("wrist_1", "wrist_2"),
        ("wrist_2", "wrist_3"),
        ("wrist_3", "tool_flange"),
    ),
    fixed_base=True,
)


class RoboticArmPhysics(ArticulatedPhysics):
    SPEC = ROBOTIC_ARM_SPEC


__all__ = ["ROBOTIC_ARM_SPEC", "RoboticArmPhysics"]

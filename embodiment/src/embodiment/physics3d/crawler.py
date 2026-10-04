"""Physics3D constitution for the four-legged crawler body."""

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


# ---------------------------------------------------------------------------
# crawler-v1: four-limbed, low-centre-of-mass body; 3 DoF per limb.
# ---------------------------------------------------------------------------

CRAWLER_JOINT_SPECS: tuple[JointSpec, ...] = (
    JointSpec("front_left_hip_yaw", (0, 0, 1), _deg(-45), _deg(45), 12.0, 1.5, 5.0),
    JointSpec("front_left_hip_pitch", (0, 1, 0), _deg(-65), _deg(75), 18.0, 2.0, 5.0),
    JointSpec("front_left_knee_pitch", (0, 1, 0), _deg(-100), _deg(25), 14.0, 1.6, 6.0),
    JointSpec("front_right_hip_yaw", (0, 0, 1), _deg(-45), _deg(45), 12.0, 1.5, 5.0),
    JointSpec("front_right_hip_pitch", (0, 1, 0), _deg(-65), _deg(75), 18.0, 2.0, 5.0),
    JointSpec("front_right_knee_pitch", (0, 1, 0), _deg(-100), _deg(25), 14.0, 1.6, 6.0),
    JointSpec("rear_left_hip_yaw", (0, 0, 1), _deg(-45), _deg(45), 14.0, 1.5, 5.0),
    JointSpec("rear_left_hip_pitch", (0, 1, 0), _deg(-75), _deg(65), 20.0, 2.0, 5.0),
    JointSpec("rear_left_knee_pitch", (0, 1, 0), _deg(-25), _deg(100), 16.0, 1.6, 6.0),
    JointSpec("rear_right_hip_yaw", (0, 0, 1), _deg(-45), _deg(45), 14.0, 1.5, 5.0),
    JointSpec("rear_right_hip_pitch", (0, 1, 0), _deg(-75), _deg(65), 20.0, 2.0, 5.0),
    JointSpec("rear_right_knee_pitch", (0, 1, 0), _deg(-25), _deg(100), 16.0, 1.6, 6.0),
)

CRAWLER_SEGMENTS = {
    "body": SegmentSpec(10.0, (0.62, 0.34, 0.20), (0, 0, 0), (0.34, 0.46, 0.56, 1)),
    "front_left_upper": SegmentSpec(1.0, (0.10, 0.10, 0.28), (0, 0, -0.14), (0.30, 0.64, 0.76, 1)),
    "front_left_lower": SegmentSpec(0.7, (0.09, 0.09, 0.28), (0, 0, -0.14), (0.36, 0.72, 0.82, 1)),
    "front_left_foot": SegmentSpec(
        0.25, (0.16, 0.12, 0.06), (0, 0.03, -0.02), (0.40, 0.76, 0.84, 1)
    ),
    "front_right_upper": SegmentSpec(1.0, (0.10, 0.10, 0.28), (0, 0, -0.14), (0.82, 0.52, 0.26, 1)),
    "front_right_lower": SegmentSpec(0.7, (0.09, 0.09, 0.28), (0, 0, -0.14), (0.88, 0.60, 0.30, 1)),
    "front_right_foot": SegmentSpec(
        0.25, (0.16, 0.12, 0.06), (0, 0.03, -0.02), (0.92, 0.66, 0.34, 1)
    ),
    "rear_left_upper": SegmentSpec(1.2, (0.11, 0.11, 0.30), (0, 0, -0.15), (0.30, 0.64, 0.76, 1)),
    "rear_left_lower": SegmentSpec(0.8, (0.09, 0.09, 0.30), (0, 0, -0.15), (0.36, 0.72, 0.82, 1)),
    "rear_left_foot": SegmentSpec(
        0.28, (0.18, 0.13, 0.06), (0, -0.03, -0.02), (0.40, 0.76, 0.84, 1)
    ),
    "rear_right_upper": SegmentSpec(1.2, (0.11, 0.11, 0.30), (0, 0, -0.15), (0.82, 0.52, 0.26, 1)),
    "rear_right_lower": SegmentSpec(0.8, (0.09, 0.09, 0.30), (0, 0, -0.15), (0.88, 0.60, 0.30, 1)),
    "rear_right_foot": SegmentSpec(
        0.28, (0.18, 0.13, 0.06), (0, -0.03, -0.02), (0.92, 0.66, 0.34, 1)
    ),
}

CRAWLER_TOPOLOGY: tuple[JointTopology, ...] = (
    JointTopology("front_left_hip_yaw", "body", "fl_yaw_carrier", (-0.26, 0.15, 0.0)),
    JointTopology("front_left_hip_pitch", "fl_yaw_carrier", "front_left_upper", (0, 0, 0)),
    JointTopology("front_left_knee_pitch", "front_left_upper", "front_left_lower", (0, 0, -0.28)),
    JointTopology("front_right_hip_yaw", "body", "fr_yaw_carrier", (0.26, 0.15, 0.0)),
    JointTopology("front_right_hip_pitch", "fr_yaw_carrier", "front_right_upper", (0, 0, 0)),
    JointTopology(
        "front_right_knee_pitch", "front_right_upper", "front_right_lower", (0, 0, -0.28)
    ),
    JointTopology("rear_left_hip_yaw", "body", "rl_yaw_carrier", (-0.26, -0.15, 0.0)),
    JointTopology("rear_left_hip_pitch", "rl_yaw_carrier", "rear_left_upper", (0, 0, 0)),
    JointTopology("rear_left_knee_pitch", "rear_left_upper", "rear_left_lower", (0, 0, -0.30)),
    JointTopology("rear_right_hip_yaw", "body", "rr_yaw_carrier", (0.26, -0.15, 0.0)),
    JointTopology("rear_right_hip_pitch", "rr_yaw_carrier", "rear_right_upper", (0, 0, 0)),
    JointTopology("rear_right_knee_pitch", "rear_right_upper", "rear_right_lower", (0, 0, -0.30)),
)

# Passive foot pads are fixed to each distal lower link; they add geometry, not
# actuated degrees of freedom.
CRAWLER_SPEC = ArticulatedBodySpec(
    body_kind="crawler-v1",
    state_schema_version=3,
    spawn_height=0.62,
    base_link_name="body",
    joint_specs=CRAWLER_JOINT_SPECS,
    joint_topology=CRAWLER_TOPOLOGY,
    fixed_link_topology=(
        FixedLinkTopology("front_left_lower", "front_left_foot", (0, 0, -0.28)),
        FixedLinkTopology("front_right_lower", "front_right_foot", (0, 0, -0.28)),
        FixedLinkTopology("rear_left_lower", "rear_left_foot", (0, 0, -0.30)),
        FixedLinkTopology("rear_right_lower", "rear_right_foot", (0, 0, -0.30)),
    ),
    segments=CRAWLER_SEGMENTS,
    contact_link_names=(
        "front_left_upper",
        "front_left_lower",
        "front_left_foot",
        "front_right_upper",
        "front_right_lower",
        "front_right_foot",
        "rear_left_upper",
        "rear_left_lower",
        "rear_left_foot",
        "rear_right_upper",
        "rear_right_lower",
        "rear_right_foot",
    ),
    structural_neighbour_names=(
        ("body", "front_left_upper"),
        ("front_left_upper", "front_left_lower"),
        ("body", "front_right_upper"),
        ("front_right_upper", "front_right_lower"),
        ("body", "rear_left_upper"),
        ("rear_left_upper", "rear_left_lower"),
        ("body", "rear_right_upper"),
        ("rear_right_upper", "rear_right_lower"),
    ),
)


class CrawlerPhysics(ArticulatedPhysics):
    SPEC = CRAWLER_SPEC


__all__ = ["CRAWLER_SPEC", "CrawlerPhysics"]

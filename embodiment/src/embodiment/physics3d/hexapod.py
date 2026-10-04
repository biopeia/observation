"""Physics3D constitution for a six-legged, 18-DoF hexapod.

Dimensions and actuator values are structural placeholders, not calibrated
properties or evidence of locomotion capability.
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


_LEGS = (
    ("front_left", 0.29, 0.18),
    ("middle_left", 0.0, 0.18),
    ("rear_left", -0.29, 0.18),
    ("front_right", 0.29, -0.18),
    ("middle_right", 0.0, -0.18),
    ("rear_right", -0.29, -0.18),
)

_joints: list[JointSpec] = []
_topology: list[JointTopology] = []
_fixed: list[FixedLinkTopology] = []
_segments: dict[str, SegmentSpec] = {
    "body": SegmentSpec(8.0, (0.72, 0.38, 0.18), (0, 0, 0), (0.34, 0.46, 0.56, 1)),
}
_contacts: list[str] = []
_neighbours: list[tuple[str, str]] = []

for _name, _x, _y in _LEGS:
    _coxa, _femur, _tibia, _foot = (
        f"{_name}_{part}" for part in ("coxa", "femur", "tibia", "foot")
    )
    _yaw, _hip, _knee = (f"{_name}_{part}" for part in ("coxa_yaw", "femur_pitch", "tibia_pitch"))
    _joints.extend(
        (
            JointSpec(_yaw, (0, 0, 1), _deg(-45), _deg(45), 10.0, 1.2, 4.0),
            JointSpec(_hip, (0, 1, 0), _deg(-70), _deg(70), 14.0, 1.6, 4.0),
            JointSpec(_knee, (0, 1, 0), _deg(-100), _deg(25), 12.0, 1.4, 5.0),
        )
    )
    _topology.extend(
        (
            JointTopology(_yaw, "body", _coxa, (_x, _y, 0)),
            JointTopology(_hip, _coxa, _femur, (0, 0.12 if _y > 0 else -0.12, 0)),
            JointTopology(_knee, _femur, _tibia, (0, 0, -0.22)),
        )
    )
    _segments[_coxa] = SegmentSpec(
        0.35, (0.10, 0.22, 0.10), (0, 0.11 if _y > 0 else -0.11, 0), (0.38, 0.65, 0.74, 1)
    )
    _segments[_femur] = SegmentSpec(0.55, (0.10, 0.10, 0.22), (0, 0, -0.11), (0.42, 0.72, 0.80, 1))
    _segments[_tibia] = SegmentSpec(0.40, (0.09, 0.09, 0.20), (0, 0, -0.10), (0.46, 0.74, 0.82, 1))
    _segments[_foot] = SegmentSpec(
        0.18, (0.14, 0.12, 0.06), (0, 0.02, -0.02), (0.50, 0.77, 0.82, 1)
    )
    _fixed.append(FixedLinkTopology(_tibia, _foot, (0, 0, -0.20)))
    _contacts.extend((_coxa, _femur, _tibia, _foot))
    _neighbours.extend((("body", _coxa), (_coxa, _femur), (_femur, _tibia), (_tibia, _foot)))

HEXAPOD_SPEC = ArticulatedBodySpec(
    body_kind="hexapod-v1",
    state_schema_version=1,
    spawn_height=0.48,
    base_link_name="body",
    joint_specs=tuple(_joints),
    joint_topology=tuple(_topology),
    fixed_link_topology=tuple(_fixed),
    segments=_segments,
    contact_link_names=tuple(_contacts),
    structural_neighbour_names=tuple(_neighbours),
)


class HexapodPhysics(ArticulatedPhysics):
    SPEC = HEXAPOD_SPEC


__all__ = ["HEXAPOD_SPEC", "HexapodPhysics"]

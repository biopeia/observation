"""Spot-inspired quadruped apparatus, based on public Spot anatomy data.

The 12 opaque actuators map to three rotational joints per leg. Geometry and
actuator values are simulation approximations, not a calibrated Spot model.
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
    ("front_left", 0.35, 0.16),
    ("front_right", 0.35, -0.16),
    ("rear_left", -0.35, 0.16),
    ("rear_right", -0.35, -0.16),
)
_joints: list[JointSpec] = []
_topology: list[JointTopology] = []
_fixed: list[FixedLinkTopology] = []
_segments: dict[str, SegmentSpec] = {
    # Approximate the documented 1.1 x 0.5 m overall footprint; this is not
    # Boston Dynamics CAD geometry or mass distribution.
    "body": SegmentSpec(18.0, (0.78, 0.34, 0.20), (0, 0, 0), (0.88, 0.68, 0.12, 1)),
}
_contacts: list[str] = []
_neighbours: list[tuple[str, str]] = []

for _name, _x, _y in _LEGS:
    _hip, _upper, _lower, _foot = (
        f"{_name}_{part}" for part in ("hip_carrier", "upper", "lower", "foot")
    )
    _abduction, _hip_pitch, _knee = (
        f"{_name}_{part}" for part in ("hip_abduction", "hip_pitch", "knee_pitch")
    )
    # Three actuated joints per leg, matching Spot's documented 12-DoF layout
    # (three motors in each of four legs); torque values are simulator choices.
    _joints.extend(
        (
            JointSpec(_abduction, (1, 0, 0), _deg(-45), _deg(45), 30.0, 2.0, 8.0),
            JointSpec(_hip_pitch, (0, 1, 0), _deg(-90), _deg(90), 30.0, 2.0, 8.0),
            JointSpec(_knee, (0, 1, 0), _deg(-135), _deg(45), 30.0, 2.0, 8.0),
        )
    )
    _topology.extend(
        (
            JointTopology(_abduction, "body", _hip, (_x, _y, 0)),
            JointTopology(_hip_pitch, _hip, _upper, (0, 0, 0)),
            JointTopology(_knee, _upper, _lower, (0, 0, -0.27)),
        )
    )
    _segments[_hip] = SegmentSpec(0.8, (0.16, 0.12, 0.12), (0, 0, 0), (0.16, 0.17, 0.18, 1))
    _segments[_upper] = SegmentSpec(1.2, (0.12, 0.12, 0.27), (0, 0, -0.135), (0.16, 0.17, 0.18, 1))
    _segments[_lower] = SegmentSpec(0.9, (0.10, 0.10, 0.27), (0, 0, -0.135), (0.16, 0.17, 0.18, 1))
    _segments[_foot] = SegmentSpec(0.30, (0.16, 0.11, 0.06), (0, 0, -0.02), (0.08, 0.09, 0.10, 1))
    _fixed.append(FixedLinkTopology(_lower, _foot, (0, 0, -0.27)))
    _contacts.extend((_hip, _upper, _lower, _foot))
    # These simplified boxes overlap at the chassis even though the links are
    # separated in the kinematic tree. Exclude that modeled self-contact so it
    # cannot saturate the upper-link contact receptors before world contact.
    _neighbours.extend(
        (("body", _hip), ("body", _upper), (_hip, _upper), (_upper, _lower), (_lower, _foot))
    )

SPOT_INSPIRED_SPEC = ArticulatedBodySpec(
    body_kind="spot-inspired-v1",
    state_schema_version=1,
    # With zero joint angles, the 0.27 m upper/lower links and passive foot
    # place the sole at approximately ground level in the default pose.
    spawn_height=0.59,
    base_link_name="body",
    joint_specs=tuple(_joints),
    joint_topology=tuple(_topology),
    fixed_link_topology=tuple(_fixed),
    segments=_segments,
    contact_link_names=tuple(_contacts),
    structural_neighbour_names=tuple(_neighbours),
)


class SpotInspiredPhysics(ArticulatedPhysics):
    SPEC = SPOT_INSPIRED_SPEC


__all__ = ["SPOT_INSPIRED_SPEC", "SpotInspiredPhysics"]

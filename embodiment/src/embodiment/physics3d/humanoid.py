"""Hard-limited anthropomorphic Physics3D body described as URDF, simulated by MuJoCo.

Human-readable anatomy exists only inside this apparatus module. Symbiont sees
only opaque rec.N/eff.N channels. The URDF is generated from the canonical
constitution at runtime so joint ranges are mechanical constraints owned by
Bullet, not controller suggestions.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

from embodiment.physics3d.articulated import ArticulatedBodySpec, ArticulatedPhysics
from embodiment.physics3d.mechanics import (
    CARRIER_MASS,
    END_RANGE_DAMPING,
    END_RANGE_MARGIN,
    END_RANGE_STIFFNESS,
    MECHANICAL_LIMIT_GUARD,
    JointLimit,
    JointSpec,
    JointTopology,
    SegmentSpec,
)

BODY_KIND = "anthropomorphic-v6"
# 7: the state carries the engine state needed to continue exactly (ADR-0066).
BODY_STATE_SCHEMA_VERSION = 7
PHYSICS_CONSTRAINT_ERP = 0.8
PASSIVE_TONE_STIFFNESS_FRACTION = 0.55
PASSIVE_TONE_TORQUE_CAP_FRACTION = 0.45
MOTOR_DOF = 31
SOMATIC_REGION_COUNT = 15
GLOBAL_KINEMATIC_RECEPTORS = 10
ECOLOGICAL_RECEPTORS = 1
PHYSICAL_RECEPTOR_COUNT = (
    MOTOR_DOF * 2 + GLOBAL_KINEMATIC_RECEPTORS + SOMATIC_REGION_COUNT * 2 + ECOLOGICAL_RECEPTORS
)
INTEROCEPTIVE_RECEPTOR_COUNT = 4
TOTAL_RECEPTOR_COUNT = PHYSICAL_RECEPTOR_COUNT + INTEROCEPTIVE_RECEPTOR_COUNT


def physical_receptor_contract_ids() -> tuple[str, ...]:
    return tuple(f"rec.{i}" for i in range(PHYSICAL_RECEPTOR_COUNT))


def interoceptive_receptor_contract_ids() -> tuple[str, ...]:
    return tuple(
        f"rec.{i}"
        for i in range(
            PHYSICAL_RECEPTOR_COUNT,
            PHYSICAL_RECEPTOR_COUNT + INTEROCEPTIVE_RECEPTOR_COUNT,
        )
    )


def receptor_contract_ids() -> tuple[str, ...]:
    return tuple(f"rec.{i}" for i in range(TOTAL_RECEPTOR_COUNT))


def effector_contract_ids(motor_count: int = MOTOR_DOF) -> tuple[str, ...]:
    if motor_count < 1:
        raise ValueError("motor_count must be positive")
    return tuple(f"eff.{i}" for i in range(motor_count * 2))


def _deg(value: float) -> float:
    return math.radians(value)


JOINT_SPECS: tuple[JointSpec, ...] = (
    JointSpec("trunk_yaw", (0.0, 0.0, 1.0), _deg(-45), _deg(45), 18.0, 2.8, 3.5),
    JointSpec("trunk_roll", (0.0, 1.0, 0.0), _deg(-30), _deg(30), 18.0, 2.8, 3.5),
    JointSpec("trunk_pitch", (1.0, 0.0, 0.0), _deg(-35), _deg(55), 22.0, 3.2, 3.5),
    JointSpec("neck_yaw", (0.0, 0.0, 1.0), _deg(-70), _deg(70), 3.0, 0.45, 4.5),
    JointSpec("neck_pitch", (1.0, 0.0, 0.0), _deg(-45), _deg(55), 3.0, 0.45, 4.5),
    JointSpec("left_shoulder_yaw", (0.0, 0.0, 1.0), _deg(-90), _deg(90), 9.0, 1.2, 5.0),
    JointSpec("left_shoulder_roll", (0.0, 1.0, 0.0), _deg(-30), _deg(160), 10.0, 1.3, 5.0),
    JointSpec("left_shoulder_pitch", (1.0, 0.0, 0.0), _deg(-45), _deg(170), 10.0, 1.3, 5.0),
    JointSpec("left_elbow_pitch", (1.0, 0.0, 0.0), _deg(0), _deg(145), 7.0, 0.9, 6.0),
    JointSpec("left_forearm_roll", (0.0, 0.0, 1.0), _deg(-80), _deg(80), 3.5, 0.45, 7.0),
    JointSpec("left_wrist_pitch", (1.0, 0.0, 0.0), _deg(-60), _deg(75), 2.5, 0.35, 7.0),
    JointSpec("left_wrist_deviation", (0.0, 1.0, 0.0), _deg(-20), _deg(35), 2.0, 0.35, 7.0),
    JointSpec("right_shoulder_yaw", (0.0, 0.0, 1.0), _deg(-90), _deg(90), 9.0, 1.2, 5.0),
    JointSpec("right_shoulder_roll", (0.0, 1.0, 0.0), _deg(-160), _deg(30), 10.0, 1.3, 5.0),
    JointSpec("right_shoulder_pitch", (1.0, 0.0, 0.0), _deg(-45), _deg(170), 10.0, 1.3, 5.0),
    JointSpec("right_elbow_pitch", (1.0, 0.0, 0.0), _deg(0), _deg(145), 7.0, 0.9, 6.0),
    JointSpec("right_forearm_roll", (0.0, 0.0, 1.0), _deg(-80), _deg(80), 3.5, 0.45, 7.0),
    JointSpec("right_wrist_pitch", (1.0, 0.0, 0.0), _deg(-60), _deg(75), 2.5, 0.35, 7.0),
    JointSpec("right_wrist_deviation", (0.0, 1.0, 0.0), _deg(-35), _deg(20), 2.0, 0.35, 7.0),
    JointSpec("left_hip_yaw", (0.0, 0.0, 1.0), _deg(-40), _deg(40), 22.0, 3.0, 4.0),
    JointSpec("left_hip_roll", (0.0, 1.0, 0.0), _deg(-20), _deg(40), 24.0, 3.2, 4.0),
    JointSpec("left_hip_pitch", (1.0, 0.0, 0.0), _deg(-20), _deg(125), 28.0, 3.5, 4.0),
    JointSpec("left_knee_pitch", (1.0, 0.0, 0.0), _deg(0), _deg(140), 24.0, 2.6, 5.0),
    JointSpec("left_ankle_pitch", (1.0, 0.0, 0.0), _deg(-20), _deg(45), 12.0, 1.8, 5.0),
    JointSpec("left_ankle_roll", (0.0, 1.0, 0.0), _deg(-15), _deg(15), 10.0, 1.6, 5.0),
    JointSpec("right_hip_yaw", (0.0, 0.0, 1.0), _deg(-40), _deg(40), 22.0, 3.0, 4.0),
    JointSpec("right_hip_roll", (0.0, 1.0, 0.0), _deg(-40), _deg(20), 24.0, 3.2, 4.0),
    JointSpec("right_hip_pitch", (1.0, 0.0, 0.0), _deg(-20), _deg(125), 28.0, 3.5, 4.0),
    JointSpec("right_knee_pitch", (1.0, 0.0, 0.0), _deg(0), _deg(140), 24.0, 2.6, 5.0),
    JointSpec("right_ankle_pitch", (1.0, 0.0, 0.0), _deg(-20), _deg(45), 12.0, 1.8, 5.0),
    JointSpec("right_ankle_roll", (0.0, 1.0, 0.0), _deg(-15), _deg(15), 10.0, 1.6, 5.0),
)
if len(JOINT_SPECS) != MOTOR_DOF:
    raise RuntimeError("anthropomorphic-v6 must expose exactly 31 motor DoF")

JOINT_LIMITS: dict[int, JointLimit] = {
    ordinal: JointLimit(spec.lower, spec.upper) for ordinal, spec in enumerate(JOINT_SPECS)
}
JOINT_AXES: dict[int, tuple[float, float, float]] = {
    ordinal: spec.axis for ordinal, spec in enumerate(JOINT_SPECS)
}


_LEFT = (0.22, 0.60, 0.76, 1.0)
_LEFT2 = (0.28, 0.70, 0.84, 1.0)
_RIGHT = (0.85, 0.50, 0.22, 1.0)
_RIGHT2 = (0.92, 0.62, 0.28, 1.0)


SEGMENTS: dict[str, SegmentSpec] = {
    "pelvis": SegmentSpec(4.0, (0.32, 0.20, 0.22), (0.0, 0.0, 0.0), (0.28, 0.44, 0.58, 1.0)),
    "torso": SegmentSpec(12.2, (0.40, 0.22, 0.50), (0.0, 0.0, 0.21), (0.32, 0.50, 0.65, 1.0)),
    "head": SegmentSpec(2.0, (0.21, 0.21, 0.23), (0.0, 0.0, 0.12), (0.55, 0.68, 0.76, 1.0)),
    "left_upper_arm": SegmentSpec(0.82, (0.13, 0.13, 0.31), (0.0, 0.0, -0.155), _LEFT),
    "left_forearm": SegmentSpec(0.48, (0.11, 0.11, 0.27), (0.0, 0.0, -0.135), _LEFT2),
    "left_hand": SegmentSpec(0.18, (0.09, 0.15, 0.18), (0.0, 0.0, -0.09), _LEFT2),
    "right_upper_arm": SegmentSpec(0.82, (0.13, 0.13, 0.31), (0.0, 0.0, -0.155), _RIGHT),
    "right_forearm": SegmentSpec(0.48, (0.11, 0.11, 0.27), (0.0, 0.0, -0.135), _RIGHT2),
    "right_hand": SegmentSpec(0.18, (0.09, 0.15, 0.18), (0.0, 0.0, -0.09), _RIGHT2),
    "left_thigh": SegmentSpec(4.25, (0.15, 0.15, 0.40), (0.0, 0.0, -0.20), _LEFT),
    "left_shin": SegmentSpec(1.30, (0.13, 0.13, 0.40), (0.0, 0.0, -0.20), _LEFT2),
    "left_foot": SegmentSpec(0.42, (0.11, 0.26, 0.07), (0.0, -0.075, -0.035), _LEFT2),
    "right_thigh": SegmentSpec(4.25, (0.15, 0.15, 0.40), (0.0, 0.0, -0.20), _RIGHT),
    "right_shin": SegmentSpec(1.30, (0.13, 0.13, 0.40), (0.0, 0.0, -0.20), _RIGHT2),
    "right_foot": SegmentSpec(0.42, (0.11, 0.26, 0.07), (0.0, -0.075, -0.035), _RIGHT2),
}

JOINT_TOPOLOGY: tuple[JointTopology, ...] = (
    JointTopology("trunk_yaw", "pelvis", "trunk_yaw_carrier", (0.0, 0.0, 0.10)),
    JointTopology("trunk_roll", "trunk_yaw_carrier", "trunk_roll_carrier", (0.0, 0.0, 0.0)),
    JointTopology("trunk_pitch", "trunk_roll_carrier", "torso", (0.0, 0.0, 0.0)),
    JointTopology("neck_yaw", "torso", "neck_yaw_carrier", (0.0, 0.0, 0.48)),
    JointTopology("neck_pitch", "neck_yaw_carrier", "head", (0.0, 0.0, 0.0)),
    JointTopology("left_shoulder_yaw", "torso", "left_shoulder_yaw_carrier", (-0.28, 0.0, 0.36)),
    JointTopology(
        "left_shoulder_roll",
        "left_shoulder_yaw_carrier",
        "left_shoulder_roll_carrier",
        (0.0, 0.0, 0.0),
    ),
    JointTopology(
        "left_shoulder_pitch", "left_shoulder_roll_carrier", "left_upper_arm", (0.0, 0.0, 0.0)
    ),
    JointTopology("left_elbow_pitch", "left_upper_arm", "left_elbow_carrier", (0.0, 0.0, -0.31)),
    JointTopology("left_forearm_roll", "left_elbow_carrier", "left_forearm", (0.0, 0.0, 0.0)),
    JointTopology("left_wrist_pitch", "left_forearm", "left_wrist_carrier", (0.0, 0.0, -0.27)),
    JointTopology("left_wrist_deviation", "left_wrist_carrier", "left_hand", (0.0, 0.0, 0.0)),
    JointTopology("right_shoulder_yaw", "torso", "right_shoulder_yaw_carrier", (0.28, 0.0, 0.36)),
    JointTopology(
        "right_shoulder_roll",
        "right_shoulder_yaw_carrier",
        "right_shoulder_roll_carrier",
        (0.0, 0.0, 0.0),
    ),
    JointTopology(
        "right_shoulder_pitch", "right_shoulder_roll_carrier", "right_upper_arm", (0.0, 0.0, 0.0)
    ),
    JointTopology("right_elbow_pitch", "right_upper_arm", "right_elbow_carrier", (0.0, 0.0, -0.31)),
    JointTopology("right_forearm_roll", "right_elbow_carrier", "right_forearm", (0.0, 0.0, 0.0)),
    JointTopology("right_wrist_pitch", "right_forearm", "right_wrist_carrier", (0.0, 0.0, -0.27)),
    JointTopology("right_wrist_deviation", "right_wrist_carrier", "right_hand", (0.0, 0.0, 0.0)),
    JointTopology("left_hip_yaw", "pelvis", "left_hip_yaw_carrier", (-0.10, 0.0, -0.10)),
    JointTopology(
        "left_hip_roll", "left_hip_yaw_carrier", "left_hip_roll_carrier", (0.0, 0.0, 0.0)
    ),
    JointTopology("left_hip_pitch", "left_hip_roll_carrier", "left_thigh", (0.0, 0.0, 0.0)),
    JointTopology("left_knee_pitch", "left_thigh", "left_shin", (0.0, 0.0, -0.40)),
    JointTopology("left_ankle_pitch", "left_shin", "left_ankle_pitch_carrier", (0.0, 0.0, -0.40)),
    JointTopology("left_ankle_roll", "left_ankle_pitch_carrier", "left_foot", (0.0, 0.0, 0.0)),
    JointTopology("right_hip_yaw", "pelvis", "right_hip_yaw_carrier", (0.10, 0.0, -0.10)),
    JointTopology(
        "right_hip_roll", "right_hip_yaw_carrier", "right_hip_roll_carrier", (0.0, 0.0, 0.0)
    ),
    JointTopology("right_hip_pitch", "right_hip_roll_carrier", "right_thigh", (0.0, 0.0, 0.0)),
    JointTopology("right_knee_pitch", "right_thigh", "right_shin", (0.0, 0.0, -0.40)),
    JointTopology(
        "right_ankle_pitch", "right_shin", "right_ankle_pitch_carrier", (0.0, 0.0, -0.40)
    ),
    JointTopology("right_ankle_roll", "right_ankle_pitch_carrier", "right_foot", (0.0, 0.0, 0.0)),
)
if tuple(item.joint_name for item in JOINT_TOPOLOGY) != tuple(spec.name for spec in JOINT_SPECS):
    raise RuntimeError("joint topology order must exactly match JOINT_SPECS")

CONTACT_LINK_NAMES = (
    "torso",
    "head",
    "left_upper_arm",
    "left_forearm",
    "left_hand",
    "right_upper_arm",
    "right_forearm",
    "right_hand",
    "left_thigh",
    "left_shin",
    "left_foot",
    "right_thigh",
    "right_shin",
    "right_foot",
)
STRUCTURAL_NEIGHBOUR_NAMES = (
    ("pelvis", "torso"),
    ("torso", "head"),
    ("torso", "left_upper_arm"),
    ("left_upper_arm", "left_forearm"),
    ("left_forearm", "left_hand"),
    ("torso", "right_upper_arm"),
    ("right_upper_arm", "right_forearm"),
    ("right_forearm", "right_hand"),
    ("pelvis", "left_thigh"),
    ("left_shin", "left_foot"),
    ("pelvis", "right_thigh"),
    ("right_shin", "right_foot"),
    # Carriers with zero offset share AABB space with their structural neighbours;
    # exclude them to suppress spurious self-collision impulses in trunk and hips.
    ("pelvis", "left_hip_roll_carrier"),
    ("pelvis", "right_hip_roll_carrier"),
    ("trunk_yaw_carrier", "torso"),
)


def _fmt(values: Sequence[float]) -> str:
    return " ".join(f"{float(value):.10g}" for value in values)


def _box_inertia(mass: float, size: tuple[float, float, float]) -> tuple[float, float, float]:
    x, y, z = size
    return (
        mass * (y * y + z * z) / 12.0,
        mass * (x * x + z * z) / 12.0,
        mass * (x * x + y * y) / 12.0,
    )


CYLINDRICAL_COLLISION_LINKS = frozenset(
    {
        "left_upper_arm",
        "left_forearm",
        "right_upper_arm",
        "right_forearm",
        "left_thigh",
        "left_shin",
        "right_thigh",
        "right_shin",
    }
)


def _cylinder_inertia(
    mass: float,
    *,
    radius: float,
    length: float,
) -> tuple[float, float, float]:
    transverse = mass * (3.0 * radius * radius + length * length) / 12.0
    axial = 0.5 * mass * radius * radius
    return transverse, transverse, axial


def _segment_link_xml(name: str, segment: SegmentSpec) -> str:
    xyz = _fmt(segment.origin)
    size = _fmt(segment.size)
    color = _fmt(segment.color)

    if name in CYLINDRICAL_COLLISION_LINKS:
        radius = min(segment.size[0], segment.size[1]) / 2.0
        length = segment.size[2]
        ixx, iyy, izz = _cylinder_inertia(
            segment.mass,
            radius=radius,
            length=length,
        )
        collision_geometry = f'<cylinder radius="{radius:.10g}" length="{length:.10g}"/>'
    else:
        ixx, iyy, izz = _box_inertia(segment.mass, segment.size)
        collision_geometry = f'<box size="{size}"/>'

    return f"""
  <link name="{name}">
    <inertial>
      <origin xyz="{xyz}" rpy="0 0 0"/>
      <mass value="{segment.mass:.10g}"/>
      <inertia ixx="{ixx:.10g}" ixy="0" ixz="0" iyy="{iyy:.10g}" iyz="0" izz="{izz:.10g}"/>
    </inertial>
    <visual>
      <origin xyz="{xyz}" rpy="0 0 0"/>
      <geometry><box size="{size}"/></geometry>
      <material name="{name}_material"><color rgba="{color}"/></material>
    </visual>
    <collision>
      <origin xyz="{xyz}" rpy="0 0 0"/>
      <geometry>{collision_geometry}</geometry>
    </collision>
  </link>"""


def _carrier_link_xml(name: str) -> str:
    # Small but non-zero inertia avoids singular mass matrices while adding no
    # collision or visual geometry.
    return f"""
  <link name="{name}">
    <inertial>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <mass value="{CARRIER_MASS:.10g}"/>
      <inertia ixx="0.0001" ixy="0" ixz="0" iyy="0.0001" iyz="0" izz="0.0001"/>
    </inertial>
  </link>"""


def mechanical_joint_limits(spec: JointSpec) -> tuple[float, float]:
    """Return Bullet stop limits inset from the canonical anatomical envelope.

    Bullet revolute constraints exhibit a small, repeatable solver penetration
    under aggressive torque. The guard band keeps that numerical slop inside
    the organism's true anatomical range rather than redefining the anatomy.
    """
    span = spec.upper - spec.lower
    guard = min(MECHANICAL_LIMIT_GUARD, span * 0.1)
    return spec.lower + guard, spec.upper - guard


def build_anthropomorphic_urdf() -> str:
    links = {"pelvis", *(item.child_link for item in JOINT_TOPOLOGY)}
    link_xml = []
    for name in links:
        if name in SEGMENTS:
            link_xml.append(_segment_link_xml(name, SEGMENTS[name]))
        else:
            link_xml.append(_carrier_link_xml(name))

    spec_by_name = {spec.name: spec for spec in JOINT_SPECS}
    joint_xml = []
    for item in JOINT_TOPOLOGY:
        spec = spec_by_name[item.joint_name]
        mechanical_lower, mechanical_upper = mechanical_joint_limits(spec)
        joint_xml.append(
            f"""
  <joint name="{spec.name}" type="revolute">
    <parent link="{item.parent_link}"/>
    <child link="{item.child_link}"/>
    <origin xyz="{_fmt(item.origin)}" rpy="0 0 0"/>
    <axis xyz="{_fmt(spec.axis)}"/>
    <limit lower="{mechanical_lower:.12g}" upper="{mechanical_upper:.12g}" effort="{spec.max_motor_torque:.12g}" velocity="{spec.max_velocity:.12g}"/>
    <dynamics damping="0" friction="0"/>
  </joint>"""
        )
    return (
        '<?xml version="1.0"?>\n'
        '<robot name="symbiont_anthropomorphic_v6">'
        + "".join(link_xml)
        + "".join(joint_xml)
        + "\n</robot>\n"
    )


def _end_range_resistance(
    spec: JointSpec,
    *,
    position: float,
    velocity: float,
) -> float:
    """Passive ligament-like resistance entirely inside the hard URDF range."""
    lower_zone = spec.lower + min(END_RANGE_MARGIN, (spec.upper - spec.lower) * 0.2)
    upper_zone = spec.upper - min(END_RANGE_MARGIN, (spec.upper - spec.lower) * 0.2)
    torque = 0.0
    if position < lower_zone:
        torque = END_RANGE_STIFFNESS * (lower_zone - position) - END_RANGE_DAMPING * velocity
    elif position > upper_zone:
        torque = -END_RANGE_STIFFNESS * (position - upper_zone) - END_RANGE_DAMPING * velocity
    bound = spec.max_motor_torque * 1.5
    return max(-bound, min(bound, torque))


def _neutral_rest_position(spec: JointSpec) -> float:
    lower, upper = mechanical_joint_limits(spec)
    return max(lower, min(upper, 0.0))


def _passive_postural_tone(
    spec: JointSpec,
    *,
    position: float,
    velocity: float,
) -> float:
    """Elastic neutral-rest tissue torque.

    Dissipation is not returned here: the viscous part is the joint's own
    damping, integrated by the engine.
    """
    del velocity
    rest = _neutral_rest_position(spec)
    stiffness = spec.max_motor_torque * PASSIVE_TONE_STIFFNESS_FRACTION
    elastic_cap = spec.max_motor_torque * PASSIVE_TONE_TORQUE_CAP_FRACTION
    return max(
        -elastic_cap,
        min(elastic_cap, stiffness * (rest - position)),
    )


ANTHROPOMORPHIC_SPEC = ArticulatedBodySpec(
    body_kind=BODY_KIND,
    state_schema_version=BODY_STATE_SCHEMA_VERSION,
    spawn_height=1.08,
    base_link_name="pelvis",
    joint_specs=JOINT_SPECS,
    joint_topology=JOINT_TOPOLOGY,
    segments=SEGMENTS,
    contact_link_names=CONTACT_LINK_NAMES,
    structural_neighbour_names=STRUCTURAL_NEIGHBOUR_NAMES,
)


class HumanoidPhysics(ArticulatedPhysics):
    """31-DoF humanoid with engine-enforced anatomical joint constraints."""

    SPEC = ANTHROPOMORPHIC_SPEC

    # The body's own receptor surface; subclasses may append apparatus.
    physical_receptor_ids = physical_receptor_contract_ids()

    def _urdf(self) -> str:
        return build_anthropomorphic_urdf()

    def _passive_torque(self, spec: JointSpec, *, position: float, velocity: float) -> float:
        # Near either end of its range a joint meets ligament-like resistance
        # before the hard stop; everywhere, elastic tissue pulls it to rest.
        # Viscous dissipation is the joint's own damping.
        return _passive_postural_tone(
            spec, position=position, velocity=velocity
        ) + _end_range_resistance(spec, position=position, velocity=velocity)

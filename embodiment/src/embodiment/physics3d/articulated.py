"""Generic opaque articulated Physics3D apparatus.

This module owns only physical mechanics. Human-readable joint/link names are
observer-side metadata; organisms see ordinal rec.N / eff.N channels only.
"""

from __future__ import annotations

import math
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from embodiment.physics3d.mechanics import (
    BODY_MATERIAL,
    CARRIER_MASS,
    END_RANGE_DAMPING,
    END_RANGE_MARGIN,
    END_RANGE_STIFFNESS,
    JOINT_LIMIT_SOLVER_TOLERANCE,
    MECHANICAL_LIMIT_GUARD,
    ActuatorWork,
    JointSpec,
    JointTopology,
    MotorBinding,
    SegmentSpec,
    SurfaceMaterial,
)

NAME_PREFIX = "body."
# MuJoCo's URDF importer would otherwise weld massless carrier links into
# their parents and renumber the joints of the opaque contract.
_URDF_COMPILER = '<mujoco><compiler fusestatic="false" discardvisual="true"/></mujoco>'
# Joint limits are anatomical: MuJoCo's default soft constraint lets a loaded
# joint pass its limit by several degrees.  The stiffest stable response is a
# time constant of two timesteps with near-rigid impedance.
JOINT_LIMIT_IMPEDANCE = (0.99, 0.999, 0.001, 0.5, 2.0)
GLOBAL_KINEMATIC_RECEPTORS = 10
ECOLOGICAL_RECEPTORS = 1
INTEROCEPTIVE_RECEPTOR_COUNT = 4


@dataclass(frozen=True, slots=True)
class FixedLinkTopology:
    parent_link: str
    child_link: str
    origin: tuple[float, float, float]


@dataclass(frozen=True, slots=True)
class ArticulatedBodySpec:
    body_kind: str
    state_schema_version: int
    spawn_height: float
    base_link_name: str
    joint_specs: tuple[JointSpec, ...]
    joint_topology: tuple[JointTopology, ...]
    segments: Mapping[str, SegmentSpec]
    contact_link_names: tuple[str, ...]
    structural_neighbour_names: tuple[tuple[str, str], ...]
    fixed_link_topology: tuple[FixedLinkTopology, ...] = ()
    body_material: SurfaceMaterial = BODY_MATERIAL

    @property
    def motor_dof(self) -> int:
        return len(self.joint_specs)

    @property
    def somatic_region_count(self) -> int:
        return 1 + len(self.contact_link_names)

    @property
    def physical_receptor_count(self) -> int:
        return (
            self.motor_dof * 2
            + GLOBAL_KINEMATIC_RECEPTORS
            + self.somatic_region_count * 2
            + ECOLOGICAL_RECEPTORS
        )

    @property
    def total_receptor_count(self) -> int:
        return self.physical_receptor_count + INTEROCEPTIVE_RECEPTOR_COUNT

    @property
    def effector_count(self) -> int:
        return self.motor_dof * 2

    def physical_receptor_ids(self) -> tuple[str, ...]:
        return tuple(f"rec.{i}" for i in range(self.physical_receptor_count))

    def interoceptive_receptor_ids(self) -> tuple[str, ...]:
        return tuple(
            f"rec.{i}"
            for i in range(
                self.physical_receptor_count,
                self.total_receptor_count,
            )
        )

    def receptor_ids(self) -> tuple[str, ...]:
        return tuple(f"rec.{i}" for i in range(self.total_receptor_count))

    def effector_ids(self) -> tuple[str, ...]:
        return tuple(f"eff.{i}" for i in range(self.effector_count))


def _fmt(values: Sequence[float]) -> str:
    return " ".join(f"{float(value):.10g}" for value in values)


def _box_inertia(mass: float, size: tuple[float, float, float]) -> tuple[float, float, float]:
    x, y, z = size
    return (
        mass * (y * y + z * z) / 12.0,
        mass * (x * x + z * z) / 12.0,
        mass * (x * x + y * y) / 12.0,
    )


def _segment_link_xml(name: str, segment: SegmentSpec) -> str:
    ixx, iyy, izz = _box_inertia(segment.mass, segment.size)
    return f"""
  <link name="{name}">
    <inertial>
      <origin xyz="{_fmt(segment.origin)}" rpy="0 0 0"/>
      <mass value="{segment.mass:.10g}"/>
      <inertia ixx="{ixx:.10g}" ixy="0" ixz="0" iyy="{iyy:.10g}" iyz="0" izz="{izz:.10g}"/>
    </inertial>
    <visual>
      <origin xyz="{_fmt(segment.origin)}" rpy="0 0 0"/>
      <geometry><box size="{_fmt(segment.size)}"/></geometry>
      <material name="{name}_material"><color rgba="{_fmt(segment.color)}"/></material>
    </visual>
    <collision>
      <origin xyz="{_fmt(segment.origin)}" rpy="0 0 0"/>
      <geometry><box size="{_fmt(segment.size)}"/></geometry>
    </collision>
  </link>"""


def _carrier_link_xml(name: str) -> str:
    return f"""
  <link name="{name}">
    <inertial>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <mass value="{CARRIER_MASS:.10g}"/>
      <inertia ixx="0.0001" ixy="0" ixz="0" iyy="0.0001" iyz="0" izz="0.0001"/>
    </inertial>
  </link>"""


def _mechanical_joint_limits(spec: JointSpec) -> tuple[float, float]:
    span = spec.upper - spec.lower
    guard = min(MECHANICAL_LIMIT_GUARD, span * 0.1)
    return spec.lower + guard, spec.upper - guard


def _end_range_resistance(spec: JointSpec, *, position: float, velocity: float) -> float:
    lower_zone = spec.lower + min(END_RANGE_MARGIN, (spec.upper - spec.lower) * 0.2)
    upper_zone = spec.upper - min(END_RANGE_MARGIN, (spec.upper - spec.lower) * 0.2)
    torque = 0.0
    if position < lower_zone:
        torque = END_RANGE_STIFFNESS * (lower_zone - position) - END_RANGE_DAMPING * velocity
    elif position > upper_zone:
        torque = -END_RANGE_STIFFNESS * (position - upper_zone) - END_RANGE_DAMPING * velocity
    bound = spec.max_motor_torque * 1.5
    return max(-bound, min(bound, torque))


def _restore_vector(
    payload: Mapping[str, object],
    key: str,
    expected_size: int,
) -> tuple[float, ...]:
    raw = payload.get(key)
    if not isinstance(raw, (list, tuple)) or len(raw) != expected_size:
        raise ValueError(f"{key} must contain {expected_size} values")
    values: list[float] = []
    for item in raw:
        if isinstance(item, bool) or not isinstance(item, (int, float)):
            raise ValueError(f"{key} must contain numeric values")
        values.append(float(item))
    return tuple(values)


def build_articulated_urdf(spec: ArticulatedBodySpec) -> str:
    if len(spec.joint_specs) != len(spec.joint_topology):
        raise ValueError("joint specs/topology length mismatch")
    if tuple(item.joint_name for item in spec.joint_topology) != tuple(
        item.name for item in spec.joint_specs
    ):
        raise ValueError("joint topology order must match joint specs")

    links = {
        spec.base_link_name,
        *(item.child_link for item in spec.joint_topology),
        *(item.child_link for item in spec.fixed_link_topology),
    }
    link_xml = [
        _segment_link_xml(name, spec.segments[name])
        if name in spec.segments
        else _carrier_link_xml(name)
        for name in links
    ]
    by_name = {item.name: item for item in spec.joint_specs}
    joint_xml: list[str] = []
    for topo in spec.joint_topology:
        joint = by_name[topo.joint_name]
        lower, upper = _mechanical_joint_limits(joint)
        joint_xml.append(
            f"""
  <joint name="{joint.name}" type="revolute">
    <parent link="{topo.parent_link}"/>
    <child link="{topo.child_link}"/>
    <origin xyz="{_fmt(topo.origin)}" rpy="0 0 0"/>
    <axis xyz="{_fmt(joint.axis)}"/>
    <limit lower="{lower:.12g}" upper="{upper:.12g}" effort="{joint.max_motor_torque:.12g}" velocity="{joint.max_velocity:.12g}"/>
    <dynamics damping="{joint.passive_damping:.12g}" friction="0"/>
  </joint>"""
        )
    for topo in spec.fixed_link_topology:
        joint_xml.append(
            f'''\n  <joint name="{topo.child_link}_fixed" type="fixed">
    <parent link="{topo.parent_link}"/>
    <child link="{topo.child_link}"/>
    <origin xyz="{_fmt(topo.origin)}" rpy="0 0 0"/>
  </joint>'''
        )
    return (
        '<?xml version="1.0"?>\n'
        f'<robot name="symbiont_{spec.body_kind.replace("-", "_")}">'
        + "".join(link_xml)
        + "".join(joint_xml)
        + "\n</robot>\n"
    )


class ArticulatedPhysics:
    """Configurable MuJoCo body with an opaque ordinal sensorimotor contract."""

    SPEC: ArticulatedBodySpec

    def __init__(self, scene: Any, *, spawn_height: float | None = None) -> None:
        spec = self.SPEC
        self.scene = scene
        self._sensor_values: dict[str, float] = {}
        self._applied_torque_by_joint: dict[int, float] = {}
        self._external_field_signal = 0.0
        self._bound_revision = -1
        self.motor_joint_indices = tuple(range(spec.motor_dof))
        self._joint_ordinal_by_index = {index: index for index in self.motor_joint_indices}
        self._link_index_by_name: dict[str, int] = {
            spec.base_link_name: -1,
            **{item.child_link: ordinal for ordinal, item in enumerate(spec.joint_topology)},
            **{
                item.child_link: len(spec.joint_topology) + ordinal
                for ordinal, item in enumerate(spec.fixed_link_topology)
            },
        }
        self._contact_links = (
            -1,
            *(self._link_index_by_name[name] for name in spec.contact_link_names),
        )
        self.motor_bindings = tuple(
            MotorBinding(
                joint_index=joint_index,
                positive_port=f"eff.{ordinal * 2}",
                negative_port=f"eff.{ordinal * 2 + 1}",
            )
            for ordinal, joint_index in enumerate(self.motor_joint_indices)
        )
        self.receptor_ids = spec.physical_receptor_ids()
        self.effector_ids = spec.effector_ids()
        self.observer_joint_specs = spec.joint_specs
        self.observer_contact_region_names = (
            spec.base_link_name,
            *spec.contact_link_names,
        )
        self._add_to_scene(spec.spawn_height if spawn_height is None else float(spawn_height))
        scene.recompile()
        self._bind()
        # Zero is outside the range of some joints; start each at the nearest
        # position inside its mechanical limits.
        for ordinal, joint in enumerate(spec.joint_specs):
            lower, upper = _mechanical_joint_limits(joint)
            scene.data.qpos[self._joint_qpos[ordinal]] = min(max(0.0, lower), upper)
        scene.forward()

    # -- construction ---------------------------------------------------------
    def _add_to_scene(self, spawn_height: float) -> None:
        spec = self.SPEC
        mujoco = self.scene.mj
        urdf = re.sub(r"(<robot[^>]*>)", r"\1" + _URDF_COMPILER, self._urdf(), count=1)
        loaded = mujoco.MjSpec.from_string(urdf)
        frame = self.scene.spec.worldbody.add_frame(pos=[0.0, 0.0, float(spawn_height)])
        root = frame.attach_body(loaded.worldbody.first_body(), NAME_PREFIX, "")
        root.add_freejoint(name=f"{NAME_PREFIX}root")
        material = spec.body_material
        friction = [
            material.lateral_friction,
            material.spinning_friction,
            material.rolling_friction,
        ]
        for geom in self.scene.spec.geoms:
            if geom.name.startswith(NAME_PREFIX) or geom.parent.name.startswith(NAME_PREFIX):
                geom.friction = friction
        limit_response = [2.0 * float(self.scene.spec.option.timestep), 1.0]
        damping = {f"{NAME_PREFIX}{item.name}": item.passive_damping for item in spec.joint_specs}
        for joint in self.scene.spec.joints:
            if joint.name in damping:
                joint.solref_limit = limit_response
                joint.solimp_limit = list(JOINT_LIMIT_IMPEDANCE)
                # Viscous joint damping, integrated implicitly by the engine.
                # (linear, quadratic, cubic) coefficients; only the linear one.
                joint.damping = [float(damping[joint.name]), 0.0, 0.0]
        # A link and its parent never collide in MuJoCo; structural neighbours
        # joined through a massless carrier need an explicit exclusion.
        for left, right in spec.structural_neighbour_names:
            self.scene.spec.add_exclude(
                bodyname1=f"{NAME_PREFIX}{left}", bodyname2=f"{NAME_PREFIX}{right}"
            )

    def _urdf(self) -> str:
        return build_articulated_urdf(self.SPEC)

    def _passive_torque(self, spec: JointSpec, *, position: float, velocity: float) -> float:
        """Torque the body's own tissue adds to a joint, beside the command."""
        return _end_range_resistance(spec, position=position, velocity=velocity)

    def _bind(self) -> None:
        """Resolve this body's element ids in the scene's current model."""
        spec = self.SPEC
        scene = self.scene
        model = scene.model
        root_joint = scene.name_to_id("joint", f"{NAME_PREFIX}root")
        self._root_qpos = int(model.jnt_qposadr[root_joint])
        self._root_dof = int(model.jnt_dofadr[root_joint])
        joint_ids = [
            scene.name_to_id("joint", f"{NAME_PREFIX}{item.name}") for item in spec.joint_specs
        ]
        self._joint_qpos = tuple(int(model.jnt_qposadr[joint]) for joint in joint_ids)
        self._joint_dof = tuple(int(model.jnt_dofadr[joint]) for joint in joint_ids)
        for ordinal, joint in enumerate(joint_ids):
            lower, upper = _mechanical_joint_limits(spec.joint_specs[ordinal])
            low, high = (float(value) for value in model.jnt_range[joint])
            if abs(low - lower) > 1e-6 or abs(high - upper) > 1e-6 or not model.jnt_limited[joint]:
                raise RuntimeError(
                    f"MuJoCo did not load limits for {spec.joint_specs[ordinal].name}"
                )
        self._body_id_by_link = {
            index: scene.name_to_id("body", f"{NAME_PREFIX}{name}")
            for name, index in self._link_index_by_name.items()
        }
        self.body_id = self._body_id_by_link[-1]
        # Every engine body of this organism; ids move when the scene is rebuilt.
        self.body_ids = frozenset(self._body_id_by_link.values())
        self._link_by_body_id = {body: index for index, body in self._body_id_by_link.items()}
        self._qpos_addresses = (
            *range(self._root_qpos, self._root_qpos + 7),
            *self._joint_qpos,
        )
        self._dof_addresses = (
            *range(self._root_dof, self._root_dof + 6),
            *self._joint_dof,
        )
        self._bound_revision = scene.revision

    def _current(self) -> tuple[Any, Any]:
        if self._bound_revision != self.scene.revision:
            self._bind()
        return self.scene.model, self.scene.data

    # -- opaque environment signal ---------------------------------------------
    def set_opaque_environment_state(self, *, external_field: float) -> None:
        value = float(external_field)
        if not math.isfinite(value) or not 0.0 <= value <= 1.0:
            raise ValueError("external_field must be within [0, 1]")
        self._external_field_signal = value

    @staticmethod
    def _bounded_contact_load(value: float, scale: float = 120.0) -> float:
        return math.tanh(max(0.0, float(value)) / max(scale, 1e-12))

    @staticmethod
    def _signed_unit(value: float, scale: float) -> float:
        return 0.5 + 0.5 * math.tanh(float(value) / max(scale, 1e-12))

    # -- kinematic reads ----------------------------------------------------------
    def joint_states(self) -> list[tuple[float, float]]:
        _model, data = self._current()
        return [
            (float(data.qpos[position]), float(data.qvel[velocity]))
            for position, velocity in zip(self._joint_qpos, self._joint_dof)
        ]

    def base_pose(self) -> tuple[list[float], list[float]]:
        """Base position and orientation as (x, y, z) and (x, y, z, w)."""
        _model, data = self._current()
        q = self._root_qpos
        w, x, y, z = (float(data.qpos[q + offset]) for offset in (3, 4, 5, 6))
        return [float(data.qpos[q + offset]) for offset in range(3)], [x, y, z, w]

    def link_pose(self, link_name: str) -> tuple[list[float], list[float]]:
        """World position and rotation (nine row-major values) of a link frame."""
        _model, data = self._current()
        body = self._body_id_by_link[self._link_index_by_name[link_name]]
        return data.xpos[body].tolist(), data.xmat[body].tolist()

    def base_velocity(self) -> tuple[list[float], list[float]]:
        """Linear and angular base velocity, both in the world frame."""
        _model, data = self._current()
        v = self._root_dof
        linear = [float(data.qvel[v + offset]) for offset in range(3)]
        local = [float(data.qvel[v + offset]) for offset in (3, 4, 5)]
        rotation = data.xmat[self.body_id]
        angular = [
            sum(float(rotation[row * 3 + column]) * local[column] for column in range(3))
            for row in range(3)
        ]
        return linear, angular

    def contact_details(self) -> list[dict[str, object]]:
        """Observer-side description of each contact this body takes part in."""
        model, data = self._current()
        mujoco = self.scene.mj
        import numpy

        name_by_link = {index: name for name, index in self._link_index_by_name.items()}
        force = numpy.zeros(6)
        details: list[dict[str, object]] = []
        for index in range(int(data.ncon)):
            contact = data.contact[index]
            bodies = (
                int(model.geom_bodyid[contact.geom1]),
                int(model.geom_bodyid[contact.geom2]),
            )
            for own, other in (bodies, bodies[::-1]):
                if own not in self._link_by_body_id:
                    continue
                mujoco.mj_contactForce(model, data, index, force)
                link = self._link_by_body_id[own]
                details.append(
                    {
                        "link_index": link,
                        "link_name": name_by_link[link],
                        "position": [float(value) for value in contact.pos],
                        "normal": [float(value) for value in contact.frame[:3]],
                        "normal_force": max(0.0, float(force[0])),
                        # Negative while the surfaces interpenetrate.
                        "distance": float(contact.dist),
                        "other_body_id": other,
                        "other_link_name": name_by_link.get(self._link_by_body_id.get(other)),
                    }
                )
        return details

    def _contact_loads(self) -> tuple[set[int], dict[int, float], int]:
        """Links of this body in contact, their peak normal force, contact count."""
        model, data = self._current()
        mujoco = self.scene.mj
        import numpy

        force = numpy.zeros(6)
        active: set[int] = set()
        peak = {link: 0.0 for link in self._contact_links}
        count = 0
        for index in range(int(data.ncon)):
            contact = data.contact[index]
            links = [
                self._link_by_body_id[body]
                for body in (
                    int(model.geom_bodyid[contact.geom1]),
                    int(model.geom_bodyid[contact.geom2]),
                )
                if body in self._link_by_body_id
            ]
            if not links:
                continue
            count += 1
            mujoco.mj_contactForce(model, data, index, force)
            normal = max(0.0, float(force[0]))
            for link in links:
                active.add(link)
                if link in peak:
                    peak[link] = max(peak[link], normal)
        return active, peak, count

    def mass_distribution(self) -> tuple[float, list[float]]:
        """Total mass and world-frame centre of mass of the body."""
        model, data = self._current()
        total = 0.0
        weighted = [0.0, 0.0, 0.0]
        for body in self._body_id_by_link.values():
            mass = max(0.0, float(model.body_mass[body]))
            total += mass
            for axis in range(3):
                weighted[axis] += mass * float(data.xipos[body][axis])
        if total <= 0.0:
            return 0.0, self.base_pose()[0]
        return total, [value / total for value in weighted]

    def joint_torques(self) -> list[float]:
        """Torque applied at each joint for the next step: command plus passive."""
        _model, data = self._current()
        return [float(data.qfrc_applied[address]) for address in self._joint_dof]

    # -- receptors and effectors -----------------------------------------------------
    def sample_receptors(self) -> Mapping[str, float]:
        values: list[float] = []
        for position, velocity in self.joint_states():
            values.extend((self._signed_unit(position, math.pi), self._signed_unit(velocity, 6.0)))

        _position, orientation = self.base_pose()
        linear_velocity, angular_velocity = self.base_velocity()
        values.extend(max(0.0, min(1.0, 0.5 + 0.5 * float(q))) for q in orientation)
        values.extend(self._signed_unit(v, 4.0) for v in linear_velocity)
        values.extend(self._signed_unit(v, 6.0) for v in angular_velocity)

        active_links, peak_force, _count = self._contact_loads()
        values.extend(1.0 if link in active_links else 0.0 for link in self._contact_links)
        values.append(self._external_field_signal)
        values.extend(self._bounded_contact_load(peak_force[link]) for link in self._contact_links)

        # The spec's own receptors; a subclass may append further channels.
        receptor_ids = self.SPEC.physical_receptor_ids()
        if len(values) != len(receptor_ids):
            raise RuntimeError(
                f"physics receptor contract mismatch: {len(values)} != {len(receptor_ids)}"
            )
        self._sensor_values = dict(zip(receptor_ids, values))
        return dict(self._sensor_values)

    def receptor_value(self, receptor_id: str) -> float:
        return float(self._sensor_values.get(receptor_id, 0.0))

    def apply_effectors(
        self,
        activations: Mapping[str, float],
        *,
        torque_scale: float = 1.0,
    ) -> None:
        scale = max(0.0, float(torque_scale))
        applied: dict[int, float] = {}
        for ordinal, binding in enumerate(self.motor_bindings):
            positive = max(0.0, min(1.0, float(activations.get(binding.positive_port, 0.0))))
            negative = max(0.0, min(1.0, float(activations.get(binding.negative_port, 0.0))))
            spec = self.SPEC.joint_specs[ordinal]
            applied[binding.joint_index] = (positive - negative) * spec.max_motor_torque * scale
        self._applied_torque_by_joint = applied
        self.prepare_physics_substep()

    def prepare_physics_substep(self) -> None:
        """Set each joint's torque for the next step: command plus end-range resistance."""
        _model, data = self._current()
        for ordinal, (position, velocity) in enumerate(self.joint_states()):
            passive = self._passive_torque(
                self.SPEC.joint_specs[ordinal], position=position, velocity=velocity
            )
            commanded = float(self._applied_torque_by_joint.get(ordinal, 0.0))
            data.qfrc_applied[self._joint_dof[ordinal]] = commanded + passive

    def actuator_work_step(self, dt: float) -> ActuatorWork:
        if not math.isfinite(float(dt)) or dt <= 0.0:
            raise ValueError("dt must be finite and positive")
        states = self.joint_states()
        positive = 0.0
        negative = 0.0
        for index, torque in self._applied_torque_by_joint.items():
            if abs(float(torque)) <= 1e-9:
                continue
            work = float(torque) * states[index][1] * float(dt)
            if work >= 0.0:
                positive += work
            else:
                negative += -work
        return ActuatorWork(
            positive_j=float(positive),
            negative_j=float(negative),
            absolute_j=float(positive + negative),
            net_j=float(positive - negative),
        )

    def mechanical_work_step(self, dt: float) -> float:
        """Compatibility scalar: absolute commanded actuator effort."""
        return self.actuator_work_step(dt).absolute_j

    # -- physical state -------------------------------------------------------------
    def export_physical_state(self) -> dict[str, object]:
        _model, data = self._current()
        base_position, base_orientation = self.base_pose()
        linear_velocity, angular_velocity = self.base_velocity()
        joints = [
            {
                "joint_index": int(index),
                "joint_name": self.SPEC.joint_specs[index].name,
                "position": position,
                "velocity": velocity,
                "applied_torque": float(self._applied_torque_by_joint.get(index, 0.0)),
            }
            for index, (position, velocity) in enumerate(self.joint_states())
        ]

        links: list[dict[str, object]] = []
        for name, index in sorted(self._link_index_by_name.items(), key=lambda item: item[1]):
            body = self._body_id_by_link[index]
            w, x, y, z = (float(value) for value in data.xquat[body])
            links.append(
                {
                    "link_index": int(index),
                    "link_name": str(name),
                    "position": [float(value) for value in data.xpos[body]],
                    "orientation": [x, y, z, w],
                }
            )
        total_mass, center_of_mass = self.mass_distribution()
        active_links, _peak, contact_count = self._contact_loads()
        return {
            "schema_version": self.SPEC.state_schema_version,
            "body_kind": self.SPEC.body_kind,
            "base_position": base_position,
            "base_orientation": base_orientation,
            "linear_velocity": linear_velocity,
            "angular_velocity": angular_velocity,
            "center_of_mass": center_of_mass,
            "total_mass": float(total_mass),
            "joints": joints,
            "links": links,
            "contact_links": sorted(active_links),
            "contacts": self.contact_details(),
            "contact_count": contact_count,
            # ADR-0066 decision 5: what the engine needs to continue this body
            # exactly.  The readable fields above are derived from it.
            "engine_state": {
                "qpos": [float(data.qpos[address]) for address in self._qpos_addresses],
                "qvel": [float(data.qvel[address]) for address in self._dof_addresses],
                "warmstart": [
                    float(data.qacc_warmstart[address]) for address in self._dof_addresses
                ],
            },
        }

    def restore_physical_state(
        self,
        payload: Mapping[str, object],
        *,
        strict_anatomical_limits: bool = True,
    ) -> None:
        if payload.get("schema_version") != self.SPEC.state_schema_version:
            raise ValueError("unsupported physics body state schema")
        if payload.get("body_kind") != self.SPEC.body_kind:
            raise ValueError(f"body state is not compatible with {self.SPEC.body_kind}")
        engine = payload.get("engine_state")
        if not isinstance(engine, Mapping):
            raise ValueError("body state has no engine state")
        _model, data = self._current()
        qpos = _restore_vector(engine, "qpos", len(self._qpos_addresses))
        qvel = _restore_vector(engine, "qvel", len(self._dof_addresses))
        warmstart = _restore_vector(engine, "warmstart", len(self._dof_addresses))
        if not all(math.isfinite(value) for value in (*qpos, *qvel, *warmstart)):
            raise ValueError("body state contains non-finite values")
        if strict_anatomical_limits:
            for ordinal, spec in enumerate(self.SPEC.joint_specs):
                position = qpos[7 + ordinal]
                if not (
                    spec.lower - JOINT_LIMIT_SOLVER_TOLERANCE
                    <= position
                    <= spec.upper + JOINT_LIMIT_SOLVER_TOLERANCE
                ):
                    raise ValueError(f"joint state outside hard anatomical limit: {spec.name}")
        else:
            # Observer-only display of a recorded state: project an excursion
            # onto the mechanical range instead of refusing to draw it.
            projected = list(qpos)
            for ordinal, spec in enumerate(self.SPEC.joint_specs):
                lower, upper = _mechanical_joint_limits(spec)
                projected[7 + ordinal] = min(max(projected[7 + ordinal], lower), upper)
            qpos = tuple(projected)
        for address, value in zip(self._qpos_addresses, qpos):
            data.qpos[address] = value
        for address, value in zip(self._dof_addresses, qvel):
            data.qvel[address] = value
        for address, value in zip(self._dof_addresses, warmstart):
            data.qacc_warmstart[address] = value
        self._applied_torque_by_joint = {}
        for address in self._joint_dof:
            data.qfrc_applied[address] = 0.0
        self.scene.forward()
        # Recomputing the derived state also re-solves the constraints and
        # overwrites the solver's warm start; put the saved one back so the
        # next step is the one the saved body would have taken.
        for address, value in zip(self._dof_addresses, warmstart):
            data.qacc_warmstart[address] = value

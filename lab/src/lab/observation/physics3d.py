"""Passive adapter from Physics3D viewer frames to observer telemetry."""

from __future__ import annotations

import threading
import uuid
from dataclasses import asdict, is_dataclass
from typing import Any, Mapping, Protocol

from embodiment.observation import BodyPoseSample, JointKinematicState, JointKinematicsSample
from lab.observation.body_pose import body_pose_observation
from lab.observation.joint_kinematics import joint_kinematics_observation
from lab.observation.contracts import ObservedFrame
from lab.observation.plane import ObservationPlane
from lab.observation.projection import mind_snapshot_from_rich_state, runtime_tick_events
from lab.observation.world_scene import WorldScenePublisher, project_world_scene


def _body_descriptor_for_state(physical_state: Mapping[str, object]):
    from lab.integration.physics3d.bodies import DEFAULT_BODY_REGISTRY

    body_kind = str(physical_state.get("body_kind") or "anthropomorphic-v6")
    try:
        return DEFAULT_BODY_REGISTRY.get(body_kind)
    except ValueError:
        return DEFAULT_BODY_REGISTRY.get("anthropomorphic-v6")


def _optional_text(source: Mapping[str, Any], key: str) -> str | None:
    value = source.get(key)
    return str(value) if value is not None else None


def _topology_revision(rich_state: Mapping[str, Any]) -> int | None:
    cognition = rich_state.get("cognition")
    value = cognition.get("topology_revision") if isinstance(cognition, Mapping) else None
    if value is None:
        value = rich_state.get("topology_revision")
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


class EventSink(Protocol):
    def push(self, event: dict[str, Any]) -> None: ...


class Physics3DObservationBridge:
    """Viewer-compatible passive bridge.

    The only reverse path is lifecycle stop; it cannot provide motor, learning,
    reward, environment, or cognitive commands. Every event also carries a
    Lab-owned run identity so presentation state cannot cross run boundaries.

    Managed sessions may additionally provide the organism/body identities that
    the Lab already resolved when launching the run. Runtime payload identity,
    when present, always wins; the launch identity is only a non-invented
    fallback when a projection omits a field the Lab already knows.
    """

    def __init__(
        self,
        sink: EventSink,
        *,
        run_id: str | None = None,
        organism_id: str | None = None,
        body_id: str | None = None,
        observation_plane: ObservationPlane | None = None,
    ) -> None:
        self._sink = sink
        self._run_id = str(run_id or f"observer:{uuid.uuid4()}")
        self._organism_id = str(organism_id) if organism_id is not None else None
        self._body_id = str(body_id) if body_id is not None else None
        self._observation_plane = observation_plane
        self._stop = threading.Event()
        self._pending_frames: dict[int, dict[str, Any]] = {}
        self._world_publisher = WorldScenePublisher()

    @property
    def run_id(self) -> str:
        return self._run_id

    @property
    def organism_id(self) -> str | None:
        return self._organism_id

    @property
    def body_id(self) -> str | None:
        return self._body_id

    def _identity(self, source: Mapping[str, Any], key: str) -> str | None:
        value = _optional_text(source, key)
        if value is None and key == "organism_id":
            value = _optional_text(source, "symbiont_id")
        if value is not None:
            if key == "organism_id" and self._organism_id != value:
                self._organism_id = value
            return value
        if key == "organism_id":
            return self._organism_id
        if key == "body_id":
            return self._body_id
        return None

    def _apply_known_identity(self, event: dict[str, Any], source: Mapping[str, Any]) -> None:
        event["run_id"] = self._run_id
        for key in ("organism_id", "body_id", "embodiment_id"):
            value = self._identity(source, key)
            if value is not None:
                event[key] = value

    def start(self) -> None:
        return None

    @property
    def is_alive(self) -> bool:
        return not self._stop.is_set()

    def poll_commands(self) -> list[dict[str, Any]]:
        return [{"type": "stop"}] if self._stop.is_set() else []

    def poll_stop(self) -> bool:
        return self._stop.is_set()

    def request_stop(self) -> None:
        self._stop.set()

    def _publish_canonical_body_pose(
        self,
        *,
        physical_state: Mapping[str, object],
        physics_step: int,
        simulation_time_s: float,
    ) -> None:
        """Publish canonical Body Pose only when source semantics are explicit.

        Current Physics3D generic coordinates are not presumed to be canonical.
        The source must provide a semantic declaration proving the values already
        satisfy the accepted Body Pose contract. Otherwise this path fails closed.
        """
        if self._observation_plane is None:
            return

        semantics = physical_state.get("body_pose_semantics")
        if not isinstance(semantics, Mapping):
            return
        if semantics.get("position_unit") != "m":
            return
        if semantics.get("handedness") != "right":
            return
        if semantics.get("up_axis") != "+z":
            return
        if semantics.get("orientation") != "xyzw":
            return

        reference_frame = semantics.get("reference_frame")
        body_frame = semantics.get("body_frame")
        if not isinstance(reference_frame, str) or not reference_frame.strip():
            return
        if not isinstance(body_frame, str) or not body_frame.strip():
            return

        body_id = self._identity(physical_state, "body_id")
        base_position = physical_state.get("base_position")
        base_orientation = physical_state.get("base_orientation")
        if (
            body_id is None
            or not isinstance(base_position, (list, tuple))
            or len(base_position) != 3
            or not isinstance(base_orientation, (list, tuple))
            or len(base_orientation) != 4
        ):
            return

        try:
            sample = BodyPoseSample(
                body_id=body_id,
                reference_frame=reference_frame,
                body_frame=body_frame,
                position_m=tuple(float(value) for value in base_position),
                orientation_xyzw=tuple(float(value) for value in base_orientation),
                sample_kind="physics_step",
                sample_value=int(physics_step),
                sample_time_s=float(simulation_time_s),
                contract_revision=str(semantics.get("contract_revision") or "v1"),
            )
        except (TypeError, ValueError):
            return

        self._observation_plane.publish(body_pose_observation(sample, run_id=self._run_id))


    def _publish_canonical_joint_kinematics(
        self,
        *,
        physical_state: Mapping[str, object],
        physics_step: int,
        simulation_time_s: float,
    ) -> None:
        """Publish one co-sampled Body-local revolute-joint snapshot."""

        if self._observation_plane is None:
            return

        semantics = physical_state.get("joint_kinematics_semantics")
        if not isinstance(semantics, Mapping):
            return
        if semantics.get("joint_type") != "revolute":
            return
        if semantics.get("position_unit") != "rad":
            return
        if semantics.get("velocity_unit") != "rad/s":
            return
        if semantics.get("identity_scope") != "body_local":
            return

        body_id = self._identity(physical_state, "body_id")
        raw_joints = physical_state.get("joints")
        if body_id is None or not isinstance(raw_joints, (list, tuple)) or not raw_joints:
            return

        joints: list[JointKinematicState] = []
        try:
            for item in raw_joints:
                if not isinstance(item, Mapping):
                    return
                index = int(item["joint_index"])
                position = float(item["position"])
                velocity = float(item["velocity"])
                joints.append(
                    JointKinematicState(
                        joint_id=f"{body_id}:joint:{index}",
                        position_rad=position,
                        velocity_rad_s=velocity,
                    )
                )
            sample = JointKinematicsSample(
                body_id=body_id,
                joints=tuple(joints),
                sample_kind="physics_step",
                sample_value=int(physics_step),
                sample_time_s=float(simulation_time_s),
                contract_revision=str(semantics.get("contract_revision") or "v1"),
            )
        except (KeyError, TypeError, ValueError):
            return

        self._observation_plane.publish(
            joint_kinematics_observation(sample, run_id=self._run_id)
        )

    def publish_pose_frame(
        self,
        *,
        physical_state: Mapping[str, object],
        tick: int,
        substep_index: int,
        physics_step: int,
        simulation_time_s: float,
        tick_simulation_span_s: float,
        sampling_hz: float = 60.0,
    ) -> None:
        """Publish one lightweight observer-only physical pose frame."""
        if self._stop.is_set():
            return

        self._publish_canonical_body_pose(
            physical_state=physical_state,
            physics_step=physics_step,
            simulation_time_s=simulation_time_s,
        )
        self._publish_canonical_joint_kinematics(
            physical_state=physical_state,
            physics_step=physics_step,
            simulation_time_s=simulation_time_s,
        )

        descriptor = _body_descriptor_for_state(physical_state)
        joint_specs = descriptor.observer_joint_specs
        joints: list[dict[str, object]] = []

        raw_joints = physical_state.get("joints", ())
        if isinstance(raw_joints, (list, tuple)):
            for item in raw_joints:
                if not isinstance(item, Mapping):
                    continue
                try:
                    index = int(item.get("joint_index", -1))
                except (TypeError, ValueError):
                    continue
                name = (
                    joint_specs[index].name if 0 <= index < len(joint_specs) else f"joint_{index}"
                )
                try:
                    position = float(item["position"])
                except (KeyError, TypeError, ValueError):
                    continue
                joints.append({"name": name, "position": position})

        links: list[dict[str, object]] = []
        raw_links = physical_state.get("links", ())
        if isinstance(raw_links, (list, tuple)):
            for item in raw_links:
                if not isinstance(item, Mapping):
                    continue
                position = item.get("position")
                orientation = item.get("orientation")
                if (
                    item.get("link_name") is None
                    or not isinstance(position, (list, tuple))
                    or len(position) != 3
                    or not isinstance(orientation, (list, tuple))
                    or len(orientation) != 4
                ):
                    continue
                try:
                    links.append(
                        {
                            "name": str(item["link_name"]),
                            "position": [float(value) for value in position],
                            "orientation": [float(value) for value in orientation],
                        }
                    )
                except (TypeError, ValueError):
                    continue

        event: dict[str, Any] = {
            "type": "body_pose",
            "source": "physics3d",
            "body_kind": descriptor.body_kind,
            "tick": int(tick),
            "substep_index": int(substep_index),
            "physics_step": int(physics_step),
            "simulation_time_s": float(simulation_time_s),
            "tick_simulation_span_s": float(tick_simulation_span_s),
            "joints": joints,
            "links": links,
            "provenance": {
                "owner": "observer",
                "feeds_back": False,
                "sampling_hz": float(sampling_hz),
            },
        }
        self._apply_known_identity(event, physical_state)
        self._publish_canonical_body_pose(
            physical_state=physical_state,
            physics_step=physics_step,
            simulation_time_s=simulation_time_s,
        )
        base_position = physical_state.get("base_position")
        if isinstance(base_position, (list, tuple)) and len(base_position) == 3:
            event["base_position"] = [float(value) for value in base_position]
        base_orientation = physical_state.get("base_orientation")
        if isinstance(base_orientation, (list, tuple)) and len(base_orientation) == 4:
            event["base_orientation"] = [float(value) for value in base_orientation]

        center_of_mass = physical_state.get("center_of_mass")
        if isinstance(center_of_mass, (list, tuple)) and len(center_of_mass) == 3:
            try:
                event["center_of_mass"] = [float(value) for value in center_of_mass]
            except (TypeError, ValueError):
                pass

        raw_contacts = physical_state.get("contacts", ())
        contacts: list[dict[str, object]] = []
        if isinstance(raw_contacts, (list, tuple)):
            for item in raw_contacts:
                if not isinstance(item, Mapping):
                    continue
                position = item.get("position")
                normal = item.get("normal")
                if (
                    not isinstance(position, (list, tuple))
                    or len(position) != 3
                    or not isinstance(normal, (list, tuple))
                    or len(normal) != 3
                ):
                    continue
                try:
                    contacts.append(
                        {
                            "link_name": str(item.get("link_name", "")),
                            "position": [float(value) for value in position],
                            "normal": [float(value) for value in normal],
                            "normal_force": max(0.0, float(item.get("normal_force", 0.0))),
                        }
                    )
                except (TypeError, ValueError):
                    continue
        if contacts:
            event["contacts"] = contacts
        self._sink.push(event)

    def publish(self, snapshot: Any, *, physical_state: dict[str, object]) -> None:
        if self._stop.is_set():
            return

        if is_dataclass(snapshot) and not isinstance(snapshot, type):
            record = asdict(snapshot)
        elif isinstance(snapshot, Mapping):
            record = dict(snapshot)
        else:
            raise TypeError("Physics3D snapshot must be a dataclass or mapping")

        descriptor = _body_descriptor_for_state(physical_state)
        joint_specs = descriptor.observer_joint_specs
        joints: list[dict[str, object]] = []

        raw_joints = physical_state.get("joints", ())
        if isinstance(raw_joints, (list, tuple)):
            for item in raw_joints:
                if not isinstance(item, Mapping):
                    continue
                try:
                    index = int(item.get("joint_index", -1))
                except (TypeError, ValueError):
                    continue
                joint: dict[str, object] = {}
                if 0 <= index < len(joint_specs):
                    joint["name"] = joint_specs[index].name
                else:
                    joint["name"] = f"joint_{index}"
                if item.get("position") is not None:
                    try:
                        joint["position"] = float(item["position"])
                    except (TypeError, ValueError):
                        pass
                joints.append(joint)

        links: list[dict[str, object]] = []
        raw_links = physical_state.get("links", ())
        if isinstance(raw_links, (list, tuple)):
            for item in raw_links:
                if not isinstance(item, Mapping):
                    continue
                raw_position = item.get("position")
                raw_orientation = item.get("orientation")
                if (
                    item.get("link_name") is None
                    or not isinstance(raw_position, (list, tuple))
                    or len(raw_position) != 3
                    or not isinstance(raw_orientation, (list, tuple))
                    or len(raw_orientation) != 4
                ):
                    continue
                try:
                    links.append(
                        {
                            "name": str(item["link_name"]),
                            "position": [float(value) for value in raw_position],
                            "orientation": [float(value) for value in raw_orientation],
                        }
                    )
                except (TypeError, ValueError):
                    continue

        projected = {
            **record,
            "source": "physics3d",
            "run_id": self._run_id,
            "body_kind": descriptor.body_kind,
            "joints": joints,
            "links": links,
        }
        identity_source = {**record, **physical_state}
        self._apply_known_identity(projected, identity_source)
        if physical_state.get("base_position") is not None:
            projected["base_position"] = physical_state["base_position"]
        elif record.get("base_position") is not None:
            projected["base_position"] = record["base_position"]
        if physical_state.get("base_orientation") is not None:
            projected["base_orientation"] = physical_state["base_orientation"]
        elif record.get("base_orientation") is not None:
            projected["base_orientation"] = record["base_orientation"]

        raw_resource = physical_state.get("locomotion_resource")
        if isinstance(raw_resource, Mapping):
            position = raw_resource.get("position")
            if isinstance(position, (list, tuple)) and len(position) == 3:
                try:
                    projected["resource_position"] = [float(value) for value in position]
                except (TypeError, ValueError):
                    pass

        frame_tick = None
        try:
            frame_tick = int(projected.get("tick"))
        except (TypeError, ValueError):
            pass

        components: dict[str, Any] = {}
        for event in runtime_tick_events(projected):
            # Projection intentionally keeps its historical shape, but the
            # bridge is the canonical identity boundary. Seal every emitted
            # component with the same Lab/runtime identity as the coherent frame.
            self._apply_known_identity(event, projected)
            self._sink.push(event)
            event_type = str(event.get("type") or "")
            if event_type:
                components[event_type] = dict(event)
        if frame_tick is not None:
            self._pending_frames[frame_tick] = components
            # Rendering is deliberately sparse, so only a tiny number of
            # not-yet-paired frames should ever exist.
            for stale_tick in sorted(self._pending_frames)[:-4]:
                self._pending_frames.pop(stale_tick, None)

    def publish_rich_state(self, rich_state: Mapping[str, Any]) -> None:
        if self._stop.is_set():
            return
        world = project_world_scene(rich_state)
        if world is not None:
            world_event = self._world_publisher.event(world)
            self._apply_known_identity(world_event, rich_state)
            self._sink.push(world_event)
        snapshot = mind_snapshot_from_rich_state(rich_state)
        tick = snapshot.get("tick")
        try:
            frame_tick = int(tick)
        except (TypeError, ValueError):
            frame_tick = None

        mind_event: dict[str, Any] = {
            "type": "mind_snapshot",
            "source": "physics3d",
            "tick": tick,
            "snapshot": snapshot,
            "coherent_frame_follows": frame_tick is not None,
        }
        self._apply_known_identity(mind_event, rich_state)
        instance_id = _optional_text(rich_state, "instance_id")
        if instance_id is not None:
            mind_event["instance_id"] = instance_id
        topology_revision = _topology_revision(rich_state)
        if topology_revision is not None:
            mind_event["topology_revision"] = topology_revision
        self._sink.push(mind_event)

        if frame_tick is None:
            return
        components = self._pending_frames.pop(frame_tick, {})
        frame = ObservedFrame(
            tick=frame_tick,
            source="physics3d",
            run_id=self._run_id,
            organism_id=self._identity(rich_state, "organism_id"),
            instance_id=_optional_text(rich_state, "instance_id"),
            body_id=self._identity(rich_state, "body_id"),
            embodiment_id=self._identity(rich_state, "embodiment_id"),
            topology_revision=topology_revision,
            body=components.get("body"),
            cognition=components.get("cognition"),
            vitals=components.get("vitals"),
            mind=snapshot,
        )
        self._sink.push(frame.as_event())

    def close(self) -> None:
        self.request_stop()

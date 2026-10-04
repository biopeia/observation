"""Read-only spatial truth adapter. Never a world model given to Symbiont."""

from __future__ import annotations

from copy import deepcopy
from uuid import uuid4


class PhysicsWorldObserver:
    """Session-scoped IDs; geometry comes from the active collision engine."""

    def __init__(self) -> None:
        self.world_id = f"physics3d.{uuid4().hex}"
        self._ids: dict[str, str] = {}
        self._next_id = 0

    def capture(self, runtime) -> dict:
        scene = runtime.scene
        model, data = scene.model, scene.data
        own = runtime.apparatus.body_ids
        geoms_by_body: dict[int, list[int]] = {}
        for geom in range(int(model.ngeom)):
            geoms_by_body.setdefault(int(model.geom_bodyid[geom]), []).append(geom)
        # Entities are keyed by engine body name, which survives a scene rebuild.
        native = {
            body: scene.mj.mj_id2name(model, scene.mj.mjtObj.mjOBJ_BODY, body)
            for body in geoms_by_body
            if body not in own
        }
        for removed in set(self._ids) - set(native.values()):
            del self._ids[removed]
        for body in sorted(native):
            if native[body] not in self._ids:
                self._ids[native[body]] = f"entity.{self._next_id}"
                self._next_id += 1
        resource_body = runtime.resource.body_id
        entities = {}
        for body in sorted(native):
            shapes = []
            for geom in geoms_by_body[body]:
                kind = scene.mj.mjtGeom(int(model.geom_type[geom])).name.removeprefix("mjGEOM_")
                size = [float(value) for value in model.geom_size[geom]]
                w, x, y, z = (float(value) for value in model.geom_quat[geom])
                shapes.append(
                    {
                        "kind": kind.lower(),
                        # Full extents for a box, radius for a sphere,
                        # (length, radius) for a cylinder or capsule.
                        "dimensions": {
                            "BOX": [2.0 * value for value in size],
                            "SPHERE": [size[0]] * 3,
                            "CYLINDER": [2.0 * size[1], size[0], 0.0],
                            "CAPSULE": [2.0 * size[1], size[0], 0.0],
                        }.get(kind, size),
                        "position": [float(value) for value in model.geom_pos[geom]],
                        "orientation": [x, y, z, w],
                    }
                )
            w, x, y, z = (float(value) for value in data.xquat[body])
            eid = self._ids[native[body]]
            entity = {
                "id": eid,
                "position": [float(value) for value in data.xpos[body]],
                "orientation": [x, y, z, w],
                "shapes": shapes,
                "exists": True,
                "material": {
                    "mass": float(model.body_mass[body]),
                    "lateral_friction": float(model.geom_friction[geoms_by_body[body][0]][0]),
                },
                "provenance": "physics-collision-geometry",
            }
            if body == resource_body:
                entity["field"] = {
                    "radius": runtime.resource.field_radius,
                    "active": runtime.resource.remaining > 0,
                    "form": "isotropic-scalar",
                }
            entities[eid] = entity
        descriptor = runtime.body_descriptor
        specs = descriptor.observer_joint_specs
        regions = descriptor.observer_contact_region_names
        # Joint names and link attachments are apparatus facts, not cognitive names.
        joint_links = {
            item.joint_name: item.child_link for item in descriptor.observer_joint_topology
        }
        receptors = {}
        ordinal = 0
        for spec in specs:
            for channel in ("angle", "angular_velocity"):
                receptors[f"rec.{ordinal}"] = {
                    "modality": "proprioception",
                    "joint": spec.name,
                    "link": joint_links.get(spec.name),
                    "channel": channel,
                }
                ordinal += 1
        for _ in range(10):
            receptors[f"rec.{ordinal}"] = {"modality": "kinematics", "link": None}
            ordinal += 1
        for region in regions:
            receptors[f"rec.{ordinal}"] = {"modality": "contact", "link": region}
            ordinal += 1
        receptors[f"rec.{ordinal}"] = {
            "modality": "scalar_field",
            "link": None,
            "source_entity_id": self._ids[native[resource_body]],
            "source_attribution": "observer-only; no direction or object identity sensed",
        }
        ordinal += 1
        for region in regions:
            receptors[f"rec.{ordinal}"] = {"modality": "contact_load", "link": region}
            ordinal += 1
        contacts = []
        for i, item in enumerate(runtime.apparatus.contact_details()):
            other = item["other_body_id"]
            # A contact between two of the organism's links is listed once per link.
            if other in own and item["link_name"] > str(item["other_link_name"]):
                continue
            contacts.append(
                {
                    "id": f"contact.{i}",
                    "link": item["link_name"],
                    "entity_id": self._ids.get(native.get(other)),
                    "self_contact": other in own,
                    "position": item["position"],
                    "normal": item["normal"],
                    "normal_force": item["normal_force"],
                    "phase": "post-action",
                }
            )
        return {
            "world_id": self.world_id,
            "entities": entities,
            "receptors": receptors,
            "contacts": contacts,
            "coordinates": {"up": "z", "units": "metres", "quaternion": "xyzw"},
            "environment": "physics3d",
            "environment_recipe": deepcopy(getattr(runtime, "environment_recipe", None)),
            "provenance": {"owner": "observer", "feeds_back": False},
        }

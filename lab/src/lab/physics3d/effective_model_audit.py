"""Read-only audit of declared Physics3D apparatus against compiled MuJoCo truth.

The audit never mutates MjSpec, MjModel, MjData or sensor state. It records
source declarations, compiled values and the relationship between them.
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
from dataclasses import asdict, dataclass
from typing import Any, Mapping, Sequence

from embodiment.physics3d.articulated import ArticulatedBodySpec
from embodiment.physics3d.mechanics import SurfaceMaterial

AUDIT_SCHEMA_VERSION = 1


@dataclass(frozen=True, slots=True)
class AuditFinding:
    path: str
    declared: object
    effective: object
    relation: str
    severity: str
    note: str = ""

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def _plain(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if hasattr(value, "tolist"):
        return _plain(value.tolist())
    if isinstance(value, Mapping):
        return {
            str(key): _plain(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_plain(item) for item in value]
    try:
        return int(value)
    except (TypeError, ValueError):
        return str(value)


def _same(left: object, right: object, tolerance: float = 1e-9) -> bool:
    if isinstance(left, bool) or isinstance(right, bool):
        return left == right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return math.isclose(float(left), float(right), rel_tol=tolerance, abs_tol=tolerance)
    if isinstance(left, Sequence) and not isinstance(left, (str, bytes)):
        if not isinstance(right, Sequence) or isinstance(right, (str, bytes)):
            return False
        return len(left) == len(right) and all(_same(a, b, tolerance) for a, b in zip(left, right))
    return left == right


def _finding(
    path: str,
    declared: object,
    effective: object,
    relation: str,
    severity: str = "info",
    note: str = "",
) -> AuditFinding:
    return AuditFinding(path, _plain(declared), _plain(effective), relation, severity, note)


def _enum_name(value: Any) -> str:
    name = getattr(value, "name", None)
    return str(name) if name is not None else str(int(value))


def _name(scene: Any, kind: Any, identifier: int, fallback: str) -> str:
    value = scene.mj.mj_id2name(scene.model, kind, int(identifier))
    return str(value or f"{fallback}#{identifier}")


def _body_name(scene: Any, identifier: int) -> str:
    return _name(scene, scene.mj.mjtObj.mjOBJ_BODY, identifier, "body")


def _joint_name(scene: Any, identifier: int) -> str:
    return _name(scene, scene.mj.mjtObj.mjOBJ_JOINT, identifier, "joint")


def _geom_name(scene: Any, identifier: int) -> str:
    return _name(scene, scene.mj.mjtObj.mjOBJ_GEOM, identifier, "geom")


def _options(scene: Any) -> dict[str, object]:
    option = scene.model.opt
    enum_fields = {"integrator", "solver", "cone", "jacobian"}
    fields = (
        "timestep",
        "gravity",
        "integrator",
        "solver",
        "iterations",
        "ls_iterations",
        "tolerance",
        "ls_tolerance",
        "cone",
        "jacobian",
        "impratio",
        "density",
        "viscosity",
        "wind",
        "magnetic",
    )
    result: dict[str, object] = {}
    for field in fields:
        if not hasattr(option, field):
            continue
        value = getattr(option, field)
        result[field] = _enum_name(value) if field in enum_fields else _plain(value)
    return result


def _inventory(scene: Any) -> dict[str, object]:
    model = scene.model
    bodies = []
    for identifier in range(int(model.nbody)):
        bodies.append(
            {
                "id": identifier,
                "name": _body_name(scene, identifier),
                "mass": float(model.body_mass[identifier]),
                "inertia": _plain(model.body_inertia[identifier]),
                "inertial_position": _plain(model.body_ipos[identifier]),
                "dof_count": int(model.body_dofnum[identifier]),
                "mocap_id": int(model.body_mocapid[identifier]),
            }
        )
    joints = []
    for identifier in range(int(model.njnt)):
        dof = int(model.jnt_dofadr[identifier])
        joints.append(
            {
                "id": identifier,
                "name": _joint_name(scene, identifier),
                "type": _enum_name(scene.mj.mjtJoint(int(model.jnt_type[identifier]))),
                "limited": bool(model.jnt_limited[identifier]),
                "range": _plain(model.jnt_range[identifier]),
                "dof_damping": float(model.dof_damping[dof]) if dof < int(model.nv) else None,
                "solref_limit": _plain(model.jnt_solref[identifier]),
                "solimp_limit": _plain(model.jnt_solimp[identifier]),
            }
        )
    geoms = []
    for identifier in range(int(model.ngeom)):
        body = int(model.geom_bodyid[identifier])
        geoms.append(
            {
                "id": identifier,
                "name": _geom_name(scene, identifier),
                "body": _body_name(scene, body),
                "type": _enum_name(scene.mj.mjtGeom(int(model.geom_type[identifier]))),
                "size": _plain(model.geom_size[identifier]),
                "position": _plain(model.geom_pos[identifier]),
                "friction": _plain(model.geom_friction[identifier]),
                "rgba": _plain(model.geom_rgba[identifier]),
                "contype": int(model.geom_contype[identifier]),
                "conaffinity": int(model.geom_conaffinity[identifier]),
            }
        )
    return {
        "counts": {
            "nbody": int(model.nbody),
            "njnt": int(model.njnt),
            "ngeom": int(model.ngeom),
            "nq": int(model.nq),
            "nv": int(model.nv),
            "nu": int(model.nu),
        },
        "options": _options(scene),
        "bodies": bodies,
        "joints": joints,
        "geoms": geoms,
    }


def _scene_findings(scene: Any, timestep: float, gravity: Sequence[float]) -> list[AuditFinding]:
    options = _options(scene)
    findings = [
        _finding(
            "scene.timestep",
            timestep,
            options.get("timestep"),
            "exact" if _same(timestep, options.get("timestep")) else "mismatch",
            "info" if _same(timestep, options.get("timestep")) else "error",
        ),
        _finding(
            "scene.gravity",
            list(gravity),
            options.get("gravity"),
            "exact" if _same(list(gravity), options.get("gravity")) else "mismatch",
            "info" if _same(list(gravity), options.get("gravity")) else "error",
        ),
    ]
    for field in (
        "integrator",
        "solver",
        "iterations",
        "ls_iterations",
        "tolerance",
        "ls_tolerance",
        "cone",
        "jacobian",
        "impratio",
    ):
        if field in options:
            findings.append(
                _finding(
                    f"scene.{field}",
                    None,
                    options[field],
                    "implicit",
                    "warning",
                    "Effective value comes from the pinned MuJoCo version default, not PhysicsScene.",
                )
            )
    return findings


def _joint_findings(scene: Any, spec: ArticulatedBodySpec) -> list[AuditFinding]:
    model = scene.model
    findings: list[AuditFinding] = []
    for source in spec.joint_specs:
        identifier = scene.name_to_id("joint", f"body.{source.name}")
        dof = int(model.jnt_dofadr[identifier])
        effective_range = [float(value) for value in model.jnt_range[identifier]]
        span = source.upper - source.lower
        guard = min(math.radians(2.0), span * 0.1)
        expected_range = [source.lower + guard, source.upper - guard]
        range_ok = _same(expected_range, effective_range, 1e-6)
        damping = float(model.dof_damping[dof])
        damping_ok = _same(source.passive_damping, damping, 1e-7)
        findings.extend(
            [
                _finding(
                    f"joint.{source.name}.range",
                    [source.lower, source.upper],
                    effective_range,
                    "transformed" if range_ok else "mismatch",
                    "info" if range_ok else "error",
                    "Anatomical range is deterministically inset by the mechanical guard.",
                ),
                _finding(
                    f"joint.{source.name}.passive_damping",
                    source.passive_damping,
                    damping,
                    "exact" if damping_ok else "mismatch",
                    "info" if damping_ok else "error",
                    "Expected in mjModel.dof_damping.",
                ),
                _finding(
                    f"joint.{source.name}.max_motor_torque",
                    source.max_motor_torque,
                    None,
                    "runtime",
                    note="Bounded in apply_effectors and written through qfrc_applied; no MuJoCo actuator exists.",
                ),
                _finding(
                    f"joint.{source.name}.max_velocity",
                    source.max_velocity,
                    None,
                    "missing",
                    "warning",
                    "Declared in source/URDF but not enforced by current MuJoCo dynamics.",
                ),
                _finding(
                    f"joint.{source.name}.limit_solver",
                    "apparatus override",
                    {
                        "solref": _plain(model.jnt_solref[identifier]),
                        "solimp": _plain(model.jnt_solimp[identifier]),
                    },
                    "transformed",
                    note="Near-rigid limit response is applied after URDF import.",
                ),
            ]
        )
    return findings


def _segment_findings(scene: Any, spec: ArticulatedBodySpec) -> list[AuditFinding]:
    model = scene.model
    findings: list[AuditFinding] = []
    for name, source in sorted(spec.segments.items()):
        identifier = scene.name_to_id("body", f"body.{name}")
        mass = float(model.body_mass[identifier])
        mass_ok = _same(source.mass, mass, 1e-6)
        findings.extend(
            [
                _finding(
                    f"segment.{name}.mass",
                    source.mass,
                    mass,
                    "exact" if mass_ok else "mismatch",
                    "info" if mass_ok else "error",
                    "Compiled mass read directly from mjModel.",
                ),
                _finding(
                    f"segment.{name}.compiled_inertia",
                    {"size": source.size, "origin": source.origin},
                    {
                        "inertia": _plain(model.body_inertia[identifier]),
                        "inertial_position": _plain(model.body_ipos[identifier]),
                    },
                    "transformed",
                    note="Source geometry/inertial declaration becomes MuJoCo principal-inertia form.",
                ),
            ]
        )
    return findings


def _material_findings(
    path: str,
    material: Any,
    effective_friction: Sequence[float] | Sequence[Sequence[float]] | None,
) -> list[AuditFinding]:
    expected = [material.lateral_friction, material.spinning_friction, material.rolling_friction]
    if effective_friction is None:
        friction_ok = False
    elif effective_friction and isinstance(effective_friction[0], Sequence):
        friction_ok = all(_same(expected, item, 1e-7) for item in effective_friction)
    else:
        friction_ok = _same(expected, effective_friction, 1e-7)
    findings = [
        _finding(
            f"{path}.friction",
            expected,
            effective_friction,
            "exact" if friction_ok else "mismatch",
            "info" if friction_ok else "error",
        )
    ]
    for field in ("restitution", "linear_damping", "angular_damping"):
        findings.append(
            _finding(
                f"{path}.{field}",
                getattr(material, field),
                None,
                "missing",
                "warning",
                "Declared material field has no active mapping into the MuJoCo model.",
            )
        )
    return findings


def _body_material_findings(scene: Any, spec: ArticulatedBodySpec) -> list[AuditFinding]:
    values = [
        [float(value) for value in scene.model.geom_friction[geom]]
        for geom in range(int(scene.model.ngeom))
        if _body_name(scene, int(scene.model.geom_bodyid[geom])).startswith("body.")
    ]
    return _material_findings("material.body", spec.body_material, values)


def _ground_findings(scene: Any, material: SurfaceMaterial) -> list[AuditFinding]:
    try:
        identifier = scene.name_to_id("geom", "ground")
    except KeyError:
        return [_finding("material.ground", asdict(material), None, "missing", "error", "Ground geom is absent.")]
    friction = [float(value) for value in scene.model.geom_friction[identifier]]
    return _material_findings("material.ground", material, friction)


def _resource_findings(scene: Any, resource: Any | None) -> list[AuditFinding]:
    if resource is None:
        return []
    from environment.physics3d.resource import RESOURCE_MATERIAL

    geoms = [
        geom
        for geom in range(int(scene.model.ngeom))
        if _body_name(scene, int(scene.model.geom_bodyid[geom])) == resource.BODY_NAME
    ]
    friction = [float(value) for value in scene.model.geom_friction[geoms[0]]] if geoms else None
    return _material_findings("material.resource", RESOURCE_MATERIAL, friction)


def _environment_findings(scene: Any, recipe: Mapping[str, Any] | None) -> list[AuditFinding]:
    if recipe is None:
        return []
    findings: list[AuditFinding] = []
    for index, fixture in enumerate(recipe.get("fixtures", [])):
        body_name = f"fixture.{index}"
        geoms = [
            geom
            for geom in range(int(scene.model.ngeom))
            if _body_name(scene, int(scene.model.geom_bodyid[geom])) == body_name
        ]
        if not geoms:
            findings.append(_finding(f"environment.{body_name}", fixture, None, "missing", "error"))
            continue
        geom = geoms[0]
        if fixture.get("motion"):
            masks = {
                "contype": int(scene.model.geom_contype[geom]),
                "conaffinity": int(scene.model.geom_conaffinity[geom]),
            }
            ok = masks == {"contype": 0, "conaffinity": 0}
            findings.append(
                _finding(
                    f"environment.{body_name}.collision",
                    {"contype": 0, "conaffinity": 0},
                    masks,
                    "exact" if ok else "mismatch",
                    "info" if ok else "error",
                    "Moving visual sources must be non-colliding.",
                )
            )
            continue
        friction = [float(value) for value in scene.model.geom_friction[geom]]
        lateral_ok = _same(fixture.get("friction"), friction[0], 1e-7)
        findings.extend(
            [
                _finding(
                    f"environment.{body_name}.lateral_friction",
                    fixture.get("friction"),
                    friction[0],
                    "exact" if lateral_ok else "mismatch",
                    "info" if lateral_ok else "error",
                ),
                _finding(
                    f"environment.{body_name}.other_friction",
                    None,
                    friction[1:],
                    "implicit",
                    "warning",
                    "Recipe declares only lateral friction; torsional/rolling components remain defaults.",
                ),
            ]
        )
    return findings


def _vision_findings(apparatus: Any) -> list[AuditFinding]:
    visual = getattr(apparatus, "visual_apparatus", None)
    if visual is None:
        return []
    from modality.vision import AMBIENT_FRACTION, BACKGROUND_LUMINANCE, LIGHT_DIRECTION

    topology_count = len(getattr(visual.topology, "neighbours", {}))
    receptor_count = len(visual.receptor_ids)
    return [
        _finding(
            "vision.receptor_topology",
            receptor_count,
            topology_count,
            "exact" if receptor_count == topology_count else "mismatch",
            "info" if receptor_count == topology_count else "error",
            "Checks topology completeness without sampling or mutating the sensor.",
        ),
        _finding("vision.background_luminance", None, BACKGROUND_LUMINANCE, "provisional", "warning", "Pending apparatus qualification."),
        _finding("vision.ambient_fraction", None, AMBIENT_FRACTION, "provisional", "warning", "Pending apparatus qualification."),
        _finding("vision.light_direction", None, LIGHT_DIRECTION, "provisional", "warning", "Pending apparatus qualification."),
    ]


def audit_effective_model(
    *,
    scene: Any,
    apparatus: Any,
    body_spec: ArticulatedBodySpec,
    declared_timestep: float,
    declared_gravity: Sequence[float],
    ground_material: SurfaceMaterial,
    resource: Any | None = None,
    environment_recipe: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    """Return a deterministic JSON-safe audit for one already compiled scene."""
    findings = [
        *_scene_findings(scene, declared_timestep, declared_gravity),
        *_joint_findings(scene, body_spec),
        *_segment_findings(scene, body_spec),
        *_body_material_findings(scene, body_spec),
        *_ground_findings(scene, ground_material),
        *_resource_findings(scene, resource),
        *_environment_findings(scene, environment_recipe),
        *_vision_findings(apparatus),
    ]
    findings.sort(key=lambda item: item.path)
    summary = {
        "total": len(findings),
        "errors": sum(item.severity == "error" for item in findings),
        "warnings": sum(item.severity == "warning" for item in findings),
        **{
            relation: sum(item.relation == relation for item in findings)
            for relation in (
                "exact",
                "transformed",
                "runtime",
                "implicit",
                "missing",
                "provisional",
                "mismatch",
            )
        },
    }
    report: dict[str, object] = {
        "schema_version": AUDIT_SCHEMA_VERSION,
        "body_kind": body_spec.body_kind,
        "engine": {
            "name": "mujoco",
            "version": str(getattr(scene.mj, "__version__", "unknown")),
        },
        "host": {"python": platform.python_version(), "platform": platform.platform()},
        "model": _inventory(scene),
        "findings": [item.as_dict() for item in findings],
        "summary": summary,
    }
    canonical = json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    report["report_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return report


def report_json(report: Mapping[str, object], *, pretty: bool = True) -> str:
    if pretty:
        return json.dumps(report, sort_keys=True, indent=2) + "\n"
    return json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n"


__all__ = ["AUDIT_SCHEMA_VERSION", "AuditFinding", "audit_effective_model", "report_json"]

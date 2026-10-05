"""Read-only audit of declared Physics3D apparatus against compiled MuJoCo truth.

The audit deliberately does not mutate ``MjSpec``, ``MjModel`` or ``MjData``.
It records what source declarations say, what MuJoCo actually compiled, and
whether the relationship is exact, transformed, implicit, or missing.

This is apparatus instrumentation, not organism input and not calibration.
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping, Sequence

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
    note: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def _plain(value: Any) -> Any:
    """Convert numpy/MuJoCo values into deterministic JSON-compatible values."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if hasattr(value, "tolist"):
        return _plain(value.tolist())
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_plain(item) for item in value]
    try:
        return int(value)
    except (TypeError, ValueError):
        return str(value)


def _same_number(left: object, right: object, *, tolerance: float = 1e-9) -> bool:
    if isinstance(left, bool) or isinstance(right, bool):
        return left == right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return math.isclose(float(left), float(right), rel_tol=tolerance, abs_tol=tolerance)
    return left == right


def _same_sequence(left: Sequence[object], right: Sequence[object], *, tolerance: float = 1e-9) -> bool:
    return len(left) == len(right) and all(
        _same_number(a, b, tolerance=tolerance) for a, b in zip(left, right)
    )


def _finding(
    path: str,
    declared: object,
    effective: object,
    *,
    relation: str,
    severity: str = "info",
    note: str = "",
) -> AuditFinding:
    return AuditFinding(
        path=path,
        declared=_plain(declared),
        effective=_plain(effective),
        relation=relation,
        severity=severity,
        note=note,
    )


def _enum_name(value: Any) -> str:
    name = getattr(value, "name", None)
    return str(name) if name is not None else str(int(value))


def _option_snapshot(scene: Any) -> dict[str, object]:
    option = scene.model.opt
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
        if field in {"integrator", "solver", "cone", "jacobian"}:
            result[field] = _enum_name(value)
        else:
            result[field] = _plain(value)
    return result


def _body_name(scene: Any, body_id: int) -> str:
    name = scene.mj.mj_id2name(scene.model, scene.mj.mjtObj.mjOBJ_BODY, int(body_id))
    return str(name or f"body#{body_id}")


def _joint_name(scene: Any, joint_id: int) -> str:
    name = scene.mj.mj_id2name(scene.model, scene.mj.mjtObj.mjOBJ_JOINT, int(joint_id))
    return str(name or f"joint#{joint_id}")


def _geom_name(scene: Any, geom_id: int) -> str:
    name = scene.mj.mj_id2name(scene.model, scene.mj.mjtObj.mjOBJ_GEOM, int(geom_id))
    return str(name or f"geom#{geom_id}")


def _model_inventory(scene: Any) -> dict[str, object]:
    model = scene.model
    joints: list[dict[str, object]] = []
    for joint_id in range(int(model.njnt)):
        dof = int(model.jnt_dofadr[joint_id])
        joints.append(
            {
                "id": joint_id,
                "name": _joint_name(scene, joint_id),
                "type": _enum_name(scene.mj.mjtJoint(int(model.jnt_type[joint_id]))),
                "limited": bool(model.jnt_limited[joint_id]),
                "range": _plain(model.jnt_range[joint_id]),
                "dof_damping": float(model.dof_damping[dof]) if dof < int(model.nv) else None,
                "solref_limit": _plain(model.jnt_solref[joint_id]),
                "solimp_limit": _plain(model.jnt_solimp[joint_id]),
            }
        )

    bodies: list[dict[str, object]] = []
    for body_id in range(int(model.nbody)):
        bodies.append(
            {
                "id": body_id,
                "name": _body_name(scene, body_id),
                "mass": float(model.body_mass[body_id]),
                "inertia": _plain(model.body_inertia[body_id]),
                "inertial_position": _plain(model.body_ipos[body_id]),
                "dof_count": int(model.body_dofnum[body_id]),
                "mocap_id": int(model.body_mocapid[body_id]),
            }
        )

    geoms: list[dict[str, object]] = []
    for geom_id in range(int(model.ngeom)):
        body_id = int(model.geom_bodyid[geom_id])
        geoms.append(
            {
                "id": geom_id,
                "name": _geom_name(scene, geom_id),
                "body": _body_name(scene, body_id),
                "type": _enum_name(scene.mj.mjtGeom(int(model.geom_type[geom_id]))),
                "size": _plain(model.geom_size[geom_id]),
                "position": _plain(model.geom_pos[geom_id]),
                "friction": _plain(model.geom_friction[geom_id]),
                "rgba": _plain(model.geom_rgba[geom_id]),
                "contype": int(model.geom_contype[geom_id]),
                "conaffinity": int(model.geom_conaffinity[geom_id]),
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
        "options": _option_snapshot(scene),
        "bodies": bodies,
        "joints": joints,
        "geoms": geoms,
    }


def _joint_findings(scene: Any, spec: ArticulatedBodySpec) -> list[AuditFinding]:
    findings: list[AuditFinding] = []
    model = scene.model
    for source in spec.joint_specs:
        name = f"body.{source.name}"
        joint_id = scene.name_to_id("joint", name)
        dof = int(model.jnt_dofadr[joint_id])
        effective_range = [float(value) for value in model.jnt_range[joint_id]]
        span = source.upper - source.lower
        guard = min(math.radians(2.0), span * 0.1)
        expected_range = [source.lower + guard, source.upper - guard]
        findings.append(
            _finding(
                f"joint.{source.name}.range",
                [source.lower, source.upper],
                effective_range,
                relation="transformed" if _same_sequence(expected_range, effective_range, tolerance=1e-6) else "mismatch",
                severity="info" if _same_sequence(expected_range, effective_range, tolerance=1e-6) else "error",
                note="Canonical anatomical range is inset by the mechanical guard before compilation.",
            )
        )
        effective_damping = float(model.dof_damping[dof])
        findings.append(
            _finding(
                f"joint.{source.name}.passive_damping",
                source.passive_damping,
                effective_damping,
                relation="exact" if _same_number(source.passive_damping, effective_damping, tolerance=1e-7) else "mismatch",
                severity="info" if _same_number(source.passive_damping, effective_damping, tolerance=1e-7) else "error",
                note="Joint viscous damping is expected to be compiled into dof_damping.",
            )
        )
        findings.append(
            _finding(
                f"joint.{source.name}.max_motor_torque",
                source.max_motor_torque,
                None,
                relation="runtime",
                note="Motor torque is enforced by apply_effectors through qfrc_applied; there is no MuJoCo actuator.",
            )
        )
        findings.append(
            _finding(
                f"joint.{source.name}.max_velocity",
                source.max_velocity,
                None,
                relation="missing",
                severity="warning",
                note="Declared in the source/URDF but not enforced by the compiled MuJoCo dynamics.",
            )
        )
        findings.append(
            _finding(
                f"joint.{source.name}.limit_solver",
                "apparatus override",
                {
                    "solref": _plain(model.jnt_solref[joint_id]),
                    "solimp": _plain(model.jnt_solimp[joint_id]),
                },
                relation="transformed",
                note="Near-rigid anatomical stop parameters are applied after URDF import.",
            )
        )
    return findings


def _segment_findings(scene: Any, spec: ArticulatedBodySpec) -> list[AuditFinding]:
    findings: list[AuditFinding] = []
    model = scene.model
    for name, source in sorted(spec.segments.items()):
        body_id = scene.name_to_id("body", f"body.{name}")
        effective_mass = float(model.body_mass[body_id])
        findings.append(
            _finding(
                f"segment.{name}.mass",
                source.mass,
                effective_mass,
                relation="exact" if _same_number(source.mass, effective_mass, tolerance=1e-6) else "mismatch",
                severity="info" if _same_number(source.mass, effective_mass, tolerance=1e-6) else "error",
                note="Compiled body mass read directly from mjModel.",
            )
        )
        findings.append(
            _finding(
                f"segment.{name}.compiled_inertia",
                {"size": source.size, "origin": source.origin},
                {
                    "inertia": _plain(model.body_inertia[body_id]),
                    "inertial_position": _plain(model.body_ipos[body_id]),
                },
                relation="transformed",
                note="Inertia is generated from source geometry and then represented in MuJoCo principal-inertia form.",
            )
        )
    return findings


def _material_findings(scene: Any, spec: ArticulatedBodySpec) -> list[AuditFinding]:
    material = spec.body_material
    body_geoms = [
        geom_id
        for geom_id in range(int(scene.model.ngeom))
        if _body_name(scene, int(scene.model.geom_bodyid[geom_id])).startswith("body.")
    ]
    effective = [
        [float(value) for value in scene.model.geom_friction[geom_id]] for geom_id in body_geoms
    ]
    expected = [material.lateral_friction, material.spinning_friction, material.rolling_friction]
    relation = "exact" if effective and all(_same_sequence(expected, item, tolerance=1e-7) for item in effective) else "mismatch"
    findings = [
        _finding(
            "material.body.friction",
            expected,
            effective,
            relation=relation,
            severity="info" if relation == "exact" else "error",
            note="All body collision geoms should receive the declared three-component MuJoCo friction vector.",
        )
    ]
    for field in ("restitution", "linear_damping", "angular_damping"):
        findings.append(
            _finding(
                f"material.body.{field}",
                getattr(material, field),
                None,
                relation="missing",
                severity="warning",
                note="The field is declared by SurfaceMaterial but has no mapping into the active MuJoCo model.",
            )
        )
    return findings


def _scene_findings(scene: Any, *, declared_timestep: float, declared_gravity: Sequence[float]) -> list[AuditFinding]:
    options = _option_snapshot(scene)
    findings = [
        _finding(
            "scene.timestep",
            declared_timestep,
            options.get("timestep"),
            relation="exact" if _same_number(declared_timestep, options.get("timestep")) else "mismatch",
            severity="info" if _same_number(declared_timestep, options.get("timestep")) else "error",
        ),
        _finding(
            "scene.gravity",
            list(declared_gravity),
            options.get("gravity"),
            relation="exact"
            if isinstance(options.get("gravity"), list)
            and _same_sequence(list(declared_gravity), options["gravity"])
            else "mismatch",
            severity="info"
            if isinstance(options.get("gravity"), list)
            and _same_sequence(list(declared_gravity), options["gravity"])
            else "error",
        ),
    ]
    for field in ("integrator", "solver", "iterations", "ls_iterations", "tolerance", "ls_tolerance", "cone", "jacobian", "impratio"):
        if field in options:
            findings.append(
                _finding(
                    f"scene.{field}",
                    None,
                    options[field],
                    relation="implicit",
                    severity="warning",
                    note="Effective MuJoCo option is not explicitly selected by PhysicsScene and therefore comes from the pinned engine version default.",
                )
            )
    return findings


def _ground_findings(scene: Any, material: SurfaceMaterial) -> list[AuditFinding]:
    try:
        geom_id = scene.name_to_id("geom", "ground")
    except KeyError:
        return [_finding("material.ground", asdict(material), None, relation="missing", severity="warning", note="No ground geom in audited scene.")]
    effective = [float(value) for value in scene.model.geom_friction[geom_id]]
    expected = [material.lateral_friction, material.spinning_friction, material.rolling_friction]
    findings = [
        _finding(
            "material.ground.friction",
            expected,
            effective,
            relation="exact" if _same_sequence(expected, effective, tolerance=1e-7) else "mismatch",
            severity="info" if _same_sequence(expected, effective, tolerance=1e-7) else "error",
        )
    ]
    for field in ("restitution", "linear_damping", "angular_damping"):
        findings.append(
            _finding(
                f"material.ground.{field}",
                getattr(material, field),
                None,
                relation="missing",
                severity="warning",
                note="Declared ground material field has no active MuJoCo mapping.",
            )
        )
    return findings


def _resource_findings(scene: Any, resource: Any | None) -> list[AuditFinding]:
    if resource is None:
        return []
    from environment.physics3d.resource import RESOURCE_MATERIAL

    geoms = [
        geom_id
        for geom_id in range(int(scene.model.ngeom))
        if _body_name(scene, int(scene.model.geom_bodyid[geom_id])) == resource.BODY_NAME
    ]
    effective = [float(value) for value in scene.model.geom_friction[geoms[0]]] if geoms else None
    expected = [
        RESOURCE_MATERIAL.lateral_friction,
        RESOURCE_MATERIAL.spinning_friction,
        RESOURCE_MATERIAL.rolling_friction,
    ]
    findings = [
        _finding(
            "material.resource.friction",
            expected,
            effective,
            relation="exact" if effective is not None and _same_sequence(expected, effective, tolerance=1e-7) else "mismatch",
            severity="info" if effective is not None and _same_sequence(expected, effective, tolerance=1e-7) else "error",
        )
    ]
    for field in ("restitution", "linear_damping", "angular_damping"):
        findings.append(
            _finding(
                f"material.resource.{field}",
                getattr(RESOURCE_MATERIAL, field),
                None,
                relation="missing",
                severity="warning",
                note="Declared resource material field has no active MuJoCo mapping.",
            )
        )
    return findings


def _environment_findings(scene: Any, recipe: Mapping[str, Any] | None) -> list[AuditFinding]:
    if recipe is None:
        return []
    findings: list[AuditFinding] = []
    for index, fixture in enumerate(recipe.get("fixtures", [])):
        body_name = f"fixture.{index}"
        geoms = [
            geom_id
            for geom_id in range(int(scene.model.ngeom))
            if _body_name(scene, int(scene.model.geom_bodyid[geom_id])) == body_name
        ]
        if not geoms:
            findings.append(_finding(f"environment.{body_name}", fixture, None, relation="missing", severity="error"))
            continue
        geom = geoms[0]
        friction = [float(value) for value in scene.model.geom_friction[geom]]
        if fixture.get("motion"):
            findings.append(
                _finding(
                    f"environment.{body_name}.collision",
                    "visual-only kinematic source",
                    {"contype": int(scene.model.geom_contype[geom]), "conaffinity": int(scene.model.geom_conaffinity[geom])},
                    relation="exact" if int(scene.model.geom_contype[geom]) == 0 and int(scene.model.geom_conaffinity[geom]) == 0 else "mismatch",
                    severity="info" if int(scene.model.geom_contype[geom]) == 0 and int(scene.model.geom_conaffinity[geom]) == 0 else "error",
                )
            )
        else:
            findings.append(
                _finding(
                    f"environment.{body_name}.lateral_friction",
                    fixture.get("friction"),
                    friction[0],
                    relation="exact" if _same_number(fixture.get("friction"), friction[0], tolerance=1e-7) else "mismatch",
                    severity="info" if _same_number(fixture.get("friction"), friction[0], tolerance=1e-7) else "error",
                    note="Fixture recipe declares lateral friction only; torsional and rolling values remain engine defaults.",
                )
            )
            findings.append(
                _finding(
                    f"environment.{body_name}.other_friction",
                    None,
                    friction[1:],
                    relation="implicit",
                    severity="warning",
                    note="Torsional and rolling friction are not declared by the environment recipe.",
                )
            )
    return findings


def _vision_findings(apparatus: Any) -> list[AuditFinding]:
    visual = getattr(apparatus, "visual_apparatus", None)
    if visual is None:
        return []
    from modality.vision import AMBIENT_FRACTION, BACKGROUND_LUMINANCE, LIGHT_DIRECTION

    return [
        _finding("vision.background_luminance", None, BACKGROUND_LUMINANCE, relation="provisional", severity="warning", note="Provisional analytic vision constant pending apparatus qualification."),
        _finding("vision.ambient_fraction", None, AMBIENT_FRACTION, relation="provisional", severity="warning", note="Provisional analytic vision constant pending apparatus qualification."),
        _finding("vision.light_direction", None, LIGHT_DIRECTION, relation="provisional", severity="warning", note="Provisional analytic vision constant pending apparatus qualification."),
        _finding("vision.receptor_count", len(visual.receptor_ids), len(visual.sample()), relation="exact", note="One deterministic sample is used only to verify complete receptor coverage; it is not fed to an organism."),
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
    """Return a deterministic, JSON-safe audit report for one compiled scene."""
    findings = [
        *_scene_findings(scene, declared_timestep=declared_timestep, declared_gravity=declared_gravity),
        *_joint_findings(scene, body_spec),
        *_segment_findings(scene, body_spec),
        *_material_findings(scene, body_spec),
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
        "exact": sum(item.relation == "exact" for item in findings),
        "transformed": sum(item.relation == "transformed" for item in findings),
        "runtime": sum(item.relation == "runtime" for item in findings),
        "implicit": sum(item.relation == "implicit" for item in findings),
        "missing": sum(item.relation == "missing" for item in findings),
        "provisional": sum(item.relation == "provisional" for item in findings),
        "mismatch": sum(item.relation == "mismatch" for item in findings),
    }
    report: dict[str, object] = {
        "schema_version": AUDIT_SCHEMA_VERSION,
        "body_kind": body_spec.body_kind,
        "engine": {"name": "mujoco", "version": str(scene.mj.__version__)},
        "host": {"python": platform.python_version(), "platform": platform.platform()},
        "model": _model_inventory(scene),
        "findings": [item.as_dict() for item in findings],
        "summary": summary,
    }
    canonical = json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    report["report_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return report


def report_json(report: Mapping[str, object], *, pretty: bool = True) -> str:
    return json.dumps(report, sort_keys=True, indent=2 if pretty else None, separators=None if pretty else (",", ":")) + "\n"


__all__ = [
    "AUDIT_SCHEMA_VERSION",
    "AuditFinding",
    "audit_effective_model",
    "report_json",
]

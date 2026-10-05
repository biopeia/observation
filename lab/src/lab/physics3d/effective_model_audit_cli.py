"""CLI for auditing every canonical Physics3D apparatus against compiled MuJoCo truth."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Callable

from embodiment.physics3d.asymmetric import ASYMMETRIC_SPEC, AsymmetricPhysics
from embodiment.physics3d.crawler import CRAWLER_SPEC, CrawlerPhysics
from embodiment.physics3d.hexapod import HEXAPOD_SPEC, HexapodPhysics
from embodiment.physics3d.humanoid import ANTHROPOMORPHIC_SPEC, HumanoidPhysics
from embodiment.physics3d.mechanics import GROUND_MATERIAL
from embodiment.physics3d.robotic_arm import ROBOTIC_ARM_SPEC, RoboticArmPhysics
from embodiment.physics3d.scene import DEFAULT_GRAVITY, PhysicsScene
from embodiment.physics3d.vision import VisionHumanoidPhysics
from environment.physics3d.environments import ENVIRONMENT_NAMES, build_environment, environment_recipe
from environment.physics3d.resource import PhysicalResource
from lab.physics3d.effective_model_audit import audit_effective_model
from modality.vision import VisualApparatus

TIMESTEP = 1.0 / 240.0


def _vision_factory(scene: Any) -> VisionHumanoidPhysics:
    return VisionHumanoidPhysics(scene, receptor_array_factory=VisualApparatus)


BODY_CASES: dict[str, tuple[Any, Callable[[Any], Any]]] = {
    ANTHROPOMORPHIC_SPEC.body_kind: (ANTHROPOMORPHIC_SPEC, HumanoidPhysics),
    CRAWLER_SPEC.body_kind: (CRAWLER_SPEC, CrawlerPhysics),
    ASYMMETRIC_SPEC.body_kind: (ASYMMETRIC_SPEC, AsymmetricPhysics),
    HEXAPOD_SPEC.body_kind: (HEXAPOD_SPEC, HexapodPhysics),
    ROBOTIC_ARM_SPEC.body_kind: (ROBOTIC_ARM_SPEC, RoboticArmPhysics),
    "anthropomorphic-v6-vision": (ANTHROPOMORPHIC_SPEC, _vision_factory),
}


def _scenario(body_kind: str, environment_name: str) -> dict[str, object]:
    spec, factory = BODY_CASES[body_kind]
    scene = PhysicsScene(timestep=TIMESTEP, gravity=DEFAULT_GRAVITY)
    scene.add_ground(GROUND_MATERIAL)
    recipe = environment_recipe(environment_name)
    build_environment(scene, recipe)
    resource = PhysicalResource(scene)
    apparatus = factory(scene)
    report = audit_effective_model(
        scene=scene,
        apparatus=apparatus,
        body_spec=spec,
        declared_timestep=TIMESTEP,
        declared_gravity=DEFAULT_GRAVITY,
        ground_material=GROUND_MATERIAL,
        resource=resource,
        environment_recipe=recipe,
    )
    report["scenario"] = {
        "body_kind": body_kind,
        "environment": environment_name,
        "timestep": TIMESTEP,
        "gravity": list(DEFAULT_GRAVITY),
    }
    return report


def run(*, bodies: list[str], environments: list[str]) -> dict[str, object]:
    scenarios = [_scenario(body, environment) for body in bodies for environment in environments]
    summary = {
        "scenarios": len(scenarios),
        "errors": sum(int(item["summary"]["errors"]) for item in scenarios),
        "warnings": sum(int(item["summary"]["warnings"]) for item in scenarios),
        "mismatches": sum(int(item["summary"]["mismatch"]) for item in scenarios),
        "missing": sum(int(item["summary"]["missing"]) for item in scenarios),
        "implicit": sum(int(item["summary"]["implicit"]) for item in scenarios),
        "provisional": sum(int(item["summary"]["provisional"]) for item in scenarios),
    }
    result: dict[str, object] = {
        "schema_version": 1,
        "kind": "mujoco-effective-model-audit-suite",
        "bodies": bodies,
        "environments": environments,
        "scenarios": scenarios,
        "summary": summary,
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    result["suite_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return result


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--body",
        action="append",
        choices=sorted(BODY_CASES),
        help="Body kind to audit; repeatable. Defaults to every canonical body.",
    )
    parser.add_argument(
        "--environment",
        action="append",
        choices=sorted(ENVIRONMENT_NAMES),
        help="Environment to audit; repeatable. Defaults to every canonical environment.",
    )
    parser.add_argument("--output", type=Path, help="Write JSON here instead of stdout.")
    parser.add_argument(
        "--fail-on-mismatch",
        action="store_true",
        help="Exit 2 only when a declared-vs-effective mismatch is present.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    report = run(
        bodies=args.body or sorted(BODY_CASES),
        environments=args.environment or sorted(ENVIRONMENT_NAMES),
    )
    encoded = json.dumps(report, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    else:
        sys.stdout.write(encoded)
    if args.fail_on_mismatch and int(report["summary"]["mismatches"]) > 0:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

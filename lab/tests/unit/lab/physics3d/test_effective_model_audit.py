from __future__ import annotations

import copy
import json

import pytest

from embodiment.physics3d.crawler import CRAWLER_SPEC, CrawlerPhysics
from embodiment.physics3d.mechanics import GROUND_MATERIAL
from embodiment.physics3d.scene import DEFAULT_GRAVITY, PhysicsScene
from environment.physics3d.environments import build_environment, environment_recipe
from environment.physics3d.resource import PhysicalResource
from lab.physics3d.effective_model_audit import AUDIT_SCHEMA_VERSION, audit_effective_model, report_json


def _apparatus(environment_name: str = "contact-garden-v1"):
    pytest.importorskip("mujoco")
    scene = PhysicsScene(timestep=1.0 / 240.0, gravity=DEFAULT_GRAVITY)
    scene.add_ground(GROUND_MATERIAL)
    recipe = environment_recipe(environment_name)
    build_environment(scene, recipe)
    resource = PhysicalResource(scene)
    body = CrawlerPhysics(scene)
    return scene, recipe, resource, body


def _audit(environment_name: str = "contact-garden-v1"):
    scene, recipe, resource, body = _apparatus(environment_name)
    report = audit_effective_model(
        scene=scene,
        apparatus=body,
        body_spec=CRAWLER_SPEC,
        declared_timestep=1.0 / 240.0,
        declared_gravity=DEFAULT_GRAVITY,
        ground_material=GROUND_MATERIAL,
        resource=resource,
        environment_recipe=recipe,
    )
    return scene, body, report


def test_effective_model_audit_has_no_declared_compiled_mismatches() -> None:
    _scene, _body, report = _audit()

    assert report["schema_version"] == AUDIT_SCHEMA_VERSION
    assert report["body_kind"] == CRAWLER_SPEC.body_kind
    assert report["engine"]["name"] == "mujoco"
    assert report["summary"]["errors"] == 0
    assert report["summary"]["mismatch"] == 0
    assert len(report["report_sha256"]) == 64


def test_effective_model_audit_makes_known_contract_gaps_explicit() -> None:
    _scene, _body, report = _audit()
    by_path = {item["path"]: item for item in report["findings"]}

    assert by_path["joint.front_left_hip_yaw.max_velocity"]["relation"] == "missing"
    assert by_path["material.body.restitution"]["relation"] == "missing"
    assert by_path["material.body.linear_damping"]["relation"] == "missing"
    assert by_path["material.body.angular_damping"]["relation"] == "missing"
    assert by_path["scene.integrator"]["relation"] == "implicit"
    assert by_path["scene.solver"]["relation"] == "implicit"
    assert by_path["environment.fixture.0.other_friction"]["relation"] == "implicit"


def test_effective_model_audit_checks_compiled_mass_damping_and_friction() -> None:
    _scene, _body, report = _audit()
    by_path = {item["path"]: item for item in report["findings"]}

    assert by_path["segment.body.mass"]["relation"] == "exact"
    assert by_path["joint.front_left_hip_yaw.passive_damping"]["relation"] == "exact"
    assert by_path["material.body.friction"]["relation"] == "exact"
    assert by_path["material.ground.friction"]["relation"] == "exact"
    assert by_path["material.resource.friction"]["relation"] == "exact"


def test_effective_model_audit_does_not_mutate_mujoco_state() -> None:
    scene, recipe, resource, body = _apparatus()
    qpos_before = scene.data.qpos.copy()
    qvel_before = scene.data.qvel.copy()
    warmstart_before = scene.data.qacc_warmstart.copy()

    audit_effective_model(
        scene=scene,
        apparatus=body,
        body_spec=CRAWLER_SPEC,
        declared_timestep=1.0 / 240.0,
        declared_gravity=DEFAULT_GRAVITY,
        ground_material=GROUND_MATERIAL,
        resource=resource,
        environment_recipe=recipe,
    )

    assert scene.data.qpos.tolist() == qpos_before.tolist()
    assert scene.data.qvel.tolist() == qvel_before.tolist()
    assert scene.data.qacc_warmstart.tolist() == warmstart_before.tolist()


def test_report_encoding_is_stable_for_same_compiled_model() -> None:
    _scene, _body, first = _audit("flat-v1")
    _scene, _body, second = _audit("flat-v1")

    # Host and engine identity are part of the report, but two constructions in
    # the same process must still yield byte-identical canonical content.
    assert report_json(first, pretty=False) == report_json(second, pretty=False)
    assert json.loads(report_json(first))["report_sha256"] == first["report_sha256"]


def test_audit_report_is_detached_plain_data() -> None:
    _scene, _body, report = _audit()
    detached = copy.deepcopy(report)
    json.dumps(detached, sort_keys=True)

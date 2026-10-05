from __future__ import annotations

import pytest

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


def _vision(scene):
    return VisionHumanoidPhysics(scene, receptor_array_factory=VisualApparatus)


BODY_CASES = (
    (ANTHROPOMORPHIC_SPEC, HumanoidPhysics),
    (CRAWLER_SPEC, CrawlerPhysics),
    (ASYMMETRIC_SPEC, AsymmetricPhysics),
    (HEXAPOD_SPEC, HexapodPhysics),
    (ROBOTIC_ARM_SPEC, RoboticArmPhysics),
    (ANTHROPOMORPHIC_SPEC, _vision),
)


def _run(spec, factory, environment_name: str):
    pytest.importorskip("mujoco")
    scene = PhysicsScene(timestep=TIMESTEP, gravity=DEFAULT_GRAVITY)
    scene.add_ground(GROUND_MATERIAL)
    recipe = environment_recipe(environment_name)
    build_environment(scene, recipe)
    resource = PhysicalResource(scene)
    apparatus = factory(scene)
    return audit_effective_model(
        scene=scene,
        apparatus=apparatus,
        body_spec=spec,
        declared_timestep=TIMESTEP,
        declared_gravity=DEFAULT_GRAVITY,
        ground_material=GROUND_MATERIAL,
        resource=resource,
        environment_recipe=recipe,
    )


@pytest.mark.parametrize(("spec", "factory"), BODY_CASES)
def test_every_canonical_body_has_a_clean_declared_to_compiled_mapping(spec, factory) -> None:
    report = _run(spec, factory, "flat-v1")

    assert report["summary"]["errors"] == 0
    assert report["summary"]["mismatch"] == 0
    assert report["summary"]["missing"] > 0  # known, explicit contract gaps


@pytest.mark.parametrize("environment_name", ENVIRONMENT_NAMES)
def test_every_canonical_environment_is_auditable(environment_name: str) -> None:
    report = _run(CRAWLER_SPEC, CrawlerPhysics, environment_name)

    assert report["summary"]["errors"] == 0
    assert report["summary"]["mismatch"] == 0
    fixture_findings = [
        item for item in report["findings"] if str(item["path"]).startswith("environment.fixture.")
    ]
    if environment_recipe(environment_name)["fixtures"]:
        assert fixture_findings

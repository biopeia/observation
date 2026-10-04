from __future__ import annotations

import math

import pytest

from embodiment.physics3d.alternative_bodies import (
    ASYMMETRIC_SPEC,
    CRAWLER_SPEC,
    AsymmetricPhysics,
    CrawlerPhysics,
)
from embodiment.physics3d.articulated import build_articulated_urdf
from embodiment.physics3d.humanoid import ANTHROPOMORPHIC_SPEC, HumanoidPhysics


@pytest.mark.parametrize("spec", [CRAWLER_SPEC, ASYMMETRIC_SPEC])
def test_alternative_body_urdf_contains_exact_motor_constitution(spec) -> None:
    urdf = build_articulated_urdf(spec)

    assert urdf.count("<joint name=") == spec.motor_dof
    assert urdf.count('type="revolute"') == spec.motor_dof
    for joint in spec.joint_specs:
        assert f'name="{joint.name}"' in urdf


@pytest.mark.parametrize("spec", [CRAWLER_SPEC, ASYMMETRIC_SPEC])
def test_alternative_body_contract_dimensions_are_self_consistent(spec) -> None:
    assert spec.effector_count == spec.motor_dof * 2
    assert len(spec.effector_ids()) == spec.effector_count
    assert len(spec.receptor_ids()) == spec.total_receptor_count
    assert len(spec.interoceptive_receptor_ids()) == 4
    assert spec.total_receptor_count == (
        spec.motor_dof * 2 + 10 + spec.somatic_region_count * 2 + 1 + 4
    )


BODIES = [
    (CrawlerPhysics, CRAWLER_SPEC),
    (AsymmetricPhysics, ASYMMETRIC_SPEC),
    (HumanoidPhysics, ANTHROPOMORPHIC_SPEC),
]


def _scene():
    pytest.importorskip("mujoco")
    from embodiment.physics3d.scene import PhysicsScene

    scene = PhysicsScene(timestep=1.0 / 240.0)
    scene.spec.worldbody.add_geom(
        name="ground", type=scene.mj.mjtGeom.mjGEOM_PLANE, size=[0.0, 0.0, 1.0]
    )
    return scene


def _drive(scene, body, ticks: int, *, start: int = 0) -> None:
    """Deterministic, body-agnostic actuation: ten substeps per tick."""
    ports = body.effector_ids
    for tick in range(start, start + ticks):
        body.apply_effectors(
            {port: ((tick * 7 + index * 3) % 11) / 10.0 for index, port in enumerate(ports)}
        )
        for _ in range(10):
            body.prepare_physics_substep()
            scene.step()


@pytest.mark.parametrize(("body_cls", "spec"), BODIES)
def test_alternative_body_loads_headless(body_cls, spec) -> None:
    body = body_cls(_scene())
    assert len(body.motor_joint_indices) == spec.motor_dof
    assert len(body.effector_ids) == spec.effector_count
    assert len(body.receptor_ids) == spec.physical_receptor_count

    sampled = body.sample_receptors()
    assert tuple(sampled) == body.receptor_ids
    assert all(0.0 <= value <= 1.0 for value in sampled.values())
    checkpoint = body.export_physical_state()
    assert checkpoint["body_kind"] == spec.body_kind
    assert checkpoint["schema_version"] == spec.state_schema_version
    assert len(checkpoint["joints"]) == spec.motor_dof
    links = {spec.base_link_name, *(item.child_link for item in spec.joint_topology)}
    assert checkpoint["total_mass"] == pytest.approx(
        sum(spec.segments[name].mass if name in spec.segments else 0.05 for name in links)
    )


@pytest.mark.parametrize(("body_cls", "spec"), BODIES)
def test_alternative_body_settles_on_the_ground_without_exploding(body_cls, spec) -> None:
    scene = _scene()
    body = body_cls(scene)
    _drive(scene, body, 300)
    state = body.export_physical_state()
    assert all(abs(value) < 50.0 for value in state["base_position"])
    assert 0.0 < state["base_position"][2] < spec.spawn_height + 0.5
    assert state["contact_count"] > 0
    tolerance = math.radians(0.5)
    for joint, joint_spec in zip(state["joints"], spec.joint_specs):
        assert joint_spec.lower - tolerance <= joint["position"] <= joint_spec.upper + tolerance


@pytest.mark.parametrize(("body_cls", "spec"), BODIES)
def test_alternative_body_replays_identically(body_cls, spec) -> None:
    """ADR-0065: same seed, state and conditions give the same trajectory."""
    states = []
    for _ in range(2):
        scene = _scene()
        body = body_cls(scene)
        _drive(scene, body, 200)
        states.append((body.export_physical_state(), body.sample_receptors()))
    assert states[0] == states[1]


@pytest.mark.parametrize(("body_cls", "spec"), BODIES)
def test_alternative_body_checkpoint_restores_the_exact_state(body_cls, spec) -> None:
    """ADR-0066 decision 5: run N equals run k, save, restore into a new world, run N-k."""
    import json

    straight_scene = _scene()
    straight = body_cls(straight_scene)
    _drive(straight_scene, straight, 200)

    first_scene = _scene()
    first = body_cls(first_scene)
    _drive(first_scene, first, 120)
    saved = json.loads(json.dumps(first.export_physical_state()))

    second_scene = _scene()
    second = body_cls(second_scene)
    second.restore_physical_state(saved)
    assert second.export_physical_state()["engine_state"] == saved["engine_state"]
    _drive(second_scene, second, 80, start=120)

    assert second.export_physical_state() == straight.export_physical_state()


def test_body_state_without_engine_state_is_rejected() -> None:
    body = CrawlerPhysics(_scene())
    state = body.export_physical_state()
    del state["engine_state"]
    with pytest.raises(ValueError, match="no engine state"):
        body.restore_physical_state(state)

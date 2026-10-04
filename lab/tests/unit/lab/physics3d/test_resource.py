from __future__ import annotations

import pytest

from embodiment.physics3d.humanoid import HumanoidPhysics
from environment.physics3d.resource import PhysicalResource


@pytest.fixture
def scene():
    pytest.importorskip("mujoco")
    from embodiment.physics3d.scene import PhysicsScene

    return PhysicsScene(timestep=1.0 / 240.0, gravity=(0.0, 0.0, 0.0))


def test_resource_field_is_local_scalar_and_extinguishes_when_depleted(scene):
    resource = PhysicalResource(
        scene,
        position=(2.0, 0.0, 0.0),
        radius=0.2,
        field_radius=4.0,
        remaining=10.0,
        transfer_per_tick=2.0,
    )

    near = resource.field_at((1.0, 0.0, 0.0))
    far = resource.field_at((0.0, 0.0, 0.0))

    assert 0.0 < far < near < 1.0
    resource.remaining = 0.0
    assert resource.field_at((2.0, 0.0, 0.0)) == 0.0


def test_resource_debits_only_absorbed_material(scene):
    resource = PhysicalResource(
        scene,
        remaining=10.0,
        transfer_per_tick=2.0,
    )

    assert resource.offered_material() == 2.0
    assert resource.consume_absorbed(0.4) == pytest.approx(0.4)
    assert resource.remaining == pytest.approx(9.6)


def test_resource_contact_is_physical_not_semantic(scene):
    resource = PhysicalResource(scene)
    sphere = scene.mj.mjtGeom.mjGEOM_SPHERE
    for name, x in (("overlapping", resource.position[0] + 0.1), ("distant", 0.0)):
        body = scene.spec.worldbody.add_body(name=name, pos=[x, 0.0, resource.position[2]])
        body.add_freejoint()
        body.add_geom(type=sphere, size=[0.1, 0.0, 0.0])
    scene.recompile()
    overlapping = scene.name_to_id("body", "overlapping")
    distant = scene.name_to_id("body", "distant")

    assert resource.touching({distant}) is False
    assert resource.touching({overlapping}) is True
    assert resource.touching({overlapping, distant}) is True
    resource.remaining = 0.0
    assert resource.touching({overlapping}) is False


def test_opaque_environment_state_accepts_only_bounded_scalars():
    body = HumanoidPhysics.__new__(HumanoidPhysics)
    body._external_field_signal = 0.0

    body.set_opaque_environment_state(external_field=0.3)
    assert body._external_field_signal == pytest.approx(0.3)

    with pytest.raises(ValueError):
        body.set_opaque_environment_state(external_field=1.1)


def test_world_loss_equals_body_gain_for_accepted_physical_transfer(scene):
    from symbiont.core.embodiment.metabolism import MetabolicLedger
    from symbiont.core.embodiment.physiology import LivingBodyState

    resource = PhysicalResource(
        scene,
        remaining=10.0,
        transfer_per_tick=2.0,
    )
    state = LivingBodyState(energy_reserve=0.5, max_energy=2.0)
    ledger = MetabolicLedger(
        replenishment={k: 0.0 for k in ("observation", "cognition", "persistence", "maintenance")},
        body_state=state,
    )

    world_before = resource.remaining
    body_before = state.energy_reserve
    offered = resource.offered_material()
    accepted = ledger.intake_untyped(offered)
    consumed = resource.consume_absorbed(accepted)

    assert consumed == pytest.approx(accepted)
    assert world_before - resource.remaining == pytest.approx(state.energy_reserve - body_before)
    assert accepted == pytest.approx(1.5)

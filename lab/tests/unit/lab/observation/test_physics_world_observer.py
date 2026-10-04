"""Actual collision-engine geometry and descriptor-specific receptor anchoring."""

from types import SimpleNamespace

import pytest

from environment.physics3d.resource import PhysicalResource
from lab.integration.physics3d.bodies import DEFAULT_BODY_REGISTRY
from lab.physics3d.world_observation import PhysicsWorldObserver

pytestmark = pytest.mark.slow


@pytest.mark.parametrize("body_kind", tuple(DEFAULT_BODY_REGISTRY._descriptors))
def test_world_observer_reads_real_shapes_for_each_body_without_mutating_physics(body_kind):
    pytest.importorskip("mujoco")
    from embodiment.physics3d.scene import PhysicsScene

    scene = PhysicsScene(timestep=1.0 / 240.0)
    scene.add_ground()
    descriptor = DEFAULT_BODY_REGISTRY.get(body_kind)
    apparatus = descriptor.apparatus_factory(scene)
    resource = PhysicalResource(scene, radius=0.27, position=(2.0, 1.0, 0.27))
    runtime = SimpleNamespace(
        scene=scene, apparatus=apparatus, resource=resource, body_descriptor=descriptor
    )
    before = apparatus.export_physical_state()
    observer = PhysicsWorldObserver()
    first = observer.capture(runtime)
    assert apparatus.export_physical_state() == before
    assert len(first["entities"]) == 2
    expected_receptors = (
        len(descriptor.observer_joint_specs) * 2
        + 10
        + len(descriptor.observer_contact_region_names) * 2
        + 1
    )
    assert len(first["receptors"]) == expected_receptors
    sphere = next(e for e in first["entities"].values() if "field" in e)
    assert sphere["position"] == [2.0, 1.0, 0.27]
    assert sphere["shapes"][0]["dimensions"][0] == pytest.approx(0.27)
    assert {r["link"] for r in first["receptors"].values() if r["modality"] == "contact"} == set(
        descriptor.observer_contact_region_names
    )
    assert all(r["link"] for r in first["receptors"].values() if r["modality"] == "proprioception")
    obstacle = scene.spec.worldbody.add_body(name="obstacle", pos=[5, 1, 2], mocap=True)
    obstacle.add_geom(type=scene.mj.mjtGeom.mjGEOM_BOX, size=[0.2, 0.3, 0.4])
    scene.recompile()
    second = observer.capture(runtime)
    (new_id,) = second["entities"].keys() - first["entities"].keys()
    box = second["entities"][new_id]
    assert box["shapes"][0]["dimensions"] == pytest.approx([0.4, 0.6, 0.8])
    mocap = scene.model.body_mocapid[scene.name_to_id("body", "obstacle")]
    scene.data.mocap_pos[mocap] = [6, 1, 2]
    scene.forward()
    assert observer.capture(runtime)["entities"][new_id]["position"] == [6, 1, 2]
    scene.spec.delete(obstacle)
    scene.recompile()
    assert new_id not in observer.capture(runtime)["entities"]

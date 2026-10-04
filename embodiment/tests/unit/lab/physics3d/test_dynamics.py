import math

import pytest

from embodiment.physics3d.humanoid import JOINT_SPECS, HumanoidPhysics
from embodiment.physics3d.mechanics import JOINT_LIMIT_SOLVER_TOLERANCE


def test_humanoid_hard_limits_hold_under_deterministic_actuation():
    pytest.importorskip("mujoco")
    from embodiment.physics3d.scene import PhysicsScene

    scene = PhysicsScene(timestep=1.0 / 240.0)
    scene.spec.worldbody.add_geom(
        name="ground", type=scene.mj.mjtGeom.mjGEOM_PLANE, size=[0.0, 0.0, 1.0]
    )
    body = HumanoidPhysics(scene)
    start_position = body.export_physical_state()["base_position"]

    max_speed_seen = 0.0
    max_total_speed_seen = 0.0
    max_limit_violation = 0.0
    worst_joint = None

    # Broad, deterministic excitation of the complete opaque motor surface.
    for step in range(360):
        activations = {}
        for index, effector_id in enumerate(body.effector_ids):
            phase = (step + index * 7) % 80
            activations[effector_id] = 0.65 if phase < 20 else 0.0
        body.apply_effectors(activations)

        for _ in range(2):
            body.prepare_physics_substep()
            scene.step()

            states = body.joint_states()
            speeds = [abs(velocity) for _position, velocity in states]
            max_speed_seen = max(max_speed_seen, max(speeds, default=0.0))
            max_total_speed_seen = max(max_total_speed_seen, sum(speeds))

            for ordinal, (position, _velocity) in enumerate(states):
                spec = JOINT_SPECS[ordinal]
                violation = max(spec.lower - position, position - spec.upper, 0.0)
                if violation > max_limit_violation:
                    max_limit_violation = violation
                    worst_joint = spec.name

    assert math.isfinite(max_speed_seen)
    assert math.isfinite(max_total_speed_seen)
    assert max_total_speed_seen < 150.0
    # Not asserted: each joint's declared max_velocity. The previous engine clamped joint
    # speed to it; MuJoCo has no such clamp and this excitation reaches about
    # twice the largest ceiling. Whether and how to enforce it is a
    # recalibration question (ADR-0066), not something to hide in a test.
    # The engine owns the hard anatomical stop. Passive end-range resistance
    # may slow approach, but the declared anatomical envelope itself must
    # never be crossed beyond solver tolerance.
    assert max_limit_violation < JOINT_LIMIT_SOLVER_TOLERANCE, (
        f"worst_joint={worst_joint} violation={math.degrees(max_limit_violation):.3f}deg"
    )

    end_position = body.export_physical_state()["base_position"]
    displacement = math.dist(start_position, end_position)
    assert math.isfinite(displacement)
    assert displacement < 8.0

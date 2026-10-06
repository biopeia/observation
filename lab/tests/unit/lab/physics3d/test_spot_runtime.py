import pytest

from embodiment.physics3d.bodies import SPOT_INSPIRED_V1
from embodiment.physics3d.spot import SPOT_INSPIRED_SPEC


def test_spot_runtime_starts_at_declared_pose_without_passive_settling() -> None:
    pytest.importorskip("mujoco")
    from lab.physics3d.runtime import Physics3DEmbodimentRuntime

    runtime = Physics3DEmbodimentRuntime(
        gui=False,
        body_kind=SPOT_INSPIRED_V1.body_kind,
        physics_substeps_per_tick=1,
    )
    try:
        position, orientation = runtime.apparatus.base_pose()
        linear, angular = runtime.apparatus.base_velocity()
        assert position[2] == pytest.approx(SPOT_INSPIRED_SPEC.spawn_height)
        assert orientation == pytest.approx((0.0, 0.0, 0.0, 1.0))
        assert linear == pytest.approx((0.0, 0.0, 0.0))
        assert angular == pytest.approx((0.0, 0.0, 0.0))
        assert runtime._settling_result is None
        runtime.step()
    finally:
        runtime.close()

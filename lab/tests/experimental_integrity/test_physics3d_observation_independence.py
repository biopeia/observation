"""P1 A5: canonical Physics3D observation must not alter causal state."""

from __future__ import annotations

import pytest

pytest.importorskip("mujoco")

from lab.physics3d.runtime import Physics3DEmbodimentRuntime


def _matched_runtimes(
    *, seed: int, body_kind: str, environment: str | None
) -> tuple[Physics3DEmbodimentRuntime, Physics3DEmbodimentRuntime]:
    """Fork two runs from one captured organism/body state."""
    source = Physics3DEmbodimentRuntime(
        gui=False,
        seed=seed,
        organism_id=f"phase-a-a5-{body_kind}-{seed}",
        body_kind=body_kind,
        environment=environment,
        physics_substeps_per_tick=1,
    )
    try:
        physical_state, _ = source.physical_checkpoint()
        organism_state = source.checkpoint(advance_lineage=False)
    finally:
        source.close()

    def restore() -> Physics3DEmbodimentRuntime:
        return Physics3DEmbodimentRuntime(
            gui=False,
            seed=seed,
            organism_id=f"phase-a-a5-{body_kind}-{seed}",
            body_kind=body_kind,
            environment=environment,
            physics_substeps_per_tick=1,
            runtime_checkpoint=organism_state,
            physical_state=physical_state,
        )

    return restore(), restore()


@pytest.mark.parametrize("seed", [127, 149])
@pytest.mark.parametrize(
    ("body_kind", "environment"),
    [
        ("anthropomorphic-v6", None),
        ("anthropomorphic-v6-vision", "vision-nursery-d1-v1"),
        ("anthropomorphic-v6-vision", "vision-nursery-d1-v2"),
    ],
    ids=["v6-flat", "vision-d1-v1", "vision-d1-v2"],
)
def test_observation_toggle_preserves_canonical_organism_and_physics_state(
    seed: int, body_kind: str, environment: str | None
) -> None:
    """Compare observer ON/OFF from one captured state across canonical setups."""
    unobserved, observed = _matched_runtimes(
        seed=seed, body_kind=body_kind, environment=environment
    )
    try:
        assert unobserved.organism.state_hash() == observed.organism.state_hash()
        assert unobserved.passive_physical_state() == observed.passive_physical_state()

        for _ in range(16):
            unobserved.step(include_observability=False)
            observed.step(include_observability=True)

            # The organism hash covers causal state, including learning,
            # competence, model lifecycle and provenance registers.
            assert unobserved.organism.state_hash() == observed.organism.state_hash()
            assert unobserved.organism.last_motor_intents == observed.organism.last_motor_intents
            assert unobserved.organism.last_actuations == observed.organism.last_actuations

            # Compare apparatus consequences as well as the organism state.
            unobserved_physical, unobserved_tick = unobserved.physical_checkpoint()
            observed_physical, observed_tick = observed.physical_checkpoint()
            assert unobserved_tick == observed_tick
            assert unobserved_physical == observed_physical
    finally:
        unobserved.close()
        observed.close()

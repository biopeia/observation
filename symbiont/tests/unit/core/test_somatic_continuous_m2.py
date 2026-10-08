"""Contract tests for M2 continuous somatic dynamics and Gate G1."""

from __future__ import annotations

import pytest

from symbiont.core.embodiment.duration import PhysicalDuration
from symbiont.core.embodiment.homeostasis import HomeostaticController
from symbiont.core.embodiment.metabolism import MetabolicLedger
from symbiont.core.embodiment.physiology import LivingBodyState
from symbiont.core.orchestration.runtime import OrganismRuntime


def _controller_state() -> tuple[LivingBodyState, MetabolicLedger, HomeostaticController]:
    state = LivingBodyState(
        energy_reserve=1.0,
        max_energy=2.0,
        structural_integrity=0.50,
        temperature=0.80,
        fatigue=0.60,
    )
    metabolism = MetabolicLedger(body_state=state)
    return state, metabolism, HomeostaticController(body_state=state)


def test_m2_reference_duration_preserves_legacy_single_step_exactly() -> None:
    state, metabolism, controller = _controller_state()
    config = controller.config
    work = 0.20

    expected_fatigue = (
        state.fatigue
        + work * config.fatigue_work_gain
        - config.fatigue_recovery_rate
    )
    expected_temperature = (
        state.temperature
        + (config.thermal_setpoint - state.temperature) * config.thermal_relaxation_rate
        + work * config.thermal_work_gain
    )
    expected_repair = config.autonomous_repair_rate

    repaired = controller.constitutive_step(
        metabolism,
        embodied_work=work,
        resting=False,
        physical_duration=PhysicalDuration(config.somatic_reference_duration_s),
    )

    assert state.fatigue == pytest.approx(expected_fatigue, abs=1e-15)
    assert state.temperature == pytest.approx(expected_temperature, abs=1e-15)
    assert repaired == pytest.approx(expected_repair, abs=1e-15)
    assert state.structural_integrity == pytest.approx(0.50 + expected_repair, abs=1e-15)


def _run_partitioned_somatic_path(partitions: int) -> tuple[float, float, float, float]:
    state, metabolism, controller = _controller_state()
    reference = controller.config.somatic_reference_duration_s
    total_duration = 4.0 * reference
    total_work = 0.20
    dt = PhysicalDuration(total_duration / partitions)
    work = total_work / partitions

    total_repair = 0.0
    for _ in range(partitions):
        total_repair += controller.constitutive_step(
            metabolism,
            embodied_work=work,
            resting=True,
            physical_duration=dt,
        )

    return state.temperature, state.fatigue, state.structural_integrity, total_repair


def test_g1_somatic_path_is_invariant_to_time_partition() -> None:
    coarse = _run_partitioned_somatic_path(4)
    medium = _run_partitioned_somatic_path(8)
    fine = _run_partitioned_somatic_path(16)

    for candidate in (medium, fine):
        assert candidate[0] == pytest.approx(coarse[0], abs=1e-12)
        assert candidate[1] == pytest.approx(coarse[1], abs=1e-12)
        assert candidate[2] == pytest.approx(coarse[2], abs=1e-12)
        assert candidate[3] == pytest.approx(coarse[3], abs=1e-12)


def test_zero_physical_duration_is_noop_without_work() -> None:
    state, metabolism, controller = _controller_state()
    before = (state.temperature, state.fatigue, state.structural_integrity)

    repaired = controller.constitutive_step(
        metabolism,
        embodied_work=0.0,
        resting=True,
        physical_duration=PhysicalDuration(0.0),
    )

    assert repaired == 0.0
    assert (state.temperature, state.fatigue, state.structural_integrity) == before


def test_zero_physical_duration_rejects_nonzero_work() -> None:
    _, metabolism, controller = _controller_state()

    with pytest.raises(ValueError, match="positive physical_duration"):
        controller.constitutive_step(
            metabolism,
            embodied_work=0.01,
            physical_duration=PhysicalDuration(0.0),
        )


def test_organism_tick_rejects_untyped_physical_duration() -> None:
    runtime = OrganismRuntime(
        discover_senses=False,
        bootstrap_semantic_senses=False,
        interoception_enabled=False,
        investigate_ticks=0,
        min_samples=1,
    )
    with pytest.raises(TypeError, match="PhysicalDuration"):
        runtime.tick(physical_duration=0.01)  # type: ignore[arg-type]

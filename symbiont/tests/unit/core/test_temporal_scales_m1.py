"""Contract test suite for Phase M1: Temporal Scales and Clock Separation v1.

Verifies gates G-M1.1 through G-M1.7 as defined in
docs/design/core/temporal-scales-and-clock-separation-v1.md.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
import time

import pytest

from symbiont.core.embodiment.duration import PhysicalDuration
from symbiont.core.embodiment.physiology import LivingBodyState
from symbiont.core.orchestration.cycle import CycleStep
from symbiont.core.orchestration.runtime import OrganismRuntime
from symbiont.core.cognition.host_self_model import IDLE_GRACE_TICKS, UNOBSERVED_CYCLES_GRACE
from symbiont.modeling.telemetry import CommunicationTelemetry
from symbiont.sensory.evidence import EvidenceCount, SampleCount
from symbiont.sensory.predictive_credit import PairwisePredictiveEvidence


# ---------------------------------------------------------------------------
# G-M1.1: Cognitive Isolation (T_p not in Cognition)
# ---------------------------------------------------------------------------
def test_g_m1_1_cognitive_isolation_ast():
    """Static AST check: no module under cognition imports physical duration or physics."""
    import symbiont.cognition
    import symbiont.core.cognition

    cognition_dirs = [
        Path(symbiont.cognition.__file__).parent,
        Path(symbiont.core.cognition.__file__).parent,
    ]

    prohibited_import_substrings = {
        "duration",
        "PhysicalDuration",
        "mujoco",
        "physics3d",
    }

    scanned_files = 0
    for cdir in cognition_dirs:
        if not cdir.exists():
            continue
        for py_file in cdir.glob("**/*.py"):
            scanned_files += 1
            content = py_file.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(py_file))

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        for prohibited in prohibited_import_substrings:
                            assert prohibited not in alias.name, (
                                f"G-M1.1 violation: {py_file} directly imports prohibited symbol '{alias.name}'"
                            )
                elif isinstance(node, ast.ImportFrom):
                    mod_name = node.module or ""
                    for prohibited in prohibited_import_substrings:
                        assert prohibited not in mod_name, (
                            f"G-M1.1 violation: {py_file} imports from prohibited module '{mod_name}'"
                        )
                    for alias in node.names:
                        assert alias.name != "PhysicalDuration", (
                            f"G-M1.1 violation: {py_file} imports PhysicalDuration"
                        )

    assert scanned_files > 0, "AST check must inspect at least one cognition module"


# ---------------------------------------------------------------------------
# G-M1.2: Host Non-Leakage (Host Wall Time does not leak into organism state)
# ---------------------------------------------------------------------------
def test_g_m1_2_host_non_leakage_across_synthetic_delays():
    """Determinism regression: organism trajectories under synthetic delays remain bitwise identical."""
    body_kwargs = {
        "energy_reserve": 10.0,
        "max_energy": 10.0,
        "growth_progress": 1.0,
        "age_ticks": 0,
    }

    # Run 1: fast, zero sleep
    rt1 = OrganismRuntime(
        organism_id="org_test_m1_det",
        living_body_state=LivingBodyState(**body_kwargs),
        discover_senses=False,
        bootstrap_semantic_senses=False,
        interoception_enabled=False,
        investigate_ticks=0,
        min_samples=1,
    )
    for _ in range(5):
        rt1.tick()
    ckpt1 = rt1.checkpoint()

    # Run 2: synthetic CPU jitter / sleep between ticks
    rt2 = OrganismRuntime(
        organism_id="org_test_m1_det",
        living_body_state=LivingBodyState(**body_kwargs),
        discover_senses=False,
        bootstrap_semantic_senses=False,
        interoception_enabled=False,
        investigate_ticks=0,
        min_samples=1,
    )
    for _ in range(5):
        time.sleep(0.005)  # synthetic host latency delay
        rt2.tick()
        time.sleep(0.005)
    ckpt2 = rt2.checkpoint()

    # Checkpoints must be completely identical regardless of host wall-time elapsed
    assert json.dumps(ckpt1, sort_keys=True) == json.dumps(ckpt2, sort_keys=True), (
        "G-M1.2 violation: host wall-time delay caused drift in deterministic organism checkpoint"
    )


# ---------------------------------------------------------------------------
# G-M1.3: Scale Separation (T_s != T_e)
# ---------------------------------------------------------------------------
def test_g_m1_3_scale_separation_cycle_vs_experiential():
    """Contract test: advancing scheduler cycles (T_s) with zero observations does not advance T_e."""
    evidence = PairwisePredictiveEvidence(source_id="p1", target_id="p2")
    assert evidence.observations == 0
    assert isinstance(evidence.observations, EvidenceCount)

    # Simulate scheduler cycles advancing without perceptual observations
    scheduler_step = CycleStep(0)
    for _ in range(10):
        scheduler_step = CycleStep(scheduler_step + 1)
        # evidence receives no observation
        assert evidence.observations == 0  # T_e remains stationary

    assert scheduler_step == 10
    assert evidence.observations == 0

    # Observation arrival advances T_e
    evidence.observe(0.5, 0.8)
    assert evidence.observations == 1
    assert isinstance(evidence.observations, EvidenceCount)
    assert scheduler_step == 10  # T_s does not couple back


# ---------------------------------------------------------------------------
# G-M1.4: Checkpoint Continuity (Restore of snapshot preserves separated scales)
# ---------------------------------------------------------------------------
def test_g_m1_4_checkpoint_continuity_separated_scales():
    """Roundtrips preserve T_s, body-local cycle count, and typed T_e evidence."""
    rt = OrganismRuntime(
        organism_id="sym_m1_ckpt",
        living_body_state=LivingBodyState(
            energy_reserve=5.0,
            max_energy=5.0,
            growth_progress=1.0,
            age_ticks=10,
        ),
        tick_count=100,
        discover_senses=False,
        bootstrap_semantic_senses=False,
        interoception_enabled=False,
        investigate_ticks=0,
        min_samples=1,
    )
    rt.run(5)

    assert rt.tick_count == 105  # T_s
    assert rt.living_body_state.age_ticks == 15  # T_s^body

    ckpt = rt.checkpoint()
    assert ckpt["saved_at_tick"] == 105
    assert ckpt["living_body"]["age_ticks"] == 15

    restored = OrganismRuntime.from_checkpoint(
        ckpt,
        discover_senses=False,
        bootstrap_semantic_senses=False,
        interoception_enabled=False,
        investigate_ticks=0,
        min_samples=1,
    )

    assert restored.tick_count == 105
    assert restored.living_body_state.age_ticks == 15
    assert isinstance(restored.tick_count, CycleStep)

    evidence = PairwisePredictiveEvidence(source_id="source", target_id="target")
    for value in (0.1, 0.2, 0.3):
        evidence.observe(value, value * 2.0)
    evidence_payload = evidence.checkpoint(include_replay=True)
    restored_evidence = PairwisePredictiveEvidence.restore(evidence_payload)
    assert restored_evidence.observations == EvidenceCount(3)
    assert isinstance(restored_evidence.observations, EvidenceCount)
    assert restored_evidence.checkpoint(include_replay=True) == evidence_payload


# ---------------------------------------------------------------------------
# G-M1.5: Deterministic Replay (identical deterministic configuration/input)
# ---------------------------------------------------------------------------
def test_g_m1_5_deterministic_replay_trace_equality():
    """Identical deterministic configuration and inputs yield identical checkpoints."""
    def run_trajectory():
        rt = OrganismRuntime(
            organism_id="org_replay_seed_42",
            living_body_state=LivingBodyState(
                energy_reserve=8.0,
                max_energy=10.0,
                growth_progress=1.0,
                age_ticks=0,
            ),
            discover_senses=False,
            bootstrap_semantic_senses=False,
            interoception_enabled=False,
            investigate_ticks=0,
            min_samples=1,
        )
        results = [rt.tick() for _ in range(4)]
        return results, rt.checkpoint()

    results1, ckpt1 = run_trajectory()
    results2, ckpt2 = run_trajectory()

    assert json.dumps(ckpt1, sort_keys=True) == json.dumps(ckpt2, sort_keys=True)
    assert len(results1) == len(results2)


# ---------------------------------------------------------------------------
# G-M1.6: Bounded Equation Preservation (touched M1 mechanisms)
# ---------------------------------------------------------------------------
def test_g_m1_6_zero_equation_drift():
    """Verify exact numerical preservation for the behavior-bearing mechanisms touched by M1."""
    # 1. Predictive credit formulas
    ev = PairwisePredictiveEvidence(source_id="a", target_id="b")
    # Feed 4 observations
    for i in range(4):
        ev.observe(float(i), float(i * 2))

    # Analytical effective weight after 4 steps: sum_{k=0}^3 0.97^k
    # 1 + 0.97 + 0.97^2 + 0.97^3 = 3.822773
    expected_weight = 1.0 + 0.97 + (0.97**2) + (0.97**3)
    assert ev.effective_weight == pytest.approx(expected_weight, rel=1e-6)
    assert ev.observations == 4

    # 2. Host self-model grace constant
    assert UNOBSERVED_CYCLES_GRACE == 20
    assert IDLE_GRACE_TICKS == 20


# ---------------------------------------------------------------------------
# G-M1.7: Semantic Equivalence & Backwards Compatibility
# ---------------------------------------------------------------------------
def test_g_m1_7_semantic_equivalence_and_backwards_compatibility():
    """Test JSON/checkpoint serialization, type coercion, and backward compatibility."""
    # 1. CycleStep
    cs = CycleStep(42)
    assert isinstance(cs, int)
    assert cs == 42
    assert repr(cs) == "CycleStep(42)"
    assert json.loads(json.dumps({"step": cs})) == {"step": 42}
    with pytest.raises(ValueError):
        CycleStep(-1)

    # 2. EvidenceCount & SampleCount
    ec = EvidenceCount(15)
    sc = SampleCount(15)
    assert isinstance(ec, int)
    assert ec == 15
    assert sc == ec
    assert repr(ec) == "EvidenceCount(15)"
    assert json.loads(json.dumps({"count": ec})) == {"count": 15}
    with pytest.raises(ValueError):
        EvidenceCount(-5)

    # 3. PhysicalDuration
    pd = PhysicalDuration(0.016)
    assert isinstance(pd, float)
    assert pd == pytest.approx(0.016)
    assert repr(pd) == "PhysicalDuration(0.016)"
    assert json.loads(json.dumps({"dt": pd})) == {"dt": pytest.approx(0.016)}
    with pytest.raises(ValueError):
        PhysicalDuration(-0.1)

    # 4. TelemetryBuffer retention_cycles <-> max_age_ticks bidirectional compatibility
    # Constructor with retention_cycles
    t1 = CommunicationTelemetry(retention_cycles=100)
    assert t1.retention_cycles == 100
    assert t1.max_age_ticks == 100
    ckpt_t1 = t1.checkpoint()
    assert ckpt_t1["retention_cycles"] == 100
    assert ckpt_t1["max_age_ticks"] == 100

    # Restore from legacy checkpoint containing only max_age_ticks
    legacy_payload = {
        "schema_version": CommunicationTelemetry.SCHEMA_VERSION,
        "max_events": 1000,
        "max_events_per_tick": 256,
        "max_age_ticks": 64,
        "events": [],
        "grounding_events": [],
        "history_truncated": False,
    }
    t_restored_legacy = CommunicationTelemetry.restore(legacy_payload)
    assert t_restored_legacy.retention_cycles == 64
    assert t_restored_legacy.max_age_ticks == 64

    # Restore from modern checkpoint containing only retention_cycles
    modern_payload = {
        "schema_version": CommunicationTelemetry.SCHEMA_VERSION,
        "max_events": 1000,
        "max_events_per_tick": 256,
        "retention_cycles": 128,
        "events": [],
        "grounding_events": [],
        "history_truncated": False,
    }
    t_restored_modern = CommunicationTelemetry.restore(modern_payload)
    assert t_restored_modern.retention_cycles == 128
    assert t_restored_modern.max_age_ticks == 128


# ---------------------------------------------------------------------------
# M1.1 hardening: temporal scalar constructors fail closed
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("bad", [True, False, 1.5, 3.9, "4", None])
def test_cycle_step_rejects_ambiguous_non_integer_inputs(bad):
    with pytest.raises(TypeError):
        CycleStep(bad)


@pytest.mark.parametrize("bad", [True, False, 1.5, 3.9, "4", None])
def test_evidence_count_rejects_ambiguous_non_integer_inputs(bad):
    with pytest.raises(TypeError):
        EvidenceCount(bad)


@pytest.mark.parametrize("bad", [True, False, "0.1", None])
def test_physical_duration_rejects_non_numeric_inputs(bad):
    with pytest.raises(TypeError):
        PhysicalDuration(bad)


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_physical_duration_rejects_non_finite_inputs(bad):
    with pytest.raises(ValueError):
        PhysicalDuration(bad)


def test_telemetry_constructor_rejects_conflicting_retention_aliases():
    with pytest.raises(ValueError, match="must match"):
        CommunicationTelemetry(max_age_ticks=64, retention_cycles=128)


def test_telemetry_restore_rejects_conflicting_retention_aliases():
    payload = {
        "schema_version": CommunicationTelemetry.SCHEMA_VERSION,
        "max_events": 1000,
        "max_events_per_tick": 256,
        "max_age_ticks": 64,
        "retention_cycles": 128,
        "events": [],
        "grounding_events": [],
        "history_truncated": False,
    }
    with pytest.raises(ValueError, match="conflicting"):
        CommunicationTelemetry.restore(payload)


def test_temporal_scalar_types_reject_cross_scale_values():
    with pytest.raises(TypeError):
        CycleStep(EvidenceCount(3))
    with pytest.raises(TypeError):
        EvidenceCount(CycleStep(3))
    with pytest.raises(TypeError):
        PhysicalDuration(CycleStep(3))
    with pytest.raises(TypeError):
        PhysicalDuration(EvidenceCount(3))

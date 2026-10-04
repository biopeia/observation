"""Cognitive Cycle v1 (docs/design/cognition/cognitive-cycle-v1.md), wave W0.

Locks the parts of the cycle contract that already hold on main; it changes
no organism behaviour.  The gaps recorded as findings F1-F5 are deliberately
not asserted here.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from symbiont.actuation.evidence import CausalEvidenceLedger, SensorimotorTransition
from symbiont.modeling.experience import EpistemicStatus, ExperienceRecord, SourceKind

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "symbiont" / "src" / "symbiont"


def _tick_source() -> str:
    source = (SOURCE / "core" / "orchestration" / "runtime.py").read_text(encoding="utf-8")
    start = source.index("    def tick(")
    return source[start : source.index("\n    def run(", start)]


def test_tick_runs_the_cycle_phases_in_canonical_order() -> None:
    """§2: grounding, consequence, reconciliation, representation, consolidation, action."""
    tick = _tick_source()
    phases = (
        "self._perception_domain.step(",
        "self._action_domain.observe_consequences(",
        "self._generative_cognition.note_factual_outcome(",
        "self._cognition_domain.step(",
        "self._memory_domain.observe(",
        "self._action_domain.act(",
        "self._epistemic_domain.investigate(",
    )
    positions = [tick.index(phase) for phase in phases]
    assert positions == sorted(positions)


def test_motor_caused_consequence_has_one_identity_derived_from_its_attempt() -> None:
    """§5.1: the fact id names the attempt, not any learner's view of it."""
    acquisition = (SOURCE / "actuation" / "acquisition.py").read_text(encoding="utf-8")
    assert 'f"transition:{closed.attempt_id}"' in acquisition
    assert 'transition_id=f"transition.{digest}"' in acquisition


def test_causal_evidence_cites_the_transition_as_causal_ref() -> None:
    """§5.1: `causal.{transition_id}` is the evidence reference of the fact."""
    transition = SensorimotorTransition(
        transition_id="transition.x",
        tick_start=0,
        tick_end=1,
        context_ref="context.x",
        commitment_id="commitment.x",
        controller_id="controller.x",
        competence_id=None,
        attempt_id="attempt.x",
        intervention_signature_id="signature.x",
        state_before_ref="state.0",
        motor_command_ref="command.x",
        actuation_ref="actuation.x",
        prediction_ref=None,
        state_after_ref="state.1",
    )
    evidence = CausalEvidenceLedger().observe(transition)
    assert evidence.evidence_id == "causal.transition.x"
    assert evidence.transition_id == transition.transition_id


def test_runtime_reconciles_imagination_against_the_causal_fact_reference() -> None:
    """§5.1: the body's consequence reaches Generative Cognition under its fact id."""
    tick = _tick_source()
    assert 'evidence_refs=(f"causal.{transition.transition_id}",)' in tick


def test_model_output_cannot_be_recorded_as_observed() -> None:
    """§3, §15 decision 1: no subsystem manufactures factual authority."""
    with pytest.raises(ValueError, match="model-generated content cannot be marked observed"):
        ExperienceRecord(
            record_id="model.x",
            organism_id="organism.x",
            tick_class=0,
            context_tokens=("sense.x",),
            action_token=None,
            outcome_tokens=("outcome.x",),
            epistemic_status=EpistemicStatus.OBSERVED,
            evidence_refs=("evidence.x",),
            confidence_class=7,
            source_kind=SourceKind.MODEL,
        )

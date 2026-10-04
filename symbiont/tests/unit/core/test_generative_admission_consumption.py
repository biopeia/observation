"""Generative hypotheses can represent an existing affordance, not create authority."""

from __future__ import annotations

from types import SimpleNamespace

from symbiont.agency.affordance import ActionAffordance, affordance_id_for
from symbiont.agency.intention import AdmissionRoute
from symbiont.cognition.generative.agenda import AgendaSource, GenerativeTarget
from symbiont.cognition.generative.resident import ResidentGenerativeCognition
from symbiont.cognition.generative.types import (
    EpistemicOrigin,
    GeneratedFeature,
    GenerativeOperation,
    GenerativeState,
    GenerativeTransition,
)
from symbiont.core.orchestration.runtime import OrganismRuntime


def test_live_hypothesis_changes_production_admission_only_for_existing_affordance():
    cognition = ResidentGenerativeCognition(organism_id="organism.generative-test")
    runtime = OrganismRuntime(
        organism_id="organism.generative-test", generative_cognition=cognition
    )
    cognition.agenda.add_target(
        GenerativeTarget(
            target_id="gc.prospective.competence.test",
            source=AgendaSource.PROSPECTIVE_DECISION,
            source_refs=("competence.test",),
            created_tick=1,
            uncertainty=0.6,
            persistence=0.5,
            recurrence=1,
        )
    )
    state = GenerativeState(
        state_id="state.generated",
        episode_id="episode.generated",
        origin=EpistemicOrigin.IMAGINED,
        parent_state_id=None,
        depth=1,
        features=(GeneratedFeature("effect.relief", None, 0.6),),
        active_concept_ids=(),
        relation_refs=(),
        source_episode_ids=("episode.source",),
        source_model_ids=("model.test",),
        source_state_ids=(),
        uncertainty=0.6,
        coherence=0.8,
        generative_tick=1,
    )
    transition = GenerativeTransition(
        transition_id="transition.generated",
        episode_id="episode.generated",
        source_state_id="state.source",
        target_state_id="state.generated",
        operation=GenerativeOperation.PREDICT,
        model_ids=("model.test",),
        uncertainty_before=0.7,
        uncertainty_after=0.6,
        predicted_outcomes=("effect.relief",),
        generative_tick=1,
    )
    hypothesis = cognition._ensure_hypothesis(
        target_id="gc.prospective.competence.test",
        episode_id="episode.generated",
        transition=transition,
        final_state=state,
    )
    assert hypothesis is not None

    affordance = ActionAffordance(
        affordance_id=affordance_id_for(
            competence_id="competence.test",
            anticipated_effect_id="effect.relief",
            context_ref="context.test",
            embodiment_id=None,
        ),
        competence_id="competence.test",
        anticipated_effect_id="effect.relief",
        context_ref="context.test",
        embodiment_id=None,
        prediction_confidence=0.4,
        controllability=0.6,
        executability_confidence=0.8,
        prediction_ref="prediction.test",
        evidence_refs=("causal.test",),
    )

    class Resolver:
        @staticmethod
        def for_effect(*, effect_id, **_kwargs):
            return (affordance,) if effect_id == "effect.relief" else ()

    # No live hypothesis means this route has no representation, despite the
    # affordance. The test changes no execution binding or physical authority.
    cognition.hypotheses.clear()
    baseline = runtime._choose_acquired_action(
        cognition=SimpleNamespace(readouts_for_family=lambda _family: {}),
        percepts=(),
        affordances=(affordance,),
        resolver=Resolver(),
        context_ref="context.test",
        signal_references={},
        tick=1,
    )
    assert baseline is None

    cognition.hypotheses[hypothesis.hypothesis_id] = hypothesis
    decision = runtime._choose_acquired_action(
        cognition=SimpleNamespace(readouts_for_family=lambda _family: {}),
        percepts=(),
        affordances=(affordance,),
        resolver=Resolver(),
        context_ref="context.test",
        signal_references={},
        tick=1,
    )
    assert decision is not None
    assert decision.admission is AdmissionRoute.GENERATIVE
    assert decision.competence_id == "competence.test"
    assert hypothesis.hypothesis_id in decision.origin_refs

    # The resident's factual-reconciliation API retires the unsupported
    # prediction. This supplies a bounded evidence reference directly; it does
    # not validate the upstream runtime's factual-outcome provenance.
    cognition.calibration.record_prediction(
        model_id="model.test",
        operation=GenerativeOperation.PREDICT,
        depth=state.depth,
        uncertainty=state.uncertainty,
    )
    assert (
        cognition.note_factual_outcome(
            action_id="competence.test",
            outcome_tokens=("effect.other",),
            evidence_refs=("experience.factual",),
            model_ids=("model.test",),
        )
        == 1
    )
    assert hypothesis.status.value == "contradicted"
    assert (
        runtime._choose_acquired_action(
            cognition=SimpleNamespace(readouts_for_family=lambda _family: {}),
            percepts=(),
            affordances=(affordance,),
            resolver=Resolver(),
            context_ref="context.test",
            signal_references={},
            tick=2,
        )
        is None
    )

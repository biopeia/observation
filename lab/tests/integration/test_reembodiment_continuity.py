"""Longitudinal Integrity v1 §12: re-embodiment continuity.

Mechanical continuity only: the Symbiont's own state survives a Body
replacement and current-Body authority is withdrawn. Nothing here measures
whether the retained knowledge is useful in the new Body.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

import pytest

from lab.integration.organism import restore_canonical_organism
from lab.studies.learning.agency_acquisition_body import (
    CausalBody,
    build_subject,
    run_ticks,
    subject_lifecycle,
)
from symbiont.actuation.binding import BindingStatus
from symbiont.cognition.limits import KernelLimits
from symbiont.core.embodiment.transition import (
    EmbodimentDescriptor,
    prepare_fresh_embodiment_checkpoint,
    update_lifecycle_for_checkpoint,
)
from symbiont.core.regulation.reactive_memory import ReactiveMemory
from symbiont.core.regulation.reactivity import InnateReactivity
from symbiont.core.social import SocialHabitat
from symbiont.core.social.interactions import EcologicalResourcePool
from symbiont.host.checkpoint import CheckpointError, stamp_checkpoint_identity
from symbiont.host.continuity import REGISTER, Reembodiment
from symbiont.modeling import (
    ArchitectureId,
    ModelArtifactManifest,
    ModelObjective,
    ModelState,
    NativeTokenizer,
    SequenceMessage,
    SymbolMessage,
    SymbolSequence,
    TrainingRequest,
)
from symbiont.modeling.private_runtime import PrivateModelOrganismRuntime

ORGANISM_ID = "reembodied-subject"
DEVELOPMENT_TICKS = 600
SAVE_METADATA = {"checkpoint_lineage", "runtime_provenance"}
# Body-owned state the transform takes from the fresh Body.
FRESH_BODY_FIELDS = {
    "living_body",
    "metabolism",
    "homeostasis",
    "physiology",
    "sensory_system",
    "sensory_development",
    "rhythms",
    "rhythms_replay",
    "drift",
    "drift_replay",
    "pending_embodied_work",
    "resting_requested",
}


def _subject(body: CausalBody) -> PrivateModelOrganismRuntime:
    return build_subject(
        body,
        organism_id=ORGANISM_ID,
        runtime_class=PrivateModelOrganismRuntime,
        factorized_effects=True,
    )


def _json(payload: dict) -> dict:
    return json.loads(json.dumps(payload))


def _competence_ids(runtime: PrivateModelOrganismRuntime) -> set[str]:
    return {item.competence_id for item in runtime._action_domain.competence_library.items}


class _Case:
    """Body A developed, then the same Symbiont moved into a fresh Body B."""

    def __init__(self) -> None:
        body_a = CausalBody(actuator_count=4, seed=127)
        developed = _subject(body_a)
        self.initial = _json(developed.checkpoint())
        run_ticks(developed, body_a, DEVELOPMENT_TICKS)
        habitat = SocialHabitat(EcologicalResourcePool({"food": 1.0}))
        habitat.admit(ORGANISM_ID)
        habitat.admit("reembodiment-peer")
        developed.join_social_habitat(habitat)
        assert developed.request_social_exchange("reembodiment-peer", "food", 0.1).granted > 0
        developed.ancestry_training = True
        parent_tokenizer = NativeTokenizer.from_records(developed.experience_ledger.records)
        parent_request = TrainingRequest(
            organism_id=developed.organism_id,
            corpus_hash="a" * 64,
            tokenizer_hash=parent_tokenizer.tokenizer_hash,
            architecture_id=ArchitectureId.GRU_V1,
            objective=ModelObjective.NEXT_TOKEN,
            seed=7,
            context_window=32,
            requested_parameters=1_000_000,
            requested_epochs=4,
            requested_steps=100,
            created_tick_class=0,
        )
        parent_artifact = ModelArtifactManifest.build(
            request=parent_request,
            parameter_count=100_000,
            weights_hash="c" * 64,
            artifact_bytes=1024,
        )
        shadow = developed.adopt_private_model(
            parent_artifact,
            evaluation_summary=(0, 1),
            validation_loss=1.0,
            baseline_loss=2.0,
            vocabulary=parent_tokenizer.vocabulary,
        )
        child_vocabulary = (*parent_tokenizer.vocabulary, "reembodiment.novel-token")
        child_tokenizer = NativeTokenizer(vocabulary=child_vocabulary)
        child_request = TrainingRequest(
            organism_id=developed.organism_id,
            corpus_hash="d" * 64,
            tokenizer_hash=child_tokenizer.tokenizer_hash,
            architecture_id=ArchitectureId.GRU_V1,
            objective=ModelObjective.NEXT_TOKEN,
            seed=8,
            context_window=32,
            requested_parameters=1_000_000,
            requested_epochs=4,
            requested_steps=100,
            created_tick_class=0,
            parent_model_id=shadow.model_id,
            adaptation_reason="ancestry",
        )
        child_artifact = ModelArtifactManifest.build(
            request=child_request,
            parameter_count=100_000,
            weights_hash="e" * 64,
            artifact_bytes=1024,
        )
        child = developed.adopt_private_model(
            child_artifact,
            evaluation_summary=(0, 1),
            validation_loss=0.8,
            baseline_loss=1.0,
            vocabulary=child_vocabulary,
        )
        developed.activate_private_model(
            child.model_id, promotion_authorized=True, evaluation_summary=(1, 2)
        )
        developed.originate_social_claim(
            proposition_tokens=("sense.a", "relates", "sense.b"),
            evidence_id="evidence.own",
            confidence_class=5,
        )
        # Include acquired receiver-side symbol/sequence grounding in the same
        # developed subject as the other longitudinal subsystems below.
        sender_id = "reembodiment-peer"
        symbol_id = developed.symbol_policy.symbol_space[0]
        developed.symbol_grounding_ledger.receive(
            SymbolMessage(
                symbol_id,
                sender_id,
                developed.organism_id,
                DEVELOPMENT_TICKS - 2,
            ),
            tick=DEVELOPMENT_TICKS - 2,
        )
        developed.observe_symbolic_outcome("outcome.symbol", tick=DEVELOPMENT_TICKS - 1)
        sequence = SymbolSequence(tuple(developed.symbol_policy.symbol_space[:2]))
        developed.sequence_grounding_ledger.receive(
            SequenceMessage(
                sequence,
                sender_id,
                developed.organism_id,
                DEVELOPMENT_TICKS - 2,
            ),
            tick=DEVELOPMENT_TICKS - 2,
        )
        developed.observe_sequence_outcome(("outcome.sequence",), tick=DEVELOPMENT_TICKS - 1)
        domain = developed._action_domain
        self.body_a_fingerprint = body_a.surface.contract_fingerprint
        self.valid_bindings_in_a = sum(
            binding.status is BindingStatus.VALID for binding in domain.execution_bindings.items
        )
        self.competences_in_a = _competence_ids(developed)
        self.graph_nodes_in_a = {node.node_id for node in developed.cognitive_bridge.graph.nodes}
        self.experience_in_a = [r.record_id for r in developed.experience_ledger.records]
        self.active_model_id = developed.model_registry.active.model_id
        self.ancestor_model_id = shadow.model_id
        self.child_vocabulary = child_vocabulary
        self.own_social_claims = developed.social_evidence_ledger.claims
        self.social_relations = _json(developed.social_ledger.checkpoint())
        self.symbol_grounding = _json(developed.symbol_grounding_ledger.checkpoint())
        self.sequence_grounding = _json(developed.sequence_grounding_ledger.checkpoint())
        self.previous = _json(developed.checkpoint())
        self.previous = update_lifecycle_for_checkpoint(
            self.previous,
            contract=EmbodimentDescriptor("causal-body-a", 4, 4),
            state="active",
        )
        del developed

        # Reuse Body A's opaque receptor IDs in a distinct, differently sized
        # Body. Re-embodiment must not rely on source IDs being globally unique
        # to avoid reactivating old-body sensory bindings.
        self.body_b = CausalBody(actuator_count=6, seed=127)
        assert set(body_a.receptor_ids) & set(self.body_b.receptor_ids)
        self.fresh = _json(_subject(self.body_b).checkpoint())
        self.transformed = prepare_fresh_embodiment_checkpoint(
            self.previous,
            self.fresh,
            contract=EmbodimentDescriptor(
                body_kind="causal-body-b", receptor_count=6, effector_count=6
            ),
            canonical_contract_fingerprint=self.body_b.surface.contract_fingerprint,
        )

    def restore(self, payload: dict | None = None) -> PrivateModelOrganismRuntime:
        return restore_canonical_organism(
            _json(self.transformed if payload is None else payload),
            PrivateModelOrganismRuntime,
            host_lifecycle=subject_lifecycle(self.body_b),
            host_reading_providers=(self.body_b,),
            kernel_limits=KernelLimits(),
            actuator_constitution_override=self.body_b.surface,
            bootstrap_semantic_senses=False,
            discover_senses=True,
            min_samples=1,
            interoception_mode="absent",
        )


@pytest.fixture(scope="module")
def case() -> _Case:
    return _Case()


def test_body_a_development_is_not_trivial(case: _Case) -> None:
    """Guard against the composed continuity fixture silently going empty.

    Presence alone is insufficient for this test: the acquired subsystems below
    must contain state produced by the development run before re-embodiment.
    """
    assert case.previous["saved_at_tick"] == DEVELOPMENT_TICKS
    assert case.valid_bindings_in_a >= 1
    assert case.competences_in_a
    assert case.graph_nodes_in_a
    assert case.experience_in_a
    assert case.previous["gene_expression"]
    assert case.previous["gene_expression"]["update_count"] > 0
    assert case.previous["gene_expression"]["effective_structural_plasticity"] > 0.0
    assert case.previous["gene_expression"] != case.initial["gene_expression"]
    assert case.previous["development"]["tick"] == DEVELOPMENT_TICKS
    assert case.previous["development"] != case.initial["development"]
    assert case.previous["self_model"]
    assert case.previous["signal_knowledge"]["profiles"]
    assert case.previous["generative_cognition"]["hypotheses"]
    assert case.previous["episodic_memory"]["episodes"]
    assert case.previous["experience_ledger"]["records"]
    assert case.previous["body_schema"]["parts"]
    assert case.previous["body_schema"]["cognitive_learning"]["regions"]
    assert case.previous["body_schema"]["boundary_evidence"]["self_caused_channels"]
    assert case.previous["sensory_system"]["sensors"]
    action_state = case.previous["actuation"]["action_domain"]
    assert action_state["sensorimotor_v2"]["causal_evidence"]
    assert action_state["sensorimotor_v2"]["competences"]
    assert action_state["sensorimotor_v2"]["execution_bindings"]
    assert case.active_model_id
    assert case.previous["private_model_registry"]["records"]
    assert case.previous["training_ancestry"]["vocabularies"][case.ancestor_model_id]
    assert len(case.child_vocabulary) > len(
        case.previous["training_ancestry"]["vocabularies"][case.ancestor_model_id]
    )
    assert case.own_social_claims
    assert case.previous["social_evidence_ledger"]["held"]
    assert case.previous["social_ledger"]["relations"]
    assert case.previous["symbol_grounding_ledger"]["associations"]
    assert case.previous["sequence_grounding_ledger"]["associations"]
    # The current runtime does not support acquired epigenetic prior keys. This
    # fixture therefore asserts the absence rather than implying such state is
    # part of the tested continuity claim; SYM-10 remains a separate gap.
    assert case.previous["epigenetic_priors"] == []


def test_symbiont_owned_state_is_preserved_exactly(case: _Case) -> None:
    preserved = (
        {
            field
            for entry in REGISTER
            if entry.reembodiment is Reembodiment.PRESERVED
            for field in entry.checkpoint_fields
        }
        - SAVE_METADATA
        - {"body_schema"}
        - {"innate_reactivity"}
    )

    changed = {
        field
        for field in preserved
        if field in case.previous and case.transformed.get(field) != case.previous[field]
    }

    # last_runtime_vital_state shares its owner with preserved chronology but is
    # a Body fact: a fresh Body always starts active.
    assert changed <= {"last_runtime_vital_state"}
    assert len(preserved & set(case.previous)) > 40


def test_body_owned_state_comes_from_the_fresh_body(case: _Case) -> None:
    mixed_checkpoint_fields = {
        field for entry in REGISTER for field in entry.nested_checkpoint_fields
    }
    registered_fresh_fields = {
        field
        for entry in REGISTER
        if entry.reembodiment is Reembodiment.REPLACED
        for field in entry.checkpoint_fields
        if field not in mixed_checkpoint_fields
    }
    assert registered_fresh_fields == FRESH_BODY_FIELDS

    for field in sorted(FRESH_BODY_FIELDS):
        assert case.transformed[field] == case.fresh[field], field
    assert case.transformed["last_runtime_vital_state"] == "active"
    archived = case.transformed["embodiment_archive"]["body_memories"]
    assert any(
        item["sensory_prior"]
        == {
            "sensory_system": case.previous["sensory_system"],
            "sensory_development": case.previous["sensory_development"],
        }
        for item in archived
    )


def test_percept_name_baselines_reset_but_capability_acclimation_is_preserved(
    case: _Case,
) -> None:
    # The developed subject has non-empty rhythm/drift replay state. Those
    # estimators are keyed by percept name, which is not a stable Body-source
    # identity; they must restart from the new Body's fresh checkpoint.
    for field in ("rhythms", "rhythms_replay", "drift", "drift_replay"):
        assert case.previous[field]
        assert case.previous[field] != case.fresh[field]
        assert case.transformed[field] == case.fresh[field]

    # Acclimation is keyed by opaque capability identity and remains an
    # organism-owned longitudinal prior rather than current-body authority.
    assert case.transformed["acclimation"] == case.previous["acclimation"]


def test_identity_and_time_continue_and_the_transform_is_recorded(case: _Case) -> None:
    lineage = case.transformed["checkpoint_lineage"]

    assert case.transformed["organism_id"] == ORGANISM_ID
    assert case.transformed["saved_at_tick"] == DEVELOPMENT_TICKS
    assert lineage["transforms"] == ["re-embodiment"]
    assert lineage["parent_checkpoint_hash"] == case.previous["checkpoint_lineage"]["checkpoint_id"]

    restored = case.restore()
    assert restored.organism_id == ORGANISM_ID
    assert restored.tick_count == DEVELOPMENT_TICKS


def test_current_body_authority_is_withdrawn(case: _Case) -> None:
    restored = case.restore()
    domain = restored._action_domain

    assert domain.surface.contract_fingerprint == case.body_b.surface.contract_fingerprint
    assert domain.surface.contract_fingerprint != case.body_a_fingerprint
    assert not any(
        binding.status is BindingStatus.VALID for binding in domain.execution_bindings.items
    )
    assert domain.active_commitment is None
    assert "embodiment_episode" not in case.transformed

    lifecycle = case.transformed["embodiment_lifecycle"]
    assert lifecycle["epoch"] == 2
    assert lifecycle["current"]["started_tick"] == DEVELOPMENT_TICKS
    assert lifecycle["current"]["contract_fingerprint"] == (
        case.body_b.surface.contract_fingerprint
    )
    assert [entry["ended_tick"] for entry in lifecycle["history"]] == [DEVELOPMENT_TICKS]


def test_knowledge_survives_as_knowledge_without_authority(case: _Case) -> None:
    restored = case.restore()

    action_entry = next(entry for entry in REGISTER if entry.attribute == "_action_domain")
    assert dict(action_entry.nested_reembodiment) == {
        "actuation.enabled": Reembodiment.REPLACED,
        "actuation.constitution": Reembodiment.REPLACED,
        "actuation.pending_motor_observation": Reembodiment.REPLACED,
        "actuation.pending_proprioception": Reembodiment.REPLACED,
        "action_domain.schema_version": Reembodiment.NOT_APPLICABLE,
        "action_domain.selection_threshold": Reembodiment.REPLACED,
        "action_domain.actuator_evidence": Reembodiment.REPLACED,
        "action_domain.competence_development": Reembodiment.REPLACED,
        "action_domain.sensorimotor_v2.effect_space": Reembodiment.PRESERVED,
        "action_domain.sensorimotor_v2.schema_version": Reembodiment.NOT_APPLICABLE,
        "action_domain.sensorimotor_v2.causal_evidence": Reembodiment.PRESERVED,
        "action_domain.sensorimotor_v2.agency_acquisition": Reembodiment.PRESERVED,
        "action_domain.sensorimotor_v2.exploration": Reembodiment.PRESERVED,
        "action_domain.sensorimotor_v2.competences": Reembodiment.PRESERVED,
        "action_domain.sensorimotor_v2.composition": Reembodiment.PRESERVED,
        "action_domain.sensorimotor_v2.surface_binding": Reembodiment.REPLACED,
        "action_domain.sensorimotor_v2.execution_bindings": Reembodiment.INVALIDATED,
        "action_domain.sensorimotor_v2.binding_invalidation": Reembodiment.REPLACED,
        "action_domain.active_commitment": Reembodiment.INVALIDATED,
        "action_domain.last_executed_controller_seed_id": Reembodiment.INVALIDATED,
        "action_domain.pending_motor_observation": Reembodiment.INVALIDATED,
        "action_domain.pending_proprioception": Reembodiment.INVALIDATED,
        "executive_intention.schema_version": Reembodiment.NOT_APPLICABLE,
        "executive_intention.active": Reembodiment.INVALIDATED,
        "executive_intention.active_commitment_id": Reembodiment.INVALIDATED,
        "executive_intention.progress_evidence": Reembodiment.INVALIDATED,
        "executive_intention.consecutive_mismatches": Reembodiment.INVALIDATED,
        "executive_intention.reconciliation_trace": Reembodiment.INVALIDATED,
        "executive_intention.formed": Reembodiment.PRESERVED,
        "executive_intention.counts": Reembodiment.PRESERVED,
        "executive_intention.outcome_evidence": Reembodiment.PRESERVED,
    }
    declared = dict(action_entry.nested_reembodiment)

    def covered_fields(prefix: str) -> set[str]:
        return {
            path.removeprefix(f"{prefix}.").split(".", maxsplit=1)[0]
            for path in declared
            if path.startswith(f"{prefix}.")
        }

    current_action = case.transformed["actuation"]["action_domain"]
    assert covered_fields("actuation") | {"action_domain"} == set(case.transformed["actuation"])
    assert covered_fields("action_domain") == set(current_action)
    assert covered_fields("action_domain.sensorimotor_v2") == set(
        current_action["sensorimotor_v2"]
    )
    assert covered_fields("executive_intention") == set(case.transformed["executive_intention"])
    prior_v2 = case.previous["actuation"]["action_domain"]["sensorimotor_v2"]
    fresh_v2 = case.fresh["actuation"]["action_domain"]["sensorimotor_v2"]
    current_v2 = current_action["sensorimotor_v2"]
    fresh_action = case.fresh["actuation"]["action_domain"]
    for field in ("selection_threshold", "actuator_evidence", "competence_development"):
        assert current_action[field] == fresh_action[field], field
    for field in (
        "effect_space",
        "causal_evidence",
        "agency_acquisition",
        "exploration",
        "competences",
        "composition",
    ):
        assert current_v2[field] == prior_v2[field], field
    assert current_v2["surface_binding"] == fresh_v2["surface_binding"]
    assert current_v2["execution_bindings"]["items"] == []
    assert current_v2["binding_invalidation"] == "reembodiment"
    assert current_action["active_commitment"] is None
    assert current_action["last_executed_controller_seed_id"] is None
    assert current_action["pending_motor_observation"] == []
    assert current_action["pending_proprioception"] == {}

    lifecycle_entry = next(entry for entry in REGISTER if entry.attribute == "_lifecycle_domain")
    assert dict(lifecycle_entry.nested_reembodiment) == {
        "first_life_history_events.sense": Reembodiment.PRESERVED,
        "first_life_history_events.concept": Reembodiment.PRESERVED,
        "first_life_history_events.prediction": Reembodiment.PRESERVED,
        "last_runtime_vital_state": Reembodiment.REPLACED,
        "last_runtime_development_phase": Reembodiment.PRESERVED,
    }
    assert {
        path for path, _policy in lifecycle_entry.nested_reembodiment
    } == {
        f"first_life_history_events.{event}"
        for event in case.transformed["first_life_history_events"]
    } | {"last_runtime_vital_state", "last_runtime_development_phase"}
    assert case.transformed["last_runtime_vital_state"] == "active"
    assert case.transformed["last_runtime_development_phase"] == case.previous[
        "last_runtime_development_phase"
    ]
    development_entry = next(
        entry for entry in REGISTER if entry.attribute == "_developmental_tracker"
    )
    assert set(dict(development_entry.nested_reembodiment)) == set(case.transformed["development"])
    assert dict(development_entry.nested_reembodiment) == {
        "schema_version": Reembodiment.NOT_APPLICABLE,
        "tick": Reembodiment.PRESERVED,
        "stress_ticks": Reembodiment.PRESERVED,
        "recovery_events": Reembodiment.PRESERVED,
        "repair_events": Reembodiment.PRESERVED,
        "excretion_events": Reembodiment.PRESERVED,
        "maintenance_burden": Reembodiment.PRESERVED,
        "retention_burden": Reembodiment.PRESERVED,
        "previous_stressed": Reembodiment.REPLACED,
    }

    # The prior BodySchema survives in the closed episode archive, but no
    # Body A entry is exposed as active knowledge about Body B.
    prior_schema = _json(case.previous["body_schema"])
    current_schema = _json(case.transformed["body_schema"])
    prior_boundary = prior_schema["boundary_evidence"]
    body_schema_entry = next(entry for entry in REGISTER if entry.attribute == "_body_schema")
    assert dict(body_schema_entry.nested_reembodiment) == {
        "schema_version": Reembodiment.NOT_APPLICABLE,
        "id_salt": Reembodiment.PRESERVED,
        "state": Reembodiment.REPLACED,
        "parts": Reembodiment.INVALIDATED,
        "dependencies": Reembodiment.INVALIDATED,
        "global_state": Reembodiment.NOT_APPLICABLE,
        "cognitive_learning": Reembodiment.INVALIDATED,
        "sensorimotor_view": Reembodiment.INVALIDATED,
        "boundary_evidence": Reembodiment.INVALIDATED,
    }
    assert set(dict(body_schema_entry.nested_reembodiment)) == set(current_schema)
    assert current_schema["state"] == "undeveloped"
    assert current_schema["parts"] == []
    assert current_schema["dependencies"] == []
    assert current_schema["cognitive_learning"] == {
        "channel_support": [],
        "coactivity_support": [],
        "regions": [],
        "dependency_evidence": [],
    }
    assert current_schema["sensorimotor_view"] == {"support": [], "agentic_features": []}
    assert current_schema["boundary_evidence"] != prior_boundary
    assert restored.body_schema.state == "undeveloped"
    assert restored.body_schema.part_count == 0
    assert (
        case.transformed["embodiment_lifecycle"]["history"][0]["body_schema"]
        == (case.previous["body_schema"])
    )
    assert current_schema["id_salt"] == prior_schema["id_salt"]
    assert prior_boundary["self_caused_channels"]
    assert {node.node_id for node in restored.cognitive_bridge.graph.nodes} == (
        case.graph_nodes_in_a
    )
    assert [r.record_id for r in restored.experience_ledger.records] == case.experience_in_a
    assert restored.model_registry.active.model_id == case.active_model_id
    assert restored.model_registry.active.state is ModelState.ACTIVE
    assert restored.model_registry.get(case.ancestor_model_id).state is ModelState.SHADOW
    restored_checkpoint = restored.checkpoint()
    assert restored_checkpoint["sensory_system"] == case.transformed["sensory_system"]
    assert restored_checkpoint["sensory_development"] == case.transformed["sensory_development"]
    assert restored_checkpoint["training_ancestry"]["vocabularies"][case.active_model_id] == list(
        case.child_vocabulary
    )
    assert restored.social_evidence_ledger.claims == case.own_social_claims
    assert _json(restored.social_ledger.checkpoint()) == case.social_relations
    assert _json(restored.symbol_grounding_ledger.checkpoint()) == case.symbol_grounding
    assert _json(restored.sequence_grounding_ledger.checkpoint()) == case.sequence_grounding
    assert _competence_ids(restored) >= case.competences_in_a
    assert not any(
        binding.status is BindingStatus.VALID
        for binding in restored._action_domain.execution_bindings.items
    )


def test_experience_continues_in_body_b_without_erasing_body_a_knowledge(
    case: _Case,
) -> None:
    # A Body of its own: the module fixture's Body B must stay untouched.
    body_b = CausalBody(actuator_count=6, seed=311)
    restored = restore_canonical_organism(
        _json(case.transformed),
        PrivateModelOrganismRuntime,
        host_lifecycle=subject_lifecycle(body_b),
        host_reading_providers=(body_b,),
        kernel_limits=KernelLimits(),
        actuator_constitution_override=body_b.surface,
        bootstrap_semantic_senses=False,
        discover_senses=True,
        min_samples=1,
        interoception_mode="absent",
    )
    run_ticks(restored, body_b, 50)

    assert restored.tick_count == DEVELOPMENT_TICKS + 50
    current_body_signals = {
        restored._signal_identity.signal_id(capability_id) for capability_id in body_b.receptor_ids
    }
    assert set(restored.body_schema.self_caused_channels) <= current_body_signals
    assert len(restored.experience_ledger.records) > len(case.experience_in_a)
    recorded = {record.record_id for record in restored.experience_ledger.records}
    retained = recorded | {record.record_id for record in restored.experience_archive.records}
    assert set(case.experience_in_a) <= retained
    assert _competence_ids(restored) >= case.competences_in_a


def test_registered_nested_reembodiment_paths_resolve_in_checkpoint(case: _Case) -> None:
    for entry in REGISTER:
        for path, _policy in entry.nested_reembodiment:
            candidates = {
                path
                if path == root or path.startswith(f"{root}.")
                else f"{root}.{path}"
                for root in entry.nested_checkpoint_fields
            }
            assert sum(_has_path(case.transformed, candidate) for candidate in candidates) == 1, (
                entry.attribute,
                path,
                candidates,
            )


def test_registered_archived_priors_match_the_closed_body_snapshot(case: _Case) -> None:
    memories = case.transformed["embodiment_archive"]["body_memories"]
    for entry in REGISTER:
        if entry.archived_as_prior is None:
            continue
        assert "embodiment_archive.body_memories[*]." in entry.archived_as_prior
        suffix = entry.archived_as_prior.split("body_memories[*].", maxsplit=1)[1]
        path = suffix.split(".")
        original = case.previous[entry.checkpoint_field]
        assert any(
            _value_at(memory, ".".join(path)) == original
            for memory in memories
            if all(_has_path(memory, ".".join(path[:index])) for index in range(1, len(path) + 1))
        ), (entry.attribute, entry.archived_as_prior)


def test_nested_continuity_policies_cover_every_checkpoint_field(case: _Case) -> None:
    """A classified aggregate must not hide unclassified sibling fields."""
    for entry in REGISTER:
        if not entry.nested_reembodiment:
            continue
        policies = dict(entry.nested_reembodiment)
        for root in entry.nested_checkpoint_fields:
            aggregate = case.transformed
            for part in root.split("."):
                assert isinstance(aggregate, Mapping) and part in aggregate, (entry.attribute, root)
                aggregate = aggregate[part]
            if not isinstance(aggregate, Mapping):
                assert root in policies, (entry.attribute, root)
                continue

            covered: set[str] = set()
            for path in policies:
                candidates = [
                    path
                    if path == other or path.startswith(f"{other}.")
                    else f"{other}.{path}"
                    for other in entry.nested_checkpoint_fields
                ]
                resolved = [candidate for candidate in candidates if _has_path(case.transformed, candidate)]
                assert len(resolved) == 1, (entry.attribute, path, candidates)
                candidate = resolved[0]
                if candidate == root or candidate.startswith(f"{root}."):
                    covered.add(candidate.removeprefix(f"{root}.").split(".", maxsplit=1)[0])
            assert covered == set(aggregate), (entry.attribute, root, covered, set(aggregate))


def test_nested_reembodiment_policies_match_transformed_values(case: _Case) -> None:
    for entry in REGISTER:
        for path, policy in entry.nested_reembodiment:
            candidates = [
                path
                if path == root or path.startswith(f"{root}.")
                else f"{root}.{path}"
                for root in entry.nested_checkpoint_fields
            ]
            resolved = [candidate for candidate in candidates if _has_path(case.transformed, candidate)]
            assert len(resolved) == 1, (entry.attribute, path, candidates)
            resolved_path = resolved[0]
            actual = _value_at(case.transformed, resolved_path)

            if policy is Reembodiment.PRESERVED:
                assert actual == _value_at(case.previous, resolved_path), (entry.attribute, path)
            elif policy is Reembodiment.REPLACED:
                if resolved_path == "last_runtime_vital_state":
                    assert actual == case.fresh["living_body"]["vital_state"]
                elif resolved_path == "actuation.action_domain.sensorimotor_v2.binding_invalidation":
                    assert actual == "reembodiment"
                else:
                    assert actual == _value_at(case.fresh, resolved_path), (entry.attribute, path)


def _has_path(payload: Mapping[str, Any], path: str) -> bool:
    current: Any = payload
    for part in path.split("."):
        if not isinstance(current, Mapping) or part not in current:
            return False
        current = current[part]
    return True


def _value_at(payload: Mapping[str, Any], path: str) -> Any:
    current: Any = payload
    for part in path.split("."):
        assert isinstance(current, Mapping) and part in current, path
        current = current[part]
    return current


def test_reembodiment_withdraws_an_inflight_intention_before_checkpoint(case: _Case) -> None:
    previous = _json(case.previous)
    intention = previous["executive_intention"]
    intention.update(
        {
            "active": {
                "intent_id": "body-a-intention",
                "competence_id": "body-a-competence",
                "anticipated_effect_id": "effect.old-body",
                "context_ref": None,
                "embodiment_id": "body-a",
                "origin_refs": [],
                "prediction_ref": "prediction.old-body",
                "confidence": 0.8,
                "epistemic_relevance": 0.6,
                "homeostatic_relevance": 0.4,
                "supporting_affordance_id": "affordance.old-body",
                "created_tick": DEVELOPMENT_TICKS - 2,
                "activated_tick": DEVELOPMENT_TICKS - 1,
                "last_progress_tick": DEVELOPMENT_TICKS - 1,
                "status": "active",
                "termination_reason": None,
                "admission": "cognitive",
            },
            "active_commitment_id": "commitment.old-body",
            "progress_evidence": 3,
            "consecutive_mismatches": 2,
            "reconciliation_trace": {"observed_atoms": ["body-a-signal"]},
        }
    )
    previous = stamp_checkpoint_identity(previous, transform="test-seed-inflight-intention")

    transformed = prepare_fresh_embodiment_checkpoint(
        previous,
        case.fresh,
        contract=EmbodimentDescriptor(
            body_kind="causal-body-b", receptor_count=6, effector_count=6
        ),
        canonical_contract_fingerprint=case.body_b.surface.contract_fingerprint,
    )

    assert transformed["executive_intention"]["active"] is None
    assert transformed["executive_intention"]["active_commitment_id"] is None
    assert transformed["executive_intention"]["progress_evidence"] == 0
    assert transformed["executive_intention"]["consecutive_mismatches"] == 0
    assert transformed["executive_intention"]["reconciliation_trace"] is None
    assert transformed["executive_intention"]["formed"] == intention["formed"]
    assert transformed["executive_intention"]["counts"] == intention["counts"]
    assert transformed["executive_intention"]["outcome_evidence"] == intention["outcome_evidence"]


def test_reembodiment_resets_only_body_specific_development_edge(case: _Case) -> None:
    previous = _json(case.previous)
    previous["development"]["previous_stressed"] = True
    previous = stamp_checkpoint_identity(previous, transform="test-prior-body-stress-edge")

    transformed = prepare_fresh_embodiment_checkpoint(
        previous,
        case.fresh,
        contract=EmbodimentDescriptor(
            body_kind="causal-body-b", receptor_count=6, effector_count=6
        ),
        canonical_contract_fingerprint=case.body_b.surface.contract_fingerprint,
    )

    assert transformed["development"]["previous_stressed"] is False
    assert {
        key: value
        for key, value in transformed["development"].items()
        if key != "previous_stressed"
    } == {
        key: value for key, value in previous["development"].items() if key != "previous_stressed"
    }


def test_reembodiment_resets_reactivity_frame_but_preserves_learned_memory(case: _Case) -> None:
    previous = _json(case.previous)
    detector = InnateReactivity(smoothing=1.0)
    detector.evaluate(percepts={"opaque.reused": 0.1}, homeostatic_deviation=0.1)
    detector.evaluate(percepts={"opaque.reused": 0.9}, homeostatic_deviation=0.4)
    memory = ReactiveMemory()
    memory.observe(signature="r3:s0:c0", primitive_id="competence.learned", relief=0.2)
    memory.observe(signature="r3:s0:c0", primitive_id="competence.learned", relief=0.2)
    previous["innate_reactivity"] = {
        "schema_version": 1,
        "reactivity": detector.checkpoint(),
        "memory": memory.checkpoint(),
    }
    previous = stamp_checkpoint_identity(previous, transform="test-reactivity-frame")

    transformed = prepare_fresh_embodiment_checkpoint(
        previous,
        case.fresh,
        contract=EmbodimentDescriptor(
            body_kind="causal-body-b", receptor_count=6, effector_count=6
        ),
        canonical_contract_fingerprint=case.body_b.surface.contract_fingerprint,
    )

    reactivity = transformed["innate_reactivity"]
    assert isinstance(reactivity, dict)
    reset_detector = reactivity["reactivity"]
    assert isinstance(reset_detector, dict)
    assert reset_detector["previous_deviation"] is None
    assert reset_detector["previous_percepts"] == {}
    assert reset_detector["smoothed_velocity"] == 0.0
    assert reset_detector["surprise_threshold"] == 0.18
    assert reactivity["memory"] == previous["innate_reactivity"]["memory"]

    restored_detector = InnateReactivity.restore(reset_detector)
    first_body_b_frame = restored_detector.evaluate(
        percepts={"opaque.reused": 0.9}, homeostatic_deviation=0.4
    )
    assert first_body_b_frame.surprise == 0.0
    assert first_body_b_frame.deviation_velocity == 0.0


def test_a_modified_reembodied_checkpoint_is_rejected(case: _Case) -> None:
    tampered = dict(case.transformed)
    tampered["generation"] = case.transformed["generation"] + 1

    with pytest.raises(CheckpointError, match="does not match its recorded checkpoint_id"):
        case.restore(tampered)


def _fields(reembodiment: Reembodiment) -> set[str]:
    return {
        field
        for entry in REGISTER
        if entry.reembodiment is reembodiment
        for field in entry.checkpoint_fields
    } - SAVE_METADATA


def test_the_whole_lifecycle_holds_per_register_entry(case: _Case) -> None:
    """state -> checkpoint -> restore -> checkpoint -> re-embodiment -> restore -> checkpoint.

    Each step is checked against what the register declares for the field, not
    against field presence: a restore that silently substituted a default, or a
    re-embodiment that carried Body state across, fails here by name.
    """
    body_a = CausalBody(actuator_count=4, seed=127)
    restarted = restore_canonical_organism(
        _json(case.previous),
        PrivateModelOrganismRuntime,
        host_lifecycle=subject_lifecycle(body_a),
        host_reading_providers=(body_a,),
        kernel_limits=KernelLimits(),
        actuator_constitution_override=body_a.surface,
        bootstrap_semantic_senses=False,
        discover_senses=True,
        min_samples=1,
        interoception_mode="absent",
    )
    resaved = _json(restarted.checkpoint())
    resaved = update_lifecycle_for_checkpoint(
        resaved,
        contract=EmbodimentDescriptor("causal-body-a", 4, 4),
        state="active",
    )

    # Restore followed by save is lossless for every field the register owns.
    assert {
        field
        for field in set(case.previous) - SAVE_METADATA
        if resaved[field] != case.previous[field]
    } == set()
    assert (
        resaved["checkpoint_lineage"]["parent_checkpoint_hash"]
        == (case.previous["checkpoint_lineage"]["checkpoint_id"])
    )

    transformed = prepare_fresh_embodiment_checkpoint(
        resaved,
        case.fresh,
        contract=EmbodimentDescriptor(
            body_kind="causal-body-b", receptor_count=6, effector_count=6
        ),
        canonical_contract_fingerprint=case.body_b.surface.contract_fingerprint,
    )
    reembodied = case.restore(transformed)
    final = _json(reembodied.checkpoint())

    # BodySchema's active evidence resets for the new Body; the old full schema
    # remains in the closed episode archive as historical evidence.
    nested_fields = {
        field
        for entry in REGISTER
        if entry.nested_reembodiment
        for field in entry.nested_checkpoint_fields
    }
    preserved = (_fields(Reembodiment.PRESERVED) & set(resaved)) - {"body_schema"} - nested_fields
    invalidated = _fields(Reembodiment.INVALIDATED) & set(resaved)
    # ``actuation`` carries both the domain (authority invalidated) and the new
    # Body's enablement; the domain rule governs the field as a whole.
    replaced = (_fields(Reembodiment.REPLACED) & set(resaved)) - invalidated
    assert len(preserved) > 40 and replaced and invalidated

    assert {field for field in preserved if final[field] != resaved[field]} <= {
        "last_runtime_vital_state"
    }
    assert {field for field in replaced if final[field] != case.fresh[field]} == set()
    assert invalidated == {"actuation", "executive_intention"}
    # Knowledge is carried, authority is not: the action domain is neither the
    # old Body's state nor a naive fresh one, and no intention is in flight.
    assert final["actuation"] != resaved["actuation"]
    assert final["actuation"] != case.fresh["actuation"]
    assert final["executive_intention"]["active"] is None
    assert final["executive_intention"]["active_commitment_id"] is None

    lineage = final["checkpoint_lineage"]
    assert lineage["parent_checkpoint_hash"] == transformed["checkpoint_lineage"]["checkpoint_id"]
    assert lineage["transforms"] == ["re-embodiment"]
    assert "unverified_legacy_origin" not in lineage
    assert not any(
        binding.status is BindingStatus.VALID
        for binding in reembodied._action_domain.execution_bindings.items
    )
    assert _competence_ids(reembodied) >= case.competences_in_a

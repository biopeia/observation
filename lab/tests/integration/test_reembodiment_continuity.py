"""Longitudinal Integrity v1 §12: re-embodiment continuity.

Mechanical continuity only: the Symbiont's own state survives a Body
replacement and current-Body authority is withdrawn. Nothing here measures
whether the retained knowledge is useful in the new Body.
"""

from __future__ import annotations

import json

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
)
from symbiont.core.social import SocialHabitat
from symbiont.core.social.interactions import EcologicalResourcePool
from symbiont.host.checkpoint import CheckpointError
from symbiont.host.continuity import REGISTER, Reembodiment
from symbiont.modeling import (
    ArchitectureId,
    ModelArtifactManifest,
    ModelObjective,
    ModelState,
    NativeTokenizer,
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
        self.previous = _json(developed.checkpoint())
        del developed

        self.body_b = CausalBody(actuator_count=6, seed=311)
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
    # The current runtime does not support acquired epigenetic prior keys. This
    # fixture therefore asserts the absence rather than implying such state is
    # part of the tested continuity claim; SYM-10 remains a separate gap.
    assert case.previous["epigenetic_priors"] == []


def test_symbiont_owned_state_is_preserved_exactly(case: _Case) -> None:
    preserved = {
        field
        for entry in REGISTER
        if entry.reembodiment is Reembodiment.PRESERVED
        for field in entry.checkpoint_fields
    } - SAVE_METADATA - {"body_schema"}

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
    for field in sorted(FRESH_BODY_FIELDS):
        assert case.transformed[field] == case.fresh[field], field
    assert case.transformed["last_runtime_vital_state"] == "active"


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

    # The prior BodySchema survives in the closed episode archive, but no
    # Body A entry is exposed as active knowledge about Body B.
    prior_schema = _json(case.previous["body_schema"])
    current_schema = _json(case.transformed["body_schema"])
    prior_boundary = prior_schema["boundary_evidence"]
    body_schema_entry = next(entry for entry in REGISTER if entry.attribute == "_body_schema")
    assert dict(body_schema_entry.nested_reembodiment) == {
        "parts": Reembodiment.INVALIDATED,
        "dependencies": Reembodiment.INVALIDATED,
        "cognitive_learning": Reembodiment.INVALIDATED,
        "sensorimotor_view": Reembodiment.INVALIDATED,
        "boundary_evidence": Reembodiment.INVALIDATED,
    }
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
    assert case.transformed["embodiment_lifecycle"]["history"][0]["body_schema"] == (
        case.previous["body_schema"]
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
    assert restored.checkpoint()["training_ancestry"]["vocabularies"][
        case.active_model_id
    ] == list(case.child_vocabulary)
    assert restored.social_evidence_ledger.claims == case.own_social_claims
    assert _json(restored.social_ledger.checkpoint()) == case.social_relations
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
        restored._signal_identity.signal_id(capability_id)
        for capability_id in body_b.receptor_ids
    }
    assert set(restored.body_schema.self_caused_channels) <= current_body_signals
    assert len(restored.experience_ledger.records) > len(case.experience_in_a)
    recorded = {record.record_id for record in restored.experience_ledger.records}
    retained = recorded | {record.record_id for record in restored.experience_archive.records}
    assert set(case.experience_in_a) <= retained
    assert _competence_ids(restored) >= case.competences_in_a


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
    preserved = (_fields(Reembodiment.PRESERVED) & set(resaved)) - {"body_schema"}
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

"""Longitudinal state ownership register (Longitudinal Integrity v1, LI-P0).

One entry per runtime attribute of the organism runtimes. Each entry assigns
exactly one continuity class and records where the state is checkpointed, how
it is restored, how re-embodiment treats it and whether it is covered by the
checkpoint state identity (``checkpoint_lineage.checkpoint_id``).

The register describes the code as it is, including contracts it does not yet
meet: ``known_gap`` names the audit finding that tracks the unmet part. It is
validated against the live runtimes by ``lab/tests/unit/host/test_continuity_register.py``
so a new attribute or checkpoint field cannot be added unclassified.

Nested state is owned by the subsystem named in ``owner`` through its own
checkpoint contract. ``nested_reembodiment`` records explicitly audited
subfield behavior when the aggregate checkpoint field has mixed re-embodiment
semantics, including retained knowledge inside a field whose authority is
invalidated. ``archived_as_prior`` distinguishes a current-state field that is
replaced or invalidated from historical knowledge copied into the embodiment
archive; it does not grant that archive active authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ContinuityClass(StrEnum):
    MUST_PRESERVE = "must_preserve"
    MUST_RESET = "must_reset"
    MAY_RECOMPUTE = "may_recompute"
    MUST_REAPPLY_CONFIG = "must_reapply_config"
    MUST_INVALIDATE_AUTHORITY = "must_invalidate_authority"


class Reembodiment(StrEnum):
    PRESERVED = "preserved"
    REPLACED = "replaced_by_fresh_body"
    INVALIDATED = "authority_invalidated"
    NOT_APPLICABLE = "not_applicable"
    MIXED = "mixed_nested_policy"


CORE = "core"
MODELED = "modeled"
PRIVATE_MODEL = "private_model"
LAYERS = (CORE, MODELED, PRIVATE_MODEL)


@dataclass(frozen=True, slots=True)
class ContinuityEntry:
    attribute: str
    layer: str
    owner: str
    continuity: ContinuityClass
    checkpoint_field: str | None
    restore_path: str
    reembodiment: Reembodiment
    in_state_identity: bool
    known_gap: str | None = None
    extra_checkpoint_fields: tuple[str, ...] = ()
    nested_reembodiment: tuple[tuple[str, Reembodiment], ...] = ()
    nested_checkpoint_fields: tuple[str, ...] = ()
    archived_as_prior: str | None = None

    @property
    def checkpoint_fields(self) -> tuple[str, ...]:
        primary = () if self.checkpoint_field is None else (self.checkpoint_field,)
        return primary + self.extra_checkpoint_fields


_P = ContinuityClass.MUST_PRESERVE
_R = ContinuityClass.MUST_RESET
_C = ContinuityClass.MAY_RECOMPUTE
_A = ContinuityClass.MUST_REAPPLY_CONFIG
_I = ContinuityClass.MUST_INVALIDATE_AUTHORITY

_KEEP = Reembodiment.PRESERVED
_BODY = Reembodiment.REPLACED
_VOID = Reembodiment.INVALIDATED
_NA = Reembodiment.NOT_APPLICABLE

_UNHASHED_FIELDS = ("checkpoint_lineage", "runtime_provenance")
_BASE_RESTORE = "OrganismRuntime.from_checkpoint"
_MODELED_RESTORE = "ModeledOrganismRuntime.from_checkpoint"
_PRIVATE_RESTORE = "PrivateModelOrganismRuntime.from_checkpoint"
_CONSTRUCTOR = "constructor argument supplied by the launcher"
_EFFECTIVE = "effective_config, unless the launcher passes an explicit override"


def _core(
    attribute: str,
    owner: str,
    continuity: ContinuityClass,
    checkpoint_field: str | None,
    reembodiment: Reembodiment,
    *,
    restore_path: str = _BASE_RESTORE,
    known_gap: str | None = None,
    extra_checkpoint_fields: tuple[str, ...] = (),
    nested_reembodiment: tuple[tuple[str, Reembodiment], ...] = (),
    nested_checkpoint_fields: tuple[str, ...] = (),
    archived_as_prior: str | None = None,
) -> ContinuityEntry:
    return ContinuityEntry(
        attribute=attribute,
        layer=CORE,
        owner=owner,
        continuity=continuity,
        checkpoint_field=checkpoint_field,
        restore_path=restore_path,
        reembodiment=reembodiment,
        # Every other core checkpoint field is hashed into checkpoint_id.
        # Lineage is the identity itself and provenance describes the save.
        in_state_identity=checkpoint_field not in (None, *_UNHASHED_FIELDS),
        known_gap=known_gap,
        extra_checkpoint_fields=extra_checkpoint_fields,
        nested_reembodiment=nested_reembodiment,
        nested_checkpoint_fields=nested_checkpoint_fields,
        archived_as_prior=archived_as_prior,
    )


def _upper(
    layer: str,
    attribute: str,
    owner: str,
    continuity: ContinuityClass,
    checkpoint_field: str | None,
    reembodiment: Reembodiment,
    *,
    restore_path: str,
    known_gap: str | None = None,
) -> ContinuityEntry:
    return ContinuityEntry(
        attribute=attribute,
        layer=layer,
        owner=owner,
        continuity=continuity,
        checkpoint_field=checkpoint_field,
        restore_path=restore_path,
        reembodiment=reembodiment,
        # Subclasses extend the payload builder, so their fields are hashed too.
        in_state_identity=checkpoint_field not in (None, *_UNHASHED_FIELDS),
        known_gap=known_gap,
    )


def _config(attribute: str, owner: str = "runtime configuration") -> ContinuityEntry:
    """Constructor configuration recorded in effective_config and reapplied."""
    return _core(attribute, owner, _A, "effective_config", _KEEP, restore_path=_EFFECTIVE)


def _handle(attribute: str, owner: str) -> ContinuityEntry:
    """Host or process handle re-supplied by the launcher; never serialized."""
    return _core(attribute, owner, _R, None, _NA, restore_path=_CONSTRUCTOR)


def _facade(attribute: str) -> ContinuityEntry:
    """Stateless domain facade rebuilt by the constructor."""
    return _core(attribute, "core.domains", _C, None, _NA, restore_path="constructor")


REGISTER: tuple[ContinuityEntry, ...] = (
    # --- identity and organism time ------------------------------------------------
    _core("_organism_id", "organism identity", _P, "organism_id", _KEEP),
    _core("_tick_count", "organism time", _P, "saved_at_tick", _KEEP),
    _core("_generation", "lineage", _P, "generation", _KEEP),
    _core("_signal_identity", "signals.identity", _P, "signal_identity_key", _KEEP),
    _core(
        "_cognitive_self_namespace_key",
        "cognition.self_model",
        _C,
        None,
        _KEEP,
        restore_path="derived from the preserved BodySchema private salt",
    ),
    _core(
        "_last_checkpoint_hash",
        "checkpoint lineage",
        _P,
        "checkpoint_lineage",
        _KEEP,
    ),
    _core(
        "_lineage_history",
        "checkpoint lineage",
        _P,
        "checkpoint_lineage",
        _KEEP,
    ),
    # --- genome and expression -----------------------------------------------------
    _core("_genome", "genetics", _P, "genome", _KEEP),
    _core(
        "_gene_expression_state",
        "genetics.expression",
        _P,
        "gene_expression",
        _KEEP,
    ),
    _core("_germline_state", "genetics.germline", _P, "germline_state", _KEEP),
    _core("_parent_ids", "genetics.inheritance", _P, "parent_ids", _KEEP),
    _core("_epigenetic_protocol", "genetics.inheritance", _P, "epigenetic_protocol", _KEEP),
    _core("_mutation_seed", "genetics", _P, "mutation_seed", _KEEP),
    _core("_epigenetic_priors", "genetics", _P, "epigenetic_priors", _KEEP),
    _core("_epigenetic_decay", "genetics", _P, "epigenetic_decay", _KEEP),
    _core(
        "_expression_regulator",
        "genetics.expression",
        _A,
        "runtime_provenance",
        _KEEP,
        restore_path="launcher-supplied; its type is recorded and a different one is flagged as a changed condition",
    ),
    # --- sensory and adaptive learning --------------------------------------------
    _core(
        "_acclimation",
        "host.acclimation",
        _P,
        "acclimation",
        _KEEP,
        extra_checkpoint_fields=("acclimation_replay",),
    ),
    _core(
        "_rhythm_model",
        "host.rhythms",
        _R,
        "rhythms",
        _BODY,
        extra_checkpoint_fields=("rhythms_replay",),
    ),
    _core(
        "_drift_baselines",
        "host.drift",
        _R,
        "drift",
        _BODY,
        extra_checkpoint_fields=("drift_replay",),
    ),
    _core(
        "_adaptive_senses",
        "host.adaptive",
        _P,
        "sensory_development",
        _BODY,
        archived_as_prior="embodiment_archive.body_memories[*].sensory_prior.sensory_development",
    ),
    _core(
        "_sensory_system",
        "sensory",
        _P,
        "sensory_system",
        _BODY,
        archived_as_prior="embodiment_archive.body_memories[*].sensory_prior.sensory_system",
    ),
    _core("_evidence_ledger", "cognition.evidence", _P, "evidence_ledger", _KEEP),
    _core("_signal_knowledge", "signals.knowledge", _P, "signal_knowledge", _KEEP),
    _core(
        "_innate_reactivity",
        "regulation.reactivity",
        _P,
        "innate_reactivity",
        _KEEP,
        nested_reembodiment=(
            ("schema_version", _NA),
            ("reactivity.schema_version", _NA),
            ("reactivity.surprise_threshold", _KEEP),
            ("reactivity.acute_velocity", _KEEP),
            ("reactivity.smoothing", _KEEP),
            ("reactivity.previous_deviation", _BODY),
            ("reactivity.previous_percepts", _BODY),
            ("reactivity.smoothed_velocity", _BODY),
            ("memory", _KEEP),
        ),
        nested_checkpoint_fields=("innate_reactivity",),
    ),
    _core(
        "_reactive_memory",
        "regulation.reactivity",
        _P,
        "innate_reactivity",
        _KEEP,
    ),
    # --- self, body schema and cognition ------------------------------------------
    _core("_self_model", "cognition.self_model", _P, "self_model", _KEEP),
    _core(
        "_body_schema",
        "embodiment.body_schema",
        _P,
        "body_schema",
        Reembodiment.MIXED,
        archived_as_prior="embodiment_archive.body_memories[*].body_schema_prior",
        nested_reembodiment=(
            ("schema_version", _NA),
            ("id_salt", _KEEP),
            ("state", _BODY),
            ("parts", _VOID),
            ("dependencies", _VOID),
            ("global_state", _NA),
            ("cognitive_learning", _VOID),
            ("sensorimotor_view", _VOID),
            ("boundary_evidence", _VOID),
        ),
        nested_checkpoint_fields=("body_schema",),
    ),
    _core(
        "_cognitive_bridge",
        "cognition.bridge",
        _P,
        "cognitive_bridge",
        _KEEP,
        nested_reembodiment=(
            ("graph.weight_codec_version", _NA),
            ("graph.nodes", _KEEP),
            ("graph.edges", _KEEP),
            ("safety_state", _KEEP),
            ("sensory_normalizers", _KEEP),
            ("topology_revision", _KEEP),
            ("tick", _KEEP),
            ("develop_senses", _KEEP),
            ("concept_lineage", _KEEP),
            ("sense_last_seen_tick", _KEEP),
            ("orphan_since_tick", _KEEP),
            ("unrouted_since_tick", _KEEP),
            ("concept_last_active_tick", _KEEP),
            ("node_born_tick", _KEEP),
            ("node_observation_count", _KEEP),
            ("node_active_count", _KEEP),
            ("next_concept_index", _KEEP),
            ("recovery_pending", _KEEP),
            ("shadow_predictions", _KEEP),
            ("predictor_utility", _KEEP),
            ("predictor_retirement", _KEEP),
            ("structural_candidates", _KEEP),
            ("consolidation_generation", _KEEP),
            ("last_consolidated_producer_id", _KEEP),
            ("adaptive_resource_budgets.nodes", _KEEP),
            ("adaptive_resource_budgets.edges", _KEEP),
            ("adaptive_resource_budgets.senses", _KEEP),
        ),
        nested_checkpoint_fields=("cognitive_bridge",),
    ),
    _core("_memory_consolidator", "cognition.consolidation", _P, "memory", _KEEP),
    _core("_generative_cognition", "cognition.generative", _P, "generative_cognition", _KEEP),
    _core("_narrative_journal", "foundation.narrative", _P, "narrative_journal", _KEEP),
    _core(
        "_developmental_tracker",
        "embodiment.development",
        _P,
        "development",
        _KEEP,
        nested_reembodiment=(
            ("schema_version", _NA),
            ("tick", _KEEP),
            ("stress_ticks", _KEEP),
            ("recovery_events", _KEEP),
            ("repair_events", _KEEP),
            ("excretion_events", _KEEP),
            ("maintenance_burden", _KEEP),
            ("retention_burden", _KEEP),
            ("previous_stressed", _BODY),
        ),
        nested_checkpoint_fields=("development",),
    ),
    # --- body, metabolism and physiology (same-Body restart) ---------------------
    _core("_living_body_state", "embodiment.physiology", _P, "living_body", _BODY),
    _core("_metabolism", "embodiment.metabolism", _P, "metabolism", _BODY),
    _core("_homeostasis", "embodiment.homeostasis", _P, "homeostasis", _BODY),
    _core("_physiology", "embodiment.physiology", _P, "physiology", _BODY),
    _core("_assimilator", "embodiment.assimilation", _P, "assimilation", _KEEP),
    _core("_degradation", "embodiment.degradation", _P, "degradation", _KEEP),
    _core("_pending_embodied_work", "embodiment.metabolism", _P, "pending_embodied_work", _BODY),
    _core(
        "_physical_duration_for_tick",
        "embodiment timing",
        _R,
        None,
        _BODY,
        restore_path="supplied by the active Embodiment before the next organism cycle",
    ),
    _core("_resting_requested", "regulation", _P, "resting_requested", _BODY),
    _core(
        "_ontogeny",
        "embodiment.ontogeny",
        _C,
        None,
        _BODY,
        restore_path="rebuilt from the preserved living body state and physiology config",
    ),
    _core(
        "_reacclimation_remaining",
        "embodiment reacclimation",
        _R,
        None,
        _BODY,
        restore_path="reset to kernel_limits.reacclimation_ticks on every restore",
    ),
    # --- action: sensorimotor state, competences and execution authority ---------
    _core(
        "_action_domain",
        "core.domains.action",
        _I,
        "actuation",
        _VOID,
        # Live commitment, pending motor observation and the executive intention
        # are properties of this domain.
        extra_checkpoint_fields=("executive_intention",),
        nested_reembodiment=(
            # The enclosing checkpoint field is an aggregate: the fresh
            # embodiment owns its active flag and actuator surface, while the
            # learned sensorimotor state below is selectively retained.
            ("actuation.enabled", _BODY),
            ("actuation.constitution", _BODY),
            ("actuation.pending_motor_observation", _BODY),
            ("actuation.pending_proprioception", _BODY),
            ("action_domain.schema_version", _NA),
            ("action_domain.selection_threshold", _BODY),
            ("action_domain.actuator_evidence", _BODY),
            ("action_domain.competence_development", _BODY),
            ("action_domain.sensorimotor_v2.effect_space", _KEEP),
            ("action_domain.sensorimotor_v2.schema_version", _NA),
            ("action_domain.sensorimotor_v2.causal_evidence", _KEEP),
            ("action_domain.sensorimotor_v2.agency_acquisition", _KEEP),
            ("action_domain.sensorimotor_v2.exploration", _KEEP),
            ("action_domain.sensorimotor_v2.competences", _KEEP),
            ("action_domain.sensorimotor_v2.composition", _KEEP),
            ("action_domain.sensorimotor_v2.surface_binding", _BODY),
            ("action_domain.sensorimotor_v2.execution_bindings", _VOID),
            ("action_domain.sensorimotor_v2.binding_invalidation", _BODY),
            ("action_domain.active_commitment", _VOID),
            ("action_domain.last_executed_controller_seed_id", _VOID),
            ("action_domain.pending_motor_observation", _VOID),
            ("action_domain.pending_proprioception", _VOID),
            ("executive_intention.schema_version", _NA),
            ("executive_intention.active", _VOID),
            ("executive_intention.active_commitment_id", _VOID),
            ("executive_intention.progress_evidence", _VOID),
            ("executive_intention.consecutive_mismatches", _VOID),
            ("executive_intention.reconciliation_trace", _VOID),
            ("executive_intention.formed", _KEEP),
            ("executive_intention.counts", _KEEP),
            ("executive_intention.outcome_evidence", _KEEP),
        ),
        nested_checkpoint_fields=("actuation", "executive_intention"),
    ),
    _core("_actuation_enabled", "runtime configuration", _A, "actuation", _BODY),
    _core(
        "_executive_admission_policy",
        "agency.policy",
        _A,
        "runtime_provenance",
        _KEEP,
        restore_path="runtime_provenance.session_controls, unless the launcher passes an explicit override",
    ),
    # --- social epistemic state and communication --------------------------------
    _core("_social_ledger", "social.relations", _P, "social_ledger", _KEEP),
    _core("_social_resource_ledger", "social.relations", _P, "social_resource_ledger", _KEEP),
    _core("_exchange_guard", "social.exchange", _P, "exchange_guard", _KEEP),
    _core("_exchange_sequence", "social.exchange", _P, "exchange_sequence", _KEEP),
    _core("_social_exchange_quantum", "social.exchange", _P, "social_exchange_quantum", _KEEP),
    _core("_social_exchange_cost", "social.exchange", _P, "social_exchange_cost", _KEEP),
    # --- recorded constructor configuration --------------------------------------
    _config("_attention_budget"),
    _config("_investigate_ticks"),
    _config("_conflict_z"),
    _config("_min_samples"),
    _config("_profile_version"),
    _config("_competence_gate"),
    _config("_retention_prices"),
    _config("_discover_senses"),
    _config("_bootstrap_semantic_senses"),
    _config("_explicit_metabolism"),
    _config("_auto_promote_predictors"),
    _config("_interoception_enabled"),
    _config("_interoception_mode"),
    _config("_physiology_config", "embodiment.physiology_config"),
    # --- runtime-only configuration recorded as provenance ------------------------
    _core(
        "_cognitive_plasticity_enabled",
        "runtime configuration",
        _A,
        "runtime_provenance",
        _KEEP,
        restore_path="runtime_provenance.session_controls, unless the launcher passes an explicit override",
    ),
    _core(
        "_predictor_promotion_enabled",
        "runtime configuration",
        _A,
        "runtime_provenance",
        _KEEP,
        restore_path="runtime_provenance.session_controls, unless the launcher passes an explicit override",
    ),
    _core(
        "_kernel_limits",
        "cognition.limits",
        _A,
        "runtime_provenance",
        _KEEP,
        restore_path="runtime_provenance.session_controls, unless the launcher passes an explicit override",
    ),
    _core(
        "_persist_replay_state",
        "runtime configuration",
        _A,
        "runtime_provenance",
        _KEEP,
        restore_path="runtime_provenance.session_controls, unless the launcher passes an explicit override",
    ),
    _core(
        "_restored_session_controls",
        "runtime configuration",
        _R,
        None,
        _NA,
        restore_path="set by from_checkpoint to the controls the checkpoint recorded",
    ),
    # --- host and process handles ------------------------------------------------
    _handle("_lifecycle", "host.lifecycle"),
    _handle("_reading_providers", "host.providers"),
    _handle("_host_sense_source", "host.providers"),
    _handle("_interoception_provider", "host.providers"),
    _handle("_habitat", "social.ecology"),
    _handle("_resource_habitats", "social.ecology"),
    _handle("_social_habitat", "social.relations"),
    _handle("_communication_channel", "social.communication"),
    _core(
        "_habitat_released",
        "lifecycle",
        _R,
        None,
        _NA,
        restore_path="constructor: a restored organism has not released its habitat",
    ),
    _core(
        "_social_habitat_released",
        "lifecycle",
        _R,
        None,
        _NA,
        restore_path="constructor: a restored organism has not released its habitat",
    ),
    # --- domain objects -----------------------------------------------------------
    _facade("_cognition_domain"),
    _facade("_development_domain"),
    _facade("_epistemic_domain"),
    _facade("_memory_domain"),
    _facade("_perception_domain"),
    _facade("_physiology_domain"),
    _core(
        "_embodiment_domain",
        "core.domains.embodiment",
        _I,
        None,
        _VOID,
        restore_path="rebound by the embodiment apparatus from the EmbodimentEpisode",
    ),
    _core(
        "_lifecycle_domain",
        "core.domains.lifecycle",
        _P,
        "first_life_history_events",
        _KEEP,
        extra_checkpoint_fields=("last_runtime_vital_state", "last_runtime_development_phase"),
        nested_reembodiment=(
            ("first_life_history_events.sense", _KEEP),
            ("first_life_history_events.concept", _KEEP),
            ("first_life_history_events.prediction", _KEEP),
            ("last_runtime_vital_state", _BODY),
            ("last_runtime_development_phase", _KEEP),
        ),
        nested_checkpoint_fields=(
            "first_life_history_events",
            "last_runtime_vital_state",
            "last_runtime_development_phase",
        ),
    ),
    _core(
        "_regulation_domain",
        "core.domains.regulation",
        _R,
        None,
        _NA,
        restore_path="constructor: pending one-tick credit traces do not cross a restart",
    ),
    # --- modeled runtime ----------------------------------------------------------
    _upper(
        MODELED,
        "_model_registry",
        "modeling.registry",
        _P,
        "private_model_registry",
        _KEEP,
        restore_path=_MODELED_RESTORE,
    ),
    _upper(
        MODELED,
        "_experience_ledger",
        "modeling.experience",
        _P,
        "experience_ledger",
        _KEEP,
        restore_path=_MODELED_RESTORE,
    ),
    _upper(
        MODELED,
        "_experience_archive",
        "modeling.experience",
        _P,
        "experience_archive",
        _KEEP,
        restore_path=_MODELED_RESTORE,
    ),
    _upper(
        MODELED,
        "_episodic_memory",
        "modeling.episodic",
        _P,
        "episodic_memory",
        _KEEP,
        restore_path=_MODELED_RESTORE,
    ),
    _upper(
        MODELED,
        "_social_evidence_ledger",
        "modeling.culture",
        _P,
        "social_evidence_ledger",
        _KEEP,
        restore_path=_MODELED_RESTORE,
    ),
    _upper(
        MODELED,
        "_cultural_policy",
        "modeling.culture",
        _P,
        "cultural_policy",
        _KEEP,
        restore_path=_MODELED_RESTORE,
    ),
    _upper(
        MODELED,
        "_symbol_grounding_ledger",
        "modeling.symbols",
        _P,
        "symbol_grounding_ledger",
        _KEEP,
        restore_path=_MODELED_RESTORE,
    ),
    _upper(
        MODELED,
        "_symbol_policy",
        "modeling.symbols",
        _P,
        "symbol_policy",
        _KEEP,
        restore_path=_MODELED_RESTORE,
    ),
    _upper(
        MODELED,
        "_sequence_grounding_ledger",
        "modeling.sequences",
        _P,
        "sequence_grounding_ledger",
        _KEEP,
        restore_path=_MODELED_RESTORE,
    ),
    _upper(
        MODELED,
        "_sequence_decisions",
        "modeling.sequences",
        _P,
        "sequence_decisions",
        _KEEP,
        restore_path=_MODELED_RESTORE,
    ),
    _upper(
        MODELED,
        "_sequence_max_length",
        "modeling.sequences",
        _A,
        "sequence_max_length",
        _KEEP,
        restore_path=_MODELED_RESTORE,
    ),
    _upper(
        MODELED,
        "_model_request_base_cost",
        "modeling.runtime",
        _A,
        "private_model_config",
        _KEEP,
        restore_path=_MODELED_RESTORE,
    ),
    _upper(
        MODELED,
        "_model_storage_scale",
        "modeling.runtime",
        _A,
        "private_model_config",
        _KEEP,
        restore_path=_MODELED_RESTORE,
    ),
    *(
        _upper(
            MODELED,
            attribute,
            "modeling.runtime (private learning)",
            _P,
            "private_learning_state",
            _KEEP,
            restore_path=_MODELED_RESTORE,
        )
        for attribute in (
            "_private_learning_last_transition_tick",
            "_private_learning_last_corpus_hash",
            "_private_learning_latest_transition_tick",
            "_private_learning_total_transition_count",
            "_private_learning_new_transition_count",
            "_private_learning_validation_window",
            "_private_learning_settled_requests",
        )
    ),
    *(
        _upper(
            MODELED,
            attribute,
            "modeling.runtime (model ancestry)",
            _P,
            "training_ancestry",
            _KEEP,
            restore_path=_MODELED_RESTORE,
        )
        for attribute in (
            "ancestry_training",
            "trace_training_requests",
            "_ancestor_vocabularies",
            "_ancestor_child_failures",
            "_lineage_root_reasons",
            "_retirement_deferrals",
        )
    ),
    _upper(
        MODELED,
        "_private_model_bridge",
        "modeling.gateway",
        _R,
        None,
        _NA,
        restore_path="cleared on restore; the launcher re-attaches an inference bridge",
    ),
    # --- private-model runtime -----------------------------------------------------
    _upper(
        PRIVATE_MODEL,
        "_prospective_agency",
        "agency.prospective",
        _P,
        "prospective_agency",
        _KEEP,
        restore_path=_PRIVATE_RESTORE,
    ),
    _upper(
        PRIVATE_MODEL,
        "_capture_private_experience",
        "modeling.private_runtime",
        _A,
        "private_model_config",
        _KEEP,
        restore_path=_PRIVATE_RESTORE,
    ),
    _upper(
        PRIVATE_MODEL,
        "_enable_prospective_agency",
        "modeling.private_runtime",
        _A,
        "private_model_config",
        _KEEP,
        restore_path=_PRIVATE_RESTORE,
    ),
    _upper(
        PRIVATE_MODEL,
        "_shared_fact_identity",
        "modeling.private_runtime",
        _A,
        "private_model_config",
        _KEEP,
        restore_path=_PRIVATE_RESTORE,
    ),
    *(
        _upper(
            PRIVATE_MODEL,
            attribute,
            "modeling.private_runtime",
            _R,
            None,
            _NA,
            restore_path="constructor: no causal bridge is carried across a restart",
        )
        for attribute in (
            "_pending_private_frame",
            "_pending_outcome_value_credit",
            "_last_prospective_decision",
            "_last_prospective_cost",
            "_last_prospective_query_count",
        )
    ),
)


@dataclass(frozen=True, slots=True)
class EnvelopeField:
    """Checkpoint metadata, including its inventoried nested mapping paths."""

    checkpoint_field: str
    purpose: str
    in_state_identity: bool
    nested_checkpoint_fields: tuple[str, ...] = ()


ENVELOPE_FIELDS: tuple[EnvelopeField, ...] = (
    EnvelopeField("schema_version", "declared outer checkpoint format version", True),
    EnvelopeField(
        "effective_config", "recorded constructor configuration reapplied on restore", True
    ),
    EnvelopeField("constitution_fingerprint", "hash of the genome constitution", True),
    EnvelopeField(
        "checkpoint_lineage",
        "state identity and parent of this save",
        False,
        (
            "checkpoint_id",
            "parent_checkpoint_hash",
            "identity_scope",
            "schema_version",
            "continuation_condition_hash",
            "transforms",
        ),
    ),
    EnvelopeField(
        "runtime_provenance",
        "software and schema that produced the save",
        False,
        (
            "software_version",
            "checkpoint_schema_version",
            "session_controls",
            "session_controls.cognitive_plasticity_enabled",
            "session_controls.predictor_promotion_enabled",
            "session_controls.persist_replay_state",
            "session_controls.kernel_limits",
            "session_controls.kernel_limits.consolidation_epoch_ticks",
            "session_controls.kernel_limits.consolidation_interval_ticks",
            "session_controls.kernel_limits.episodic_epoch_ticks",
            "session_controls.kernel_limits.episodic_min_consolidation_epochs",
            "session_controls.kernel_limits.fast_consolidation_threshold",
            "session_controls.kernel_limits.fast_min_reliability",
            "session_controls.kernel_limits.max_concepts",
            "session_controls.kernel_limits.max_consolidation_candidates",
            "session_controls.kernel_limits.max_edges",
            "session_controls.kernel_limits.max_episodic_checkpoint_bytes",
            "session_controls.kernel_limits.max_episodic_episode_records",
            "session_controls.kernel_limits.max_episodic_episodes",
            "session_controls.kernel_limits.max_episodic_interpretations_per_episode",
            "session_controls.kernel_limits.max_episodic_replay_items",
            "session_controls.kernel_limits.max_episodic_retrieval_candidates",
            "session_controls.kernel_limits.max_incoming_consolidated_weight_norm",
            "session_controls.kernel_limits.max_nodes",
            "session_controls.kernel_limits.max_plastic_checkpoint_bytes",
            "session_controls.kernel_limits.max_salient_event_traces",
            "session_controls.kernel_limits.max_structural_mutations_per_consolidation",
            "session_controls.kernel_limits.max_tentative_edges",
            "session_controls.kernel_limits.reacclimation_ticks",
            "session_controls.kernel_limits.slow_support_epochs",
            "session_controls.executive_admission_policy",
            "session_controls.executive_admission_policy.minimum_relevance",
            "session_controls.executive_admission_policy.readout_threshold",
            "session_controls.expression_regulator",
            "changed_since_restore",
        ),
    ),
)


@dataclass(frozen=True, slots=True)
class ApparatusField:
    """Embodiment history written around the organism checkpoint by Physics3D."""

    checkpoint_field: str
    attribute: str
    continuity: ContinuityClass
    reembodiment: str


APPARATUS_FIELDS: tuple[ApparatusField, ...] = (
    ApparatusField(
        "embodiment_episode",
        "_embodiment_episode",
        _I,
        "closed and archived; a new Body always starts a new episode",
    ),
    ApparatusField(
        "embodiment_archive",
        "_embodiment_archive",
        _P,
        "preserved and extended with the closed episode",
    ),
    ApparatusField(
        "embodiment_lifecycle",
        "_embodiment_lifecycle",
        _P,
        "preserved; epoch advances and the previous epoch moves to history",
    ),
    ApparatusField(
        "embodiment_epoch_summaries",
        "_embodiment_epoch_summaries",
        _P,
        "preserved and extended with the closed epoch summary",
    ),
)


# Not written by every runtime: ancestry state exists only once ancestry training
# has been enabled, and replay accumulators only when persist_replay_state is on.
CONDITIONAL_FIELDS = frozenset(
    {"training_ancestry", "acclimation_replay", "rhythms_replay", "drift_replay"}
)


def required_checkpoint_fields(layer: str) -> frozenset[str]:
    """Fields a current-schema checkpoint of ``layer`` may not lack.

    Every checkpoint field the register assigns to that runtime, plus the save
    envelope. Absence is acceptable only from a schema that predates the field,
    never from a current save (Longitudinal Integrity v1 §5).
    """
    fields = {field for entry in entries_for(layer) for field in entry.checkpoint_fields}
    fields |= {field.checkpoint_field for field in ENVELOPE_FIELDS}
    return frozenset(fields - CONDITIONAL_FIELDS)


def entries_for(layer: str) -> tuple[ContinuityEntry, ...]:
    """Entries visible on a runtime of ``layer``, including inherited layers."""
    if layer not in LAYERS:
        raise ValueError(f"unknown continuity layer: {layer}")
    visible = LAYERS[: LAYERS.index(layer) + 1]
    return tuple(entry for entry in REGISTER if entry.layer in visible)


class LongitudinalContract(StrEnum):
    """Which rule decides what a subject keeps when its Body changes.

    The two are not interchangeable: a result obtained under one says nothing
    about the other. Every runtime class and every study names the one it uses.
    """

    CANONICAL_REEMBODIMENT = "canonical-reembodiment-v1"
    REDUCED_SEED_TRANSPLANT = "reduced-seed-transplant-v1"


class Transplant(StrEnum):
    """What a Body transplant does to one attribute of the reduced seed."""

    PRESERVED = "preserved"
    RESET = "reset_to_naive"
    DETACHED = "kept_without_current_body_grounding"
    REBOUND = "rebound_to_the_new_body"


@dataclass(frozen=True, slots=True)
class ReducedSeedEntry:
    """One attribute of ``CleanEmbodimentSeed`` under transplant.

    ``canonical`` names the ``OrganismRuntime`` register entry that owns the
    same kind of state. ``diverges`` is true where the reduced seed discards or
    ungrounds knowledge that canonical re-embodiment keeps.
    """

    attribute: str
    owner: str
    transplant: Transplant
    canonical: str | None = None
    diverges: bool = False


_T_KEEP = Transplant.PRESERVED
_T_RESET = Transplant.RESET

# The reduced seed is the apparatus of the clean-embodiment studies. On a Body
# transplant it keeps identity, time, genotype and expression and starts
# embodiment-specific inference again from naive. Canonical re-embodiment
# (``REGISTER``) keeps that inference as knowledge and withdraws only its
# authority over the Body. The two are different longitudinal semantics; every
# attribute where they differ is marked ``diverges`` so the difference is a
# declared contract instead of an accident of two implementations.
REDUCED_SEED_REGISTER: tuple[ReducedSeedEntry, ...] = (
    ReducedSeedEntry("symbiont_id", "organism identity", _T_KEEP, "_organism_id"),
    ReducedSeedEntry("total_ticks", "organism time", _T_KEEP, "_tick_count"),
    ReducedSeedEntry("genome", "genetics", _T_KEEP, "_genome"),
    ReducedSeedEntry("germline", "genetics", _T_KEEP),
    ReducedSeedEntry(
        "gene_expression_state", "genetics.expression", _T_KEEP, "_gene_expression_state"
    ),
    ReducedSeedEntry(
        "_expression_regulator", "genetics.expression", _T_KEEP, "_expression_regulator"
    ),
    ReducedSeedEntry("learning_rate", "genetics.expression", _T_KEEP),
    ReducedSeedEntry("exploration_rate", "genetics.expression", _T_KEEP),
    ReducedSeedEntry("expressed_loci", "genetics.expression", _T_KEEP),
    ReducedSeedEntry("last_epigenetic_capture", "genetics (passive telemetry)", _T_KEEP),
    ReducedSeedEntry("epigenetic_capture_count", "genetics (passive telemetry)", _T_KEEP),
    ReducedSeedEntry("epigenetic_protocol", "genetics.inheritance", _T_KEEP),
    ReducedSeedEntry("self_model", "identity continuity model", _T_KEEP, "_self_model"),
    ReducedSeedEntry("_rng", "exploration randomness", _T_KEEP),
    ReducedSeedEntry("_last_prediction_error", "last observed error", _T_KEEP),
    ReducedSeedEntry("historical_output_channels", "embodiment history", _T_KEEP),
    ReducedSeedEntry(
        "competence_library",
        "actuation.competence",
        Transplant.DETACHED,
        "_action_domain",
        diverges=True,
    ),
    ReducedSeedEntry(
        "sensorimotor_model", "embodiment.dynamics", _T_RESET, "_action_domain", diverges=True
    ),
    ReducedSeedEntry(
        "body_schema", "embodiment.body_schema", _T_RESET, "_body_schema", diverges=True
    ),
    ReducedSeedEntry(
        "action_domain", "core.domains.action", _T_RESET, "_action_domain", diverges=True
    ),
    ReducedSeedEntry("_current_surface_fingerprint", "execution authority", _T_RESET),
    ReducedSeedEntry("_channel_outputs", "execution authority", _T_RESET),
    ReducedSeedEntry("_signal_to_input", "current-Body signal mapping", _T_RESET),
    ReducedSeedEntry("last_inputs", "in-flight tick state", _T_RESET),
    ReducedSeedEntry("last_activations", "in-flight tick state", _T_RESET),
    ReducedSeedEntry("current_output_channels", "execution authority", Transplant.REBOUND),
)


__all__ = [
    "APPARATUS_FIELDS",
    "CONDITIONAL_FIELDS",
    "ENVELOPE_FIELDS",
    "LAYERS",
    "LongitudinalContract",
    "REDUCED_SEED_REGISTER",
    "REGISTER",
    "ApparatusField",
    "ContinuityClass",
    "ContinuityEntry",
    "EnvelopeField",
    "ReducedSeedEntry",
    "Reembodiment",
    "Transplant",
    "entries_for",
    "required_checkpoint_fields",
]

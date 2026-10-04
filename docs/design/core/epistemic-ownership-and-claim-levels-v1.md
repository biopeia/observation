---
id: design.core.epistemic-ownership-and-claim-levels-v1
title: "Epistemic Ownership and Claim Levels v1"
document_type: design
domain: core
status: proposed
canonical: false
implementation_status: design
date: 2026-10-04
depends_on:
  - docs/governance/constitution.md
  - docs/design/core/lifecycle-continuity-contract-v1.md
language: en
---

# Epistemic Ownership and Claim Levels v1

## 1. Purpose and limits

The runtime has several representations that can encode evidence, relations,
predictions, or hypotheses. Similar-looking representations are not assumed to
be duplicates. This document makes no consolidation or promotion decision. It
sets the minimum inventory needed before changing an epistemic subsystem or
making a functional claim about it.

The inventory is a design contract, not proof that every row has been audited
end-to-end. Unknown ownership or consumption is recorded as unknown; it must
not be filled by inference from a class name or a checkpoint field.

## 2. Required ownership record

Before a subsystem is merged, extended, or described as functionally capable,
its owner must record:

| Field | Required question |
|---|---|
| Canonical representation | What state does this subsystem own, and what does it explicitly not own? |
| Assertion semantics | What proposition or estimate can it represent? |
| Evidence source | Which witnessed events or upstream records can support an entry? |
| Revision and invalidation | How can contradictory evidence revise, retract, age, or invalidate it? |
| Persistence boundary | Which serializer/checkpoint field owns it, and what continuity class applies? |
| Consumer | Which production decision reads it, and where is that path tested? |
| Authority boundary | Can it authorize action, mutate factual world state, or only propose/inform? |
| Evaluation | Which controlled comparison could show benefit, and what result would falsify it? |

An attribute in a checkpoint register establishes classification and persistence
behavior only. It does not establish evidence quality, consumer use, or utility.

## 3. Evidence levels for capability claims

Use the strongest level actually demonstrated, not the strongest level the code
could theoretically support.

| Level | Claim | Minimum evidence |
|---|---|---|
| E0 — Present | A representation or mechanism exists | Owner, bounds, and runtime construction are identified |
| E1 — Durable | State survives the declared lifecycle boundary | Round-trip/re-embodiment tests verify the owning field and identity boundary |
| E2 — Consumed | A production path reads it and a decision can depend on it | A traced consumer path plus a test that distinguishes the consumed from unused state |
| E3 — Useful | It improves a prespecified outcome | Controlled comparison, matched budgets, adequate repetitions, and a defined analysis |
| E4 — Causal | An intervention on it caused a specified outcome | Preregistered intervention/ablation with controls and the applicable scientific review |

E0/E1 are engineering properties. E2 is a functional integration property.
E3/E4 are empirical claims and cannot be inferred from unit tests, persistence,
code surface, or a successful campaign runner.

## 4. Initial subsystem inventory

This list is a set of distinct candidate owners to trace, not a claim that they
are equivalent or already have complete contracts:

| Candidate owner | Boundary to preserve while auditing | Required next evidence |
|---|---|---|
| CognitiveGraph / cognitive bridge | Graph structure and concept updates are not ground truth about the external world | Trace sources, revision path, checkpoint owner, and decisions consuming graph state |
| SignalKnowledge | Signal relations must not silently become causal or factual claims | Trace its evidence source and every production consumer; distinguish relation semantics from causal evidence |
| EvidenceRevisionLedger | Revision history must remain distinct from current accepted content | Identify canonical owner, lifecycle behavior, and consuming reconciliation path |
| HostAcclimation | Descriptive capability baselines are estimates, not accepted claims about the world | Trace baseline updates, checkpoint ownership, and any decision consumer; distinguish its statistics from ledger dissent counts |
| Predictive learning / predictor credit | A prediction or credit estimate is not an observation | Trace target, outcome reconciliation, promotion/retirement, and decision consumer |
| Causal evidence / sensorimotor evidence | Interventions, observations, and derived causal candidates need explicit provenance | Trace the source event and ensure candidate relations are not promoted to world facts |
| Agency acquisition / competence effects | Acquired competence and its evidence are not execution permission | Trace acquisition evidence, persistence, action selection, and separately held execution bindings |
| Generative hypotheses | Counterfactual or generated hypotheses are proposals, not factual state | Trace factual reconciliation, rejection path, persistent state, and decision consumer |
| Private models and ancestry | Model persistence/lineage is distinct from model accuracy or lineage benefit | Verify checkpoint lineage; separately evaluate prediction quality and ancestry ablation |
| Episodic and consolidated memory | Retained episodes and consolidated summaries are not automatically decision-relevant memory | Trace indexing, public retrieval APIs, retrospective graph support, any internal decision consumer, and compression/revision policy |
| Social evidence | A peer claim remains attributed to its source until evidence reconciliation | Trace publication, reception, assessment, persistence, reconciliation, and decision consequence |
| Symbol/sequence grounding | Grounding links require explicit observation/interaction provenance | Trace the grounding event and downstream consumers; separate labels from validated referents |
| Provenance | Provenance records how a state/result was produced; it is not evidence for the claim itself | Verify propagation and ensure consumers do not treat metadata as factual support |
| BodySchema | Body-specific facts, hypotheses, and historical priors must not be conflated across embodiments | Trace field semantics, invalidation on re-embodiment, and runtime consumers of active-body claims |
| Genome v2 germline marks / expression | Inherited or acquired regulatory marks are not evidence of adaptive benefit | Trace acquisition, explicit protocol gates, transmission, child expression, persistence, and any phenotype/decision consequence |

The rows deliberately do not prescribe a common data model. A merge is allowed
only after the audit establishes identical assertion semantics, evidence
requirements, revision rules, lifecycle ownership, and consumer authority.

The candidate inventory is epistemic, not a list of every state owner in the
source trace in §6. It includes the additional §6 owners **HostAcclimation**,
**BodySchema**, and **Genome v2 germline marks / expression** because each can
hold a baseline, body proposition/prior, or regulatory state that may be
misread as knowledge. The §6 **SensorySystem / AdaptiveSenseModel** is excluded
from this claim inventory: it owns transduction/adaptation state, not
proposition-level evidence; its input and authority boundaries still require
their own subsystem audit. **Somatic EpigeneticPrior** is excluded as an active
epistemic owner because runtime support keys are empty and non-empty priors are
rejected; it remains recorded below as an unsupported/legacy surface, not as
evidence of acquired knowledge. **Rhythm and drift baselines** are likewise
descriptive estimators, not claims, and are excluded; HostAcclimation is
included because it supplies the baseline compared by EvidenceRevisionLedger.

## 5. Current evidence statements

- Model ancestry that survives restore is a durability result (at most E1). It
  does not demonstrate improved learning or adaptation (E3/E4).
- Generative hypotheses, scheduling, reconciliation, and persistence establish
  implemented architecture and testable state transitions. For generative
  hypotheses specifically, one resident-owned hypothesis-to-executive-admission
  path is differentially tested at E2; the other E2 rows in the inventory refer
  to distinct mechanisms and consumers. These tests do not demonstrate decision
  benefit or causal outcome attribution (E3/E4).
- Re-embodiment integration tests establish selected mechanical preservation
  and withdrawal of execution authority. They do not establish useful transfer.
- No scientific run is authorized by this document. Any E3/E4 claim must satisfy
  the repository's experiment, review, and publication gates independently.

### Provisional evidence-level inventory (source audit, 2026-10-04)

These are conservative ceilings for the traced mechanisms, not endorsements of
their scientific validity. E3 and E4 are intentionally absent: no controlled
benefit or causal-intervention evidence was reviewed for this inventory.

| Mechanism | Current level | Evidence boundary |
|---|---|---|
| CognitiveGraph / cognitive bridge | E2 — consumed | `CognitiveBridge.tick()` produces a primitive-family readout from an active graph path; `OrganismRuntime._choose_acquired_action()` passes that readout to `admit_afforded_action()`. `symbiont/tests/unit/core/test_actuation_cognition_p1.py::test_cognitive_graph_readout_changes_executive_admission` holds one affordance fixed and shows an inactive graph readout yields no decision while an active graph readout admits the competence. This establishes a tested consumer dependency, not improved outcomes or causal utility (E3/E4). |
| SignalKnowledge | E1 — durable | Persists and is surfaced to runtime/observer events; no organism decision consumer was found. |
| EvidenceRevisionLedger | E1 — durable | Persists bounded conflict counts and participates in investigation-time dissent reporting; it does not own or accept the baseline, and an isolated downstream decision consequence was not demonstrated. |
| HostAcclimation | E1 — durable | Descriptive per-capability baselines persist. The baseline is not a factual verdict, and no organism decision consequence from this baseline was demonstrated. |
| Predictive learning / predictor credit | E2 — consumed | `CognitionDomain.step()` derives downstream gain from shadow prediction candidates and passes it to `SensorySystem.update_downstream_utility()`. `symbiont/tests/unit/core/test_cognition_predictive_credit.py::test_predictor_credit_flows_through_cognition_domain_into_sensor_utility` holds the sensor and tick path fixed and varies only predictor gain, demonstrating a differential utility consequence through the production domain wiring. This is evidence of consumption/adaptation, not improved perception, action, or organism-level benefit (E3/E4). |
| Causal / sensorimotor evidence | E1 — durable | Transition evidence and derived models persist; causal truth and a differential action-ranking effect are not established. |
| Agency acquisition / competence effects | E2 — consumed | `ActionDomain.predict_competence_effect()` consumes `CompetenceEffectModel` observations; `AffordanceResolver.current()` passes the resulting confidence into `admit_afforded_action()`, where predictive uncertainty contributes to epistemic relevance. `symbiont/tests/unit/agency/test_affordances.py::test_competence_effect_evidence_changes_production_admission_without_changing_authority` varies only effect evidence while holding readout, current-body binding, and the test execution-eligibility gate fixed: six consistent observations yield no admission, while a 4:2 effect split yields admission. This demonstrates evidence consumption, not evidence quality, causal truth, physical execution, or organism-level benefit (E3/E4). |
| Generative hypotheses | E2 — consumed | `ResidentGenerativeCognition._ensure_hypothesis()` stores a predicted outcome; `OrganismRuntime._generative_affordances()` projects only active hypotheses into effect-directed affordances, and `_choose_acquired_action()` passes them to executive admission. `symbiont/tests/unit/core/test_generative_admission_consumption.py::test_live_hypothesis_changes_production_admission_only_for_existing_affordance` creates a hypothesis through the resident owner, round-trips it through the resident checkpoint, holds an existing affordance fixed, and shows admission changes only when the restored live hypothesis is present; invoking the resident factual-reconciliation API with a contradictory outcome marks it contradicted and removes that admission route. The production private-runtime callsite first creates an `OBSERVED` episode from a completed transition, then supplies its outcome tokens and evidence-reference strings to `note_factual_outcome()` with `model_ids=("private-slm",)`. The reconciliation method itself only requires nonempty reference strings; it does not resolve them against the canonical experience owner. Thus the static callsite is constrained to the observed-episode path, but the evidence-reference contract is caller-trusted rather than enforced at this API boundary. The differential test directly supplies a reference and does not cover that end-to-end lineage. Neither path establishes online hypothesis-generation quality, benefit, causal truth, or execution authority (E3/E4). |
| Private models | E2 — consumed | `PrivateModelOrganismRuntime._deliberate_prospectively()` feeds active-model outcome proposals to `ProspectiveAgency.deliberate()`. `symbiont/tests/unit/modeling/test_private_modeling_contract.py::test_private_model_prediction_changes_prospective_choice` holds affordances, graph readouts, active-model identity, and observed outcome values fixed, then reverses only the model-output mapping and verifies prospective choice reverses. This is a mocked active-model bridge integration test, not native model-quality, adaptive-benefit, or causal evidence (E3/E4). |
| Model ancestry | E1 — durable | Parent vocabulary can contribute to a child training request; persistence does not show improved learning or adaptation. |
| Episodic/consolidated memory | E1 — durable; replay path consumed, decision effect unproven | Runtime exposes recall, experience-prediction, and cognitive-replay APIs. A resting-only internal caller materializes a retrieved episode as non-factual generative replay, and consolidated episode co-occurrence can feed retrospective support into CognitiveBridge. `symbiont/tests/unit/modeling/test_private_experience_pipeline.py::test_private_runtime_resting_replays_factual_episode_without_new_experience` verifies replay materialization without adding a factual experience record. No differential test shows this replay changes a later action decision, so this remains below E2 under §3. |
| Social evidence | E1 — durable | Source-attributed claims and evidence persist and affect cultural retention/transmission; no peer-claim-to-organism-decision path was found. |
| Symbol / sequence grounding | E2 — consumed | Locally observed associations are read by grounded emission methods and tests exercise the association-dependent output; this establishes substrate-local use, not validated shared meaning. |
| Provenance | E1 — durable | A bounded live-reference frontier persists; the event ring is not persisted and provenance coverage is producer-specific. |
| BodySchema | E1 — durable | Re-embodiment tests prove archival preservation and active evidence reset; no transfer-utility claim follows. |
| Somatic EpigeneticPrior | E0 — present | Runtime support keys are empty and non-empty priors are rejected; this does not establish acquired or consumed somatic marks. |
| Genome v2 germline marks / expression | E1 — durable; end-to-end mechanical chain tested | `symbiont/tests/integration/test_germline_capture_to_budding.py::test_real_ticks_capture_germline_mark_transmitted_through_resident_budding` drives 64 actual parent runtime ticks, verifies capture of an acquired mark, checkpoints/restores the parent, exercises `ResidentOrganism` budding, and verifies the mark reaches the child and affects its birth gene expression. This closes the prior gap about an integrated test for capture → restore → actual resident reproduction → child expression. The test establishes mechanical integration and a mark-dependent expression value, not adaptive utility, improved phenotype, transgenerational benefit, or causal phenotype benefit (E3/E4). It does not demonstrate a decision consumer, so the evidence-level ceiling remains below E2 under §3. |

These levels are scoped to the mechanisms and paths named above. A subsystem
may contain lower-level components; do not promote the whole subsystem beyond
the evidence shown. Raise a level only with the required differential test or
controlled study, and record the exact scope and artifact.

## 6. Bounded source trace (completed 2026-10-04; not owner-approved)

This is a bounded source map, not completion of the owner audit in §2 or the
acceptance condition in §8.
It records direct observations from the current runtime implementation. A
checkpoint field or read path is not, by itself, evidence that a representation
is epistemically sound or that it changes a decision.

| Candidate owner | Runtime / persistence owner | Production read path found | What remains unproven or unaudited |
|---|---|---|---|
| CognitiveGraph | `OrganismRuntime._cognitive_bridge`; exported in `cognitive_bridge` by `OrganismRuntime._build_checkpoint_payload()`; implementation in `symbiont/cognition/graph.py` and `symbiont/core/cognition/bridge.py` | Perception feeds `CognitiveBridge.tick()`, which emits primitive readouts. Runtime supplies them to acquired-action admission; `ActionDomain` also builds competence proposals from readouts over its threshold. Graph structure can change through sense admission, primitive-readout synchronization, and planner-applied consolidation mutations; applied mutations update node metadata and advance `topology_revision`. Predictor errors, concept support, and actual primitive/motor outcomes update separate predictor/lifecycle/plasticity state. `observe_primitive_execution()` only records associations after the corresponding readout is admitted; `observe_homeostatic_action_outcome()` accepts a delayed intrinsic value for an actually executed opaque action and applies it to existing concept/readout context. `topology_revision` is a structural/cache revision, not a semantic assertion revision or contradiction ledger. `symbiont/tests/unit/core/test_actuation_cognition_p1.py::test_cognitive_graph_readout_changes_executive_admission` holds one affordance fixed and differentiates admission by graph readout; `symbiont/tests/unit/core/test_cognition_bridge.py::test_structural_mutation_advances_topology_revision_and_reports_mutations` checks structural revision behavior. | Graph edges and activations are not proposition-level claims with a unified evidence/provenance record. Mutation metadata and topology revision do not establish the truth, source lineage, or valid retraction of an edge. Trace the exact runtime event producers for all evidence updates and the independent semantic/revision policy before treating the graph as an evidence ledger. Admission tests establish a tested consumer dependency, not physical action, causal efficacy, or usefulness (E3/E4) |
| EvidenceRevisionLedger | `OrganismRuntime._evidence_ledger`; checkpoint field `evidence_ledger`; implementation in `symbiont/core/cognition/evidence.py` | `EpistemicDomain.investigate()` obtains `SecondLookSession` readings from selected, manifest-supported capabilities and passes them to `revise()`. The ledger computes the unweighted mean of non-null values and, when the existing baseline has positive standard deviation, records dissent at `abs(z_score) >= conflict_z` (default 2.0). Detailed dissent values are retained only in a bounded in-memory deque; the checkpoint stores only bounded per-capability conflict counts. It then calls `HostAcclimation.observe()` with those readings whether or not dissent was found. **HostAcclimation owns the baseline statistics and update rule; EvidenceRevisionLedger owns only dissent detection/counting and the returned report, not an accepted estimate or factual adjudication.** Current dissent feeds narrative/event reporting; no production consumer of persisted conflict counts or direct ledger-to-action decision path was found. | The ledger does not own accepted estimates and its persisted counts do not revise baseline or affect a traced production decision. HostAcclimation's baseline changes from valid readings independently of whether the ledger records dissent. End-to-end lineage from individual provider readings and the epistemic interpretation of the fixed z-score threshold remain owner-audit questions; persistence of contradiction counts is not decision use or evidence quality |
| Predictive learning / predictor credit | In-graph predictor nodes live in `OrganismRuntime._cognitive_bridge`; out-of-graph shadow candidates are bridge state; sensory downstream utility belongs to `SensorySystem` | `CognitionDomain.step()` updates the bridge, nominates shadow predictions when promotion is enabled, derives nonnegative `predictive_gain_by_name`, and passes it to `SensorySystem.update_downstream_utility()`. Thus shadow gain is consumed by sensory utility adaptation, not directly as action permission. `symbiont/tests/unit/core/test_cognition_predictive_credit.py::test_predictor_credit_flows_through_cognition_domain_into_sensor_utility` varies predictor gain through this production wiring and verifies a differential utility consequence. | Predictor inputs, sample alignment, retirement/promotion, and checkpoint ownership still need separate source-level audit. The test demonstrates adaptation of an internal utility measure, not improved perception, causal relation, or organism-level benefit (E3/E4) |
| Causal evidence / sensorimotor evidence | `AcquisitionState.causal_evidence` owns the bounded `CausalEvidenceLedger`; action-domain checkpoint stores its payload; effect, controllability, and agency models are derived or stored views | `AcquisitionState.learn()` records observed `SensorimotorTransition`s, updates effect estimates, and updates controllability/agency against a counterfactual-free view. `ActionDomain` reads competence effect predictions for expectation/reporting; they are not execution permission. Passive windows are recorded separately as non-intervention evidence. | Provenance strength of transition state references and effect labeling; coverage of all transition writers/consumers and restore/re-embodiment semantics; whether prediction changes any action ranking independently of execution bindings. Evidence-derived relations must not be described as causal truth without controlled intervention and alternative-opportunity support |
| Agency acquisition / competence effects | `ActionDomain` composes `AgencyAcquisition`, `CompetenceLibrary`, and `CompetenceExecutionBindingRegistry`; acquisition owns causal evidence and learned dimensions | Observed transitions update causal/effect/control/agency models. Established primitive competence evidence plus `ground_competence()` can materialize a `MotorCompetence`; separately, `ExecutionBindingRegistry.bind_from_evidence()` binds it to the current surface. Composed competences follow a separate evidence path. `affordance_resolver()` reads competence knowledge and checks executable bindings separately, preserving the distinction between prediction and permission. `symbiont/tests/unit/agency/test_affordances.py::test_competence_effect_evidence_changes_production_admission_without_changing_authority` differentially tests effect evidence while holding readout, body binding, and the test execution-eligibility gate fixed. | Full evidence lineage from each competence claim to its underlying transition set; all materialization/revocation paths and restore/re-embodiment behavior; whether any consumer treats maturity or predicted effect as sufficient authority without a current binding; controlled evidence for adaptive benefit. The admission test is not evidence quality, physical execution, or usefulness (E3/E4) |
| Epigenetic priors and germline marks | `OrganismRuntime` checkpoints `_epigenetic_priors` and decays them, but `_SUPPORTED_EPIGENETIC_KEYS` is empty, so non-empty runtime priors are rejected. `GermlineState` separately owns inherited/acquired `EpigeneticMark`s in the Genome v2 genetics API; runtime-created germline capture is disabled unless explicitly configured. | `DevelopmentDomain` updates expression and runtime tick passes selected effective expression values to `GermlineState.capture_acquired_variation()`, gated by the organism capture flag and an enabled `EpigeneticProtocol`. `OrganismRuntime.inheritance_package()` decays and includes inherited/acquired marks only when protocol transmission is enabled. The resident budding path passes that package to child construction, and child construction uses its marks to establish inherited birth expression. `symbiont/tests/integration/test_germline_capture_to_budding.py::test_real_ticks_capture_germline_mark_transmitted_through_resident_budding` covers real tick capture, parent restore, resident budding, transmission, and child expression. Runtime `EpigeneticPrior` is not consumed by gene expression. | Do not conflate somatic `EpigeneticPrior` decay with Genome v2 germline marks. The integration test establishes a mechanical acquisition-to-child-expression path under explicit protocol gates; it does not establish a decision consumer, transgenerational adaptation, scientific utility, or causal phenotype benefit (E3/E4). The somatic prior remains unsupported and rejected |
| BodySchema | `OrganismRuntime._body_schema` owns the active `BodySchemaEngine`; the current checkpoint field is `body_schema`. Closed embodiment history archives a copy of the prior schema as episode evidence. | Embodiment and action domains add sensory phenotype, self-model, cognition, and agency-boundary observations. Re-embodiment archives the prior schema and calls `reset_for_new_embodiment()` on the active schema; action restoration validates execution bindings against the current surface independently of BodySchema. | The [2026-10-04 consumer audit](../../../lab/research/audits/current/2026-10-04-body-schema-consumer-audit.md) traced active and archived readers and found no active consumer of archived `body_schema_prior`: it is serialized and used for closed-episode summaries, not restored into the active engine or used as execution authority. This supports the canonical-path authority boundary, not inference validity, cross-Body transfer utility, or arbitrary external-consumer safety. Any future promotion of archive priors into active inference requires explicit prior/fact semantics and differential consumer tests |
| SensorySystem / AdaptiveSenseModel | `OrganismRuntime._sensory_system` and `_adaptive_senses`; checkpoint fields `sensory_system` and `sensory_development`. The acquired sensory payload is archived as `BodySpecificMemory.sensory_prior`; both active systems are replaced by the fresh Body's checkpoints during re-embodiment. | `PerceptionDomain.step()` feeds organism readings into `SensorySystem.transduce()`; `transduce()` selects stored sensors by `source_ids`. `AdaptiveSenseModel` also indexes learned state by `capability_id`. The transition archives Body A's sensory state and installs Body B's fresh sensory state, so reused source/capability IDs cannot reactivate old transducers or adaptive states. | Regression tests verify archived payload equality and fresh active state; the composite developed Body A → Body B test exercises checkpoint, re-embodiment, restore and subsequent ticks. This establishes a safe active-binding boundary, not transfer utility: archived sensory learning remains historical and is not automatically applied to a new Body. |
| Episodic and consolidated memory | These are distinct stores: `ModeledOrganismRuntime` owns `_episodic_memory` and its checkpointed experience records; `OrganismRuntime` owns `_memory_consolidator` and checkpoint field `memory`. `AgentMemory`/`Episode` in `core/cognition/memory.py` is not constructed by the traced runtime path. | The episodic store exposes `recall_experiences()`, `predict_from_experience()`, and `cognitive_replay()` (`symbiont/src/symbiont/modeling/runtime.py:788-834`). In a resting-only private-runtime path (`private_runtime.py:867-883`), one retrieved replay is materialized as non-factual offline Generative Cognition state; the test `symbiont/tests/unit/modeling/test_private_experience_pipeline.py::test_private_runtime_resting_replays_factual_episode_without_new_experience` checks that no new factual experience is added. `_project_episodic_consolidation()` sends consolidated co-occurrence into `CognitiveBridge.observe_retrospective_support()` (`:774-786`). Separately, `MemoryDomain.observe()` converts drift and prediction loss to novelty/surprise signals and records attended/reliable salience; `MemoryConsolidator` stores bounded statistical or quantized salient-event projections. | Do not collapse episodic retrieval, generated replay, graph retrospective support, and consolidation summaries into one owner. Retrieved episodes affect generative replay state in the resting path, but no differential test shows replay changes a later action decision; the consolidation-to-graph path likewise lacks an episode-to-admission differential test. Specify episode evidence/provenance, retrieval/replay semantics, forgetting/eviction, and contradiction handling; distinguish the standalone `AgentMemory` API from the active runtime store. |
| Private models and ancestry | `ModeledOrganismRuntime` owns `PrivateModelRegistry`, `ExperienceLedger`, training requests, and checkpoint fields; `PrivateModelOrganismRuntime` adds temporal experience capture and prospective action deliberation | The private runtime captures t→t+1 observed outcome records, validates active predictions against those observations, and can call an active model to deliberate only over already-read-out and currently afforded competences. Model predictions influence prospective choice; real outcome value is learned from later observed outcomes. With `ancestry_training` enabled, a SHADOW parent can contribute its tokenizer vocabulary to a child training request; this is vocabulary continuity, not inherited weights or acquired organism knowledge. | Verify all restore and prediction paths against these ownership boundaries; ancestry mechanics do not establish prediction accuracy or ancestry benefit. Controlled prediction and ancestry-ablation evidence is still required before E3/E4 claims |
| Symbol/sequence grounding | `ModeledOrganismRuntime` owns receiver-side `SymbolGroundingLedger` and `SequenceGroundingLedger`; channel delivery records opaque exposures and checkpoints persist the local ledgers | `observe_symbolic_outcome()` / `observe_sequence_outcome()` associate locally observed outcome tokens with received opaque symbol/sequence tokens. Grounded emission methods select from local associations with support exceeding contradiction; the associations affect local communication choices, not world-state truth. `predict_symbolic_outcome()` / `predict_sequence()` expose the learned association. | Outcome-token authority and the external protocol that marks support/contradiction remain explicit assumptions; an association means predictive correspondence within this substrate, not validated semantic reference or shared meaning. Audit transport/source attribution and decision consequences before making stronger grounding claims |
| Provenance | `AgencyAcquisition.provenance` owns the shared `ProvenanceLog` for action/acquisition paths; the runtime exposes it and checkpointing retains the live-reference frontier | `ProvenanceLog.emit()` records structural `CausalEvent`s and updates immediate causes for produced refs; subscribers are outward-only. Events carry bounded opaque refs and scalar parameters, not evidence values or claim semantics. The recent event ring is in-memory only; checkpoint persists the live frontier, not event history. | Coverage is producer-specific, not a universal proof that all state changes have complete lineage. Missing refs/events, retired refs, and causes beyond the immediate frontier limit what can be reconstructed. Provenance explains recorded derivation; it must not be treated as evidence that its subject claim is true |
| Acclimation, rhythm, and drift baselines | `OrganismRuntime` owns `_acclimation`, `_rhythm_model`, and `_drift_baselines`; checkpoint fields are `acclimation`, `rhythms`, and `drift`, with replay accumulators where configured. Acclimation is preserved as a capability-keyed prior; rhythms and drift are reset from the fresh Body checkpoint at re-embodiment. | `PerceptionDomain.step()` updates acclimation from current cognitive readings, rhythm statistics from current percepts and macro-phase, and drift baselines by percept name. Drift observations feed memory/development/lifecycle summaries and second-look selection. Plasticity-driven sensor eviction also removes a drift baseline when its last manifest source disappears. A composite re-embodiment regression develops non-empty rhythm/drift replay state and verifies those fields are replaced with fresh-body state while acclimation is preserved. | These are descriptive adaptation statistics, not ground truth. Rhythm/drift state has percept-name rather than stable Body-source identity, so the implementation treats those estimators as body-bound and withdraws them on Body replacement. Acclimation remains a longitudinal prior keyed by opaque capability identity; that key does not independently establish utility or truth. The transition regression establishes mechanical policy, not beneficial transfer or scientific validity |
| SignalKnowledge | `OrganismRuntime._signal_knowledge`; checkpoint field `signal_knowledge`; implementation in `symbiont/core/signals/knowledge.py` | `SignalObservationBatch` supplies selected valid values under opaque signal IDs; unselected valid manifest entries are excluded from learning history. Claims are bounded descriptive stability/change, synchronous-association, one-tick lead-prediction, or endogenous self-relevance records. Stability/change/association use fixed opportunity thresholds to reach `hypothesis`; lead-prediction compares prospective loss against zero, mean, persistence, and conditional references using fixed margins, and self-relevance receives a boolean derived in `PerceptionDomain` from sensor `sampling_outcomes` (nominal success is favorable; missing, unavailable, or provider failure is unfavorable), keyed by opaque signal identity; ambiguous capabilities from one provider are excluded. Lead-prediction/self-relevance status is revised by fixed 64-tick epochs: two failed epochs yield `contested`; three successful epochs and at least 144 validation opportunities yield `supported`. Supported/hypothesis claims become `stale` after 192 ticks without observation; stale is not negative evidence. Revision events record status changes/reasons. `LifecycleDomain.events()` checks `lead_prediction` only to emit outward `first_prediction`; runtime/Observatory expose the view. No action-choice or organism-cognition consumer was found in the traced production path. | These claim classes are operational summaries, not causal/factual propositions; the self-relevance target is sensor-sampling success/availability, not an independently established organism outcome; whether this apparatus-derived target validly supports an organism-level relevance claim requires owner confirmation. The event/report path is not a decision consumer (no E2 claim); audit any intended consumer and test its decision dependence before promoting that level |
| Generative hypotheses | `OrganismRuntime._generative_cognition`; checkpoint field `generative_cognition`; implementation under `symbiont/cognition/generative/` | `_ensure_hypothesis()` stores a predicted effect in the resident owner. After a resident checkpoint round-trip, `_generative_affordances()` maps only active anticipated effects to currently resolved affordances, and `_choose_acquired_action()` supplies those to executive admission. The named test holds an existing affordance fixed, shows the restored live hypothesis changes admission, then calls the resident factual-reconciliation API with a contradictory outcome and shows the hypothesis is no longer admitted. In the private runtime, a completed transition is recorded as an `OBSERVED` episode before the callsite forwards its outcomes and evidence-reference strings, filtered to `private-slm`. The resident API checks that references are nonempty but does not resolve them against the experience store; current provenance therefore depends on the production caller honoring its contract. | The differential test uses a resolver stub and directly supplies an evidence reference; it does not validate end-to-end reference resolution or upstream factual-outcome provenance. The API boundary permits a caller to assert factual inputs without proving their canonical origin. Add a narrow contract/test at the owner boundary before treating reconciliation provenance as enforced. Also audit arbitration in the wider runtime; no E3/E4 utility claim follows from integration alone |
| Social evidence | `ModeledOrganismRuntime._social_evidence_ledger`; checkpoint field `social_evidence_ledger`; implementation in `symbiont/modeling/culture.py` | `autonomous_cultural_step()` uses local ledger state for composition and transmission; `autonomous_retention_step()` may drop claims/retire composites; validation is exposed as a separate proposal. Claim delivery is channel-mediated and source-attributed. Cultural status/lineage is projected outward for observation. No connection from social assessments to cognitive/action admission was found in the runtime path. | A canonical peer-claim assessment → reconciliation → accepted-knowledge → organism-decision path is not established; validation proposal is not acceptance. No general trust authority or socially acquired organism knowledge is implied |

The source paths above can be checked in `symbiont/core/orchestration/runtime.py`,
`symbiont/core/domains/epistemic.py`, `symbiont/core/cognition/evidence.py`, and
`symbiont/core/domains/cognition.py`, `symbiont/cognition/learning.py`, and
`symbiont/actuation/evidence.py`, `symbiont/actuation/acquisition.py`, and
`symbiont/core/domains/action.py`,
`symbiont/modeling/runtime.py`; current focused tests include
`symbiont/tests/unit/core/test_cognition_bridge.py`,
`symbiont/tests/unit/core/test_evidence_revision.py`,
`symbiont/tests/unit/core/test_signal_knowledge.py`,
`symbiont/tests/unit/cognition/test_generative_cognition_persistence.py`, and
`symbiont/tests/unit/agency/test_executive_admission.py`,
`symbiont/tests/unit/modeling/test_private_modeling_contract.py`,
`symbiont/tests/unit/modeling/test_private_experience_pipeline.py`,
`symbiont/tests/unit/test_symbols.py`,
`symbiont/tests/unit/modeling/test_sequence_substrate.py`,
`symbiont/tests/unit/actuation/test_causal_footprints.py`,
`symbiont/tests/unit/actuation/test_causal_evidence.py`,
`symbiont/tests/unit/actuation/test_sensorimotor_v2_architecture.py`, and
`symbiont/tests/unit/actuation/test_agency_before_competence.py`,
`symbiont/tests/unit/actuation/test_competence_convergence.py`, and
`symbiont/tests/unit/core/test_consolidation.py`,
`symbiont/tests/unit/core/test_social.py`. These suites cover their named
mechanisms and/or persistence. The differential tests cited above establish
selected E2 consumer paths; they do not complete the source, revision,
authority, and evaluation audit for every candidate in §4. Continue that audit
before treating SYM-07 as resolved.

## 7. Comparative boundaries and disposition

The source trace does **not** support merging the current mechanisms into one
generic knowledge store or one cognitive process. Similar predictive or
evidence-related vocabulary hides different owners, state, and consumers.
Keep the following boundaries explicit:

| Role | Current owners/examples | Disposition |
|---|---|---|
| Structured readout used in acquired-action admission | CognitiveGraph / CognitiveBridge | Keep separate from evidence ledgers: graph structure/readout is consumed, but graph edges are not a general proposition/evidence ledger. Define source and contradiction semantics before stronger factual claims. |
| Statistical estimates and predictor credit | HostAcclimation, PredictorLifecycle / predictor credit, competence-effect estimates | Keep estimates separate from factual claims and from execution permission. EvidenceRevisionLedger records bounded dissent against an acclimation baseline; it does not own that baseline or a replayable history. Predictor credit updates sensory utility, not the truth of its target. |
| Prospective proposal/model processes | Generative hypotheses, Private Models | Keep distinct for now. Generative cognition proposes anticipated effects over existing affordances; private models provide outcome proposals for already-read-out/afforded competences. Their downstream arbitration deserves a source trace, but shared prediction vocabulary alone is not duplication. Neither gets factual or motor authority. |
| Experience and retrospective support | Episodic experience store, consolidation summaries, CognitiveBridge retrospective support | Keep the episode store, its public query APIs, compressed summaries, and graph support path distinguishable. The internal action-selection consequence of retrieved episodes remains unproven. |
| Source-attributed communication associations | Social evidence, symbol grounding, sequence grounding | Keep separate from accepted world knowledge. These affect cultural retention/transmission or local communication choices; caller-supplied support and outcome labels still need provenance/reconciliation contracts. |
| Lineage / derivation metadata | Provenance | Keep separate from evidence: provenance describes recorded derivation and producer coverage, not whether the resulting claim is true. |
| Body/regulatory/permission state | BodySchema, germline marks/expression, execution bindings | Do not count these as interchangeable cognitive knowledge. Preserve historical body records, current-body state, regulatory inheritance, and present execution authorization as distinct concepts. |

### Current action-admission composition traced

The production path is a sequence of bounded gates, not a vote among all
cognitive subsystems:

1. The action domain supplies currently afforded competences; current-body
   bindings and the later action arbitrator remain the execution/authority
   boundary.
2. The base runtime can admit a competence represented by an active Cognitive
   Graph primitive readout or by a Generative Cognition anticipated effect,
   subject to epistemic or homeostatic relevance and executive policy.
3. The private-model runtime tries prospective model deliberation first, but
   only among currently afforded competences that also have active primitive
   readouts. If that returns a decision, it short-circuits the base admission
   path. If it abstains, the base graph/generative admission path runs.
4. Thus private-model proposals and generative proposals are not currently
   fused into one score. Their ordering is explicit in runtime control flow:
   private-model choice first, graph/generative fallback second. This is the
   smallest defensible architecture description; do not refactor toward a
   unified selector absent a concrete contradictory-decision case.
5. At rest, retrieved episodic replay can seed non-factual offline Generative
   Cognition state. This is a memory-to-generative bridge, not a direct motor
   command or a demonstrated later decision benefit.

This traced sequence is a code-level contract description, not a causal or
utility result. Existing differential tests cover selected readout,
competence-effect, generative-admission, and private-model paths separately;
they do not establish the complete arbitration behavior across all paths.

### Practical order

1. Complete per-owner records for assertion/effect semantics, admissible
   evidence, revision/invalidation, lifecycle/persistence, consumer authority,
   and falsifier. Split records where ownership is already distributed (for
   example, acquisition evidence vs competence materialization vs execution
   binding; private-model state vs ancestry metadata).
2. Trace source lineage and conflict/retraction behavior in the narrowest
   high-risk paths first: graph updates, predictor/outcome reconciliation,
   generative factual reconciliation, competence-effect evidence, and
   caller-supplied social/symbol/sequence assessments. For generative factual
   reconciliation, the private-runtime production caller is statically traced
   to an `OBSERVED` episode, but `note_factual_outcome()` trusts the supplied
   evidence-reference strings instead of resolving them against that owner.
   Keep this as an explicit API-contract debt; do not claim the test proves
   end-to-end provenance or redesign ownership without first specifying the
   canonical reference contract.
3. The private-model-first / base-admission-fallback ordering now has focused
   control-flow regressions in
   `symbiont/tests/unit/modeling/test_private_modeling_contract.py` (private
   return short-circuits; abstention reaches the base path). These tests lock
   precedence, not a joint score or outcome benefit. Keep current-body
   execution authority separate. Do not run an outcome campaign for this
   contract audit. For episodic memory, the internal replay-to-GC bridge is
   established; only later decision consumption remains unproven. Existing
   tests may establish E2 only for the exact paths they differentially
   exercise.
4. Only after those records expose genuinely identical semantics, evidence
   rules, lifecycle ownership, and consumers should a consolidation proposal
   be considered. This pass authorizes no merge, API redesign, or runtime
   refactor.
5. Keep E3/E4 evaluation separate. No experiment was run or authorized here;
   usefulness or causal benefit remains unclaimed.

The source audit also confirms that episodic retrieval is consumed by a
resting-only internal path to construct non-factual generative replay, in
addition to retrospective consolidation into the cognitive graph. What remains
unproven is an episode/replay-dependent later action decision and its
differential effect. This does not raise episodic decision consumption above
E1.

## 8. Audit closure and deferred debt

The bounded engineering audit requested for this inventory is complete as a
source-and-test review of the current branch. This closes the audit pass, not
the design's owner-approval condition, the listed implementation debt, or any
scientific claim. The current evidence supports these dispositions:

| Area | Audit disposition | Remaining debt |
|---|---|---|
| CognitiveGraph / bridge; predictor credit; competence-effect admission; generative admission; private-model choice | Separate production consumers and tested differential paths are identified. Their evidence ceilings are the scoped E2 claims in §5. | Complete source/retraction coverage is absent; tests establish admission/use, not evidence validity, physical execution, or benefit. |
| EvidenceRevisionLedger / HostAcclimation; SignalKnowledge | Ownership split and production roles are traced. They report dissent, maintain baselines, or expose operational signal summaries; no organism action consumer was found for the ledger or SignalKnowledge. | Provider-to-reading lineage and interpretation of fixed thresholds remain unvalidated; persisted dissent counts do not revise accepted state. |
| Causal/sensorimotor evidence and acquisition | Observed transitions, derived estimates, competence materialization, and current-body execution bindings are distinct owners. | Full evidence lineage, revocation/restore coverage, and any independent ranking consequence require narrower owner-level follow-up. No causal truth is established. |
| Episodic/consolidated memory | Storage, retrieval/replay, consolidation summaries, and graph retrospective support are distinct. The resting replay path is consumed as non-factual generative state. | No tested episode-to-later-action effect; retrieval provenance, eviction, and contradiction policy are not complete contracts. |
| Generative factual reconciliation | Production private-runtime caller is traced through an `OBSERVED` episode. | `note_factual_outcome()` trusts nonempty caller-provided evidence references and does not resolve them. Canonical reference ownership and a boundary regression remain open. |
| Social evidence; symbol/sequence grounding | Source-attributed social state and local communication associations have bounded uses; no canonical social-claim-to-action path was found. | Caller-supplied outcome authority, transport attribution, reconciliation, and any future decision path need explicit contracts. No trust or shared-meaning claim is supported. |
| Private models / ancestry | Persistence and prospective-choice consumption are mechanically covered at the stated scope; ancestry remains vocabulary continuity. | Prediction quality and ancestry utility are unproven and require separate controlled evaluation before E3/E4 claims. |
| Provenance | Structural derivation metadata and its live-reference persistence are distinguished from evidence and truth. | Producer coverage is not universal; the event ring is not a complete reconstructable history. |
| BodySchema, sensory adaptation, epigenetic/genome marks | Current-body authority, archived priors, active sensory state, somatic priors, and germline marks are kept separate; the cited mechanical re-embodiment/inheritance paths remain below utility claims. | No transfer/adaptive-benefit claim; unsupported somatic priors remain rejected; germline tests show mechanism, not benefit. |

No two candidate systems were shown to have identical assertion semantics,
evidence rules, revision behavior, persistence ownership, and consumers.
Therefore the audit recommends **no consolidation, no unified cognition
score, and no broad runtime refactor**. Keep current owners separate and
resolve the specific contract debts above only when an owner or consumer needs
them. The focused cross-subsystem engineering regression set run for this
closeout passed: 213 tests. No scientific experiment or E3/E4 evaluation was
run.

## 9. Acceptance condition

This design remains proposed until an owner approves the boundaries and
dispositions above. The source-audit pass is complete; that approval is not
implied by this report. Any future subsystem merge, capability promotion, or
claim beyond the evidence levels in §5 still requires its specific missing
§2 contract fields, implementation/test links, and (for E3/E4) the separate
controlled scientific process. Missing or conflicting ownership is a finding
to resolve; it is not permission to merge systems or infer capability.

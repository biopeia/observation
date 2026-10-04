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
| Predictive learning / predictor credit | A prediction or credit estimate is not an observation | Trace target, outcome reconciliation, promotion/retirement, and decision consumer |
| Causal evidence / sensorimotor evidence | Interventions, observations, and derived causal candidates need explicit provenance | Trace the source event and ensure candidate relations are not promoted to world facts |
| Agency acquisition / competence effects | Acquired competence and its evidence are not execution permission | Trace acquisition evidence, persistence, action selection, and separately held execution bindings |
| Generative hypotheses | Counterfactual or generated hypotheses are proposals, not factual state | Trace factual reconciliation, rejection path, persistent state, and decision consumer |
| Private models and ancestry | Model persistence/lineage is distinct from model accuracy or lineage benefit | Verify checkpoint lineage; separately evaluate prediction quality and ancestry ablation |
| Episodic memory | Retained episode is not automatically retrieved or decision-relevant memory | Trace indexing, retrieval, consumption, and any compression/revision policy |
| Social evidence | A peer claim remains attributed to its source until evidence reconciliation | Trace publication, reception, assessment, persistence, reconciliation, and decision consequence |
| Symbol/sequence grounding | Grounding links require explicit observation/interaction provenance | Trace the grounding event and downstream consumers; separate labels from validated referents |
| Provenance | Provenance records how a state/result was produced; it is not evidence for the claim itself | Verify propagation and ensure consumers do not treat metadata as factual support |

The rows deliberately do not prescribe a common data model. A merge is allowed
only after the audit establishes identical assertion semantics, evidence
requirements, revision rules, lifecycle ownership, and consumer authority.

## 5. Current evidence statements

- Model ancestry that survives restore is a durability result (at most E1). It
  does not demonstrate improved learning or adaptation (E3/E4).
- Generative hypotheses, scheduling, reconciliation, and persistence establish
  implemented architecture and testable state transitions (E0/E1). They do not
  demonstrate decision benefit or causal outcome attribution (E3/E4).
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
| CognitiveGraph / cognitive bridge | E1 — durable | Checkpoint round-trip and production readout paths exist; no test in this audit isolates a graph-state change and its resulting action. |
| SignalKnowledge | E1 — durable | Persists and is surfaced to runtime/observer events; no organism decision consumer was found. |
| EvidenceRevisionLedger | E1 — durable | Persists and participates in investigation-time baseline revision; an isolated downstream decision consequence was not demonstrated. |
| Predictive learning / predictor credit | E1 — durable | Predictor updates and sensory utility wiring exist; a differential production decision test isolating predictor state was not established. |
| Causal / sensorimotor evidence | E1 — durable | Transition evidence and derived models persist; causal truth and a differential action-ranking effect are not established. |
| Agency acquisition / competence effects | E1 — durable | Acquired competence and execution bindings are distinct and persisted; this audit did not establish a differential test of acquired evidence affecting action while authority remains independently controlled. |
| Generative hypotheses | E1 — durable | Hypotheses persist and an admission path exists; a differential test from persistent hypothesis through production decision is not established. |
| Private models | E1 — durable | The active private model is read during prospective action deliberation, but this audit did not find a differential test proving choice changes when only its state changes; no E2 claim is made. |
| Model ancestry | E1 — durable | Parent vocabulary can contribute to a child training request; persistence does not show improved learning or adaptation. |
| Episodic/consolidated memory | E1 — durable | Consolidated state persists, but no runtime retrieval or decision consumer was found. |
| Social evidence | E1 — durable | Source-attributed claims and evidence persist and affect cultural retention/transmission; no peer-claim-to-organism-decision path was found. |
| Symbol / sequence grounding | E2 — consumed | Locally observed associations are read by grounded emission methods and tests exercise the association-dependent output; this establishes substrate-local use, not validated shared meaning. |
| Provenance | E1 — durable | A bounded live-reference frontier persists; the event ring is not persisted and provenance coverage is producer-specific. |
| BodySchema | E1 — durable | Re-embodiment tests prove archival preservation and active evidence reset; no transfer-utility claim follows. |
| Somatic EpigeneticPrior | E0 — present | Runtime support keys are empty and non-empty priors are rejected; this does not establish acquired or consumed somatic marks. |
| Genome v2 germline marks / expression | E1 — durable | Genome/germline and expression mechanisms exist with persistence; no integrated experience-to-child inheritance or adaptive consequence is demonstrated. |

These levels are scoped to the mechanisms and paths named above. A subsystem
may contain lower-level components; do not promote the whole subsystem beyond
the evidence shown. Raise a level only with the required differential test or
controlled study, and record the exact scope and artifact.

## 6. Source trace started on 2026-10-04

This is a bounded source map, not completion of the owner audit in §2 or the
acceptance condition in §7.
It records direct observations from the current runtime implementation. A
checkpoint field or read path is not, by itself, evidence that a representation
is epistemically sound or that it changes a decision.

| Candidate owner | Runtime / persistence owner | Production read path found | What remains unproven or unaudited |
|---|---|---|---|
| CognitiveGraph | `OrganismRuntime._cognitive_bridge`; exported in `cognitive_bridge` by `OrganismRuntime._build_checkpoint_payload()`; implementation in `symbiont/cognition/graph.py` and `symbiont/core/cognition/bridge.py` | Perception feeds `CognitiveBridge.tick()`, which emits primitive readouts. Runtime supplies them to acquired-action admission; `ActionDomain` also builds competence proposals from readouts over its threshold. Bridge/readout and admission unit tests exist separately. | Provenance and revision paths for graph assertions; an end-to-end intervention test showing that changing only graph state changes organism action while other evidence and affordances are held fixed; therefore no causal efficacy or usefulness claim is made here |
| EvidenceRevisionLedger | `OrganismRuntime._evidence_ledger`; checkpoint field `evidence_ledger`; implementation in `symbiont/core/cognition/evidence.py` | `EpistemicDomain.investigate()` obtains `SecondLookSession` readings from selected, manifest-supported capabilities and passes them to `revise()`. The ledger computes the unweighted mean of non-null values and, when the existing baseline has positive standard deviation, records dissent at `abs(z_score) >= conflict_z` (default 2.0). Detailed dissent values are retained only in a bounded in-memory deque; the checkpoint stores only bounded per-capability conflict counts. `HostAcclimation.observe()` updates the baseline from the readings whether or not dissent was found. Current dissent feeds narrative/event reporting; no production consumer of persisted conflict counts or direct ledger-to-action decision path was found. | The ledger does not own accepted estimates and its persisted counts do not revise baseline or affect a traced production decision. End-to-end lineage from individual provider readings and the epistemic interpretation of the fixed z-score threshold remain owner-audit questions; persistence of contradiction counts is not decision use or evidence quality |
| Predictive learning / predictor credit | In-graph predictor nodes live in `OrganismRuntime._cognitive_bridge`; out-of-graph shadow candidates are bridge state; sensory downstream utility belongs to `SensorySystem` | `CognitionDomain.step()` updates the bridge, nominates shadow predictions when promotion is enabled, derives nonnegative `predictive_gain_by_name`, and passes it to `SensorySystem.update_downstream_utility()`. Thus shadow gain is consumed by sensory utility adaptation, not directly as action permission. | Trace predictor inputs, sample alignment, retirement/promotion and checkpoint ownership separately for in-graph and shadow predictors; test whether modifying predictor evidence alone changes downstream utility under controlled percept/action conditions; predictive gain over persistence is not a causal relation or demonstrated organism-level benefit |
| Causal evidence / sensorimotor evidence | `AcquisitionState.causal_evidence` owns the bounded `CausalEvidenceLedger`; action-domain checkpoint stores its payload; effect, controllability, and agency models are derived or stored views | `AcquisitionState.learn()` records observed `SensorimotorTransition`s, updates effect estimates, and updates controllability/agency against a counterfactual-free view. `ActionDomain` reads competence effect predictions for expectation/reporting; they are not execution permission. Passive windows are recorded separately as non-intervention evidence. | Provenance strength of transition state references and effect labeling; coverage of all transition writers/consumers and restore/re-embodiment semantics; whether prediction changes any action ranking independently of execution bindings. Evidence-derived relations must not be described as causal truth without controlled intervention and alternative-opportunity support |
| Agency acquisition / competence effects | `ActionDomain` composes `AgencyAcquisition`, `CompetenceLibrary`, and `CompetenceExecutionBindingRegistry`; acquisition owns causal evidence and learned dimensions | Observed transitions update causal/effect/control/agency models. Established primitive competence evidence plus `ground_competence()` can materialize a `MotorCompetence`; separately, `ExecutionBindingRegistry.bind_from_evidence()` binds it to the current surface. Composed competences follow a separate evidence path. `affordance_resolver()` reads competence knowledge and checks executable bindings separately, preserving the distinction between prediction and permission. | Full evidence lineage from each competence claim to its underlying transition set; all materialization/revocation paths and restore/re-embodiment behavior; whether any consumer treats maturity or predicted effect as sufficient authority without a current binding; controlled evidence for adaptive benefit |
| Epigenetic priors and germline marks | `OrganismRuntime` checkpoints `_epigenetic_priors` and decays them, but `_SUPPORTED_EPIGENETIC_KEYS` is empty, so non-empty runtime priors are rejected. `GermlineState` separately owns inherited/acquired `EpigeneticMark`s in the Genome v2 genetics API; the reduced `CleanEmbodimentSeed` starts with capture disabled unless explicitly configured. | `GeneExpressionState.from_genome()` can consume a `GermlineState.effective_value()`. `GermlineState.capture_acquired_variation()` requires an explicit enabled protocol; no canonical runtime writer or parent-to-child reproduction path connecting that capture to a child's inherited marks was found. The runtime `EpigeneticPrior` is not consumed by gene expression. | Do not conflate somatic `EpigeneticPrior` decay with Genome v2 germline marks. The complete experience → acquired mark → germline capture → reproduction → child expression chain is not integrated or demonstrated; no transgenerational effect or adaptation claim is supported. Decide ownership and protocol before connecting these representations |
| BodySchema | `OrganismRuntime._body_schema` owns the active `BodySchemaEngine`; the current checkpoint field is `body_schema`. Closed embodiment history archives a copy of the prior schema as episode evidence. | Embodiment and action domains add sensory phenotype, self-model, cognition, and agency-boundary observations. Re-embodiment archives the prior schema and calls `reset_for_new_embodiment()` on the active schema; action restoration validates execution bindings against the current surface independently of BodySchema. | The [2026-10-04 consumer audit](../../../lab/research/audits/current/2026-10-04-body-schema-consumer-audit.md) traced active and archived readers and found no active consumer of archived `body_schema_prior`: it is serialized and used for closed-episode summaries, not restored into the active engine or used as execution authority. This supports the canonical-path authority boundary, not inference validity, cross-Body transfer utility, or arbitrary external-consumer safety. Any future promotion of archive priors into active inference requires explicit prior/fact semantics and differential consumer tests |
| SensorySystem / AdaptiveSenseModel | `OrganismRuntime._sensory_system` and `_adaptive_senses`; checkpoint fields `sensory_system` and `sensory_development`. The acquired sensory payload is archived as `BodySpecificMemory.sensory_prior`; both active systems are replaced by the fresh Body's checkpoints during re-embodiment. | `PerceptionDomain.step()` feeds organism readings into `SensorySystem.transduce()`; `transduce()` selects stored sensors by `source_ids`. `AdaptiveSenseModel` also indexes learned state by `capability_id`. The transition archives Body A's sensory state and installs Body B's fresh sensory state, so reused source/capability IDs cannot reactivate old transducers or adaptive states. | Regression tests verify archived payload equality and fresh active state; the composite developed Body A → Body B test exercises checkpoint, re-embodiment, restore and subsequent ticks. This establishes a safe active-binding boundary, not transfer utility: archived sensory learning remains historical and is not automatically applied to a new Body. |
| Episodic memory / memory consolidation | Runtime owns `OrganismRuntime._memory_consolidator` and checkpoint field `memory`; `MemoryDomain` observes consolidation signals. `AgentMemory`/`Episode` in `core/cognition/memory.py` is not constructed by the traced runtime path. | `MemoryDomain.observe()` converts drift and prediction loss to novelty/surprise signals and records attended/reliable salience. `MemoryConsolidator` stores bounded statistical or quantized salient-event projections. No episode retrieval or action-decision read of this store was found in the traced path; runtime retained-unit charging counts drift baselines and graph nodes separately. | Do not describe this as runtime episodic recall: no episode writer/retriever/consumer path was found. Audit remaining uses of the standalone `AgentMemory` API and test whether consolidated traces affect a production decision before making a functional memory claim |
| Private models and ancestry | `ModeledOrganismRuntime` owns `PrivateModelRegistry`, `ExperienceLedger`, training requests, and checkpoint fields; `PrivateModelOrganismRuntime` adds temporal experience capture and prospective action deliberation | The private runtime captures t→t+1 observed outcome records, validates active predictions against those observations, and can call an active model to deliberate only over already-read-out and currently afforded competences. Model predictions influence prospective choice; real outcome value is learned from later observed outcomes. With `ancestry_training` enabled, a SHADOW parent can contribute its tokenizer vocabulary to a child training request; this is vocabulary continuity, not inherited weights or acquired organism knowledge. | Verify all restore and prediction paths against these ownership boundaries; ancestry mechanics do not establish prediction accuracy or ancestry benefit. Controlled prediction and ancestry-ablation evidence is still required before E3/E4 claims |
| Symbol/sequence grounding | `ModeledOrganismRuntime` owns receiver-side `SymbolGroundingLedger` and `SequenceGroundingLedger`; channel delivery records opaque exposures and checkpoints persist the local ledgers | `observe_symbolic_outcome()` / `observe_sequence_outcome()` associate locally observed outcome tokens with received opaque symbol/sequence tokens. Grounded emission methods select from local associations with support exceeding contradiction; the associations affect local communication choices, not world-state truth. `predict_symbolic_outcome()` / `predict_sequence()` expose the learned association. | Outcome-token authority and the external protocol that marks support/contradiction remain explicit assumptions; an association means predictive correspondence within this substrate, not validated semantic reference or shared meaning. Audit transport/source attribution and decision consequences before making stronger grounding claims |
| Provenance | `AgencyAcquisition.provenance` owns the shared `ProvenanceLog` for action/acquisition paths; the runtime exposes it and checkpointing retains the live-reference frontier | `ProvenanceLog.emit()` records structural `CausalEvent`s and updates immediate causes for produced refs; subscribers are outward-only. Events carry bounded opaque refs and scalar parameters, not evidence values or claim semantics. The recent event ring is in-memory only; checkpoint persists the live frontier, not event history. | Coverage is producer-specific, not a universal proof that all state changes have complete lineage. Missing refs/events, retired refs, and causes beyond the immediate frontier limit what can be reconstructed. Provenance explains recorded derivation; it must not be treated as evidence that its subject claim is true |
| Acclimation, rhythm, and drift baselines | `OrganismRuntime` owns `_acclimation`, `_rhythm_model`, and `_drift_baselines`; checkpoint fields are `acclimation`, `rhythms`, and `drift`, with replay accumulators where configured. The continuity register classifies all three as preserved on re-embodiment. | `PerceptionDomain.step()` updates acclimation from current cognitive readings, rhythm statistics from current percepts and macro-phase, and drift baselines by percept name. Drift observations feed memory/development/lifecycle summaries and second-look selection. The drift baseline is deleted when plasticity-driven sensor eviction removes its last manifest source; no corresponding body-transition invalidation was found in the traced path. | These are descriptive adaptation statistics, not ground truth. Acclimation keys by capability identity while rhythm/drift state is attached to current percept streams; preserved same-name baselines may therefore be reused after re-embodiment. Whether that reuse is a valid longitudinal prior or stale current-body authority is unresolved. Trace body/source identity changes and test the intended reacclimation behavior before changing the preservation policy or claiming SYM-06 complete |
| SignalKnowledge | `OrganismRuntime._signal_knowledge`; checkpoint field `signal_knowledge`; implementation in `symbiont/core/signals/knowledge.py` | `SignalObservationBatch` supplies selected valid values under opaque signal IDs; unselected valid manifest entries are excluded from learning history. Claims are bounded descriptive stability/change, synchronous-association, one-tick lead-prediction, or endogenous self-relevance records. Stability/change/association use fixed opportunity thresholds to reach `hypothesis`; lead-prediction compares prospective loss against zero, mean, persistence, and conditional references using fixed margins, and self-relevance receives a boolean derived in `PerceptionDomain` from sensor `sampling_outcomes` (nominal success is favorable; missing, unavailable, or provider failure is unfavorable), keyed by opaque signal identity; ambiguous capabilities from one provider are excluded. Lead-prediction/self-relevance status is revised by fixed 64-tick epochs: two failed epochs yield `contested`; three successful epochs and at least 144 validation opportunities yield `supported`. Supported/hypothesis claims become `stale` after 192 ticks without observation; stale is not negative evidence. Revision events record status changes/reasons. `LifecycleDomain.events()` checks `lead_prediction` only to emit outward `first_prediction`; runtime/Observatory expose the view. No action-choice or organism-cognition consumer was found in the traced production path. | These claim classes are operational summaries, not causal/factual propositions; the self-relevance target is sensor-sampling success/availability, not an independently established organism outcome; whether this apparatus-derived target validly supports an organism-level relevance claim requires owner confirmation. The event/report path is not a decision consumer (no E2 claim); audit any intended consumer and test its decision dependence before promoting that level |
| Generative hypotheses | `OrganismRuntime._generative_cognition`; checkpoint field `generative_cognition`; implementation under `symbiont/cognition/generative/` | `_generative_affordances()` maps anticipated effects only to currently resolved affordances. `_executive_epistemic_value()` supplies comparison-only values to `admit_afforded_action()`. The executive admits a candidate when represented, currently afforded, and sufficiently relevant; generative anticipation is one admission route, while arbitration still owns motor authority. Factual outcomes are reconciled on the next tick before the next cognition step. | Existing admission tests cover the policy boundary, not a controlled intervention on persistent hypothesis state through production runtime. Trace hypothesis evidence/revision and prove that no generated representation bypasses current affordability, arbitration, or factual reconciliation; no E3/E4 utility claim follows from integration alone |
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
mechanisms and/or persistence; they do not jointly satisfy the missing
consumer-differential audit above. Continue the source trace for the remaining
§4 candidates before treating SYM-07 as resolved.

## 7. Acceptance condition

This design remains proposed until an owner-approved audit fills every required
field in §2 for the candidate systems in §4, with links to implementation and
tests. Missing or conflicting ownership is a finding to resolve; it is not
permission to merge systems or infer capability.

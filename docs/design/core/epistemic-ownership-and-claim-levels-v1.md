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

## 6. Source trace started on 2026-10-04

This is a bounded source map, not completion of the owner audit in §2 or the
acceptance condition in §7.
It records direct observations from the current runtime implementation. A
checkpoint field or read path is not, by itself, evidence that a representation
is epistemically sound or that it changes a decision.

| Candidate owner | Runtime / persistence owner | Production read path found | What remains unproven or unaudited |
|---|---|---|---|
| CognitiveGraph | `OrganismRuntime._cognitive_bridge`; exported in `cognitive_bridge` by `OrganismRuntime._build_checkpoint_payload()`; implementation in `symbiont/cognition/graph.py` and `symbiont/core/cognition/bridge.py` | Perception feeds `CognitiveBridge.tick()`, which emits primitive readouts. Runtime supplies them to acquired-action admission; `ActionDomain` also builds competence proposals from readouts over its threshold. Bridge/readout and admission unit tests exist separately. | Provenance and revision paths for graph assertions; an end-to-end intervention test showing that changing only graph state changes organism action while other evidence and affordances are held fixed; therefore no causal efficacy or usefulness claim is made here |
| EvidenceRevisionLedger | `OrganismRuntime._evidence_ledger`; checkpoint field `evidence_ledger`; implementation in `symbiont/core/cognition/evidence.py` | `EpistemicDomain.investigate()` passes second-look sensor readings to `revise()`. The ledger compares their mean with the current acclimation baseline, records bounded dissent counts, and then updates `HostAcclimation`; no direct action-decision consumer of the ledger was found. | Exact provenance of individual readings through investigation; whether bounded conflict counts affect any production decision; current implementation revises acclimation directly, so the ledger is a contradiction summary rather than the canonical store of accepted estimates |
| Predictive learning / predictor credit | In-graph predictor nodes live in `OrganismRuntime._cognitive_bridge`; out-of-graph shadow candidates are bridge state; sensory downstream utility belongs to `SensorySystem` | `CognitionDomain.step()` updates the bridge, nominates shadow predictions when promotion is enabled, derives nonnegative `predictive_gain_by_name`, and passes it to `SensorySystem.update_downstream_utility()`. Thus shadow gain is consumed by sensory utility adaptation, not directly as action permission. | Trace predictor inputs, sample alignment, retirement/promotion and checkpoint ownership separately for in-graph and shadow predictors; test whether modifying predictor evidence alone changes downstream utility under controlled percept/action conditions; predictive gain over persistence is not a causal relation or demonstrated organism-level benefit |
| Causal evidence / sensorimotor evidence | `AcquisitionState.causal_evidence` owns the bounded `CausalEvidenceLedger`; action-domain checkpoint stores its payload; effect, controllability, and agency models are derived or stored views | `AcquisitionState.learn()` records observed `SensorimotorTransition`s, updates effect estimates, and updates controllability/agency against a counterfactual-free view. `ActionDomain` reads competence effect predictions for expectation/reporting; they are not execution permission. Passive windows are recorded separately as non-intervention evidence. | Provenance strength of transition state references and effect labeling; coverage of all transition writers/consumers and restore/re-embodiment semantics; whether prediction changes any action ranking independently of execution bindings. Evidence-derived relations must not be described as causal truth without controlled intervention and alternative-opportunity support |
| Agency acquisition / competence effects | `ActionDomain` composes `AgencyAcquisition`, `CompetenceLibrary`, and `CompetenceExecutionBindingRegistry`; acquisition owns causal evidence and learned dimensions | Observed transitions update causal/effect/control/agency models. Established primitive competence evidence plus `ground_competence()` can materialize a `MotorCompetence`; separately, `ExecutionBindingRegistry.bind_from_evidence()` binds it to the current surface. Composed competences follow a separate evidence path. `affordance_resolver()` reads competence knowledge and checks executable bindings separately, preserving the distinction between prediction and permission. | Full evidence lineage from each competence claim to its underlying transition set; all materialization/revocation paths and restore/re-embodiment behavior; whether any consumer treats maturity or predicted effect as sufficient authority without a current binding; controlled evidence for adaptive benefit |
| SignalKnowledge | `OrganismRuntime._signal_knowledge`; checkpoint field `signal_knowledge`; implementation in `symbiont/core/signals/knowledge.py` | Perception observes selected signals and returns a knowledge view. `LifecycleDomain.events()` checks for `lead_prediction` only to emit the `first_prediction` event; runtime also exposes the view in `RuntimeTickResult` and Observatory-facing results. No action-choice or organism-cognition consumer was found in the traced production path. | Exact proposition semantics and support/revision rules; whether a decision consumer is intended. Current evidence supports a learned/persisted report and an event-projection consumer, not decision-consumed knowledge (E2) |
| Generative hypotheses | `OrganismRuntime._generative_cognition`; checkpoint field `generative_cognition`; implementation under `symbiont/cognition/generative/` | Runtime reads anticipated effects and epistemic values when building action-domain services; the reconciler also receives factual outcomes | Whether hypotheses alter candidate ranking or action choice in a controlled, state-differential test; no E3/E4 utility claim follows from these reads |
| Social evidence | `ModeledOrganismRuntime._social_evidence_ledger`; checkpoint field `social_evidence_ledger`; implementation in `symbiont/modeling/culture.py` | Cultural retention/validation and explicit claim receive/originate/retransmit APIs in `symbiont/modeling/runtime.py` | A canonical peer-claim assessment → reconciliation → accepted-knowledge → organism-decision path is not established; no general trust authority is implied |

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
`symbiont/tests/unit/actuation/test_causal_evidence.py`,
`symbiont/tests/unit/actuation/test_sensorimotor_v2_architecture.py`, and
`symbiont/tests/unit/actuation/test_agency_before_competence.py`,
`symbiont/tests/unit/actuation/test_competence_convergence.py`, and
`symbiont/tests/unit/core/test_social.py`. These suites cover their named
mechanisms and/or persistence; they do not jointly satisfy the missing
consumer-differential audit above. Continue the source trace for the remaining
§4 candidates before treating SYM-07 as resolved.

## 7. Acceptance condition

This design remains proposed until an owner-approved audit fills every required
field in §2 for the candidate systems in §4, with links to implementation and
tests. Missing or conflicting ownership is a finding to resolve; it is not
permission to merge systems or infer capability.

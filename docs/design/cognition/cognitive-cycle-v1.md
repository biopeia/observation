---
id: design.cognition.cognitive-cycle-v1
title: "Cognitive Cycle v1"
document_type: design
domain: cognition
status: proposed
canonical: false
implementation_status: design
date: 2026-10-04
depends_on:
  - docs/governance/constitution.md
  - docs/design/core/epistemic-ownership-and-claim-levels-v1.md
  - docs/design/core/causal-provenance-v1.md
language: en
---

# Cognitive Cycle v1

## 1. Purpose and limits

`main` contains several cognitive mechanisms that were designed separately:
the Cognitive Graph, local predictors, sensorimotor agency, competences and
execution bindings, the executive loop, Executive Outcome Learning, the
Private Model, episodic memory, Generative Cognition, outcome value, memory
consolidation and epistemic investigation. They are not competing attempts at
one mind and this document does **not** merge them.

It does three things:

1. names the single cycle those mechanisms already take part in, phase by
   phase, with one owner and one question per phase (§2–§3);
2. fixes the transversal contracts that the mechanisms must share so that
   they describe the same experience: fact identity (§5), epistemic origin
   (§6), kinds of prediction (§7), the uncertainty vocabulary (§8), the
   evaluation vector (§10) and retention pressure (§11);
3. records, as measured findings against the code, where the current
   implementation does not yet honour those contracts, and orders the work
   into waves with their governance class (§13).

Limits:

- This is a design contract. It authorizes no behaviour change, no scientific
  run and no capability claim. Evidence levels remain those of
  [Epistemic Ownership and Claim Levels v1](../core/epistemic-ownership-and-claim-levels-v1.md) §5.
- It introduces no new store, manager, bus or universal score. Constitution
  item 17 forbids a global weighted sum; §7 of the ownership
  audit found no two systems with identical semantics. Both stand.
- The per-owner source trace is the ownership audit's §6. This document links
  to it rather than re-deriving it; where the two disagree, the code decides
  and both must be corrected.
- Code anchors are relative to `symbiont/src/symbiont/` at `main @ f703a2470`.

## 2. The cycle

```text
perceive → represent → recognise/predict → afford → generate → evaluate
   → admit intent → act → observe consequence → attribute → learn
   → reconcile → consolidate → (next tick)
```

One tick of `OrganismRuntime.tick` (`core/orchestration/runtime.py`) runs the
phases in this order. The consequence of the action issued at tick *t* is
observed at the start of tick *t+1*, before that tick's cognition, so phases
I–J of one turn of the cycle execute ahead of phases B–H of the next. The
order is asserted by
`tests/experimental_integrity/test_runtime_v2_orchestration.py`.

| Phase | Question | Owner | Runtime call | Produces |
|---|---|---|---|---|
| A. Grounding | What am I actually perceiving? | `PerceptionDomain` | `_perception_domain.step` | percepts, availability, reliability, attention, drift |
| I. Consequence | What happened after what I did? | `ActionDomain` + `AgencyAcquisition` | `_action_domain.observe_consequences` (T1) | `SensorimotorTransition`, or a passive window |
| J. Attribution and reconciliation | What does that fact revise? | each learner, for itself | same call (T2–T3), then `note_factual_outcome` | causal evidence, binding regrounding, intent outcome, hypothesis reconciliation |
| B. Representation | What internal structure is active? | `CognitiveBridge` / `CognitiveGraph` | `_cognition_domain.step` | activations, concepts, primitive/motor readouts |
| C. Recognition and prediction | What usually follows? Did this happen before? What would follow if I act? | local predictors (bridge); `EpisodicExperienceMemory`; Private Model | `_cognition_domain.step`; private runtime queries | prediction errors, shadow predictor gain, recalled episodes, temporal predictions |
| E. Generation | What could happen? | `ResidentGenerativeCognition` | inside `_cognition_domain.step` | hypotheses, replays, counterfactuals, epistemic value, consolidation signals |
| K. Consolidation | What deserves to remain? | `MemoryDomain` / `MemoryConsolidator`; bridge retention | `_memory_domain.observe`; `set_generative_retention_protection` | retained salient events, protected representations |
| D. Affordance | What can I do now? | `ActionDomain.affordance_resolver` | inside `_action_domain.act` (T5) | `ActionAffordance` |
| F. Evaluation | Which possibilities are worth trying? | `ProspectiveAgency`, `admit_afforded_action` | inside `act` (T6) | `ProspectiveDecision` |
| G. Executive admission | What will I try to bring about? | `IntentionDomain` | inside `act` (T7) | `ActionIntent` (competence C, anticipated effect E) |
| H. Action | — | `ActionArbitrator` → controller → actuators | inside `act` (T8–T11) | `MotorCommand`, open `ActionAttempt` |
| Investigation | Should I look again? | `EpistemicDomain` | `_epistemic_domain.investigate` | second-look readings, dissent |
| L. Slow learning | — | bridge structural plasticity; private-model training/promotion; regulation | `_regulation_domain…`, `_development_domain…`, modeled runtime | structural mutations, model lineage, delayed homeostatic credit |

The private-model runtime wraps this tick: it captures a private frame after
the base tick returns and finalizes the `state(t) + action(t) → state(t+1)`
episode one tick later (`modeling/private_runtime.py::tick`).

### 2.1 Loops

The phases do not all run at the same rate. The contract distinguishes four
loops by what triggers them, not by a new scheduler:

| Loop | Trigger | Members |
|---|---|---|
| Fast | every tick | sense, represent, predict, afford, admit, act, observe |
| Medium | a factual consequence exists | causal learning, binding regrounding, executive outcome, episode capture, hypothesis reconciliation |
| Slow | enough accumulated experience | structural plasticity, private-model training, promotion and degradation, concept pruning, delayed outcome-value credit |
| Offline | resting / spare capacity (`GenerativeMode.OFFLINE`) | replay, counterfactual, recombination |

## 3. Authority of each subsystem

Each row is an invariant: the subsystem answers its question and must not
take the authority in the last column. Rows marked ✔ are already enforced by
construction or by a test; the rest are contract only.

| Subsystem | Answers | Must never | Enforced |
|---|---|---|---|
| Perception | what evidence is available | produce knowledge, value or action | ✔ ordering test |
| Cognitive Graph | which acquired relations are active | plan, store episodes, act as a world model or evidence ledger | ✔ motor competences enter as readouts only |
| Local predictors | which immediate relations predict | become a full transition model | — |
| Agency (causal evidence) | what the organism can cause | choose goals | ✔ `observe_consequences` never reads cognition |
| Competence | which reusable skill was acquired | hold adaptation to one body | ✔ separate `CompetenceExecutionBinding` |
| Execution binding | whether C is executable on this body | erase the competence on re-embodiment | ✔ `BindingStatus` is separate from the competence |
| Episodic memory | what happened in a concrete earlier situation | generalize like a model | — |
| Private Model | what will probably follow state + action | declare truth; train on its own unsupported output | ✔ `ExperienceRecord` rejects `MODEL` + `OBSERVED`; corpus admits `MODEL` only when `SUPPORTED` with evidence |
| Generative Cognition | what could happen | write factual evidence; execute | ✔ no motor or ledger handle; reconciliation is inbound only |
| Outcome value | which consequences tend to reduce internal deviation | become an external reward | ✔ credited only from observed episodes |
| Executive Outcome Learning | how pursuing C→E has gone | change causal evidence, controllability or agency | ✔ separate ledger keyed `(competence, anticipated effect)` |
| Executive / intention | which consequence to pursue now | learn the world model | — |
| Memory consolidation | what is retained | reinterpret the experience | — |
| Epistemic investigation | whether to observe again | choose motor action | ✔ ADR-0005 |
| Provenance | how a state came to exist | count as evidence for the claim | ✔ outward-only subscribers |
| Cognitive Atlas / Observatory | explain the above to the researcher | take part in it | ✔ pure projection in the Lab (`lab/src/lab/observation/atlas.py`); Constitution §13 |

Two rules follow from the table. They are the decision of
[ADR-0068](../../adr/ADR-0068-factual-authority-and-single-experienced-event.md)
(Accepted):

- **No cognitive subsystem manufactures factual authority.** Factual
  authority enters only through direct observation, the observed consequence
  of an executed action, or source-attributed social evidence. A prediction,
  replay, hypothesis, counterfactual, model output or observational
  projection is never a fact.
- **One experienced event, many interpretations.** A consequence that
  happened once has one identity and one provenance; each learner interprets
  it under its own epistemology and refers to that identity.

## 4. Producer and consumer inventory

What each phase's product is consumed by, on the production path. "—" means
no consumer was found; such a product is durable state, not a functional
dependency (ownership audit §3, levels E1 vs E2).

| Product | Producer | Production consumers |
|---|---|---|
| percepts, signal references | Perception | Action (T1 state, T5), Cognition, Memory, Epistemic, private frame |
| drift observations | Perception | Memory (novelty), Development, lifecycle events, second-look selection |
| `SensorimotorTransition` | `AgencyAcquisition.close_attempt` | `CausalEvidenceLedger`; effect/controllability/agency models; binding regrounding; body-boundary inference; intent reconciliation; generative reconciliation (`competence-effect`) |
| passive window | `observe_passive_window` | causal evidence only (no-intervention baseline) |
| `IntentOutcome` | `IntentionDomain.observe_effect` | Executive Outcome ledger; commitment termination |
| executive modulation | Executive Outcome ledger | executive admission (factor, suppression) |
| primitive / motor readouts | `CognitiveBridge.tick` | executive admission; competence proposals |
| prediction errors | `CognitiveBridge.tick` | Memory (surprise); predictor lifecycle |
| shadow predictor gain | `CognitionDomain.step` | `SensorySystem.update_downstream_utility` |
| generative hypotheses | `ResidentGenerativeCognition` | executive admission through generative affordances |
| generative epistemic value | `ResidentGenerativeCognition` | prospective deliberation (tiebreak); admission epistemic relevance |
| generative consolidation signals | `consolidation_signals()` | bridge retention protection |
| `ActionAffordance` | `AffordanceResolver` | prospective deliberation; executive admission |
| `ExperienceRecord` (`OBSERVED`) | private runtime | `ExperienceLedger`; episodic memory; training corpus; active-model validation; generative reconciliation (`private-slm`); outcome-value scheduling |
| counterfactual prediction | Private Model (`ACTIVE` only) | prospective deliberation; generative adapter |
| `OutcomeValueEstimate` | `OutcomeValueLedger` | prospective policy |
| recalled / replayed episode | episodic memory | offline generative replay; retrospective graph support. No later-decision consumer is demonstrated |
| consolidated salient events | `MemoryConsolidator` | — on the decision path |
| second-look dissent | `EvidenceRevisionLedger` | narrative and events only |
| `CausalEvent` | provenance emitters | lab journal (outward only) |

## 5. The experienced transition

### 5.1 Contract

For a **motor-caused** consequence the fact already has a canonical record:
`SensorimotorTransition` (`actuation/evidence.py`). No new type is needed.

- Its identity is `transition_id`, derived from the attempt alone
  (`actuation/acquisition.py::close_attempt`), so it is stable and names one
  executed command and its first later observation.
- Its string reference in evidence lists is `causal.{transition_id}` — the
  `CausalEvidence.evidence_id` written by `CausalEvidenceLedger.observe`.
- Its provenance reference is `CausalRef("transition", transition_id)`.
- It carries what a shared outcome contract needs: state before and after
  (as references), action, observed effect and atoms, prediction and its
  error, context, competence, commitment, attempt and intervention
  signature. The embodiment is on the attempt.

Every learner that interprets a motor-caused consequence must cite that
identity. It keeps its own record and its own epistemology:

```text
SensorimotorTransition  (one identity)
   ├─ Agency             strengthens or weakens C → E
   ├─ Binding            C is still executable on this body
   ├─ Executive Outcome  pursuing C → E went well / badly
   ├─ Private experience a valid temporal episode
   ├─ Episodic memory    a concrete precedent
   ├─ Generative         hypothesis H supported / contradicted
   └─ Outcome value      deferred homeostatic credit for the outcome
```

A consequence with **no** motor cause (a `DIRECT` or `INTERNAL` private
episode, a passive window) has no `SensorimotorTransition` and keeps the
identity its owner gives it. The contract does not invent a motor fact for
it; that would violate Constitution item 35.

### 5.2 Findings against `main`

**F1 — One consequence, two identities.** The private runtime derives its
own `record_id = "transition." + sha256(organism, ticks, context, action,
outcomes)` (`modeling/private_runtime.py::_finalize_private_transition`).
It shares the `transition.` namespace with `SensorimotorTransition` but uses
different hash material, and its `evidence_refs` are synthesized per-signal
references that never name the causal transition. Nothing links the private
episode of a motor-caused consequence to the causal evidence for that same
consequence.

**F2 — The same event reaches generative reconciliation twice under
unrelated references.** `runtime.tick` calls `note_factual_outcome` with
`("causal.{transition_id}",)` for `competence-effect`; the private runtime
calls it again for the same physical consequence with up to 16 synthesized
references for `private-slm`. `model_ids` restricts each call to
hypotheses sourced from that model, and a hypothesis is reconciled only
while `HYPOTHESIZED` or `PREDICTED`, so none is reconciled twice. But
`note_factual_sources` adds every reference to the representation's source
set and `GenerativeConsolidationSignal.source_diversity` is the size of that
set (`cognition/generative/consolidation.py`). One event can therefore count
as up to 17 "independent sources", and that count feeds retention protection
in the Cognitive Graph. This is a measurement artefact on a decision-relevant
signal.

**F3 — Executive Outcome evidence does not cite the consequence.** The
`outcome_learning` provenance event is caused by the intent and commitment
only (`core/domains/intention.py`). The transition that decided the outcome
is not among its causes, so "which observed fact produced this executive
sample" is not answerable from provenance.

**F4 — Outcome-value credit is keyed by outcome token alone.** Pending
credit is `(due_tick, outcome_id, baseline, discount)`
(`modeling/private_runtime.py::_schedule_observed_outcome_value_credit`). The
episode that scheduled it is not retained, so a ledger estimate cannot be
traced to the episodes behind it.

**F5 — The reconciliation boundary trusts its caller.**
`note_factual_outcome` requires non-empty references but does not resolve
them (already recorded as debt in the ownership audit §8). With §5.1 in
force the boundary has a checkable form: a motor-caused note must carry a
`causal.` reference.

Status: F1 and F2 are closed only when `shared_fact_identity` is enabled
(§13, W1); the default organism still behaves as described above. F3–F5 are
open.

None of F1–F5 is a correctness bug in a learner. Each is a place where the
"same fact" cannot be recognised as the same.

## 6. Epistemic origin

Four origins, by what stands behind the content. They are a reading of the
existing enums, not a new one.

| Origin | Meaning | `EpistemicStatus` (`modeling/experience.py`) | `SourceKind` | Generative `HypothesisStatus` |
|---|---|---|---|---|
| observed | witnessed by the organism | `OBSERVED` | `DIRECT`, `INTERNAL`, `ACTION_OUTCOME` | — |
| inferred | derived from observations by a learner | `ASSOCIATED`, and `SUPPORTED` / `CONTRADICTED` once reconciled | `COGNITIVE` | `SUPPORTED`, `CONTRADICTED` |
| predicted | a model's expectation of what will follow what is the case | `PREDICTED` | `MODEL` | `PREDICTED` |
| counterfactual | what would follow an action not taken, or a replay | `HYPOTHESIZED` | `MODEL`, `COGNITIVE` | `HYPOTHESIZED` |

Rules:

- Origin never upgrades by itself. Only reconciliation against an observed
  fact moves predicted or counterfactual content to supported or
  contradicted, and the result is *inferred*, not *observed*.
- Content with origin predicted or counterfactual never enters a factual
  store. A counterfactual query creates no `ExperienceRecord` (already true
  for prospective deliberation and replay).
- `actuation/model.py::CausalSourceKind`, `modeling/culture.py::SocialEpistemicStatus`
  and `host/hypotheses.py::HypothesisStatus` classify other things (who
  caused an effect, the standing of a peer claim, host-capability
  hypotheses). They are not epistemic-origin enums and are left alone.
- No new enum is added. A sixth vocabulary would deepen the problem this
  section exists to bound.

## 7. Kinds of prediction

Four subsystems predict. Their outputs are not interchangeable and must keep
their kind when they cross a boundary.

| Kind | Owner | Query | Output | Stands on |
|---|---|---|---|---|
| associative | local predictors in `CognitiveBridge` | what follows this activation next tick | per-node prediction error, shadow gain | graph co-activation |
| causal | `CompetenceEffectModel` / controllability (Agency) | what does competence C cause, here | effect id + confidence | intervention evidence against passive windows |
| temporal | Private Model (`ACTIVE`) | state + action → next state | outcome token + confidence class | the organism's observed episodes |
| counterfactual | Generative Cognition | what could happen along a branch, replay or recombination | hypotheses, rollouts | any of the above, through adapters |

Generative Cognition is the only consumer allowed to combine kinds, and it
does so through adapters that name their source model
(`cognition/generative/adapters.py`): `competence-effect` (causal),
`private-slm` (temporal) and the episodic replay adapter. A causal prediction
means "I have evidence I can cause E"; a temporal one means "my model expects
E". The first is the stronger claim and is not to be averaged with the
second.

Registered today: `competence-effect` (`core/orchestration/runtime.py`) and
`private-slm` (`modeling/private_runtime.py`). `EpisodicReplayAdapter` and
`SensorimotorDynamicsGenerativeAdapter` exist but are not registered on the
production path; episodic retrieval reaches Generative Cognition only through
resting `materialize_replay` (wave W4).

## 8. Uncertainty vocabulary

Four words name four different quantities. A value of one kind is not to be
used as another without an explicit, named conversion at the boundary.

| Term | Meaning | Lives in |
|---|---|---|
| reliability | how trustworthy a source is: availability × health | perception, self-model, binding `reliability` |
| support | how much independent evidence backs a claim: counts | causal opportunities, `source_diversity`, value sample counts, executive samples |
| confidence | a model's own estimate that its output holds | `prediction_confidence`, `confidence_class` (0–7), controllability confidence |
| uncertainty | what is not determined: spread, disagreement, expected reducible error | `PredictionError.uncertainty`, generative uncertainty, model disagreement |

Conversions present on `main`, recorded so they stop being silent:

| Site | Conversion | Disposition |
|---|---|---|
| `agency/policy.py::ProspectivePolicy` | utility = mean value × value confidence × model confidence | a scalar product across owners (value × support-derived confidence × model confidence). Bounded to prospective ranking; revisit under W3 |
| `cognition/generative/adapters.py::_proposal` | confidence = `confidence_class / 7`; uncertainty = 1 − confidence | named conversion at an adapter; uncertainty here is not independent information |
| `CompetenceEffectGenerativeAdapter` | uncertainty = 1 − confidence | same |
| `core/domains/action.py::_intent_proposal` | uncertainty = 1 − intent confidence | same |
| `agency/prospective.py::admit_afforded_action` | epistemic relevance = max(generative epistemic value, 1 − prediction confidence) | mixes a generative estimate with a complement of causal confidence; keep, name it |
| `private_runtime.py::_finalize_private_transition` | `confidence_class = 7` for every observed episode | an observation is not a confident prediction; the field means "observed", not a calibrated confidence |

`1 − confidence` is a legitimate default only when the consumer has no
independent uncertainty. It must not be read back as evidence of uncertainty.

## 9. Lifecycles are not unified

These state machines look alike and answer different questions. They stay
separate.

| Subject | States | Question |
|---|---|---|
| representations (`RepresentationMaturity`) | nascent → provisional → mature → stable → weakening → retiring | has this structure earned persistence? |
| competences (`CompetenceMaturity`) | candidate → emerging → established → robust | is this skill consolidated? |
| private models | `CANDIDATE → SHADOW → ACTIVE → DEGRADED → RETIRED` | which model may answer inference? |
| execution bindings (`BindingStatus`) | `VALID`, `STALE`, `INVALIDATED` | is this competence executable on this body? |
| generative hypotheses | `HYPOTHESIZED / PREDICTED → SUPPORTED / CONTRADICTED → RETIRED` | what did reality say about this imagined outcome? |
| intents (`IntentStatus`) | pending → active → satisfied / failed / rejected / interrupted / invalidated | is this pursued consequence still open? |

What they share is a grammar, not states: each must be able to state its
existence, its authority, its evidence, its revision rule, its validity and
its provenance — the ownership record of the ownership audit §2.

## 10. Candidate evaluation is a vector

A candidate action is compared on separately owned dimensions. The carrier
already exists: `ActionEvaluation` (`actuation/action.py`), documented as
"vector-valued; deliberately not a scalar reward". No second type is added.

| Dimension | Owner | Today |
|---|---|---|
| causal confidence | Agency | `effect_confidence`, `controllability` |
| executability | execution binding | a gate in `AffordanceResolver`, not a number |
| predicted outcome and its confidence | Private Model | `CounterfactualPrediction`, prospective path only |
| executive history | Executive Outcome | a multiplicative factor and a suppression gate on relevance |
| endogenous value | `OutcomeValueLedger` | prospective path only; `homeostatic_relevance` on the model-free path |
| epistemic value | Generative Cognition | `epistemic_relevance` |
| uncertainty | the predicting owner | `uncertainty` |
| cost | physiology | `estimated_cost` — reserved, always `None` |

The admission path is a sequence of gates, not a vote (ownership audit §7):
private-model deliberation first, model-free graph/generative admission as
fallback. This design keeps that. It does not propose a joint score.

## 11. Retention pressure

Retention is decided in six places with no shared input:

| Where | Decides | Signal |
|---|---|---|
| `MemoryConsolidator` | salient-event retention | novelty, surprise, attention, reliability, coherence |
| bridge structural retirement | which graph structure survives | use, maturity, generative protection |
| generative `ConsolidationTracker` | which representations Generative Cognition protects | recurrence, cross-episode reuse, hypothesis persistence, source diversity, demand |
| episodic memory | episode eviction and compression | its own capacity policy |
| private-model registry | model archive | lifecycle |
| competence library | competence maturity | evidence |

Storage stays separate. What may converge is the *pressure*: the reasons an
item deserves to remain (it was surprising, novel, attended, reliable,
causally relevant, generatively useful, executively relevant). Only one such
bridge exists today — generative consolidation signals protecting mature
graph representations — and it is the correct shape: imagination may protect
memory; imagination may not become truth.

## 12. No single world model

With the cycle in place the organism does not need a central `WorldModel`.
What it knows about the world is distributed by kind — associations (graph),
its own causal reach (agency), concrete experience (episodic), temporal
dynamics (private model), possibilities (generative), its body (body schema)
and its skills (competences) — and Generative Cognition queries those when it
needs to imagine. Introducing a central model would recreate the merge this
document rules out.

## 13. Waves

Each wave is separately reviewable. The class is the governance class the
change would carry; only W0 is in this change.

| Wave | Content | Class | Needs before it lands |
|---|---|---|---|
| **W0** | This document; ADR-0068 (Accepted); register entry; a structural test that locks the invariants of §2–§3 and §5.1 that already hold | CONSTITUTIONAL by surface (`docs/adr/**`), under ADR-0068 | Owner review of the candidate |
| **W1** | Shared fact identity (F1, F2): a private episode whose action closed a `SensorimotorTransition` cites `causal.{transition_id}` first among its evidence references. **Mechanism implemented, off by default** (`shared_fact_identity`) | SCIENTIFIC when enabled | It changes `ExperienceRecord.content_hash` (ledger chain, corpus dedupe key) and `source_diversity`, hence retention protection. Enabling it requires an owner-approved comparison of retention and corpus composition with and without the shared reference |
| **W2** | Provenance linkage and boundary check (F3, F4, F5): a motor-caused generative note must carry a `causal.` reference; `outcome_learning` events cite `CausalRef("transition", …)`; outcome-value credit retains the scheduling episode | ORDINARY if observer-equivalent, else SCIENTIFIC | Check that the checkpointed provenance frontier stays bounded (retire transition refs) and that no decision reads the new field |
| **W3** | Evaluation vector (§10): carry executive history, endogenous value and predicted-outcome confidence as named `ActionEvaluation` fields on both admission routes; remove the product in `ProspectivePolicy` only if a contradictory-decision case is shown | SCIENTIFIC | A concrete case where the current gates and the vector disagree (ownership audit §7 item 4) |
| **W4** | Generative sources (§7): register episodic retrieval as an online generative source next to `competence-effect` and `private-slm` | SCIENTIFIC | Episodic decision consumption is below E2 today; needs a differential test before any claim |
| **W5** | Retention pressure (§11): a shared, read-only pressure record feeding the existing owners | SCIENTIFIC | Capacity measurement must stay passive (Constitution items 91–93) |
| **W6** | Remove paths made redundant by W1–W5 | per path | Only after the wave that replaces a path has landed and been measured |

W1 as implemented in `modeling/private_runtime.py` (inert unless
`shared_fact_identity=True`):

```text
_capture_private_frame(result) at tick t+1
    factual_ref = "causal." + action_domain.last_transition.transition_id
                  when a transition closed this tick, else None
_finalize_private_transition(previous, current)
    evidence = (current.factual_ref, *previous.evidence_refs, *current.evidence_refs)[:16]
tick()
    note_factual_outcome(evidence_refs=(current.factual_ref,))   # one event, one source
        when the episode has a factual_ref, else the episode's references as before
```

`last_transition` at the end of tick *t+1* is the transition closed during
*t+1* for the command issued at *t*, which is exactly the episode
`previous → current`.

## 14. Acceptance condition

This design remains proposed until the owner approves the cycle (§2), the
authority table (§3) and the contracts (§5–§11). Approval of this document
does not approve W1–W6; each needs its own decision and, where marked
SCIENTIFIC, external review and the stated measurement. A finding in §5.2 or
§8 is a recorded gap, not a licence to change the organism so that a test
passes.

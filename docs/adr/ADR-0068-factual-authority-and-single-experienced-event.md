# ADR-0068 — Factual authority and the single experienced event

- **Status:** Accepted
- **Date:** 2026-10-04
- **Decision owner:** project owner
- **Relates to:** Constitution items 32–35, 38–39, 80–88, 135; ADR-0006, ADR-0014, ADR-0016, ADR-0025, ADR-0037; [`docs/design/cognition/cognitive-cycle-v1.md`](../design/cognition/cognitive-cycle-v1.md); [`docs/design/core/epistemic-ownership-and-claim-levels-v1.md`](../design/core/epistemic-ownership-and-claim-levels-v1.md); [`docs/design/core/causal-provenance-v1.md`](../design/core/causal-provenance-v1.md)
- **Scope:** Where factual authority may enter the organism's cognition, and how one observed consequence is identified across the subsystems that learn from it. It merges no subsystem, adds no store and fixes no data layout.

## Context

The organism has several mechanisms that learn from what happened: causal
evidence and agency, execution bindings, Executive Outcome Learning, the
Private Model's experience ledger, episodic memory, generative hypothesis
reconciliation and outcome value. The ownership audit of 2026-10-04 found no
two of them with identical semantics and recommended no consolidation.

Each already keeps prediction apart from observation locally: ADR-0037
demarcates imagination, ADR-0016 isolates replay, `ExperienceRecord` rejects
model content marked observed, Generative Cognition holds no motor or ledger
handle. What is missing is the rule that holds across them, and a common way
to say "the same thing happened".

At `main @ f703a2470` one motor-caused consequence receives two unrelated
identities:

- `actuation/acquisition.py::close_attempt` names it
  `transition.{sha256("transition:" + attempt_id)}`; causal evidence records
  it as `causal.{transition_id}`.
- `modeling/private_runtime.py::_finalize_private_transition` names the same
  consequence `transition.{sha256(organism, ticks, context, action,
  outcomes)}` with synthesized evidence references that never mention the
  causal transition.

Generative reconciliation is then notified of that consequence twice, under
references that cannot be recognised as one event, and each reference is
counted as a distinct factual source for retention.

## Decision

1. **No cognitive subsystem manufactures factual authority.** Factual
   authority enters the organism only through (a) direct observation,
   (b) the observed consequence of an action it executed, and
   (c) source-attributed social evidence, which stays attributed until
   reconciled. A prediction, replay, hypothesis, counterfactual, model output
   or observational projection is never a fact and never becomes one by
   being stored, repeated, consolidated or displayed.

2. **One experienced event, many interpretations.** A consequence that
   occurred once has one identity and one provenance. Each learner keeps its
   own record and its own epistemology, and refers to that identity instead
   of reconstructing the event.

3. **The identity of a motor-caused consequence is its
   `SensorimotorTransition`.** Its evidence reference is
   `causal.{transition_id}` and its provenance reference is
   `CausalRef("transition", transition_id)`. No new record type is
   introduced.

4. **A consequence without a motor cause keeps its owner's identity.** No
   motor fact is invented for a passive window or for a private episode of
   kind `DIRECT` or `INTERNAL`.

5. **Reconciliation produces inference, not observation.** Predicted or
   counterfactual content that reality supports becomes supported; it does
   not acquire the origin *observed*.

## Consequences

- Decisions 1, 2, 4 and 5 describe boundaries that the code already keeps
  locally; they become checkable across subsystems.
- Decision 3 is **not** yet true of the default organism. Bringing the
  private episode, generative reconciliation, Executive Outcome provenance
  and outcome-value credit onto the shared identity changes
  `ExperienceRecord` content hashes and the generative `source_diversity`
  signal, which feeds retention protection. That is a behaviour change and
  is carried by separately reviewed waves (Cognitive Cycle v1 §13, W1–W2).
  The W1 mechanism exists behind `shared_fact_identity`, off by default;
  accepting this ADR does not enable it.
- Provenance stays evidence of derivation, not of truth (Constitution items
  80–88): a shared reference says two records concern one event; it does not
  make either record more credible.

## Alternatives considered

- **A new `ExperiencedTransition` record plus a learning bus.** Rejected: the
  fact already has a canonical record, and a bus would add an owner between
  the fact and its learners.
- **A universal evidence manager.** Rejected: it would force one evidence
  semantics on subsystems the audit found to differ.
- **Leave identities per subsystem.** Rejected: the same event counted as
  several independent sources is a measurement artefact on a
  decision-relevant signal.

## Status

Accepted by the project owner on 2026-10-04. The ADR is the decision record;
it does not itself edit the Constitution. Adding decisions 1 and 2 to the
Constitution's invariant list is a separate governed change.

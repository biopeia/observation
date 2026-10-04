# Cognitive Cycle v1 — W1 shared fact identity, confirmatory protocol

Design: `docs/design/cognition/cognitive-cycle-v1.md` §5.2 (F2), §13 (W1).
Decision: ADR-0068. Requested and authorized by the project owner on
2026-10-04 (confirmation scope).

Predecessor: the exploratory comparison of the same day
(`../cognitive-cycle-shared-fact-identity/`), whose factual-source question
was not testable, and the audit that found why (finding F6, corrected
before this protocol). Seed 42 and every state of the exploratory work are
excluded from this protocol.

## Regime

**CONFIRMATORY.** Everything below is frozen by the commit that adds this
file, before any run of this protocol. A change after that is a deviation
and is recorded as one.

## Research question

When private-model hypotheses are reconciled during a run, does enabling
`shared_fact_identity` make each such event count as one causal factual
source instead of several per-signal references?

This tests that the mechanism does in a living organism what its
specification says. It is not a test of benefit, and SUPPORTED would not by
itself justify enabling the flag.

## Hypothesis and decision criteria

Per seed, at the end of the horizon, let `E` be the number of distinct
factual source references of kind `evidence.` recorded by generative
consolidation, and `P` the number of `private-slm` hypotheses in status
supported or contradicted.

- **H1:** in the `on` arm `E = 0`, and in the `off` arm `E ≥ 1`.
- A seed is **testable** when `P ≥ 1` in its `off` arm and its noise floor
  is zero (below).
- **SUPPORTED:** at least two seeds are testable and H1 holds in every
  testable seed.
- **REFUTED:** H1 fails in at least one testable seed.
- **INCONCLUSIVE:** fewer than two testable seeds and no failure.

## Design

Body kind `anthropomorphic-v6-vision`. Seeds **101, 102, 103**, fixed; no
seed is added or replaced. Code: the commit that adds this file, which
includes the F6 correction.

Part A, per seed — governed launcher, scope `development`, input
`protocol-generated`: a fresh organism and body developed **128 ticks**
(`observation_hz=1`, factorized effects, private-model training synchronous
on CPU, train interval 1, checkpoint interval 128).

Part B, per seed — governed launcher, scope `confirmation`, input the
archived Part A state: three arms, each a fresh copy continued **512
ticks**, same seed, deterministic training contract (one CPU thread, one
interop thread, deterministic algorithms), train interval 1:

| Arm | `shared_fact_identity` | Role |
|---|---|---|
| `off` | False | control |
| `off_replicate` | False | noise floor |
| `on` | True | intervention |

The arms differ only in the flag, set by the Lab study at construction.

## Amendment 1 (before any arm ran)

The first launch of Part B was refused by the launcher: confirmation-scope
runs with an external snapshot require a subject of verified origin, and the
current tooling has no producer for that mark (the migration removed it; the
check remained). No arm started and no confirmatory datum exists. The
seed-101 development state already produced was discarded unread, and a
seed-102 development run was aborted at launch.

Part A and Part B therefore execute as **one** governed run per seed, scope
`confirmation`, input mode `protocol-generated`: the study develops the
subject for 128 ticks inside the run and then continues the three arms from
it. Differences from the frozen text, all forced by this layout:

- the subject is developed under the same deterministic training contract as
  the arms, instead of outside it;
- the subject is not archived by the launcher as a separate input; its
  identity is the run's own receipt.

Hypothesis, decision criteria, seeds, horizons, arms and measurements are
unchanged.

```bash
python scripts/agentctl.py run start --commit <sha> --id <id> --scope confirmation \
  --input-mode protocol-generated --seed <seed> --extra physics3d --extra modeling \
  -- python -m lab.studies.learning.shared_fact_identity {work}/subject {work} \
     --develop-ticks 128 --ticks 512 --seed <seed> --train-interval 1
```

## Measurements

Read from the per-tick checkpoint; nothing is fed back.

- Primary: `E` and `P` per arm (`factual_source_kinds`,
  `private_model_hypotheses_reconciled`).
- Secondary, descriptive only, no decision attached: factual sources sum and
  maximum, reconciliation and contradiction counts, corpus size and hash,
  model registry, first divergence tick per section between `off` and `on`.

## Validity, testability, stopping

- Noise floor: `off` and `off_replicate` must agree in every section at
  every tick. If they differ, the seed is INVALID for the primary outcome.
- An arm that ends before its horizon (organism death, launcher limit,
  error) makes its seed NOT_TESTABLE.
- A run ends at its horizon. Nothing is stopped early on its result.
- One comparison, one primary outcome: no multiplicity correction.

## Execution

```bash
python scripts/agentctl.py run start --commit <sha> --id <id> --scope confirmation \
  --input-mode snapshot --snapshot-source <part-A-state> --seed <seed> \
  --extra physics3d --extra modeling \
  -- python -m lab.studies.learning.shared_fact_identity {input} {work} \
     --ticks 512 --seed <seed> --train-interval 1
```

## Limits

Three seeds, one body kind, one developmental window (ticks 128–640), in
which a private model may or may not be promoted. The result bounds the
mechanism under these conditions only.

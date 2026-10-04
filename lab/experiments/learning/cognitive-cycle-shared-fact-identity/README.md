# Cognitive Cycle v1 — W1 shared fact identity, matched comparison

Design: `docs/design/cognition/cognitive-cycle-v1.md` §5.2 (F1, F2) and §13 (W1).
Decision: ADR-0068. Requested by the project owner on 2026-10-04.

## Purpose

Protocol for the comparison the design requires before `shared_fact_identity`
may be enabled: what the flag changes in the private ledger, the training
corpus, the generative `source_diversity` signal and the organism's
trajectory, on a developed Physics3D organism with private-model training.

## Regime

**EXPLORATORY.** Declared before execution. It characterises an effect; it
cannot support enabling the flag by itself. No threshold maps to SUPPORTED
or REFUTED. A confirmatory protocol, if wanted, is a new frozen document.

## Research question

On an organism developed with current `main`, continued for a fixed horizon
from one common state, does enabling `shared_fact_identity` change
(Q1) what the private ledger and training corpus contain,
(Q2) the generative factual-source count that feeds retention protection,
and (Q3) the organism's causal trajectory, relative to the matched default
arm and to the run-to-run noise floor?

## Part A — state development (apparatus, no hypothesis)

A fresh organism and body, `anthropomorphic-v6-vision`, developed with the
governed launcher, scope `development`, input mode `protocol-generated`:

- seeds: 42, 43, 44. Resource stopping rule: if the seed-42 development run
  exceeds 25 minutes of wall time, the campaign is limited to seed 42.
- horizon: 1536 organism ticks; `observation_hz=1`; factorized effects on;
  private-model training enabled, synchronous, CPU, train interval 1;
  checkpoint interval 256.

The resulting state directory (`organism.symbiont`, `body.json`, `models/`)
is the common input of Part B and the candidate source for the
`causal-equivalence-v1` reference snapshots. A state is offered to a suite
slot only if `agentctl equivalence run` reaches the slot's declared event
coverage on it; a slot whose coverage is not reached stays `MISSING` and is
reported as not assessable. No state is edited, synthesized or refreshed.

## Part B — matched arms

Input: the Part A state of each seed, archived by the launcher (snapshot
mode). Three arms per seed, each a fresh copy of the same input continued
for **512 ticks** with the same seed and the same deterministic training
contract as the equivalence suite (synchronous, one CPU thread, one interop
thread, deterministic algorithms, train interval 32):

| Arm | `shared_fact_identity` | Role |
|---|---|---|
| `off` | False (default) | control |
| `off_replicate` | False | noise floor: identical configuration, second execution |
| `on` | True | intervention |

The arms differ only in the flag. It is applied by the Lab study at
construction time; the organism's code and the input state are not modified.

## Measurements

Taken from the organism checkpoint the engine exposes each tick; nothing is
fed back to the organism.

- M1 ledger: observed motor-caused episodes recorded after the input tick,
  and how many cite a `causal.` reference.
- M2 corpus: size, splits and hash of the training corpus built from the
  final ledger; model registry records and active model.
- M3 generative: tracked representations, per-representation factual source
  count (sum, max), reconciliation and contradiction counts, hypotheses.
- M4 trajectory: first tick at which the full checkpoint digest differs
  between two arms, and which top-level checkpoint sections differ at the
  final tick.

Retention protection is not checkpointed; M3 and the `cognitive_bridge`
section of M4 are its observable proxies.

## Analysis plan

Per seed, then listed side by side; no pooling statistic with three seeds.

1. Validity: `off` and `off_replicate` must have identical checkpoint
   digests at every tick. If they differ, M4 for that seed is INVALID
   (trajectory differences cannot be attributed to the flag); M1–M3 are
   still reported with the replicate as the noise reference.
2. Q1: compare M1 and M2 between `off` and `on`.
3. Q2: compare M3 between `off` and `on`.
4. Q3: report the first `off`/`on` divergence tick and the differing
   sections. No divergence within the horizon is reported as such, not as
   evidence that none would occur later.

Not testable: if no private-`slm` hypothesis is reconciled in a seed's
`off` arm during the horizon, Q2 is NOT_TESTABLE for that seed (the path
the flag changes was never exercised).

## Stopping and exclusion

A run ends at its horizon, at organism death, or at a launcher resource
limit. An arm that does not reach the horizon makes its seed NOT_TESTABLE
for Part B. No seed is replaced.

## Execution

```bash
python scripts/agentctl.py run start --commit <sha> --id <id> --scope development \
  --input-mode snapshot --snapshot-source <part-A-state-dir> --seed <seed> \
  --extra physics3d --extra modeling \
  -- python -m lab.studies.learning.shared_fact_identity {input} {work}
```

## Belongs here

This protocol. Results and their reading go to `lab/research/` with the
receipts; run artifacts stay under the launcher's run directory.

## Limits

One body kind, at most three seeds, a 512-tick horizon from one
developmental stage. The result bounds what the flag does under these
conditions only. It is not a claim about benefit: no outcome metric here
says the organism is better off with the flag on.

# Scientific Experiment: shared fact identity, confirmatory comparison

Study key: `learning.cognitive-cycle-shared-fact-identity-confirmatory`.
Protocol: `lab/experiments/learning/cognitive-cycle-shared-fact-identity-confirmatory/README.md`
(frozen at `2a968c332`, Amendment 1 at `f0eb0d9b2`, both before any arm ran).
Design: `docs/design/cognition/cognitive-cycle-v1.md` §5.2, §13 (there: wave
"W1", finding "F2"). Decision: ADR-0068.
Raw results and launcher receipts, this directory:
`2026-10-04-shared-fact-identity-confirmatory-seed{101,102,103}.result.json`
and `.execution.json`.

## 1. Research question

When private-model hypotheses are reconciled during a run, does enabling
`shared_fact_identity` make each such event count as one causal factual
source instead of several per-signal references?

This tests that the mechanism does in a living organism what its
specification says. It is not a test of benefit.

## 2. Regime

CONFIRMATORY. Hypothesis, criteria, seeds, horizons, arms and measurements
were committed before execution and were not changed afterwards.

## 3. Preregistered protocol (as frozen)

Per seed, at the end of the horizon: `E` is the number of distinct factual
source references of kind `evidence.` recorded by generative consolidation
(`factual_source_kinds.evidence`; an absent key is zero), and `P` the number
of `private-slm` hypotheses in status supported or contradicted
(`private_model_hypotheses_reconciled`).

- Hypothesis: in the `on` arm `E = 0`, and in the `off` arm `E ≥ 1`.
- A seed is testable when `P ≥ 1` in its `off` arm and its noise floor is
  zero.
- SUPPORTED: at least two seeds testable and the hypothesis holds in every
  testable seed. REFUTED: it fails in at least one testable seed.
  INCONCLUSIVE: fewer than two testable seeds and no failure.
- Validity: `off` and `off_replicate` must agree, otherwise the seed is
  INVALID for the primary outcome. An arm that ends before its horizon makes
  its seed NOT_TESTABLE. No early stopping. One primary outcome.
- Seeds 101, 102, 103, fixed, none added or replaced. Body kind
  `anthropomorphic-v6-vision`. Subject: a fresh organism developed 128 ticks;
  three arms (`off`, `off_replicate`, `on`) each continue a fresh copy 512
  ticks under the deterministic training contract, train interval 1.

## 4. Execution provenance

One governed run per seed (`agentctl run start`), scope `confirmation`,
input mode `protocol-generated`, commit `f0eb0d9b2`, extras `physics3d` and
`modeling`, ceilings 8 GiB memory, 2 CPU threads, 240 wall minutes. Runs
executed sequentially on one host.

| Run id | Seed | State | Return code | Elapsed |
|---|---|---|---|---|
| `cc-w1c-s101` | 101 | complete | 0 | 1789 s |
| `cc-w1c-s102` | 102 | complete | 0 | 2363 s |
| `cc-w1c-s103` | 103 | complete | 0 | 2039 s |

Determinism recorded by every run: one CPU thread, one interop thread,
deterministic algorithms, not warn-only. Every arm of every seed ended with
exit code 0 and 513 observed ticks (input tick 128 through tick 640).

## 5. Run validity

| Seed | Arms reached the horizon | Noise floor | `P` in `off` | Validity | Testable |
|---|---|---|---|---|---|
| 101 | yes | zero | 100 | VALID | yes |
| 102 | yes | zero | 0 | VALID | **no** — NOT_TESTABLE |
| 103 | yes | zero | 0 | VALID | **no** — NOT_TESTABLE |

What "zero noise floor" was measured on: the runner compares `off` and
`off_replicate` at every one of the 513 observed ticks on eight checkpoint
sections (`actuation`, `cognitive_bridge`, `executive_intention`,
`experience_ledger`, `generative_cognition`, `living_body`, `metabolism`,
`private_model_registry`), and on every checkpoint section at the final tick
only. Both comparisons found no difference in any seed. The frozen rule says
"every section at every tick"; the remaining sections were not compared at
intermediate ticks (§9, deviation 4).

Seeds 102 and 103 are NOT_TESTABLE by the frozen testability rule: no
private-model hypothesis was reconciled in their `off` arm during the
horizon, so the path the hypothesis is about was not exercised in the
control. They are neither support nor refutation and are not replaced.

## 6. Results

Observations, per seed and arm, at the end of the horizon (`off_replicate`
equals `off` in every row).

Primary measurements:

| Seed | Arm | Factual source references by kind | `E` | `P` |
|---|---|---|---|---|
| 101 | `off` | causal 11, evidence 302 | 302 | 100 |
| 101 | `on` | causal 105 | 0 | 100 |
| 102 | `off` | causal 3 | 0 | 0 |
| 102 | `on` | causal 3 | 0 | 0 |
| 103 | `off` | causal 5 | 0 | 0 |
| 103 | `on` | causal 26 | 0 | 23 |

At the input tick every seed had no factual source reference and `P = 0`.

Secondary measurements (descriptive, no decision attached):

| Seed | Arm | Sources sum / max | Reconciliations / contradicted | Hypotheses | Tracked representations | Motor-caused episodes (citing `causal.`) | Corpus train / validation / test | Corpus hash | Model records |
|---|---|---|---|---|---|---|---|---|---|
| 101 | `off` | 315 / 64 | 111 / 104 | 118 | 9 | 467 (0) | 462 / 99 / 100 | `a87c94dc…` | 18 (1 active, 3 shadow, 14 retired) |
| 101 | `on` | 111 / 40 | 111 / 105 | 118 | 7 | 467 (467) | 459 / 98 / 100 | `22c1eafc…` | 18 (1 active, 3 shadow, 14 retired) |
| 102 | `off` | 3 / 3 | 3 / 3 | 7 | 11 | 458 (0) | 448 / 96 / 97 | `6313c937…` | 15 (1 active, 3 degraded, 11 retired) |
| 102 | `on` | 3 / 3 | 3 / 3 | 7 | 9 | 458 (458) | 450 / 96 / 97 | `196e3e66…` | 15 (1 active, 3 degraded, 11 retired) |
| 103 | `off` | 5 / 5 | 5 / 5 | 9 | 10 | 367 (0) | 449 / 96 / 97 | `360939e6…` | 14 (1 active, 3 degraded, 10 retired) |
| 103 | `on` | 40 / 14 | 40 / 40 | 46 | 14 | 375 (375) | 448 / 96 / 97 | `567988e9…` | 17 (1 active, 3 degraded, 13 retired) |

First tick at which a section differs between `off` and `on` (input tick 128,
horizon end 640; "none" means none within the horizon):

| Section | Seed 101 | Seed 102 | Seed 103 |
|---|---|---|---|
| `experience_ledger` | 130 | 130 | 130 |
| `actuation` | 131 | 131 | 131 |
| `private_model_registry` | 131 | 131 | 131 |
| `generative_cognition` | 130 | 259 | 187 |
| `living_body` | 323 | 323 | 163 |
| `metabolism` | 323 | 323 | 163 |
| `executive_intention` | none | none | 203 |
| `cognitive_bridge` | none | none | 214 |

Checkpoint sections differing between `off` and `on` at the final tick: 21
(seed 101), 21 (seed 102), 34 (seed 103).

## 7. Scientific outcome

Applying the frozen criteria:

- Seed 101: testable. `on` arm `E = 0`, `off` arm `E = 302 ≥ 1`. The
  hypothesis holds.
- Seed 102: not testable (`P = 0` in `off`).
- Seed 103: not testable (`P = 0` in `off`).

One testable seed, no failure: **INCONCLUSIVE** (run validity VALID for all
three seeds).

The single testable seed is consistent with the specification: 100
reconciled private-model hypotheses left 302 distinct `evidence.` references
in the control and none with the flag on. That is one seed and does not meet
the protocol's requirement of two.

Readings that the frozen criteria do not license, recorded so that they are
not later mistaken for support:

- In seed 103 the `on` arm reconciled 23 private-model hypotheses and
  recorded only `causal.` references (`E = 0`), while the `off` arm
  reconciled none. The testability rule is defined on the `off` arm, so this
  seed stays not testable; the `on`-arm half of the hypothesis was exercised
  there, the `off`-arm half was not.
- `E = 0` in the `on` arm of all three seeds. In seeds 102 and 103 the `off`
  arm also has `E = 0`, so those seeds cannot distinguish the flag from its
  absence on the primary measurement.

## 8. Scope and limitations

Three seeds, one body kind, one developmental window (ticks 128–640),
train interval 1, CPU, deterministic training contract.

- The question is whether the mechanism behaves as specified. Nothing here
  measures whether shared fact identity benefits the organism, and no arm is
  shown to be better off.
- Whether a private-model hypothesis is reconciled within 512 ticks of tick
  128 varied by seed (one of three control arms). A protocol on this question
  needs a horizon or state where that event is common, which this one did not
  secure.
- The flag is not causally neutral in any seed: ledger, actuation and model
  registry differ from tick 130–131 on, and in seed 103 executive intentions
  and the cognitive bridge differ too. In seed 103 the two arms therefore
  followed different trajectories (367 against 375 motor-caused episodes, 14
  against 17 model records), which is why reconciliations occurred in one arm
  and not in the other. This is a description, not a tested claim about
  cause.
- The explanations in the previous two points are post-hoc.

## 9. Protocol deviations

1. **Amendment 1 (recorded in the protocol before any arm ran).** The
   two-part layout (development run, then a confirmation run from its
   archived state) was refused by the launcher, which requires a
   verified-origin mark for external snapshots in confirmation scope and has
   no producer for it. A seed-101 development state already produced was
   discarded unread and a seed-102 development run was aborted at launch.
   Each seed therefore ran as one governed run that develops the subject and
   then continues the three arms. Consequence: the subject is developed under
   the same deterministic training contract as the arms, and is not archived
   as a separate launcher input. Hypothesis, criteria, seeds, horizons, arms
   and measurements unchanged.
2. **The subject of each run is not preserved.** The subject directory
   argument was passed as the literal text `{work}/subject` (visible in the
   `command` field of each receipt); the launcher
   substitutes `{work}` only when it is a whole argument, so the subject was
   written to a relative path inside the launcher's pinned worktree, which is
   removed after the run (checked after the campaign: none remains). The three arms copied from that same directory, so
   the comparison within each run is unaffected, and every arm's input
   metrics are recorded in the result. Consequence: the tick-128 subject
   cannot be re-examined or continued again; the final state of each arm
   remains only in the launcher's local run directory, outside version
   control. A fresh-organism development run is not bit-reproducible across
   launches, so the subject cannot be regenerated either.
3. **Result files carry the wrong labels.** Each `result.json` says
   `"protocol": "learning.cognitive-cycle-shared-fact-identity"` and
   `"regime": "exploratory"`. Both strings are constants in the runner, which
   the two protocols share. The receipts carry the correct
   `experiment_id` and scope `confirmation`. This is a labelling defect of
   the apparatus; the regime was confirmatory and the files are kept as
   produced.
4. **Noise-floor coverage is narrower than the frozen rule.** See §5: eight
   sections at every tick, all sections at the final tick only. Consequence:
   a transient difference between `off` and `off_replicate` in another
   section that vanished before the final tick would not have been seen. No
   difference was found where it was checked.

None of the four changes the outcome label: with one testable seed it is
INCONCLUSIVE with or without them.

## 10. Follow-up status

- Shared fact identity stays off by default. The owner's condition for
  making it the organism's only behaviour was a SUPPORTED outcome; that
  condition is not met and the change was not made.
- A further confirmatory test is a new protocol with new seeds, not more
  seeds added to this one. To be testable it must secure that private-model
  hypotheses are reconciled in the control arm (this protocol's seed 101
  shows it can happen from tick 128; seeds 102 and 103 show it often does
  not within 512 ticks). Choosing that horizon or state is an owner decision
  and must not be tuned on seeds 101–103.
- Seeds 101–103 and seed 42 are spent for this question.

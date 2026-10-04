# Scientific Experiment: W1 shared fact identity, matched comparison

Protocol: `lab/experiments/learning/cognitive-cycle-shared-fact-identity/README.md`.
Design: `docs/design/cognition/cognitive-cycle-v1.md` §5.2, §13. Decision: ADR-0068.
Raw result: `2026-10-04-w1-shared-fact-identity-seed42.result.json` (this directory).

## 1. Research question

On an organism developed with current `main`, continued 512 ticks from one
common state, does enabling `shared_fact_identity` change (Q1) what the
private ledger and training corpus contain, (Q2) the generative
factual-source count that feeds retention protection, and (Q3) the
organism's causal trajectory, relative to the matched default arm and to the
run-to-run noise floor?

## 2. Regime

EXPLORATORY, declared and committed before execution (`0ce589ba2`).
Amendment 1 (per-section divergence) was committed before Part B ran
(`25245d713`); amendment 2 concerns the equivalence suite only.

## 3. Execution provenance

| Run id | Scope | Commit | Input | Result |
|---|---|---|---|---|
| `cc-w1-dev-s42` | development | `0ce589ba2` | protocol-generated, seed 42 | ended at tick 256, `MemoryError` under a 3.5 GiB launcher ceiling. Apparatus failure; no state used |
| `cc-w1-dev-s42-r2` | development | `0ce589ba2` | protocol-generated, seed 42 | complete, 1536 ticks, about 31 min |
| `cc-w1-arms-s42` | development | `25245d713` | snapshot of the run above (`organism_sha256 36cff468…`, `body_sha256 b8857bc2…`) | complete, three arms × 512 ticks |

All through `agentctl run start`; receipts are in the launcher run
directories. Body kind `anthropomorphic-v6-vision`. Deterministic training
contract established: one CPU thread, one interop thread, deterministic
algorithms, not warn-only.

Input state at tick 1536: 45 private-model records (1 active, 3 degraded,
41 retired), 35 generative hypotheses, 27 reconciliations, 2048 ledger
records, development phase juvenile.

## 4. Protocol deviations

1. The first development run died on its resource ceiling and the same seed
   was rerun with a higher ceiling and an otherwise identical configuration.
   A fresh-organism development run is not bit-reproducible across launches
   (the two runs already differ at tick 24), so the rerun is a different
   organism, not a replay. Part B depends only on the common input state, so
   this does not affect the comparison.
2. The 25-minute rule fired: one seed instead of three.
3. A first launch of the comparison failed during environment
   synchronization (disk full) before any scientific child started; it
   produced no data.

## 5. Run validity

VALID. `off` and `off_replicate` have identical digests in all eight
sections at every one of the 513 observed ticks, and identical final
checkpoints. The noise floor is zero, so any `off`/`on` difference is
attributable to the flag.

Q2 is **NOT_TESTABLE**: the reconciliation count is 27 in the input state
and 27 at the end of the `off` arm. No hypothesis was reconciled during the
horizon, so the path through which the flag reduces the factual-source count
was never exercised.

## 6. Results

Measured, `off` → `on` (`off_replicate` equals `off` throughout):

| Measurement | `off` | `on` |
|---|---|---|
| observed episodes since input | 511 | 511 |
| motor-caused episodes | 399 | 399 |
| motor-caused episodes citing `causal.` | 0 | 399 |
| corpus train / validation / test | 603 / 129 / 130 | 604 / 129 / 131 |
| corpus hash | `609e68a5…` | `4c27bf4b…` |
| model records (active / degraded / retired) | 61 (1 / 3 / 57) | 61 (1 / 3 / 57) |
| tracked representations | 25 | 25 |
| factual sources, sum / max | 47 / 27 | 47 / 27 |
| reconciliations / contradicted | 27 / 27 | 27 / 27 |
| hypotheses | 35 | 35 |

First tick at which a section differs between `off` and `on` (input tick
1536, horizon end 2048):

| Section | First divergence |
|---|---|
| `experience_ledger` | 1538 |
| `actuation` | 1539 |
| `private_model_registry` | 1539 |
| `generative_cognition` | 1635 |
| `living_body` | 1699 |
| `metabolism` | 1699 |
| `cognitive_bridge` | none within the horizon |
| `executive_intention` | none within the horizon |

## 7. Exploratory post-hoc reading (not part of the declared analysis)

A field-level comparison of the two final checkpoints, made after seeing the
table above, to see what the section digests hide:

- `private_model_registry`: 16 of 61 records differ in `model_id`,
  `corpus_hash`, `artifact_hash` and `validation_loss`. The models trained
  during the horizon are different models.
- `actuation`: 98 of 113 differing leaves are provenance-frontier event ids
  and refs; the rest are state references and stored sensor readings that
  differ in the seventh decimal.
- `living_body`, `metabolism`: energy and cognition reserves differ by about
  6e-4 units.
- `prospective_agency`: outcome-value statistics differ in the seventh or
  eighth significant digit.
- `generative_cognition`: use counters of four representations differ
  (for one, activation count 64 against 32).

## 8. Scientific outcome

No SUPPORTED / REFUTED label applies: the protocol is exploratory and
declares no threshold.

- **Q1 — answered, within scope.** The flag does what it specifies: every
  motor-caused episode cites its causal transition. It also changes the
  training corpus (hash, and two more records admitted).
- **Q2 — NOT_TESTABLE.**
- **Q3 — answered, within scope.** The flag is **not causally neutral** on a
  developed organism with private-model training. The trajectory separates
  two ticks after the input and the organism ends the horizon with different
  trained models, different generative use counters and a physical state that
  differs at small magnitude. Graph structure and executive intentions did
  not differ within 512 ticks.

## 9. Scope and limitations

One organism, one seed, one body kind, 512 ticks from one developmental
stage (juvenile, tick 1536), deterministic CPU training at interval 32.

- This measures that the flag changes the organism, not whether the change
  is good. No outcome metric here says either arm is better off.
- No divergence in `cognitive_bridge` or `executive_intention` within the
  horizon is not evidence that none occurs later.
- The reason the flag was designed — one event counted once as a generative
  factual source — was not exercised and remains unmeasured.
- The magnitudes in §7 are post-hoc and unpreregistered.

## 10. Follow-up status

- Enabling `shared_fact_identity` stays unapproved. This result shows the
  change is real and reaches model training; it does not show benefit.
- A test of Q2 needs a horizon or state in which generative hypotheses are
  reconciled during the run. Whether that is worth a confirmatory protocol
  is an owner decision.
- Replication on further seeds needs about 30 minutes of development plus
  about 75 minutes of arms per seed on this host.

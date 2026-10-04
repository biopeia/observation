# Causal Equivalence Suite v1 — capture attempt and non-assessability (2026-10-04)

Requested by the project owner. Suite: `lab/experiments/equivalence/suite-v1`.
Protocol context: `lab/experiments/learning/cognitive-cycle-shared-fact-identity/README.md`
(Part A and amendment 2).

## What was asked

Capture real reference snapshots for the five suite slots, all `MISSING`
(`capture-required`), so that `agentctl publish` can attach causal-equivalence
evidence.

## What was found before running anything

The only real organism state on this host (a tick-1105 organism archived for
Promotion Stability v1 D1) is checkpoint schema 10. Current code is schema 14
and refuses it (`unsupported portable Symbiont bundle schema`), as ADR-0065
intends. Reference states had to be developed with current `main`.

## What was run

All through `agentctl run start`, scope `development`, body kind
`anthropomorphic-v6-vision`, seed 42:

| Run id | Commit | Product |
|---|---|---|
| `cc-w1-dev-s42-r2` | `0ce589ba2` | fresh organism developed 1536 ticks: 45 private-model records, one ACTIVE (a promotion occurred), 35 generative hypotheses |
| `cc-w1-reembody-s42` | `af474b943` | that state implanted in a fresh body and continued 256 ticks (tick 1792) |

Both states are capturable (`snapshot inspect`). They were captured with
`agentctl snapshot capture` into a **scratch copy of the suite outside the
repository**, verified, and each scenario was executed with the suite's own
module (`python -m lab.physics3d.equivalence_suite`), which is the code path
`agentctl publish` uses.

## Result

| Scenario | Source tick | Status | First divergence |
|---|---|---|---|
| established-anthropomorphic | 1536 | `NOT_ASSESSABLE_NONDETERMINISM` | 1560 |
| developed-cognition | 1536 | `NOT_ASSESSABLE_NONDETERMINISM` | 1560 |
| reembodied-established | 1792 | `NOT_ASSESSABLE_NONDETERMINISM` | 1800 |
| private-model-training | 1536 | `NOT_ASSESSABLE_NONDETERMINISM` | 1560 |
| promotion-eligible | 1536 | `NOT_ASSESSABLE_NONDETERMINISM` | 1560 |

Every scenario fails the suite's own self-consistency check (two executions
of the same snapshot must agree) at the first tick that is a multiple of 24
after the input, which is the first observation tick at `observation_hz=1`.

## Cause (investigated separately, same day)

Two 30-tick executions of the `established-anthropomorphic` snapshot were
compared component by component:

- organism checkpoint digest per tick: identical;
- private-model and registry digests per tick: identical;
- provenance journal and body state: identical;
- trace: differs at tick 1560 in exactly one component, `observer_projection`.

Inside `observer_projection` at that tick, exactly three leaves differ:

```text
observer_projection.pre.sensory_input.monotonic_timestamp_ns
observer_projection.timing_ms.organism
observer_projection.timing_ms.physics
```

All three are host wall-clock measurements. `run_digests` already strips
`organism_ms`, `physics_ms` and `diagnostics_ms` from the tick record as
"host-load measurements, not causal state"
(`lab/src/lab/physics3d/equivalence.py`), but not these three fields of the
observer projection. The organism is deterministic under the suite's
configuration; the suite compares a quantity that cannot repeat.

Independent corroboration: in the W1 comparison run the same day, two
executions of the same state under the deterministic training contract had
identical organism checkpoints at every one of 513 ticks.

## Consequences

- The suite cannot return PASS for any snapshot until those fields are
  excluded from the trace comparison. This is an apparatus defect in the
  equivalence control plane, not a property of the candidate states and not
  evidence about any organism change.
- No snapshot was added to the repository. Capturing references that the
  suite then reports as non-deterministic would add about 1.1 GiB of binary
  state to git history for no assessable result.
- `lab/src/lab/physics3d/equivalence.py` is a CONSTITUTIONAL surface
  (`equivalence-control-plane`). The fix is not made here; it needs an
  Accepted ADR and owner review.
- The captured candidates and the five scenario outputs are kept, read-only
  and outside git, at `.symbiont/equivalence-candidates/suite-v1-2026-10-04/`
  on the host that ran them. They are reusable once the comparison is fixed,
  provided the checkpoint schema has not moved.

## Limits

One organism, one seed. The cause was isolated on one scenario and one
observation tick; the other four scenarios share the divergence tick pattern
but were not decomposed individually. ADR-0065/0066 plan to replace the
physics substrate; references captured now would not survive that cut.

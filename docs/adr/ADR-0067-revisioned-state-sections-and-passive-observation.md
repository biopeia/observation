# ADR-0067 — Revisioned state sections, passive observation and binary canonical checkpoints

- **Status:** Accepted
- **Date:** 2026-10-04
- **Decision owner:** project owner
- **Relates to:** Constitution items 99–103, ADR-0009, ADR-0010, ADR-0023, ADR-0024, ADR-0034, ADR-0065, ADR-0066, [`docs/design/core/simulation-substrate-cut-v1.md`](../design/core/simulation-substrate-cut-v1.md), [`docs/design/telemetry/physics3d-telemetry-v4.1.md`](../design/telemetry/physics3d-telemetry-v4.1.md)
- **Scope:** How organism state is laid out so that it can be observed and persisted without copying it, and what the canonical hashed representation of a checkpoint is after the cut. It fixes no encoding, section list or file layout.

## Context

Simulation Throughput v1 measured rich telemetry at about 4.5 s per tick
amortised, roughly 90 % of wall time, spent on `deepcopy`, structural diffing,
binary encoding and episodic snapshots. A further 150 ms per tick inside the
organism step includes `deepcopy` calls.

At `migration/five-domain-architecture @ f9ae63841`:

- `lab/physics3d/telemetry/v41.py` copies whole state mappings and
  `structural.py` derives keyed path deltas by comparing copies.
- The writer runs behind `AsyncTelemetryWorker`, a thread, so it shares the
  interpreter lock with the organism step.
- `core/embodiment/memory.py` and `core/embodiment/transition.py` contain 33
  and 24 `deepcopy` call sites.
- Checkpoints hash canonical JSON; ADR-0009 decision 1 defines
  `checkpoint_hash` as the SHA-256 of the canonical runtime JSON.

ADR-0024 decision 1 requires zero dynamic allocation on the hot execution
path. The measured observation path does not meet it. The cause is structural:
an observer that is forbidden to be told what changed can only find out by
copying and comparing, and that cost grows with the organism's age.

ADR-0065 removes the obligation to keep pre-cut hashes and formats.

## Decision drivers

- Observation cost independent of total state size.
- Observer passivity: no signal into the organism, no observation logic in its
  vital loop, apparatus cost separable from organism cost (items 99–102).
- Deterministic, content-addressed checkpoints (ADR-0009, ADR-0034).
- A state layout that numeric kernels can later operate on.

## Constraints

- Telemetry must not introduce signals to the organism (item 99) and must not
  stall it (item 101).
- ADR-0010: no per-tick projections, no parallel bus, observability
  independence.
- ADR-0023: the step remains atomic and reversible.
- The checkpoint remains self-contained and identified by content (ADR-0009).

## Alternatives considered

**A. Organism-emitted change events.** The organism publishes a delta each
time it mutates state. Cheapest to encode. The organism then carries
observation logic in its vital loop and its cost is mixed with apparatus cost,
which strains items 99 and 102; it is also a parallel bus in the sense
ADR-0010 forbids.

**B. Copy-and-compare in a separate process.** Keeps the current model and
removes lock contention. Still serialises the whole state per observation, so
cost still grows with age.

**C. Revisioned immutable sections.** State is partitioned into sections that
are replaced rather than mutated, each carrying a revision. The observer keeps
references and compares revisions. The organism needs no knowledge of any
observer.

**D. Keep copy-and-compare, observe sparsely.** Already available as Level 0
of Simulation Throughput v1 and free. Does not help runs that need full
observation, and leaves the step-internal copies.

| Driver | A | B | C | D |
|---|---|---|---|---|
| Cost independent of state size | yes | no | yes | no |
| Organism unaware of observer | no | yes | yes | yes |
| Removes step-internal copies | no | no | yes | no |
| Change to organism code | moderate | none | large | none |

## Decision

1. **State is sectioned and revisioned.** Organism state is partitioned into
   sections, each owned by exactly one domain. Each section carries a
   monotonically increasing revision that its owner advances when it replaces
   the section.
2. **Sections are replaced, not mutated in place.** A reference to a section
   is a valid snapshot of it for as long as the reference is held. Step-level
   atomicity (ADR-0023) is obtained by retaining prior section references, not
   by copying.
3. **Observation is derived from revisions.** The observer learns what changed
   by comparing revisions and encodes only changed sections. The organism
   emits no events, takes no observer callbacks and holds no observer state.
4. **The canonical hashed representation is a deterministic binary encoding of
   the sections.** `checkpoint_hash` is computed over that encoding. Identity
   by content, retention and the exclusion of observer state from X are
   unchanged.
5. **The telemetry stream is section snapshots keyed by revision.** Telemetry
   v4.1 and its structural path-delta codec are retired at the cut.
6. **Large numeric sections use flat buffers.** Small structural sections may
   remain ordinary immutable records.

Alternative C is chosen. A may be used for an individual section only if
revision comparison proves too coarse for it, and only by a later explicit
decision.

## Scope and non-goals

Not decided here: the section list and granularity, the binary encoding, the
compression codec, the file layout, any columnar export for analysis, and
whether numeric kernels are compiled. This ADR does not change what is
observed, only how change is detected and stored. It does not alter the
decimated cadence, the single-serialisation rule or the no-backpressure rule
of ADR-0024.

## Consequences

**Positive.** Observation cost follows the amount of change, not the size or
age of the organism. Step-internal copies disappear. The hot path can meet
ADR-0024 decision 1. Checkpoints can write only changed sections. Flat
sections give later optimisation something to operate on.

**Negative.** A large, cross-cutting change to organism code: every domain
adopts the replace-not-mutate discipline. Pre-cut checkpoints and telemetry
are unreadable by post-cut code. All checkpoint hashes change. Existing
telemetry readers, the monitor and the observatory adapters are rewritten
against the new stream.

**Neutral.** Observation remains decimated and off the critical path; the
writer may stay asynchronous.

## Risks

- **Aliasing.** A section mutated in place after being handed out silently
  corrupts a snapshot. Python does not enforce immutability deeply.
  Mitigation: frozen records, buffer views exported read-only, and the
  observer-passivity and save/restore properties as standing tests.
- **Granularity.** Sections too coarse re-encode large state for small
  changes; too fine multiplies bookkeeping. Mitigation: decided per domain
  from measurement.
- **Feasibility is not yet shown.** How far the existing state can be
  partitioned without disturbing the atomic step was not inspected.
  Mitigation: a bounded spike on one domain precedes the work (design §9,
  step 0).

## Reversibility

Expensive once post-cut checkpoints exist, because their identity depends on
the encoding. The observation mechanism alone is moderately reversible.

## Validation

- Observer passivity: identical organism state with full and with no
  observation.
- Snapshot stability: a held section reference is unchanged after further
  ticks.
- Save/restore transparency and replay determinism (ADR-0065).
- Encoding determinism: equal state gives equal bytes and equal hash across
  the CI platforms.

## Relationships

- Depends on ADR-0065.
- Partially supersedes ADR-0009 decision 1, for the basis of
  `checkpoint_hash` only (binary section encoding instead of canonical runtime
  JSON). The rest of ADR-0009 remains authoritative.
- Partially supersedes ADR-0024 decision 3, for how deltas are derived
  (revision comparison instead of structural diff of copies). Decisions 1, 2,
  4 and 5 of ADR-0024 remain authoritative and are what this ADR implements.
- Constrained by ADR-0010 and ADR-0023.
- Retires Physics3D Telemetry v4.1 at the cut.

## Reconsider if

- The spike shows the replace-not-mutate discipline cannot be adopted without
  breaking the atomic-step contract.
- Measured observation cost after the change is still dominated by something
  other than the amount of change.

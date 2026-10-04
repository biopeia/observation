# ADR-0065 — Cut the simulation substrate over without backward compatibility

- **Status:** Accepted
- **Date:** 2026-10-04
- **Decision owner:** project owner
- **Relates to:** Constitution §14 (items 103–108), ADR-0009, ADR-0034, ADR-0042, ADR-0046, ADR-0066, ADR-0067, [`docs/design/core/simulation-substrate-cut-v1.md`](../design/core/simulation-substrate-cut-v1.md), [`docs/design/core/simulation-throughput-v1.md`](../design/core/simulation-throughput-v1.md)
- **Scope:** How the project moves from the current simulation substrate (physics engine, organism state layout, observation path, persisted formats) to its replacement, and what happens to evidence produced before the move. It selects no engine and no format; ADR-0066 and ADR-0067 do.

## Context

Simulation Throughput v1 measured one Physics3D organism at 0.19 ticks/s with
default observation and bounded it at about 28 ticks/s by physics alone. Its
admissibility rule was strict: an optimisation counts only if `runtime.json`,
the provenance journal and the body state are byte-equal against the previous
code from the same snapshot and seeds.

That rule protects comparability with existing evidence. It also forbids the
changes with the largest effect: another physics engine, another state layout,
another hashed representation, a different event or summation order. Under it,
Simulation Throughput v1 concluded that hundreds of ticks per second are not
reachable for one organism.

Current practice already leans the other way. The organism loader accepts
outer checkpoint schema 14 only and rejects older schemas without migration
(note of 2026-10-04 in ADR-0042), and recent work on the five-domain migration
removed legacy readers rather than keeping them.

The cost figures behind this decision come from one snapshot on one shared
machine. The expected gains of the replacement are estimates.

## Decision drivers

- Single-organism throughput; aggregate throughput already scales with cores.
- Scientific cost of re-establishing a baseline.
- Determinism that can be checked mechanically after the change.
- Engineering cost of carrying two substrates at once.

## Constraints

- Determinism (constitution items 103–108) continues to bind the new substrate.
- Archived scientific artifacts are immutable and are not deleted (ADR-0034).
- A scientific conclusion must not be encoded as truth before it is
  demonstrated (item 111); a conclusion demonstrated under one substrate is not
  thereby demonstrated under another.

## Alternatives considered

**A. Keep byte equivalence (Simulation Throughput v1, Levels 0–2).** Preserves
every existing result and the reference snapshots of ADR-0046. Reaches an
estimated 15–20 ticks/s and keeps the physics ceiling. No recalibration.

**B. Transitional coexistence.** New engine as a second backend, new formats
beside old readers, studies migrated one by one. Old evidence stays
reproducible on current code throughout. Costs two code paths in every domain
that touches physics, state or persistence, for an open-ended period, and
compatibility code tends to become permanent.

**C. Clean cut with one re-baseline.** One regime boundary. No old readers, no
second backend. Old evidence is reproducible only at a pinned commit.

**D. Clean cut, re-baselined per workstream.** As C, but each replacement
(state, physics, algorithms) lands on `main` separately and is re-baselined
separately. Smaller steps; the studies are rerun several times.

| Driver | A | B | C | D |
|---|---|---|---|---|
| Single-organism throughput | bounded by current engine | unbounded | unbounded | unbounded |
| Old evidence reproducible on current code | yes | yes | no | no |
| Re-baseline runs | none | per study | once | once per workstream |
| Code paths maintained | one | two | one | one |

## Decision

1. **One regime boundary.** The simulation substrate is replaced in a single
   cut, called *the cut*. Results are attributed to the pre-cut or the post-cut
   regime; there is no intermediate regime on `main`.
2. **No backward compatibility across the cut.** Post-cut code carries no
   reader, migration or adapter for pre-cut checkpoints, body states or
   telemetry, and no second backend kept to reproduce pre-cut runs.
3. **Pre-cut evidence is preserved, pinned and labelled.** It stays in the
   archive unmodified. The last commit that reproduces it is tagged before the
   cut reaches `main`, and the tag is recorded in the changelog. Pre-cut
   evidence is reproducible at that tag and nowhere else.
4. **No claim crosses the cut by argument.** A result holds in the post-cut
   regime only after its study is rerun there.
5. **Self-consistency replaces cross-version equivalence for cut work.**
   Changes that implement the cut are not required to be byte-equal to pre-cut
   code. They are required to satisfy replay determinism, save/restore
   transparency and observer passivity on the new substrate.
6. **One baseline.** The work is staged on a branch and reaches `main` once.
   The new baseline is declared once and the retained studies are rerun once.

Alternative C is chosen. D was rejected because every workstream changes the
regime, so D pays the re-baseline several times for the same end state.

## Scope and non-goals

In scope: the compatibility policy, the treatment of pre-cut evidence, the
validation rule for cut work and the integration shape.

Not decided here: the engine (ADR-0066); the state and format design
(ADR-0067); which studies are rerun; the disposition of the Physics3D A7
stability gate, whose approved apparatus is pre-cut; whether `symbiont` may
ship a compiled extension.

This ADR does not relax determinism, does not authorize changing what the
organism experiences beyond what the replacement engine and renderer force,
and does not make any scientific claim.

## Consequences

**Positive.** The engine ceiling and the copy-and-compare observation path can
be removed rather than tuned. One code path per responsibility. The
re-baseline is paid once.

**Negative.** Every pre-cut quantitative result stops being reproducible on
current code. Body, contact, physiological and sensory calibration must be
redone. Reference snapshots used for ADR-0046 equivalence evidence become
invalid and must be recaptured post-cut. Closed results that condition the
canonical organism profile (ADR-0062) are pre-cut results until rerun.

**Neutral.** Governance classes are unchanged: cut work alters organism
trajectories, so it is SCIENTIFIC or CONSTITUTIONAL at publication and takes
external review. Owner acceptance of this ADR does not replace that review.

## Risks

- The branch lives long and drifts from `main`. Mitigation: staged merges into
  the branch with the self-consistency properties as gates.
- The rerun set is underestimated and a relied-upon claim is left standing on
  pre-cut evidence. Mitigation: each retained claim is listed with its rerun
  before the baseline is declared.
- The expected gains do not materialise. Mitigation: re-profiling and two
  feasibility spikes precede the work (design §9, step 0).

## Reversibility

Expensive. Until the cut reaches `main` it can be abandoned at the cost of the
branch. Afterwards, returning means reinstating the pinned commit and
discarding post-cut evidence.

## Validation

- Replay determinism: same seed and initial state give byte-identical
  checkpoint, provenance and body state.
- Save/restore transparency: N ticks equals k ticks, checkpoint, restore,
  N−k ticks.
- Observer passivity: full observation and no observation give identical
  organism state.
- The pre-cut tag exists and reproduces a pre-cut reference run.

## Relationships

- Partially supersedes the admissibility rule of Simulation Throughput v1 §2
  for cut work. Its Level 3 exclusion stands.
- Depends on ADR-0034 for the preservation of pre-cut artifacts.
- Constrains ADR-0066 and ADR-0067.

## Reconsider if

- Step 0 shows the measured cost distribution no longer justifies replacing
  the substrate.
- A relied-upon pre-cut result cannot be rerun post-cut at acceptable cost.

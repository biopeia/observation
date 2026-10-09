# ADR-0073 — Biopeia Migration Causal and Physical Contracts

## Status

- **Status:** Accepted
- **Owner acceptance:** 2026-10-09
- **Scope:** Migration contracts that refine Biopeia Architecture v1 without reopening Pass 15 or changing AD-0021…AD-0036.

## Context

Incremental extraction into Organism, Embodiment, Environment, World, Modality,
Observation, and Lab has exposed the need to make physical commands, World
participant closure, causal publication, and operator interventions explicit.
The pinned source is evidence of CURRENT behavior, not automatic authority for
TARGET semantics. The migration must preserve source provenance while adopting
the owner-approved contracts below.

This decision elaborates accepted architecture; it does not amend the
Constitution. If implementation evidence later contradicts an accepted
constitutional invariant, stop and propose a separate decision rather than
weakening the invariant in code.

## Decision

Adopt the [Biopeia Physical-Step and Causal-Commit Integration v1
design](../design/runtime/biopeia-physical-step-integration-v1.md) for the
migration. The owner-approved contracts are:

1. **Embodiment commands use stable identity.** An actuator command is bound
   explicitly to `body_id`, `embodiment_episode_id`, `morphology_revision`,
   `effector_id`, and `command_kind`. Array/list position is never
   authoritative. The active effector descriptor defines quantity/semantics,
   unit, valid range, optional neutral value, and whether saturation is allowed.
   Public APIs have no implicit units. Out-of-range values are rejected unless
   the descriptor explicitly declares saturation.
2. **Omission is not a command.** An omitted channel means “no command for this
   channel.” It does not imply zero or neutral. A neutral value exists only when
   the effector descriptor defines one; absence and neutral may be equivalent
   only when that descriptor explicitly says so.
3. **Owners adopt solver candidates.** World authorizes the causal physical
   step; Embodiment and Environment provide their projections; a numerical
   solver computes candidate results; each owning domain validates and adopts
   its own transition; World commits the causal cut. The solver has no semantic
   authority and never mutates authoritative owner state directly. Correlation
   includes World identity/tick, physical-step identity, applicable body and
   episode identities, Environment revision, morphology revision, and
   solver/configuration revision. A failed solver, rejected candidate, or
   missing required adoption cannot produce a committed causal step.
4. **World owns causal participant completeness.** For each step, World
   derives and validates the required participant set from active World
   presence, registered causal owners, step-specific participants, and explicit
   lifecycle transitions. Callers may identify needed resources/checkpoints,
   but cannot establish roster completeness by supplying an arbitrary list.
5. **World commit identity and minimum states.** A causal cut identifies at
   least `world_id`, `causal_tick`, `commit_id`, participant owner IDs,
   owner-state/checkpoint references, versions/hashes, and commit status. The
   minimum protocol states are `PREPARING`, `COMMITTED`, and
   `RECOVERY_REQUIRED`. A cut may be published as committed only after every
   required owner state is durably identifiable and recoverable. After restart,
   recovery unambiguously identifies the last committed cut; a partial cut is
   never mistaken for complete. Uncommitted work may be discarded.
6. **Single logical writer.** The default contract is one World commit
   authority / single logical writer. Multi-process execution is not implied;
   if added, it must coordinate to preserve the single logical commit
   authority. Shared-filesystem concurrency is not a contract.
7. **No premature storage technology mandate.** This decision requires the
   durability and recovery properties above, not WAL, two-phase commit, or a
   particular storage engine. Raw solver output need not be durable unless a
   scientific protocol requires it; the durable causal cut must recover the
   adopted authoritative states.
8. **Lab intervention is attributable, not privileged.** A causal intervention
   records an explicit intervention identity, applicable experiment/run,
   operator/principal reference, requested action, target authority, causal
   applicability, and provenance. A caller-supplied `operator_id` is not
   authentication or authorization; those belong to application/control-plane
   security. Scalar/synthetic material transfer may claim controlled
   experimental transfer only, not equivalence to an endogenous physical
   mechanism without specific evidence. Target owners validate changes and
   World commits causal interventions; Lab cannot silently write authoritative
   life state. `intervention_id` identifies the intervention and is never an
   alias for `run_id`. A real `run_id` is required when the intervention occurs
   within a formal scientific execution that declares a run. Preserve study,
   experiment, or protocol identity when that actual context exists; do not
   invent a hierarchy. Interventions outside a run are permitted only when
   explicitly classified as non-experimental (or equivalent), with no
   synthetic run ID. They cannot later be attributed to a scientific run by
   timestamp proximity, operator, process, or intervention identity. Preserve
   principal/operator reference, purpose, target, action, applicability, and
   provenance; a principal reference remains distinct from authentication and
   authorization.
9. **Modality remains provisionally independent.** Keep the repository separate
   during migration because its reusable transduction contracts provide a low-
   cost decoupling seam while stateful implementations are being discovered.
   This does not create semantic authority. Each persistent modality-related
   state declares exactly one of `ORGANISM_OWNED`, `EMBODIMENT_OWNED`,
   `ENVIRONMENT_OWNED`, or `IMPLEMENTATION_EPHEMERAL`; there is no
   `MODALITY_OWNED` category absent a new explicit decision. Reconsider the
   repository only when migration is largely complete, independent versioning
   is proven unnecessary, or persistent coupling demonstrates no real boundary.
10. **Observation Semantic Model v1 is approved conceptually.** Every semantic
    claim has one primary semantic authority and one distinguishable epistemic
    basis, typed subject/scope, domain time/revision, availability state, and
    sufficient provenance/lineage. Family/revision, units, reference frames,
    measurement source, producer/asserter, snapshot coherence, replay,
    delivery guarantees, and scientific evidence admission preserve the
    distinctions in `observation-semantic-model-v1.md`. This authorizes
    semantic-family contracts and later record/envelope design. It does not
    authorize a concrete schema, serialization, API, transport, storage,
    implementation, or cutover by convenience.
11. **The next physical milestone is end-to-end.** The immediate target is the
    `FIRST BIOPEIA END-TO-END PHYSICAL CAUSAL STEP`: a minimal deterministic
    fixture executes a solver, validates/adopts owner state, durably identifies
    required owner checkpoints, and commits a World causal cut before emitting
    a passive Observation projection. It demonstrates repeatability from
    controlled initial state, input, and configuration; stable effector
    identity; omitted-channel semantics; explicit units, frames, and revisions;
    and stale-morphology rejection without a committed next cut. A minimal
    deterministic numerical solver is acceptable. This does not claim
    production crash/power-loss guarantees, physical calibration, or
    equivalence.

## Alternatives Considered

- **Carry current source behavior forward unchanged.** Rejected: positional
  command mapping, implicit missing-channel values, caller-declared World
  rosters, and under-specified intervention provenance do not meet the TARGET
  owner boundaries.
- **Give the solver semantic or persistence authority.** Rejected: numerical
  execution is a capability/substrate; owner domains retain validation and
  state authority, and World retains causal commit authority.
- **Require WAL/2PC or choose a storage engine now.** Rejected: those are
  implementation choices not established as necessary; the required property
  is recoverable, owner-closed durable commit.
- **Consolidate Modality immediately.** Rejected for the current migration
  phase; the explicit provisional boundary is low-cost and reusable. Revisit
  only at the stated evidence triggers.

## Consequences

### Positive

- Prevents positional coincidence, omitted-value defaults, or caller-supplied
  rosters from acquiring hidden authority.
- Separates numerical execution, owner state adoption, and World commit.
- Makes recovery claims testable without prematurely selecting persistence
  technology.
- Preserves attributable Lab interventions and passive Observation boundaries.

### Negative and risks

- Requires target APIs and tests to move beyond exact source behavior where that
  behavior conflicts with the approved contract.
- Adds explicit identity, descriptor, adoption, roster, and recovery work before
  a complete physical integration can be claimed.
- Existing migration candidates may need rewriting or may remain open until
  their contracts match this decision.

## Migration and Validation

- Update the Embodiment, World, Lab, and Modality target contracts and
  `MIGRATION.md` records; retain source SHA/path/blob provenance and classify
  each affected source element.
- Validate command identity and descriptor rules, omission behavior, stale
  morphology rejection, owner candidate adoption/rejection, participant
  completeness, partial-cut recovery, and single-writer assumptions with
  contract and integration tests.
- Re-pin Lab after World changes and run exact-reference tests; keep physical
  equivalence and scientific calibration claims separate from software
  contract validation.
- Keep the Observation semantic model at its approved conceptual boundary;
  advance family contracts without inferring approval of schema, transport, or
  storage. Keep migration source dispositions under active review: `DEFER` is
  provisional and is not a final inventory disposition.

## Relationships

- Elaborates, but does not reopen, Biopeia Architecture v1 / AD-0021…AD-0036.
- Constrained by the [Constitution](../governance/constitution.md),
  [ADR-0060](ADR-0060-world-responsibility-and-naming.md),
  [ADR-0070](ADR-0070-physics3d-body-models-by-morphology.md), and
  [ADR-0072](ADR-0072-persistence-contracts-by-data-class.md).
- Implemented through the linked physical-step design and repository-specific
  migration records.

---
id: design.runtime.biopeia-physical-step-integration-v1
title: "Biopeia Physical-Step and Causal-Commit Integration v1"
document_type: design
domain: runtime
status: approved
canonical: false
implementation_status: partial
owner: project-owner
decision_reference: ADR-0073
last_reviewed: 2026-10-09
language: en
---
# Biopeia Physical-Step and Causal-Commit Integration v1

**Status:** Approved by the Architecture Owner on 2026-10-09 (ADR-0073).
**Implementation:** Partial; repository slices exist, but the complete
owner-adoption and durable World-commit flow is not yet implemented or
validated.
**Scope:** Physical command identity, solver-candidate ownership, Environment
projection, causal participant closure, and World commit/recovery contracts for
the Biopeia migration.
**Non-goals:** This design does not claim solver efficacy, physical equivalence,
scientific calibration, a particular solver, persistence technology, raw solver
output retention, or an Observation schema/API/transport.

## 1. Approved causal physical-step pipeline

```text
                         WORLD
                 causal-step authority
                          │
                   opens physical step
                          │
             ┌────────────┴────────────┐
             │                         │
       EMBODIMENT                 ENVIRONMENT
    body projection             world projection
             │                         │
             └────────────┬────────────┘
                          │
                    PHYSICAL SOLVER
              numerical execution only
                          │
                  candidate results
             ┌────────────┴────────────┐
             │                         │
       EMBODIMENT                 ENVIRONMENT
      validate/adopt             validate/adopt
             │                         │
             └────────────┬────────────┘
                          │
                         WORLD
                     causal commit
```

There is no semantic `Physics` authority. The solver is a capability/substrate:
it computes candidates but does not validate, adopt, persist, or directly mutate
authoritative owner state. World opens and commits causal steps; Embodiment owns
somatic state; Environment owns environmental state.

## 2. Embodiment command contract

An actuator command identifies `body_id`, `embodiment_episode_id`,
`morphology_revision`, `effector_id`, and `command_kind`. Positional association
between actuator and effector lists is never authoritative. The active
effector descriptor is validated against the morphology revision and declares:

- quantity and command semantics;
- unit (no implicit public units);
- valid range;
- optional neutral value;
- saturation/clamping policy.

An omitted channel means **no command for this channel**, not zero and not
neutral. Omission is equivalent to neutral only if the active effector
descriptor explicitly declares that equivalence. Out-of-range values are
rejected unless that descriptor explicitly authorizes saturation. A stale or
incompatible body, episode, morphology revision, effector identity, or contract
version is rejected before solver execution/adoption.

Solver results remain candidates. Embodiment validates and adopts its body
transition; it may reject mismatched identity, episode, morphology revision,
causal tick, or contract version. A solver cannot directly mutate
Embodiment-authoritative somatic state.

## 3. World participant roster and commit object

World owns causal participant completeness. For each causal step, World derives
and validates the required participant set from:

1. active World presence;
2. registered causal owners;
3. participants required by that step;
4. explicit lifecycle transitions.

Callers and owners may identify needed resources or checkpoint references, but a
caller-supplied list is not proof that the roster is complete.

At genesis, the accepted `WorldGenesisSpec` is the authoritative input for the
initial World identity, presences, registered owners, owner identities, and
initial checkpoint references/contracts. World guarantees roster completeness
relative to that accepted specification; it does not discover authorities
omitted from it.

A causal cut identifies at minimum:

```text
world_id
causal_tick
commit_id
participant owner IDs
owner-state/checkpoint references
owner-state versions/hashes
commit status
```

The minimum protocol states are:

```text
PREPARING
COMMITTED
RECOVERY_REQUIRED
```

World may publish a cut as committed only when every required owner state is
durably identifiable and recoverable. On restart, the system determines
unambiguously the last committed causal cut. A partial cut cannot be mistaken
for complete; work after the last committed cut may be discarded. The default
is one World commit authority / single logical writer. Multiprocess execution
requires explicit coordination preserving that single logical authority;
shared-filesystem concurrency is not implied.

This design requires the durability/recovery properties, not WAL, two-phase
commit, or a storage engine. Raw solver output need not be durable unless a
scientific protocol requires it; the durable cut must identify/recover the
adopted authoritative state.

## 4. Correlation and failure

Every physical execution correlates at least:

```text
world_id
causal_tick
physical_step_id
body_id and embodiment_episode_id where applicable
environment revision
morphology revision where applicable
solver/configuration revision
```

If the solver fails, an owner rejects a candidate, or a required result cannot
be adopted, the causal step is not committed. World records failure or enters
recovery according to its commit contract. Committed state is an owner-closed
cut, not simply a successful solver return value.

## 5. Lab intervention boundary

Every causal Lab intervention is attributable through an explicit intervention
identity, operator/principal reference, requested action, target authority,
causal applicability, and provenance. `intervention_id` is never a `run_id`.
`run_id` is required only when an intervention occurs in an actual formal
scientific execution that declares a run; actual study/experiment/protocol
identity is retained where applicable. An intervention without a run is
allowed when explicitly classified as non-experimental (or equivalent), but
must not later be attributed to a run by timestamp, operator, process, or
intervention identity. Do not synthesize a run ID. A caller-supplied
`operator_id` is not authentication or authorization; those belong to
application/control-plane security. Lab requests an intervention, the target
authority validates it, World commits it if causal, and evidence records its
provenance. Lab does not silently write authoritative life state.

A scalar or synthetic transfer can claim **controlled experimental transfer**
only. It does not establish physical equivalence to an endogenous mechanism
without specific evidence.

## 6. Modality repository disposition

Modality remains a **provisional independent repository** through the current
migration because its reusable transduction contracts are a low-cost seam while
stateful implementations are still being discovered. This is not semantic
authority. Every persistent modality-related state identifies exactly one
owner category:

```text
ORGANISM_OWNED
EMBODIMENT_OWNED
ENVIRONMENT_OWNED
IMPLEMENTATION_EPHEMERAL
```

There is no `MODALITY_OWNED` category without a new explicit architecture
decision. Reconsider repository separation when migration is largely complete,
independent versioning proves unnecessary, or persistent coupling demonstrates
that the repository adds no real boundary.

## 7. Observation design gate

Observation remains passive, downstream of authoritative domain state, and
read-only. The approved Semantic Model v1 is the conceptual source for
identity, time/revision, authority/provenance, epistemic status, lineage,
availability, units, frames, part identity, snapshot/replay, and delivery
semantics. Semantic-family contracts may proceed. This does not authorize a
concrete schema, API, event transport, storage, or implementation. A family
contract must not choose transport before its semantic requirements are
defined.

## 8. Validation and migration status

The immediate milestone is **FIRST BIOPEIA END-TO-END PHYSICAL CAUSAL STEP**.
Use a minimal fixture with one World, one Organism presence, one Embodiment,
minimal Environment, at least one effector, deterministic solver/configuration,
and passive Observation. Exercise action/intention through command adaptation,
World step opening, owner projections, solver execution, candidate validation
and adoption, recoverable owner references, durable World commit, and
post-commit Observation. Demonstrate stable effector identity under collection
permutation, omitted-channel NO COMMAND, explicit units and frames,
body/episode/morphology binding, repeated deterministic results, and stale
morphology rejection with no committed next cut. A minimal deterministic
numerical solver is acceptable but is not a physical calibration claim. Prefer
a minimal MuJoCo path only if already available at low cost. Solver failure
should also leave the cut uncommitted if this does not broaden the slice.

Conformance also requires tests for owner adoption/rejection, World roster
completeness relative to the accepted `WorldGenesisSpec`, partial-cut recovery,
single-logical-writer assumptions, and failure without commit. Package tests
and green CI do not demonstrate scientific calibration or physical
equivalence.

Current candidate PRs are implementation slices, not proof of this complete
design. World #10 and Embodiment #11 have been integrated; Embodiment #13 adds
owner-side candidate adoption/checkpoint support. Lab #4 still requires review
against durable World commit and actual owner identities. Observation #3 is
integrated as transport-neutral primitives. The complete integrated flow
remains partial until the end-to-end milestone is validated.

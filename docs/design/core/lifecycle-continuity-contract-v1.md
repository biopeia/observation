---
id: design.core.lifecycle-continuity-contract-v1
title: "Lifecycle Continuity Contract v1"
document_type: design
domain: core
status: proposed
canonical: false
implementation_status: implemented
date: 2026-10-02
depends_on:
  - docs/governance/constitution.md
  - docs/design/core/longitudinal-integrity-v1.md
source_audit: research/audits/current/2026-10-02-current-state-architecture-audit.md
language: en
---

# Lifecycle Continuity Contract v1

## 1. Purpose

[Longitudinal Integrity v1](longitudinal-integrity-v1.md) established that state
survives. The
[current-state audit](../../../lab/research/audits/current/2026-10-02-current-state-architecture-audit.md)
found that what "survives" means is still decided in more than one place: two
re-embodiment semantics, two restore semantics, and a restart that is not an
uninterrupted run.

This document is the single description of every lifecycle operation and of what
each one does to each kind of state. It adds no mechanism of its own. Every rule
below is stated once in an executable register and checked by a named test; the
prose only says where to look.

It records the code as it is. Where two paths differ, the difference is declared
here and pinned by a test. Whether they should converge is an owner decision
(§8).

## 2. Who owns what

| Owner | Meaning | Lifetime |
| --- | --- | --- |
| Symbiont | The longitudinal subject: identity, organism time, genome and expression, cognition, experience, models, social knowledge, learned sensorimotor knowledge | The organism's whole life, across restarts and Bodies |
| Body | Physical and physiological state of one Body | One Body |
| Embodiment | One continuous period of one Symbiont in one Body: the episode, its execution authority and its in-flight motor state | One episode; closed and archived when the Body changes |
| Process | Handles, caches and one-tick traces of one running process | One process |
| Apparatus | Configuration and history written around the organism by the Lab | Recorded as provenance, reapplied by the launcher |

## 3. State classes

Each runtime attribute has exactly one continuity class and one re-embodiment
treatment in `src/symbiont/host/continuity.py::REGISTER`.

| Question | Class in the register | On restart | On canonical re-embodiment |
| --- | --- | --- | --- |
| Belongs to the Symbiont and may never be erased | `MUST_PRESERVE` with `Reembodiment.PRESERVED` | restored exactly | carried exactly |
| Belongs to the Body and is replaced | `MUST_PRESERVE` with `Reembodiment.REPLACED` | restored exactly (same Body) | taken from the fresh Body |
| Belongs to the Embodiment and is closed | `APPARATUS_FIELDS` (`embodiment_episode`) | restored | closed and archived; a new episode starts |
| Kept as historical knowledge without authority over the current Body | `MUST_INVALIDATE_AUTHORITY` with `Reembodiment.INVALIDATED` | restored | knowledge carried, execution bindings and in-flight commitment withdrawn |
| May be recomputed | `MAY_RECOMPUTE` | rebuilt from preserved state | rebuilt |
| Must be reset or invalidated | `MUST_RESET` | never crosses the process boundary | not applicable |
| Apparatus configuration | `MUST_REAPPLY_CONFIG` | recorded in provenance and reapplied | reapplied |

`lab/tests/unit/host/test_continuity_register.py` fails when a runtime attribute or
checkpoint field is unclassified.

### 3.1 BodySchema is episode-scoped evidence, not current-body authority

`body_schema` is a bounded learned representation (sensory-part, cognitive-region,
dependency, sensorimotor, and body-boundary evidence). The checkpoint does not
tag each item with a body/episode provenance class. At canonical re-embodiment,
the complete prior BodySchema is copied into the closed episode archive and its
learned entries are removed from the active schema. The stable opaque identity
salt remains; it does not carry learned claims. The new Body's active schema
starts undeveloped and is rebuilt only through ordinary observations after the
transition. Historical archive records and epoch summaries describe the closed
episode; they are not restored as current BodySchema or injected into current
body facts.

The current representation is episode-scoped as a whole; the engine does not
store per-item Body or episode provenance. That is safe only while all active
entries are reset at a Body transition and archives remain non-authoritative.
The audited consumers are:

| Consumer | Use | Boundary |
|---|---|---|
| `core.domains.embodiment` | Updates sensory and cognitive structure from the current sensory phenotype, self-model, and bounded cognition observations | Writes the active engine only |
| `core.domains.action` and `actuation.acquisition` | Add agency-boundary and sensorimotor evidence from current action/effect observations | Write the active engine; execution bindings remain a separate authority |
| `core.orchestration.individual` and `core.embodiment.episode` | Feed active-schema confidence into the embodiment adaptation summary and close the episode with schema/confidence and Body/episode identity | Affects the adaptation record, not action authorization or physical Body facts; snapshot does not feed schema into a new episode |
| `core.embodiment.transition` | Copies the closing schema into the episode archive, then resets learned entries in the active schema | Archive is historical; new active state starts empty |
| `core.embodiment.memory` | Stores a prior schema in a historical hypothesis package | `EmbodimentPrior` declares `hypothesis_only`; no production runtime consumer was found in this checkout |
| Runtime summaries, Lab adaptation summaries, telemetry, and Observatory projections | Report or analyze the active schema | Observer/adaptation bookkeeping; not an execution-authority source |

After re-embodiment, active consumers start from the empty new-Body schema until
it is rebuilt from new observations. Each action-domain boundary observation
considers only agency estimates updated after the current episode began. Current
physical facts come from the new Body's sensors and physiology. Execution
authority is separately withdrawn by the action-domain transition. Since items
within one active schema still have no individual provenance, future designs
that retain or merge entries across episodes must add provenance or preserve
this whole-schema reset rule.

### 3.2 Body-bound edges inside longitudinal developmental history

The `DevelopmentalTracker` accumulates lifetime counters and bounded
developmental summaries across Bodies. Its `previous_stressed` bit is
different: it compares adjacent observations and therefore belongs to the
current Body's physiological episode. Canonical re-embodiment preserves the
tracker's cumulative history but resets this edge bit before the first
observation of the new Body. Otherwise, that Body's first active observation
could be counted as recovery from stress experienced only by the closed Body.

This nested exception is declared in `REGISTER` as
`_developmental_tracker.development.previous_stressed` → `REPLACED`; the
remaining `development` checkpoint state is preserved. The transition and
register contract are tested by
`lab/tests/unit/lab/physics3d/test_reembodiment.py::test_reembodiment_does_not_count_new_body_activation_as_old_body_recovery`
and `lab/tests/unit/host/test_continuity_register.py::test_developmental_tracker_resets_only_body_bound_stress_edge`.

Evidence scope: `lab/tests/integration/test_reembodiment_continuity.py` verifies
that the archived prior BodySchema is exact, the active schema is undeveloped
after restore, current-episode boundary evidence uses Body B signal identities,
and execution bindings are not valid after restore. This is a mechanical
separation result, not evidence that BodySchema improves adaptation. Historical
schema entries remain archived data and have no current-body authority.

## 4. Lifecycle operations

| Operation | Entry point | What it is | What it is not |
| --- | --- | --- | --- |
| Save | `OrganismRuntime.checkpoint()` / `save()` | State identity over the whole organism payload, chained to its parent | A copy of the Body, the weights or the Lab journal |
| Restart | `<Runtime>.from_checkpoint(payload)` on the same Body | The same organism with the state that was saved | An uninterrupted run (§5) |
| Historical restore | `OrganismRuntime.from_checkpoint(payload)` | Reproduces the individual exactly as saved, including the absence of cognition in a cognition-less checkpoint | An upgrade |
| Owner-facing restore | `restore_resident_with_canonical_cognition(payload, runtime_class=...)` | Historical restore plus the `canonical-cognition-adoption` transform when genome and graph are absent | A neutral restore: it can produce a different organism from the same checkpoint (§6) |
| Canonical re-embodiment | `symbiont.core.embodiment.transition.prepare_fresh_embodiment_checkpoint` | The Symbiont moved into a fresh Body; knowledge carried, authority withdrawn | A reset of cognition |
| Reduced-seed transplant | `Individual.transplant_to` → `CleanEmbodimentSeed.begin_new_embodiment` | The clean-embodiment apparatus: identity, time, genotype and expression kept; embodiment-specific inference restarted from naive | Canonical re-embodiment (§7) |
| Temporal decontamination | `symbiont.core.embodiment.transition.migrate_temporal_domains` | Corrects a contaminated clock coordinate and records it | A reconstruction of the physiology already produced under that clock |

Every operation that changes organism state without the organism living through
it is an authorized transform. It re-identifies the checkpoint and names itself
in `checkpoint_lineage.transforms`.

## 5. Restart is not an uninterrupted run

A restart preserves the organism and its consolidated state. Its future is not
the future of a run that never stopped:

- one-tick causal traces are `MUST_RESET`, so the transition whose window spans
  the process boundary is never recorded;
- every restore opens the reacclimation gate, which pauses structural
  consolidation for `kernel_limits.reacclimation_ticks`.

```text
restart = same organism
        + same consolidated knowledge
        + one unrecorded transition
        + reacclimation
```

`symbiont/tests/integration/test_restart_equivalence.py` fixes the set of fields that may
differ from an uninterrupted run and asserts that exactly one transition is
absent. A claim of restart equivalence stronger than this is not supported.

## 6. Checkpoint history that outlives the save

Two facts about an organism's past are not properties of one save:

- `checkpoint_lineage.transforms` — the authorized transforms it has been
  through;
- `checkpoint_lineage.unverified_legacy_origin` — some ancestor checkpoint was
  accepted without a verifiable identity. Older schemas recorded identifiers
  with weaker or unverified coverage; the current schema-14 runtime rejects
  those checkpoint formats rather than treating the lineage marker as
  permission to restore them.

Both are carried into every later save (`lineage_history` in
`src/symbiont/host/checkpoint.py`, restored into the runtime and written back by
`checkpoint()`). Before this, a transform was visible only on the in-memory
payload that was restored and vanished at the organism's next save, and nothing
recorded that a verifiable chain began at an unverified checkpoint.

Consequences:

- "every checkpoint has a verified identity" is false; "every checkpoint saved by
  a current runtime has a verified identity, and says whether its history starts
  at an unverified one" is true;
- an experiment that needs historical reproduction must preserve the archival
  payload and its provenance; no historical runtime restore is supported by the
  current loader;
- owner-facing launchers share one adoption path for every runtime layer, so the
  CLI and the resident launcher cannot adopt differently.

Tests: `symbiont/tests/unit/core/test_canonical_birth.py`,
`tests/compatibility/checkpoint_v10/`.

### 6.1 Historical checkpoint policy

The earlier schema-10 admission decision predates the current exact-schema
loader and is not the live restore contract. The current runtime accepts only
schema 14; schemas 1–12 are rejected, including schemas 10–12. No automatic
migration path is retained. Historical files and fixtures may remain readable
as archival data, but archival readability is not runtime-format compatibility
and neither establishes state continuity nor authorizes conversion into a live
organism. Any future conversion needs an explicit, separately governed process
that preserves origin limitations in the resulting lineage.

The historic inventory and tests below describe the former admission policy;
they do not demonstrate that those payloads can currently be restored. Recheck
those documents and compatibility tests before claiming a historical organism
is runnable.

## 7. Two transplant semantics

Canonical re-embodiment and the reduced seed's transplant answer the question
"what belongs to the organism?" differently for embodiment-specific inference.

| State | Canonical re-embodiment (`OrganismRuntime`) | Reduced seed (`CleanEmbodimentSeed`) |
| --- | --- | --- |
| Identity, organism time, genome, expression | preserved | preserved |
| BodySchema | archived per closed episode; active schema reset (identity salt retained) | reset to naive |
| Sensorimotor dynamics, effects, causal evidence, controllability, agency | preserved as knowledge | reset to naive |
| Competences | preserved | preserved, effect grounding cleared |
| Execution bindings, surface, in-flight commitment | invalidated | reset |
| CognitiveGraph, experience, private models, social knowledge | preserved | not part of the reduced seed |

The reduced seed is the apparatus of the clean-embodiment studies
(`symbiont_lab.studies.embodiment`). Its semantics are declared per attribute in
`REDUCED_SEED_REGISTER`; every attribute where it discards or ungrounds something
canonical re-embodiment keeps is marked `diverges`.
`symbiont/tests/unit/host/test_reduced_seed_register.py` checks that the register covers
every attribute of the class, that the declared divergences are exactly the real
ones, and that a transplant treats each attribute as declared.

Rule for claims: a result obtained with the reduced seed says nothing about
retained knowledge after canonical re-embodiment, and the reverse. A study must
name which of the two it used.

### 7.1 Decision and enforcement (owner, 2026-10-02; issue #273)

The divergence is intentional and stays. The reduced seed is the subject of the
clean-embodiment falsification apparatus; converging it would change that
apparatus and the comparability of its recorded results. It is no longer called
"Symbiont": the class is `CleanEmbodimentSeed`, and `symbiont.core` exports no
`Symbiont` class.

Per divergent state item:

| State | Canonical owner | In the reduced seed |
| --- | --- | --- |
| BodySchema | Symbiont-owned knowledge | treated as embodiment-owned, restarted |
| Sensorimotor dynamics, effects, causal evidence, controllability, agency | Symbiont-owned knowledge | treated as embodiment-owned, restarted |
| Competence effect grounding | Symbiont-owned knowledge | cleared; the competence itself is kept |
| Execution bindings, surface, in-flight commitment | embodiment-owned authority | embodiment-owned authority |

Each contract has an identifier, `LongitudinalContract` in
`src/symbiont/host/continuity.py`:

- `canonical-reembodiment-v1` — `OrganismRuntime` and its subclasses;
- `reduced-seed-transplant-v1` — `CleanEmbodimentSeed` / `Individual`.

Both classes carry it as `LONGITUDINAL_CONTRACT`. Every module that builds a
subject declares the same constant at module level, the experiment runner writes
it to the run manifest (`longitudinal_contract`; `null` for protocols that build
no longitudinal subject), and
`tests/experimental_integrity/test_longitudinal_contract_declaration.py` fails
when a module that imports either subject does not declare its contract or
imports subjects of both.

Users of the reduced seed at the time of the decision:
`studies.embodiment.{causal_revision_sequence, heredity_leakage_challenge,
integrity_gates, label_invariance}`, `studies.genetics.genome_causal_validation`
and `symbiont_lab.world.adapter` (the `experimental_clean` World path). Users of
canonical re-embodiment: `symbiont_lab.physics3d.{runtime, reembodiment}`.

## 8. Owner decisions

1. **Convergence.** Decided 2026-10-02: no convergence; see §7.1. A later
   decision to converge or retire the seed is a SCIENTIFIC change with its own
   apparatus-impact record.
2. **Legacy sunset.** Decided 2026-10-02: admitted without a date, refused
   where a verified origin is required, and reviewed at a named schema version;
   see §6.1.
3. **Functional transfer.** Preservation is established; usefulness is not. The
   unapproved preregistration draft is
   [Re-embodiment Functional Transfer v1](../experimentation/reembodiment-functional-transfer-v1.md).

## 9. Executable references

| Rule | Register | Test |
| --- | --- | --- |
| Every runtime attribute is classified | `REGISTER` | `lab/tests/unit/host/test_continuity_register.py` |
| Current-schema checkpoints fail closed | `required_checkpoint_fields` | `symbiont/tests/unit/host/test_strict_restore.py` |
| Whole lifecycle per register entry: state → checkpoint → restore → checkpoint → re-embodiment → restore → checkpoint | `REGISTER` | `lab/tests/integration/test_reembodiment_continuity.py::test_the_whole_lifecycle_holds_per_register_entry` |
| Restart differs from an uninterrupted run only on the declared surface | — | `symbiont/tests/integration/test_restart_equivalence.py` |
| Transforms and unverified legacy origin are durable | `lineage_history` | `symbiont/tests/unit/core/test_canonical_birth.py` |
| Reduced-seed transplant contract and its divergences | `REDUCED_SEED_REGISTER` | `symbiont/tests/unit/host/test_reduced_seed_register.py` |

## 10. Claims this contract does not make

- that either transplant semantics is the scientifically correct one;
- that preserved knowledge is useful in a new Body;
- that a restart is equivalent to never having stopped;
- that a checkpoint of unverified legacy origin is untrustworthy, or trustworthy.

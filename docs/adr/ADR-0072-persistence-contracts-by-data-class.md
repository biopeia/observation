# ADR-0072: Persistence Contracts by Data Class

## Status

- **Status:** Accepted
- **Owner acceptance:** 2026-10-06

This record establishes no implementation, format migration, or backend selection.

## Context

The repository persists multiple semantically distinct classes of data: portable
organism checkpoints and bundles, Body and World state, high-rate telemetry,
causal and observer journals, browser projections, and scientific run artifacts.
They differ in authority, lifetime, reconstructibility, write rate, access
boundary, durability, and retention. Treating all of them as one “persistence”
problem risks changing a critical guarantee while addressing an unrelated
performance concern.

The current implementation and accepted decisions already assign different
contracts to several classes:

- The Constitution separates portable Symbiont state from Body state, rejects
  incompatible continuation state, and forbids silent reinterpretation.
- [ADR-0009](ADR-0009-state-x-immutable-run-provenance.md) defines portable,
  content-addressed organism bundles and immutable run provenance.
- [ADR-0018](ADR-0018-transparent-resident-lifecycle-supervision.md) requires
  bounded, durable resident persistence and clean shutdown.
- [ADR-0024](ADR-0024-high-frequency-binary-telemetry-and-decimated-transport.md)
  separates high-frequency causal execution from passive, decimated observation.
- [ADR-0067](ADR-0067-revisioned-state-sections-and-passive-observation.md)
  defines revisioned state sections, passive observation, and binary canonical
  checkpoints for its stated substrate-cut scope.
- [Lifecycle Continuity Contract v1](../design/core/lifecycle-continuity-contract-v1.md)
  distinguishes Symbiont, Body, Embodiment, process, and apparatus lifetimes.

The user-facing concern motivating this proposal is slow reads/writes and
possible memory pressure in the web path. No current measurements in this audit
establish which persistence class or reader is responsible. Disk format alone
does not establish server RSS or browser heap use; those depend on read,
projection, caching, transport, and rendering behavior.

## Decision drivers

1. Preserve explicit ownership and authority boundaries.
2. Preserve checkpoint identity, continuity, provenance, and evidence integrity.
3. Keep storage/observation work from backpressuring causal execution.
4. Make memory and I/O costs attributable to a concrete producer/consumer path.
5. Avoid a universal storage abstraction where data classes have materially
   different semantics.
6. Keep portable artifacts recoverable without relying on a live query service.

## Proposal

Define persistence contracts by **data class and use**, not by file extension or
storage engine. Every new or materially changed persistence path SHOULD identify:

1. canonical owner and authorized readers/writers;
2. semantic role: authoritative continuation state, portable artifact, append-only
   evidence, telemetry, derived index/cache, configuration, or UI-local state;
3. lifetime and identity scope (organism, Body, embodiment, run, process, or
   browser session);
4. authority, reconstructibility, and acceptable loss;
5. expected and maximum size, write/read rate, and concurrency assumptions, or
   an explicit statement that these are not yet measured;
6. required atomicity, durability, ordering, snapshot-consistency, and failure
   behavior;
7. format/schema identity, integrity validation, and compatibility/migration
   policy;
8. retention, rotation, backup, and restore behavior;
9. privacy/access limits and whether the data may reach organism, server, or
   browser memory;
10. resource budgets or measurements for producer, server, and browser where
    relevant.

The resulting inventory SHOULD keep at least these classes distinct:

| Class | Canonical role | Contract boundary to preserve |
|---|---|---|
| Symbiont checkpoint and portable bundle | Authoritative organism continuation and portable identity | Separate from Body and observer state; validate identity/schema; retain required provenance |
| Body checkpoint | Physical state of one Body | Separate authority and lifetime from portable Symbiont state |
| World checkpoint/journal | World-owned state and event history | Separate from organism state and experiment observer records |
| Physics telemetry | Passive run observations and diagnostic traces | Must not feed cognition or stall causal execution; readers need a consistent committed view |
| Causal provenance journal | Apparatus-side causal explanation history | Outward-only; distinct from the organism's bounded internal causal state |
| Observatory artifacts and projections | Passive transport and browser-facing projections | Must not expose private checkpoints or become a second state authority |
| Scientific run artifacts | Reproducibility and evidence | Preserve provenance and immutability requirements; not disposable cache |
| Models and other large artifacts | Referenced portable/runtime payloads | Separate their loading/caching profile from compact identity and index metadata |
| Configuration, credentials, and auxiliary records | Operational inputs or protected local material | Define permissions, secret handling, and recovery separately |
| Browser-local state | Presentation/session state | Bound retention and copies; never confuse it with causal continuation state |

This proposal does **not** select SQL, SQLite, files, or a hybrid backend. It does
not require one schema for all classes, change any accepted ADR, or authorize
checkpoint/telemetry format migration. A derived index may be considered only
under its own contract, including its source of truth and rebuild behavior.

## Alternatives considered

### One persistence contract and backend for all data

Would simplify the surface vocabulary, but would conflate immutable evidence,
continuation state, high-rate telemetry, UI projections, and disposable derived
data. It also risks forcing incompatible durability and performance trade-offs.
Rejected for this proposal.

### Continue with only per-subsystem implicit contracts

Preserves local flexibility and avoids a new inventory. However, current
cross-cutting analysis shows it is difficult to compare guarantees or attribute
I/O and memory costs across producers and readers. Retain subsystem-specific
mechanisms, but make their contracts discoverable through a shared inventory.

### Replace all file persistence with SQL

Could improve relational queries and transactions for selected workloads, but
does not itself make reads streaming, reduce web payloads, or bound memory. It
would add schema migration and operational concerns and could conflict with
portable, content-addressed artifacts and high-frequency binary streams. Not
selected; reconsider only with measured workload evidence and a class-specific
proposal.

## Consequences

### Positive

- Makes ownership, data authority, failure guarantees, retention, and memory
  exposure explicit before backend decisions.
- Allows profiling to target a specific producer-to-reader path.
- Preserves existing specialized formats where their contracts require them.
- Provides a basis for deciding whether an index, streaming reader, bounded cache,
  or storage backend change addresses a demonstrated bottleneck.

### Negative and risks

- Adds documentation and review work; contracts can become stale unless owned
  and checked when paths change.
- The class inventory may expose inconsistent existing guarantees that need
  separate remediation; this proposal does not authorize that remediation.
- Current performance conclusions remain unavailable until workloads are
  measured in the actual writer, server, and browser paths.

## Evidence and open questions

The code audit covered the checkpoint, World persistence, Physics3D telemetry,
provenance journal, Observatory, experiment-artifact, model-artifact, and web
projection areas. It was a source inventory, not a benchmark or exhaustive
runtime census. The following remain open:

- Which exact user operation is slow, and what are its input sizes and rates?
- Is observed memory pressure in the Python process, browser JS heap, or both?
- Which active workload reads whole files or retains full decoded histories?
- What are representative and worst-case checkpoint, telemetry, and history
  sizes, and what durability latency is actually required?
- Which existing file outputs are canonical records versus derived or temporary
  data, especially across older study implementations?

## Reconsideration

Revisit this proposal before introducing a shared persistence backend, changing
checkpoint/restore authority, altering retention of evidence, or changing
high-frequency telemetry write/read semantics. Any backend proposal should be
supported by measurements for the affected class and preserve its applicable
accepted invariants.

# Observation

This repository contains a bounded, passive projection slice extracted from the
Symbiont Lab source tree. It provides Python data structures and mapping helpers
for representing already-produced runtime observations. It does not own the
observed state and does not issue runtime commands.

Included:

- `ObservedFrame`, an inherited transitional presentation projection contract.
- `runtime_tick_events`, an inherited transitional mapping from telemetry to
  body, optional cognition, and vitals presentation records. It is not a stable
  Biopeia semantic-family contract; absent cognition data produces no cognition
  event.
- A transport-independent semantic claim model and bounded in-memory
  `ObservationPlane` for current projections, live fan-out, replay, and explicit
  rebase signaling.
- A narrow local-only, read-only HTTP bridge for the approved Frontend M1
  `embodiment.body_pose@v1` and
  `environment.finite_scalar_field@1` current projections. The bridge must be
  attached to the same in-process plane used by the World publication path; it
  is not a standalone source of observations.
- Bounded owner-projection mappings for Environment finite scalar fields and
  Embodiment BodyPose v1. These adapters preserve source authority and do not
  prove that World committed the correlated cut; publication requires
  independent World-side verification. See
  [the BodyPose mapping contract](docs/embodiment-body-pose-mapping-v1.md).

The in-memory plane remains separate from operator controls, scientific evidence
custody, UI, network streaming, remote access, the live observation bus, World
scene lifecycle, and domain-specific readers. Historical
payload keys remain in the copied projection as source behavior only; this is
not a compatibility promise or a ratified Biopeia API. The semantic model recognizes
`ORGANISM`, `EMBODIMENT`, `ENVIRONMENT`, and `WORLD` as primary authorities;
`LAB` is only appropriate for Lab-derived claims. Modality is not an
automatically authoritative domain.

The projection does not emit or accept `symbiont_tick` as a TARGET field. If a
caller supplies that source-specific key, it is ignored; it is never aliased to
the generic `tick` key. The generic `tick` projection does not by itself assert
World causal time, Organism progression, or any other domain-time semantics.

The in-memory plane orders publications by one monotonically increasing
delivery sequence (not domain time). A family-filtered stream retains this
global sequence, so skipped sequence numbers may belong to other families.
`open_stream()` is the stream API: it signals replay expiry and live queue
overflow with an explicit rebase request; it also signals rather than truncates
a current-state bootstrap that exceeds the bounded queue. There is no lossy
latest-value subscription API. Current materialization is bounded and keyed by
semantic family, contract ID and revision, and subject
(including typed identity issuer, scope, and lifetime), so distinct contract
or identity contexts cannot silently overwrite one another. The current view is
a bounded latest subset: oldest subjects are evicted at capacity, and an
absent subject in `current()` / `current_messages()` is not evidence of source
absence, unavailability, or non-existence. Epistemic kind is
also part of the key: authoritative, estimated, and inferred claims remain
separate materialized values.

The in-memory `open_stream()` delivery contract is scoped to one plane instance:
it orders observations and run-boundary control events by one global delivery
sequence; a family filter retains that sequence, so unrelated-family messages
and control events create legitimate sequence gaps.
A healthy subscription delivers each sequence at most once. Re-fetch after a
rebase may overlap already processed messages, so consumers should deduplicate
by sequence. Replay is complete only within the retained in-memory range when
the requested replay fits the bounded queue; normal live delivery is complete
until overflow. Overflow/expiry/bootstrap bounds and run boundaries require
rebase. A run boundary reserves a sequence watermark so a resumed consumer can
distinguish pre-boundary state from later publications. Rebase repairs the
materialized current view; it does not reconstruct skipped event history. The
resumed subscription remains live after the rebase marker and can deliver
later publications, with possible overlap against a refreshed current view.
This control metadata is in-memory only; there is no durability or cross-restart
resume guarantee.
The plane snapshots claim values on publication and returns detached snapshots
from current views, bootstrap, replay, and each live subscriber. The common
plane accepts only built-in scalar/container value trees (including nested
lists, tuples, and mappings); recursive containers and custom instances are
rejected before publication side effects. A family adapter must explicitly
project custom domain values into this supported representation while holding
the synchronization needed to capture a stable owner value. The plane cannot
make a racing read of owner-owned mutable state atomic. Returned snapshots are
independent mutable copies: mutating one does not alter owner state, retained
plane state, or another subscriber's delivery. This is in-process isolation,
not persistence or a wire-format commitment.
`SubjectScope.key` is a local
scope descriptor, not inherently stable identity;
stable identity requirements belong to each semantic family and use typed
identity assertions where needed.

## Optional local archive

`SQLiteObservationArchive` is an explicit, opt-in local store for observations
that have already crossed an authorized publication boundary. It is separate
from `ObservationPlane`: publishing to the plane does not automatically write
to the archive, and archive failures cannot block or roll back World. It
preserves each append (including duplicate payloads) and the complete semantic
observation/provenance payload; its local receipt sequence is storage order,
not source time, causal order, or a cross-domain join. Queries filter by exact
family and page by that receipt sequence. The archive performs no joins,
inference, expiry, overwrite, or eviction.

The configured `max_payload_bytes` is a logical limit on retained record
payloads, not a physical disk quota (SQLite pages, indexes, and journals add
overhead). Once reached, append stops and records the attempted receipt range
as a capture gap; earlier originals remain intact. Disk-full or other I/O
failures are surfaced as errors and are not guaranteed to persist gap metadata.
`LocalObservationArchiveCapture` is an explicit opt-in adapter from an
`ObservationPlane` to this archive. It starts at the plane's current delivery
sequence watermark (it does not pretend the current materialized view is
history), copies future accepted publications on a worker thread, and does not
run storage work on the publisher/World thread. Rebase/queue-overflow events
are persisted as ObservationPlane delivery-sequence gap markers; these are
not World ticks or causal joins. If a gap is recorded, the archive must not be
treated as complete history. The capture adapter does not automatically
attach to a plane; the owning runtime must opt in and manage its lifecycle.

This API does not expose an HTTP endpoint, alter current read permissions, or
admit Lab evidence. It is a local single-user prototype, not a production
retention, security, or legal-erasure system. Callers are responsible for
providing an existing trusted directory and keeping the archive local.

# Observation

This repository contains a bounded, passive projection slice extracted from the
Symbiont Lab source tree. It provides Python data structures and mapping helpers
for representing already-produced runtime observations. It does not own the
observed state and does not issue runtime commands.

Included:

- `ObservedFrame`, a transport-neutral frame projection data contract.
- `runtime_tick_events`, a pure mapping from one telemetry mapping to body,
  cognition, and vitals projection records.
- A transport-independent semantic claim model and bounded in-memory
  `ObservationPlane` for current projections, live fan-out, replay, and explicit
  rebase signaling. The plane has no wire, network, UI, or runtime writeback.

Excluded from this initial extraction: operator controls, scientific evidence
custody/provenance, UI, network/SSE transport, the live observation bus, World
scene lifecycle, and domain-specific readers. The extracted code preserves
CURRENT payload keys; it does not ratify them as final Biopeia APIs or decide
which authority owns each source field. The semantic model recognizes
`ORGANISM`, `EMBODIMENT`, `ENVIRONMENT`, and `WORLD` as primary authorities;
`LAB` is only appropriate for Lab-derived claims. Modality is not an
automatically authoritative domain.

The in-memory plane orders publications by one monotonically increasing
delivery sequence (not domain time). A family-filtered stream retains this
global sequence, so skipped sequence numbers may belong to other families.
`open_stream()` signals replay expiry and live queue overflow with an explicit
rebase request; it also signals rather than truncates a current-state bootstrap
that exceeds the bounded queue. The compatibility `subscribe()` API is
intentionally lossy:
when its bounded queue fills it keeps the newest item without gap signaling;
use `open_stream()` where replay/gap recovery matters. Current materialization
is bounded and keyed by semantic family, contract ID and revision, and subject
(including typed identity issuer, scope, and lifetime), so distinct contract
or identity contexts cannot silently overwrite one another. The current view is
a bounded latest subset: oldest subjects are evicted at capacity, and an
absent subject in `current()` / `current_messages()` is not evidence of source
absence, unavailability, or non-existence. Epistemic kind is
also part of the key: authoritative, estimated, and inferred claims remain
separate materialized values.

The in-memory `open_stream()` delivery contract is scoped to one plane instance:
it orders messages by the global publication sequence; a family filter retains
that sequence, so unrelated-family messages create legitimate sequence gaps.
A healthy subscription delivers each sequence at most once. Re-fetch after a
rebase may overlap already processed messages, so consumers should deduplicate
by sequence. Replay is complete only within the retained in-memory range when
the requested replay fits the bounded queue; normal live delivery is complete
until overflow. Overflow/expiry/bootstrap bounds require rebase. There is no
durability or cross-restart resume guarantee. `subscribe()` is at-most-once,
latest-value and lossy: queue pressure replaces queued items with the newest
item, without replay or gap signaling, and its initial snapshot may be bounded.
`SubjectScope.key` is a local scope descriptor, not inherently stable identity;
stable identity requirements belong to each semantic family and use typed
identity assertions where needed.

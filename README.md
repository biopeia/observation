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
is bounded and keyed by semantic family, contract revision, and subject, so a
new semantic revision cannot silently overwrite the previous revision's
materialized value.
`SubjectScope.key` is a local scope descriptor, not inherently stable identity;
stable identity requirements belong to each semantic family and use typed
identity assertions where needed.

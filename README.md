# Observation

This repository contains a bounded, passive projection slice extracted from the
Symbiont Lab source tree. It provides Python data structures and mapping helpers
for representing already-produced runtime observations. It does not own the
observed state and does not issue runtime commands.

Included:

- `ObservedFrame`, a transport-neutral frame projection data contract.
- `runtime_tick_events`, a pure mapping from one telemetry mapping to body,
  cognition, and vitals projection records.

Excluded from this initial extraction: operator controls, scientific evidence
custody/provenance, UI, network/SSE transport, the live observation bus, World
scene lifecycle, and domain-specific readers. The extracted code preserves
CURRENT payload keys; it does not ratify them as final Biopeia APIs or decide
which authority owns each source field.

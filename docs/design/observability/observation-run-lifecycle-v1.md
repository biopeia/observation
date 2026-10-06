# Observation Run Lifecycle v1

**Status:** Canonical extension  
**Date:** 2026-10-06  
**Extends:** `observation-identity-and-freshness-v1.md`  
**Scope:** Unified Lab `ObservationBus`, Physics3D session lifecycle, live Workbench consumers.

## 1. Purpose

Transport continuity is server-owned; live observation materialization is run-owned.
A server may host multiple sequential Physics3D runs without restarting its SSE
transport, but current presentation state from one run must never survive as
current state in the next run.

This contract makes that boundary explicit without introducing a second journal,
a second runtime, or a new longitudinal history authority.

## 2. Authority

`Physics3DSession` owns the live observation lifecycle because it is already the
single place that establishes the Lab `run_id`:

- managed sessions use the durable launch `run_id`;
- unmanaged `--physics3d` sessions use a Lab-owned `local:<uuid>` identity.

The session MUST call `ObservationBus.begin_run(run_id)` before a bridge can emit
run observations and MUST call `ObservationBus.end_run(run_id)` on every terminal
path after the bridge stops.

## 3. Server lifetime vs run lifetime

The following state is server/transport-scoped and MUST survive run boundaries:

- monotonically increasing SSE transport sequence;
- connected subscribers;
- aggregate disconnect/overflow/rebase diagnostics;
- queue/history capacity configuration.

The following state is run-scoped and MUST be invalidated at every run boundary:

- materialized current channel values;
- per-channel materialized sequence lookup;
- bounded reconnect history for the previous run;
- materialized World scene;
- delta encoder states, revisions and anchor cadence;
- pending subscriber backlog and per-client channel bases.

Persistent Physics3D telemetry is not part of this live state and MUST NOT be
deleted or reset by observation lifecycle transitions.

## 4. Boundary event

The live stream exposes an observer-owned lifecycle event:

```json
{
  "type": "observation_boundary",
  "phase": "begin",
  "run_id": "<lab-run-id>"
}
```

or:

```json
{
  "type": "observation_boundary",
  "phase": "end",
  "run_id": "<lab-run-id>"
}
```

The event is transport/observer provenance. It is not organism state and never
feeds back into Symbiont.

A `begin` boundary means the run identity is known but no live organism frame is
yet entitled to be shown. Consumers MUST enter waiting/stale presentation until
new-run evidence arrives.

An `end` boundary means there is no current Physics3D observation for that run.
Consumers MUST stop presenting its values as live.

## 5. Delta rule

A run boundary resets all `ObservationDeltaEncoder` channel bases and revisions.
Therefore the first compressible observation for every channel in the new run
MUST be an anchor. A delta MUST NEVER use an event from a previous run as its
base, even when SSE transport sequence is continuous.

The SSE sequence itself MUST NOT reset.

## 6. Subscriber rule

At a run boundary, queued old-run presentation messages are discarded for every
currently connected consumer. Their channel-base bookkeeping is also cleared.
The boundary event is then queued as the first event of the new lifecycle.

A new subscriber connecting after `begin_run` and before the first run frame MUST
receive the current boundary and MUST NOT receive a materialized value from the
previous run.

Reconnect with a cursor from the previous run is treated as a replay discontinuity
against the new run-scoped history; recovery remains anchor-based.

## 7. World rule

The materialized `/api/world-scene` value is run-scoped. It is invalidated at
both `begin_run` and `end_run` and remains unavailable until the active run emits
new World evidence.

No World scene from a previous body/run may be served as the current scene while
a new run is starting.

## 8. Workbench rule

Mind/Vision consumers MUST clear coherent-frame identity and delta decoder state
when receiving an `observation_boundary`.

- `begin` -> local Physics3D owns the source, status is waiting for the first
  coherent frame of that run;
- `end` -> local Physics3D live ownership is released and the run is no longer
  presented as current.

Body/World presentation MUST consume the boundary only as lifecycle control; it
MUST NOT pass it to the physical renderer as an observation. If `/api/state`
already identifies a run, the first SSE physical event MUST have the same
`run_id` or be rejected and trigger presentation reset.

## 9. Development history

Longitudinal Development remains reconstructed from Physics3D Telemetry v4.1.
Live bus resets do not erase Development evidence.

A telemetry run whose persisted telemetry manifest identifies the requested
organism but whose reader cannot be opened or verified MUST remain visible in
Development coverage as `availability: unreadable`. Such a run makes
`complete=false`; it MUST NOT disappear silently from coverage.

A catalog ref or alias is not sufficient evidence to attribute an unreadable run
to an `organism_id`.

## 10. Required regressions

Conformance requires executable tests for at least:

1. Run A current state is absent from a new subscriber after Run B begins.
2. Pending Run A messages are removed from already connected consumers.
3. The first compressible Run B message is an anchor with a fresh revision base.
4. SSE transport sequence remains monotonic across the boundary.
5. World materialization is null until Run B publishes new World evidence.
6. `Physics3DSession` opens and closes the bus lifecycle on real thread lifecycle.
7. Mind/Vision transition live A -> waiting B -> live B without retaining A.
8. Body rejects a first stale SSE event when `/api/state` already identifies B.
9. A boundary event never reaches the physical renderer as organism/body data.
10. Development reports attributable unreadable telemetry as incomplete coverage.

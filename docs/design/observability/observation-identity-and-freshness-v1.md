# Observation Identity and Freshness v1

**Status:** Canonical implementation contract  
**Date:** 2026-10-05  
**Scope:** Symbiont Lab observation, transport and presentation.  
**Applies to:** Physics3D ObservationBus/SSE, Observatory compatibility streams, Workbench Mind, Embodiment, World and any future passive observer.

---

## 1. Purpose

Symbiont Lab is an observer and control apparatus. It must never present a plausible value as current merely because that value existed in an earlier observation.

Every live presentation must therefore answer four separate questions:

1. **Identity:** which run and organism does this observation belong to?
2. **Time:** at which organism tick was it observed?
3. **Availability:** did the source actually report the value?
4. **Freshness:** is the displayed value still entitled to be treated as current?

Transport continuity and scientific identity are different concerns. A monotonic SSE sequence can resume a byte stream; it does not identify an organism run.

---

## 2. Canonical identity

### 2.1 Required live Physics3D identity

Every coherent Physics3D frame MUST contain:

- `source`;
- `run_id`;
- `organism_id` when an organism identity exists;
- `tick`.

A managed Physics3D session uses the durable Lab `run_id`. An unmanaged local `--physics3d` session receives an ephemeral Lab-owned `local:<uuid>` run identity. Distinct process/session lifecycles MUST NOT be indistinguishable merely because both use the `physics3d` source.

### 2.2 Optional scoped identity

When known, the observer SHOULD also carry:

- `instance_id`;
- `body_id`;
- `embodiment_id`;
- `topology_revision`.

Absence of one of these fields MUST NOT be replaced with an invented identifier.

### 2.3 Frame compatibility

The coherent frame remains `completed-render-frame-v1`; the additive identity guarantee is versioned independently as:

`observation-identity-v1`

This preserves compatible consumers while allowing new consumers to reject a frame that lacks the identity required for safe composition.

---

## 3. Identity boundaries

A presentation identity changes when any of the following changes:

- observation source;
- `run_id`;
- `organism_id`;
- Observatory `instance_id`.

A body/embodiment boundary changes when either changes:

- `body_id`;
- `embodiment_id`.

### 3.1 Run change

On `run_id` change, current live presentation state MUST be cleared before data from the new run is composed.

Observer-owned longitudinal history MAY remain available for the same `organism_id`, but each record MUST preserve its run boundary. Historical evidence from two runs MUST NOT be rendered as one coherent live frame.

### 3.2 Organism change

On `organism_id` change, all current organism-specific presentation state MUST be cleared. Development/history scope changes to the new organism.

### 3.3 Re-embodiment/body change

Cognition and organism history remain organism-owned and MAY persist when the same organism is re-embodied.

Physical presentation state MUST NOT persist across a new run/body boundary. This includes:

- pose buffers;
- interpolation state;
- contacts;
- observer trajectories;
- physical resource baselines;
- body-specific visual caches;
- materialized World presentation tied to the previous body/run.

Self Model or Body Schema information persists only when the organism continues to report it; presentation must not reconstruct it from the previous body.

---

## 4. Availability semantics

The Workbench distinguishes the following states:

| State | Meaning |
|---|---|
| `observed` | The source reported a non-null value in the current observation. |
| `observed_empty` | The source explicitly reported an empty collection. |
| `observed_null` | The source explicitly reported `null`. |
| `not_observed` | The field was absent from the current observation. |
| stale presentation | A previous observation exists but transport/source freshness has been lost. |
| unavailable | The producing source/capability is unavailable. |

An absent field is not zero, false, an empty collection, or the previous value.

Complete `body`, `cognition` and `vitals` projection events therefore replace their channel state: fields missing from the new complete projection become unknown/not observed in live presentation.

Array-shaped frontend storage MAY use `[]` for renderer type stability only when a parallel availability state preserves whether the collection was actually observed empty.

---

## 5. Derived values

The observer may derive presentation, but must not turn absence into a fact.

Examples:

- a predictor count may be derived from topology only when topology itself was observed;
- a missing topology must not imply `0 predictors`;
- activation quantization and prediction-error classes are observer-derived and belong under `observer_analysis`;
- legacy observer-derived fields found inside old cognition snapshots are adapted once at the snapshot boundary and removed from organism-owned cognition before renderers consume them.

Observer-derived values MUST retain provenance sufficient to distinguish them from organism-owned facts.

---

## 6. Coherent frame rule

A local Mind frame may be treated as coherent only when:

- it has a valid run identity;
- it belongs to the current organism identity;
- telemetry and rich snapshot refer to the same completed tick.

Identity is established before body/cognition/vitals/snapshot components are dispatched to presentation. A new run therefore clears old presentation before any new-run field is rendered.

---

## 7. Delta and SSE continuity

### 7.1 Transport sequence

`ObservationBus.stream_id` is transport identity only. It is not run identity.

### 7.2 Revision gap

A delta whose `base_revision` does not match the decoder's current channel revision MUST NOT be applied.

The frontend enters `waiting-for-anchor` for that channel and marks the observation stale rather than continuing to present the previous value as live.

### 7.3 Consumer overflow

A slow observer MUST never block the organism/runtime. When its bounded queue overflows:

1. pending presentation backlog is discarded;
2. dependency bases are cleared;
3. the next dependent channel observation is materialized as an anchor;
4. the anchor carries transport rebase reason `consumer_overflow`;
5. an aggregate overflow counter is incremented.

### 7.4 Reconnect after retained history

If `Last-Event-ID` is still within retained history, replay continues from the retained materialized history.

If requested history has rotated away, current channel anchors are sent with rebase reason `history_rotated`.

If replay would exceed the consumer queue and slicing could orphan delta dependencies, current anchors are sent with reason `replay_truncated`.

### 7.5 Visibility

Transport recovery must be both safe and observable. Normal presentation exposes at least:

- `LIVE`;
- `STALE`;
- `DISCONNECTED`;
- `NO DATA`/waiting where applicable.

Diagnostic state may additionally expose:

- stream sequence;
- channel revision;
- rebase reason;
- overflow/rebase/disconnect counters.

---

## 8. Observatory compatibility

Observatory remains an active compatibility source. Its cursor is `run_id:journal_sequence`, while the modern ObservationBus cursor is a transport sequence integer.

These protocols are intentionally different and MUST NOT be conflated.

When no local Physics3D source owns Mind:

- exactly one live Observatory instance may be selected automatically;
- zero live instances means waiting;
- more than one live instance is ambiguous and MUST NOT be resolved by array order.

---

## 9. History

`/api/organism/history` returns materialized coherent frames, not partial substitutes. A historical frame retains, when present:

- identity fields;
- body;
- cognition;
- vitals;
- mind snapshot;
- topology revision;
- provenance.

The Workbench may bootstrap Development from these frames, but identity boundaries are applied between historical frames before composition.

Development is observer-owned longitudinal evidence scoped primarily by `organism_id`; it is not organism memory.

---

## 10. Diagnostics and privacy

Expected browser disconnects remain suppressed from per-request logging to avoid noisy SSE logs. Aggregate counters retain evidence of:

- client disconnects;
- consumer overflows;
- history rebases;
- replay truncations;
- current subscriber/history/queue sizes.

These counters are observer diagnostics and never feed back into Symbiont.

---

## 11. Required regression guarantees

The implementation is not considered conformant unless automated tests cover:

1. managed and unmanaged Physics3D run identity;
2. complete-frame identity propagation;
3. absent/null/zero/false distinctions;
4. observed-empty vs not-observed collections;
5. decoder revision gaps and anchor recovery;
6. visible overflow/history rebase reasons;
7. complete history endpoint frames;
8. run and organism identity changes in frontend state;
9. ambiguous multi-instance Observatory discovery;
10. real-browser EventSource reconnect with `Last-Event-ID` and Run A → Run B DOM freshness.

---

## 12. Non-goals

This contract does not:

- change Symbiont cognition, learning, rewards or goals;
- introduce a second runtime;
- replace SSE with WebSocket;
- make observer-derived semantics organism-owned;
- remove Observatory compatibility;
- require authentication while the unified server remains hard-bound to loopback.

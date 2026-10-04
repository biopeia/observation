# Simulation Substrate Cut v1 — step 0: measurement and spikes (2026-10-04)

Design: `docs/design/core/simulation-substrate-cut-v1.md` §9, step 0.
Gate: "the cost table in §2 is confirmed or replaced, and both spikes report
feasibility."

Everything here is an apparatus measurement on one laptop, taken while other
work was running on the machine (a two-core scientific run and two agents).
Absolute times are therefore upper bounds; the split between components is
the reliable part. No scientific claim is made.

## 1. Subject

A real organism developed on `main` the same day: body kind
`anthropomorphic-v6-vision`, tick 1536, development phase juvenile, 45
private-model records, 2048 ledger records, checkpoint 32 MB as canonical
JSON in 72 top-level sections. Private-model training disabled during the
measurement.

## 2. Cost per tick at the current baseline

| Configuration | Ticks | Per tick, median | Organism step | Physics | Diagnostics |
|---|---:|---:|---:|---:|---:|
| `observation_hz=1` (study mode) | 40 | 140 ms | 104 ms | 26 ms | 5.5 ms |
| default observation | 24 | 319 ms | 217 ms | 45 ms | 20 ms |

Function-level profile (24 ticks, `observation_hz=1`, profiler overhead
included, 31.0 s total self time):

| Where | Self time | Share |
|---|---:|---:|
| closing the telemetry file at the end of the run (once) | 7.6 s | 25 % |
| `copy.deepcopy` and its helpers | 3.4 s | 11 % |
| JSON encoding and decoding | 2.3 s | 7 % |
| `fsync` (19 calls) | 1.8 s | 6 % |
| adaptive-sense relation eviction (`host/adaptive.py`) | 1.0 s | 3 % |
| PyBullet `stepSimulation` (240 calls) | 0.60 s | 1.9 % |
| PyBullet `getCameraImage`, `getContactPoints`, joint and link queries | < 0.05 s together | < 0.2 % |

**Physics split.** Of about 26 ms of physics per tick, about 25 ms is
`stepSimulation` (ten substeps at 240 Hz). Rendering for vision and contact
queries are negligible at this body and cadence.

## 3. The design's cost table is replaced

The design's §2 table (Simulation Throughput v1, an older snapshot of another
organism) gave about 5 s per tick with rich telemetry at about 90 % of wall
time, and 0.19 ticks per second.

At the current baseline, for this organism:

- a tick costs 0.14 s in study mode and 0.32 s with default observation:
  about 7 and 3 ticks per second;
- the **organism step is the dominant cost** (about 70 %), not telemetry;
- physics is 14–19 % of a tick; replacing the engine removes at most that.

Two things can explain the difference and were not separated here: work that
landed since that measurement, and organism age (the earlier subject was
older; several costs grow with age). This report does not show that the old
table was wrong for its subject.

The design's own §14 says to reconsider "if step 0 shows the cost table no
longer holds". That condition is met.

## 4. Spike — physics engine (workstream "physics and vision backend")

The simplest articulated body, `crawler-v1`, using the URDF the repository
already generates (`build_articulated_urdf`), loaded in MuJoCo 3.14.0 (CPU)
from an ephemeral environment; no dependency was added to the repository.

| Check | Result |
|---|---|
| URDF loads; floor, free joint and 12 velocity actuators added through MJCF | yes: 14 bodies, 19 geoms, `nq` 19, `nv` 18 |
| Body settles on the floor under random actuation, state finite | yes: base height 0.61 → 0.25 m, 19 contacts |
| Cost per tick, ten substeps at 240 Hz | 0.41 ms |
| Replay determinism, two runs in one process | identical state hash |
| Save/restore transparency (run 2000 = run 1000, save, restore, run 1000) | identical with the integration state (170 floats); **not** with the reduced "full physics" state, which omits solver warm-start |

**Feasible.** Two facts for the implementation: the body checkpoint must be
MuJoCo's integration state, not positions and velocities alone; and a MuJoCo
model is compiled from one scene description, so bodies (`embodiment`) and
world objects (`environment`) must hand declarative fragments to the
composition root in the Lab instead of each creating objects in a shared
client, as they do with PyBullet. PyBullet is used at about 160 call sites in
12 files, about 30 distinct functions.

Not covered: the humanoid bodies, contact recalibration, the analytic ray
caster for vision, cross-process and cross-platform determinism.

## 5. Spike — state sections (workstream "organism state layout and passive observation")

Per-tick digests of every top-level checkpoint section over 64 ticks of the
same organism:

| Measure | Value |
|---|---:|
| sections | 72 |
| sections that changed on every tick | 21, holding 40.8 % of the bytes |
| sections that never changed | 42, holding 1.4 % of the bytes |
| bytes an observer would re-encode per tick with one revision per section | 84.2 % of a full copy |

The largest sections change on almost every tick because one item is added
to them: the experience ledger (11.8 MB, changed on 63 of 64 ticks), the
actuation state (4.9 MB, every tick), sensory development (3.2 MB, every
tick), the embodiment episode (2.2 MB, every tick).

**Feasible only with a finer partition than the design describes.** One
revision per top-level section saves about 16 %. The saving has to come from
inside the sections: append-only stores exposed as "everything up to index
*n*" plus the new items, and large mappings split by key. That is a larger
change to the organism than the design assumed, and it was not spiked.

## 6. Gate

- Cost table: **replaced** (§2–§3).
- Physics spike: **feasible**.
- State-section spike: **feasible only with a finer partition**; the
  approved shape is not sufficient.

The gate's letter is met. Its purpose — deciding whether the plan still
makes sense — returns a different picture from the one the design was
approved on:

| Design expectation | Measured |
|---|---|
| telemetry about 90 % of wall time | organism step about 70 % |
| physics a hard ceiling near 28 ticks per second | physics 26 ms of a 140 ms tick |
| "W1 + W2 + W3" reach 20–30 ticks per second | replacing physics alone gains at most about 1.2× |

## 7. What this suggests (for the owner; nothing here is decided)

1. The largest lever is the organism step itself: `deepcopy`, JSON work
   inside the step, and adaptive-sense eviction — the design's workstream
   "organism hot-path algorithms". It is pure Python, needs no new
   dependency, and the cut already removed the byte-equality constraint that
   blocked it.
2. Replacing PyBullet is justified by reasons other than speed — an engine
   that is maintained, exact and cheap body state, and removing the engine
   coupling from `modality` — and costs a recalibration of every body and
   contact parameter. On speed alone it would not be the first thing to do.
3. The state-section workstream needs a design revision before it starts.
4. Measure an older organism before committing: if the step cost grows
   steeply with age, the ordering may change again.

## 8. Limits

One organism, one age, short samples (24–64 ticks), a shared machine under
load, a profiler that inflates Python-heavy code relative to native calls.
The single 7.6 s file close was measured once and belongs to the end of the
run, not to each tick.

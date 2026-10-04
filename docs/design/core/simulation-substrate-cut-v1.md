# Simulation Substrate Cut v1

Status: **approved** by the project owner (2026-10-04). Implementation:
**pending**. Decisions: [ADR-0065](../../adr/ADR-0065-simulation-substrate-clean-cut.md)
(clean cut), [ADR-0066](../../adr/ADR-0066-mujoco-physics-engine-and-engine-independent-vision.md)
(engine and vision), [ADR-0067](../../adr/ADR-0067-revisioned-state-sections-and-passive-observation.md)
(state, observation, checkpoint encoding). Owner
question: if backward compatibility is dropped entirely, which parts of the
simulation substrate should be replaced, and what does each replacement buy?

Baseline inspected: `migration/five-domain-architecture @ f9ae63841` (working
tree with uncommitted migration changes). Cost figures are those of
[Simulation Throughput v1](simulation-throughput-v1.md) (`main @ d3dac186`,
one snapshot, one shared laptop). Nothing was re-profiled for this document.
Every speed-up below is an **estimate, not a measurement**, and §9 makes
measurement the first step.

Approval covers the design and the three decisions above. It does not launch
any experiment, and it does not replace the external review that SCIENTIFIC
and CONSTITUTIONAL changes take at publication. Work starts with step 0 of §9.
See [`register.md`](../register.md).

## 1. Premise

Owner decision (2026-10-04, ADR-0065): the change is a **clean cut**. No
backward compatibility, no legacy readers, no dual formats, no second backend
kept alive to reproduce old runs.

This removes the constraint that shaped Simulation Throughput v1: byte
equality of `runtime.json`, provenance journal and body state against the
previous code. It does not remove determinism. After the cut the system must
still be deterministic against **itself**.

## 2. Current reality

Measured (Simulation Throughput v1, §1), per tick:

| Component | Cost | Causal for the organism |
|---|---:|---|
| Rich telemetry (`deepcopy`, structural diff, binary encoding, episodic snapshots) | ≈ 4.5 s amortised, ≈ 90 % of wall time | no |
| Episodic memory (≈ 7 500 projections per tick) | ≈ 200 ms | yes |
| `deepcopy` in the step, evictions, hypotheses, signal claims, sensorimotor distances | ≈ 150 ms | yes |
| PyBullet (10 substeps at 240 Hz) | ≈ 36 ms | yes |

Observed in the source at the baseline:

- **Physics.** PyBullet is imported lazily from 12 files across `lab`,
  `embodiment`, `environment` and `modality`. About 40 distinct API functions
  are used. Geometry is primitives only (box, sphere, capsule, cylinder,
  plane) plus two URDF loads. Actuation is velocity and torque control.
  Connection mode is `DIRECT`. No soft bodies and no constraints.
- **Vision.** `modality/src/modality/vision.py` samples a `side × side`
  receptor array with `getCameraImage` and `ER_TINY_RENDERER` (software
  rendering inside PyBullet).
- **Telemetry.** `lab/physics3d/telemetry/v41.py` copies whole state mappings
  with `deepcopy` and `structural.py` computes keyed path deltas between
  copies. The writer runs behind `AsyncTelemetryWorker`, a thread, so it
  shares the GIL with the organism step.
- **Organism.** `symbiont` depends only on `cryptography`. State is nested
  Python mappings and slotted dataclasses (594 of 607 dataclasses use
  `slots=True`). `core/embodiment/memory.py` and `core/embodiment/transition.py`
  hold 33 and 24 `deepcopy` call sites.
- **Persistence.** Canonical JSON (`sort_keys`, compact separators) feeds the
  integrity hashes; telemetry is a bespoke binary format.
- **Boundaries.** An import-linter contract states that the organism imports
  no physics, tensor or imaging backend, and that the four domain libraries
  are mutually independent.

Gap worth recording: [ADR-0024](../../adr/ADR-0024-high-frequency-binary-telemetry-and-decimated-transport.md)
requires zero dynamic allocation on the hot execution path. The measured
telemetry path does not meet it.

## 3. Constraints that survive the cut

- **Determinism** (constitution §14, items 103–108): same seed, initial state
  and conditions give the same trajectory.
- **Observer passivity and cost separation** (items 99–102): telemetry adds no
  signal to the organism, does not stall its life, and apparatus cost stays
  distinguishable from organism cost.
- **Domain boundaries** (item 8 and the import-linter contracts): the organism
  stays free of physics, tensor and imaging backends.
- **Frozen evidence is not rewritten.** Dropping compatibility means old
  evidence stops being reproducible by current code; it does not mean editing
  or deleting it.
- **Governance class.** Every workstream changes organism trajectories or
  experience, so none can be ORDINARY under
  [ADR-0046](../../adr/ADR-0046-proportional-governance-equivalence-and-pinned-runs.md).

Preferences, not constraints: keeping `symbiont` dependency-free, keeping the
research code in Python, avoiding a second build toolchain.

## 4. Decision drivers

1. Throughput of a single organism, since parallel arms already scale with
   cores.
2. Scientific cost of re-establishing a baseline, paid once rather than per
   change.
3. Iteration speed on organism code, which changes weekly.
4. Determinism that can be checked mechanically.
5. Long-term maintenance of each dependency.

## 5. Proposed design

Five workstreams. W1–W3 are the proposal; W4 is conditional on measurement;
W5 follows from W1.

### W1. Organism state layout and passive observation

Decision record: ADR-0067.

**Problem.** The observer learns what changed by copying everything and
comparing copies. That is the dominant cost and it grows with organism age.

**Proposal.** The organism state is partitioned into sections, each with a
monotonically increasing revision that the owning domain bumps on mutation.
Sections are replaced, not mutated in place, so an observer holding a
reference to an old section holds a valid snapshot at zero copy cost. The
observer compares revisions and encodes only sections that changed.

- The organism does not know an observer exists. It publishes no events and
  takes no observer callbacks; revisions are part of its own state discipline.
- The step-internal `deepcopy` calls disappear for the same reason: a
  transactional step keeps the previous section reference instead of copying.
- Sections that are large and numeric (episodic store, sensorimotor
  statistics) move to flat buffers so that W4 and W5 have something to work
  on. Sections that are small and structural stay as dataclasses.

**Alternative considered: organism-emitted change events.** Cheaper to encode,
but the organism then carries observation logic in its vital loop, which
strains items 99 and 102. Rejected as the default; acceptable for a section
only if revision comparison proves too coarse.

**Alternative considered: keep copy-and-diff, run it in another process.**
Removes GIL contention but still pays serialisation of the whole state every
observation. Does not address growth with age.

**Unknown.** How far the existing state can be partitioned without touching
the atomic-step contract was not inspected. A bounded spike on one domain
precedes any commitment (see §9).

### W2. Physics and vision backend

Decision record: ADR-0066.

**Proposal.** Replace PyBullet with MuJoCo (CPU) outright. PyBullet is removed
from all 12 files; no second backend remains.

| Option | For | Against |
|---|---|---|
| **MuJoCo (CPU)** | Actively maintained, official Python bindings, deterministic, built for articulated bodies in contact. Full physical state is a few flat arrays, so body checkpoints are exact and cheap. Loads URDF. | Soft-contact model differs from Bullet: body and contact parameters need recalibration. Offscreen rendering needs an OpenGL context. |
| Rapier (Rust) | Bit-level cross-platform determinism mode. | No mature official Python bindings; a PyO3 layer would be ours to own. Articulated multibody is less exercised. |
| Jolt | Fast, deterministic. | Python bindings immature. |
| GPU batch engines (MJX, Warp, Brax, Isaac, Genesis) | Thousands of worlds in parallel. | The organism is one Python object per process and does not vectorise; physics would stop being the bottleneck without raising throughput. |
| Keep PyBullet | No recalibration. | Upstream development has largely stopped; wheel availability for future Python versions is a risk (not verified). |

**Vision.** Two options were considered:

1. MuJoCo's renderer. Least code; ties vision to an OpenGL context and to the
   engine.
2. An analytic ray caster over the primitive geometry, owned by `modality`.
   Deterministic, engine-independent and trivially testable; costs new code
   and only works while the world stays primitive.

Decided (ADR-0066): option 2, because it removes the last coupling between
`modality` and the physics engine and keeps headless runs free of GPU or
windowing requirements.

**Seam.** `embodiment/physics3d/contracts.py` already defines
`Physics3DAppliance` and `MotorPortPair`. The replacement lands behind that
seam; the organism side does not change.

### W3. Organism hot-path algorithms

With trajectory equivalence to the old code no longer required, the Level 1
list of Simulation Throughput v1 is implemented without its equivalence
harness, and may additionally change event order and float summation order:

- incremental episodic reinterpretation instead of re-projecting every
  episode on each record;
- indexed structures for adaptive-sense and signal-claim eviction;
- removal of step-internal copies (delivered by W1).

This stays pure Python. It is the cheapest change per unit of gain and it must
come before any native code: a native O(N)-per-record loop is still O(N).

### W4. Native kernels (conditional)

Only if profiling after W1–W3 shows the organism step still dominating.

**Proposal.** A small Rust extension (PyO3, built with maturin) holding
numeric kernels over the flat buffers from W1: episodic projection and
similarity, sensorimotor distances, and the telemetry encoder on the lab side.
`cryptography` already brings a Rust-built wheel into the dependency tree, so
this is not the first native component, but it is the first one built here.

| Option | For | Against |
|---|---|---|
| **Rust kernels over flat buffers** | Large constant-factor gain on tight loops; memory safety; releases the GIL for the telemetry encoder. | New build toolchain in CI; two languages; kernels must be deterministic across platforms (avoid fused multiply-add and fast-math, pin transcendental implementations). |
| mypyc on existing typed modules | No rewrite; Python semantics preserved; slotted dataclasses compile well. | Smaller gain, least on dict-heavy code. |
| Whole organism in Rust | Highest ceiling. | ≈ 63 k lines of organism code and ≈ 31 k lines of tests rewritten; research iteration slows. Not proposed. |
| NumPy/Numba/JAX inside `symbiont` | Fast on arrays. | Violates the "organism imports no tensor backend" contract. |

Recommendation: try mypyc first on the modules W3 leaves hot; adopt Rust only
for kernels where mypyc is not enough.

Where a native kernel lives must respect the import contract: organism
kernels ship inside `symbiont`; the telemetry encoder ships inside `lab`.

### W5. Persistence and telemetry formats

Follows from W1; not a goal in itself.

- **Checkpoint.** A canonical deterministic binary encoding replaces canonical
  JSON as the hashed representation. Section revisions from W1 let a
  checkpoint write only changed sections.
- **Telemetry.** Telemetry v4.1 is retired. The new stream is section
  snapshots keyed by revision, with a columnar export (Parquet) for analysis
  on the lab side.
- **Compression.** One codec for all new artifacts (zstd).

Old checkpoints and old telemetry are not readable by the new code.

## 6. Expected throughput

Estimates only. They assume the Simulation Throughput v1 cost table still
holds and that MuJoCo steps this body in a few milliseconds per tick, which
has not been measured here.

| Configuration | Step | Ticks/s, one organism |
|---|---:|---:|
| Today, default observation | ≈ 5 s | 0.19 (measured) |
| W1 + W2 + W3 | 30–50 ms | 20–30 |
| W1 + W2 + W3 + W4 | 10–20 ms | 50–100 |
| "Hundreds of ticks per second" | < 5 ms | needs most of the hot loop native |

The 28 ticks/s physics ceiling of Simulation Throughput v1 belongs to
PyBullet and goes away with W2; the organism step becomes the limit.

## 7. Consequences

**Positive.** Observation cost stops scaling with organism age. Physics stops
being a hard ceiling. Body checkpoints become exact arrays. `modality` loses
its engine dependency. ADR-0024 becomes true of the implementation.

**Negative.** Every prior quantitative result is non-reproducible by current
code. Body, contact, physiology and sensory thresholds need recalibration
under the new physics and renderer. Studies whose conclusions are still relied
upon must be rerun. W4 adds a build toolchain.

**Neutral.** Parallel arms and seeds keep using process pools. Torch stays
where it is, on the lab side.

## 8. Handling of prior evidence

- Tag the last commit that reproduces existing evidence before the first
  workstream merges, and record the tag in the changelog.
- Archived evidence stays in place, marked as belonging to the pre-cut regime.
- No conclusion is carried across the cut by argument. A claim holds in the
  new regime only after its study is rerun there.
- Interaction to resolve first:
  [Physics3D A7 Stability Gate v1](../embodiment/physics3d-a7-stability-gate-v1.md)
  is approved and partially implemented against PyBullet 3.2.7. W2 invalidates
  its apparatus. The owner decides whether A7 runs before the cut, is
  re-specified after it, or is closed as not assessable.

## 9. Sequence and gates

0. **Measure.** Re-profile at the current baseline; split the 36 ms physics
   figure into stepping, rendering and contact queries; spike W1 on one domain
   and W2 on the simplest body. Gate: the cost table in §2 is confirmed or
   replaced, and both spikes report feasibility.
1. **W1** — state sections, revisions, passive observer.
2. **W2** — MuJoCo and the vision sampler, then recalibration.
3. **W3** — hot-path algorithms.
4. **Profile again.** Gate for W4: organism step is the dominant cost and W3
   is exhausted.
5. **W4**, if the gate passes. **W5** lands with W1 and is finalised here.
6. **One new baseline.** Declare it once, at the end, and rerun the studies
   that matter once. Each workstream changes the regime; re-baselining after
   each would multiply the scientific cost.

Development is staged on a long-lived branch; `main` moves to the new regime
in one step at 6.

## 10. Validation

The old equivalence harness compares against code that no longer exists. It is
replaced by self-consistency properties:

- **Replay determinism.** Two runs from the same seed and initial state give
  byte-identical checkpoints, provenance and body state.
- **Save/restore transparency.** Run N ticks, versus run k, checkpoint,
  restore, run N−k: identical final state.
- **Observer passivity.** Full observation versus no observation: identical
  organism state. (Simulation Throughput v1 verified this for the current
  apparatus; it must hold for the new one.)
- **Cross-platform determinism** for any W4 kernel, on the CI platforms.
- **Throughput benchmarks** in CI for the step, the episodic record path and
  the telemetry encoder, so regressions are visible.

## 11. Non-goals

- Changing what the organism experiences beyond what the new physics and
  renderer force. Fewer substeps, cheaper vision or a simplified world remain
  Level 3 of Simulation Throughput v1 and stay out of scope.
- Vectorising the organism or running many organisms per process.
- Replacing torch, the HTTP server or the CLI.
- Any scientific claim. This is apparatus and substrate.

## 12. Decisions

Decided on 2026-10-04:

| Decision | Record |
|---|---|
| Clean cut, pre-cut evidence pinned and labelled, one re-baseline | ADR-0065 |
| MuJoCo (CPU) as the single engine; visual sampling by a ray caster owned by `modality` | ADR-0066 |
| Revisioned state sections, passive observation, binary canonical checkpoint | ADR-0067 |

Still open, for the owner:

1. Disposition of the A7 stability gate (§8).
2. Which studies are rerun for the new baseline.
3. Whether `symbiont` may carry a compiled extension. This is decided only if
   the W4 gate of §9 passes, and it needs its own ADR.

## 13. Relationships

- Decisions: ADR-0065, ADR-0066, ADR-0067 (linked in the header).
- Supersedes the Level 1 and Level 2 plan of
  [Simulation Throughput v1](simulation-throughput-v1.md) and its byte-equality
  admissibility rule for cut work; its measurements remain the cost baseline
  and its Level 3 exclusion is kept.
- Retires [Physics3D Telemetry v4.1](../telemetry/physics3d-telemetry-v4.1.md)
  at the cut (ADR-0067).
- Invalidates the apparatus of the
  [Physics3D A7 Stability Gate v1](../embodiment/physics3d-a7-stability-gate-v1.md)
  (ADR-0066); disposition open.
- Partially superseded ADRs: ADR-0009 decision 1 (hash basis), ADR-0011
  decision 3 (renderer identity), ADR-0024 decision 3 (delta derivation).
- Constrained by [ADR-0024](../../adr/ADR-0024-high-frequency-binary-telemetry-and-decimated-transport.md),
  [ADR-0046](../../adr/ADR-0046-proportional-governance-equivalence-and-pinned-runs.md)
  and the [constitution](../../governance/constitution.md).

## 14. Reconsider if

- Step 0 shows the cost table no longer holds (for example, Level 1 work has
  already landed).
- MuJoCo cannot reproduce stable contact for the existing bodies after
  recalibration.
- The organism becomes vectorisable, which would reopen the GPU batch engines.

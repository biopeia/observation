# ADR-0066 — MuJoCo as the single Physics3D engine and engine-independent visual sampling

- **Status:** Accepted
- **Date:** 2026-10-04
- **Decision owner:** project owner
- **Relates to:** Constitution item 8 and §14, ADR-0011, ADR-0035, ADR-0042, ADR-0055, ADR-0060, ADR-0063, ADR-0065, ADR-0067, [`docs/design/core/simulation-substrate-cut-v1.md`](../design/core/simulation-substrate-cut-v1.md), [`docs/design/embodiment/physics3d-a7-stability-gate-v1.md`](../design/embodiment/physics3d-a7-stability-gate-v1.md)
- **Scope:** Which rigid-body engine executes Physics3D bodies and environments after the cut, and which component owns visual sampling. It does not define body models, contact parameters or calibration values.

## Context

Physics3D runs on PyBullet. At `migration/five-domain-architecture @ f9ae63841`:

- PyBullet is imported lazily from 12 files in `lab`, `embodiment`,
  `environment` and `modality`. About 40 distinct API functions are used.
- Geometry is primitives (box, sphere, capsule, cylinder, plane) plus two URDF
  loads. Actuation is velocity and torque control. No soft bodies, no
  constraints. Connection mode is `DIRECT`.
- `modality/src/modality/vision.py` samples the receptor array through
  PyBullet's `getCameraImage` with `ER_TINY_RENDERER`. ADR-0011 decision 3
  requires the apparatus to use "the deterministic CPU renderer" and to depend
  only on simulation state.
- An import-linter contract forbids the organism from importing any physics,
  tensor or imaging backend. `embodiment/physics3d/contracts.py` defines the
  appliance seam (`Physics3DAppliance`, `MotorPortPair`).

Simulation Throughput v1 measured PyBullet at about 36 ms per tick (10
substeps at 240 Hz), which bounds one organism at about 28 ticks/s. That
figure was not split into stepping, rendering and contact queries.

PyBullet's upstream development has largely stopped. Availability of wheels
for future Python versions was not verified.

ADR-0065 removes the requirement to keep pre-cut trajectories reproducible on
current code, which is what previously made an engine change inadmissible.

## Decision drivers

- Step cost for one articulated body in contact.
- Determinism of stepping and of visual sampling.
- Maintenance and Python-version support of the dependency.
- Exact, cheap capture and restore of physical state.
- Domain independence: `modality` should not need the physics engine.

## Constraints

- Same seed, state and conditions give the same trajectory (item 103).
- The organism imports no physics, tensor or imaging backend.
- The four domain libraries stay mutually independent.
- ADR-0011: receptors are opaque, deliver bounded luminance only, sample once
  per cognition tick, and are fed by nothing from the presentation path.
- ADR-0035: one canonical somatic truth; the engine supplies mechanics, not a
  second physiological authority.

## Alternatives considered

**Engine.**

| Option | For | Against |
|---|---|---|
| MuJoCo (CPU) | Actively maintained; official Python bindings; deterministic stepping; designed for articulated bodies in contact; physical state is a small set of flat arrays; loads URDF. | Soft-contact model differs from Bullet's, so body and contact parameters are recalibrated; offscreen rendering needs an OpenGL context. |
| Rapier | Cross-platform bit-level determinism mode. | No mature official Python bindings, so a binding layer would be owned here; articulated multibody less exercised. |
| Jolt | Fast and deterministic. | Python bindings immature. |
| GPU batch engines (MJX, Warp, Brax, Isaac, Genesis) | Thousands of worlds in parallel. | The organism is one Python object per process and does not vectorise; throughput per organism would not rise. |
| Keep PyBullet | No recalibration; the approved A7 apparatus stays valid. | Keeps the measured ceiling; upstream largely inactive. |

**Visual sampling.**

| Option | For | Against |
|---|---|---|
| Analytic ray caster over primitive geometry, owned by `modality` | Deterministic by construction; no GPU or windowing requirement; `modality` no longer needs the engine; easy to test. | New code to own; valid only while world geometry stays primitive. |
| MuJoCo's renderer | No new sampling code. | Needs an OpenGL context in headless runs; ties `modality` to the engine; determinism across drivers must be established. |

## Decision

1. **MuJoCo (CPU) is the single Physics3D engine after the cut.** PyBullet is
   removed from every domain. No second engine is retained.
2. **The engine sits behind the existing appliance seam.** Bodies, motor ports
   and environments reach the engine only through the `embodiment` and
   `environment` Physics3D contracts. Nothing in `symbiont` changes its
   imports.
3. **Visual sampling is owned by `modality` and does not use an engine
   renderer.** The receptor array is sampled by a deterministic CPU ray caster
   that takes scene geometry and link poses as plain data. `modality` does not
   import the engine.
4. **The receptor contract of ADR-0011 is unchanged.** Opaque receptor ids,
   bounded luminance in `[0, 1]`, one sample per cognition tick, dependence on
   simulation state only, and the perceptual topology all stand. Only the
   identity of the renderer changes.
5. **Body state is captured as the engine's full physical state.** A body
   checkpoint restores the engine to the exact state it was saved from.

## Scope and non-goals

Not decided here: body descriptions (URDF retained or rewritten as MJCF),
solver settings, substep count, contact and friction values, luminance model
details, and the calibration protocol. Those belong to the implementation and,
where they change experience, to their own study.

This ADR does not change substep count or scene complexity to gain speed; that
remains excluded as Level 3 of Simulation Throughput v1. It does not introduce
GPU execution.

## Consequences

**Positive.** The engine-imposed ceiling of about 28 ticks/s is removed.
Body checkpoints become exact. `modality` loses its only engine dependency.
Headless runs need neither GPU nor display. The dependency is maintained.

**Negative.** All Physics3D trajectories change. Body, contact, physiology
and sensory thresholds are recalibrated. Luminance values differ from the
PyBullet renderer's, so visual acquisition evidence is pre-cut. The approved
Physics3D A7 stability gate was specified and probed against PyBullet 3.2.7;
its apparatus is invalidated and its disposition is an open owner decision.
The ray caster is new code to maintain.

**Neutral.** Torch, process-pool parallelism and the monitor's role are
unaffected, though the monitor's PyBullet GUI path is replaced.

## Risks

- MuJoCo may not give stable contact for the existing bodies after
  recalibration. Mitigation: a spike on the simplest body precedes the work.
- The expected step cost of a few milliseconds per tick is an estimate.
  Mitigation: measured in the same spike.
- World geometry may later stop being primitive, which the ray caster does not
  cover. That would reopen decision 3.

## Reversibility

Expensive after the cut: body calibration and post-cut evidence depend on the
engine. Decision 3 is the more reversible part, since the receptor contract
isolates the sampler.

## Validation

- Import-linter: `modality` and `symbiont` import no engine; domain
  independence holds.
- Replay determinism and save/restore transparency (ADR-0065) on every body.
- Sampler determinism: identical geometry and poses give identical luminance
  across the CI platforms.
- A stability check per body before any study is launched on it.

## Relationships

- Depends on ADR-0065.
- Partially supersedes ADR-0011 decision 3, for the identity of the renderer
  only. The rest of ADR-0011 remains authoritative.
- Related to ADR-0055 (Physics3D module layout) and ADR-0060 (environment
  responsibilities), which it does not alter.

## Reconsider if

- The spike shows unstable contact or no meaningful step-cost reduction.
- World geometry requires meshes or textures.
- The organism becomes vectorisable, which would make batch engines relevant.

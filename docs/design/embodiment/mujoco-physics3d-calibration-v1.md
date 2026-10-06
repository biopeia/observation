---
id: design.embodiment.mujoco-physics3d-calibration-v1
title: "MuJoCo Physics3D Apparatus Calibration v1"
document_type: design
domain: embodiment
status: approved
canonical: false
implementation_status: partial
language: en
---
# MuJoCo Physics3D Apparatus Calibration v1

**State:** bounded apparatus-calibration design approved by the project owner on
2026-10-05; not a frozen protocol.
Some source-level models and deterministic mechanical-contract tests are
implemented under ADR-0070. This proposal authorizes no parameter changes,
calibration runs, or scientific campaign.

## 1. Purpose and limits

Specify an owner-approved, reviewable calibration plan for the MuJoCo
Physics3D substrate and independent analytic vision ray caster introduced by
[ADR-0066](../../adr/ADR-0066-mujoco-physics-engine-and-engine-independent-vision.md).
The work assesses apparatus behavior and observability, not organism
competence, biological robustness, or equivalence with the retired PyBullet
apparatus. The closed A7 PyBullet protocol and its numerical settings are
historical and non-transferable.

ADR-0070 separately authorizes source-level hexapod and fixed-base robotic-arm
models plus deterministic mechanical-contract tests. The owner's approval of
this design covers the bounded apparatus-calibration plan only; it does not
authorize parameter changes, calibration runs, or experiments. Any later
scientific study requires its own reviewed and frozen protocol plus explicit
owner authorization. Calibration results must not be presented as scientific
outcomes. Do not tune the organism or its behavior to satisfy apparatus
checks.

## 2. Calibration contract to resolve before execution

Before selecting acceptance criteria, record for each body and scene:

- source revision, body descriptor and revision, software/dependency versions,
  seed, spawn state, timestep, gravity, solver/contact settings;
- declared inputs separately from effective compiled MuJoCo model values;
- geom/link geometry, mass and inertia, joint limits and damping, actuator
  settings, contact materials, and fixture/resource recipe;
- raw observations, artifacts, any candidate parameter set, and explicit
  disposition of each check.

The owner/reviewer must select body ordering, scenarios, tolerances, and
required observables before execution. This document intentionally specifies
no numeric acceptance thresholds. Missing observables or non-convergence are
reported as not evaluable; do not silently alter conditions after observing a
failure. Numerical settings and thresholds are protocol inputs, not defaults
to be inferred from the retired PyBullet gate or from the current software
defaults.

### Fixed-base robotic arm requirement

The planned robotic arm is a **fixed-base** embodiment: its root is anchored to
the world and is not a floating/free joint. Its six rotational axes actuate
only the articulated links; they must not translate or rotate the root. The
arm model and any later characterization must declare this base constraint
explicitly. This requirement does not select a mounting transform, link
geometry, actuator limits, tool/gripper, calibration scenario, or acceptance
threshold.

The current articulated-body implementation supports both fixed and floating
roots; the robotic-arm model selects `fixed_base=True` (ADR-0070). The fixed
root constraint and its mechanical-contract tests are implementation evidence
only. They do not establish calibrated arm behavior, apparatus validity, or
scientific evidence. Any calibration characterization must still declare the
body descriptor/revision and record the compiled root/joint structure in its
model audit.

### Candidate external reference for the arm

The UR5e is the recommended **reference candidate** for evolving the arm's
observer presentation and, later, its documented physical profile: its
manufacturer lists six rotating joints, 850 mm reach, 5 kg payload, 20.7 kg
weight, and a 149 mm footprint. This is a candidate for design comparison,
not a claim that `robotic-arm-v1` is UR5e-equivalent and not a selection of
calibrated inputs. The present arm dimensions, mass distribution, joint ranges
and actuators remain provisional; do not replace them with values inferred
from these summary specifications.

Before a future profile becomes a physics target, pin authoritative revisioned
source data for link transforms, masses/inertias, joint limits and actuator
dynamics, then complete the owner/reviewer protocol decisions below. A past
UR5e ROS-description mass issue was addressed by merged upstream PR #187; this
history is a reason to pin and audit the exact data revision, not evidence that
every current model source is wrong. No external meshes or dynamics are imported
by this design.

Sources: [UR5e manufacturer specifications](https://www.universal-robots.com/manuals/EN/HTML/SW5_19/Content/prod-usr-man/complianceUR5e/H_g5_sections/appendix_g5/tech_spec_sheet.htm),
[upstream UR5e mass correction PR #187](https://github.com/UniversalRobots/Universal_Robots_ROS2_Description/pull/187).

## 3. Stages for a separately authorized calibration

If a separate calibration protocol is reviewed, frozen and explicitly
authorized, its stages should be run independently with inputs and outputs
preserved:

1. **Model/effective-parameter audit.** Compare descriptor and material
   declarations with the compiled model and runtime readback. Resolve semantic
   mappings before interpreting a parameter as physically active.
2. **Passive body support and settling.** For each canonical body, record
   convergence, residual base/joint motion, posture, support/normal loads,
   contact count, penetration, and finite-state checks under a pinned scene.
3. **Isolated contact/material cases.** Exercise ground, resource, and
   representative fixture contacts with prescribed initial conditions. Record
   contact force/impulse, slip, rebound, penetration, and effective material
   values. Keep actuation checks separate from passive checks.
4. **Vision apparatus.** Use fixed poses and scenes with known geometry and
   albedos. Record per-ray hit/miss and range, luminance values and summaries,
   clipping, and deterministic output hashes; verify the contract's `[0,1]`
   luminance bounds. Keep receptor observations passive and out of organism
   inputs unless separately authorized.
5. **Per-body coverage and report.** Begin with an owner-selected simple body,
   then repeat the same bounded contract for every canonical body. Report
   source/effective values, deviations, raw artifacts, rejected candidates,
   reproducibility, limitations, and not-evaluable outcomes.

## 4. Known implementation gaps to resolve

Source audit indicates material declarations do not all map transparently to
effective simulator settings: restitution and some damping fields appear not
to be applied, while friction composition differs from the retired engine.
World observation exposes only a subset of material properties. The analytic
ray caster has deterministic unit-level checks, but durable per-receptor
telemetry is limited. These are audit findings, not authorization to change
runtime mappings or telemetry. Decide whether each is an intended contract,
instrumentation gap, or separately scoped implementation change before
calibration.

## 5. Owner/reviewer checklist for execution-protocol readiness

Before an execution protocol can be proposed for review, the owner/reviewer
should record a disposition for every item below. A blank or deferred item is
an open decision, not implied approval. Approval of this design makes the
bounded design authoritative; it does not freeze an execution protocol or
authorize a run.

1. **Scope and bodies:** select the first body, the canonical-body inventory
   and order, and whether all bodies use the same scenarios or require
   explicitly justified body-specific cases. Confirm that the fixed-base arm
   is tested as fixed-base and floating-root bodies retain their own contract.
2. **Model/effective-value audit:** enumerate each declaration to inspect and
   the compiled/runtime field that represents it; state which fields are
   expected to agree exactly, which are transformations, and which are not
   represented. Resolve or explicitly classify restitution, damping, friction
   combination, limits, actuator constraints, and solver/contact parameters.
3. **Passive support/settling:** select the scene, initial state, observation
   interval, convergence definition, residual-motion observables and
   owner-supplied tolerances. Separate an unevaluated/non-converged result from
   a pass or failure under the selected rule.
4. **Contact characterization:** define each ground/resource/fixture case,
   initial conditions and actuation (if any), and the observables used to
   characterize normal/tangential response, slip, rebound and penetration.
   Specify which checks are passive and which are driven; do not mix their
   interpretations.
5. **Vision characterization:** pin scene geometry, poses, receptor layout,
   albedos and lighting/background assumptions; define expected per-ray
   records and luminance summaries, clipping/finite checks, deterministic
   comparison method, and how the observations remain passive and outside
   organism inputs.
6. **Coverage and repetition:** state runs/repeats/seeds and whether repeats
   are exact replays or independent initializations; prescribe the comparison
   and report treatment for missing, invalid, divergent and non-deterministic
   artifacts.
7. **Disposition and change control:** specify who classifies a discrepancy
   as intended contract, instrumentation gap, implementation change, or
   not-evaluable result; require any parameter change to be separately
   reviewed, versioned and rerun under a new pinned configuration rather than
   silently changing conditions mid-run.
8. **Governance boundary:** identify the review/approval record for this
   bounded apparatus plan and explicitly state that the recorded design
   approval does not freeze a scientific protocol or authorize calibration
   execution or a scientific experiment. A later campaign requires its own
   reviewed/frozen protocol and explicit authorization.

### Owner disposition — 2026-10-06

The project owner accepted the following bounded preparation recommendations:

- The first descriptive stage is the existing owner-approved and frozen
  [Crawler Passive Characterization v1](crawler-passive-characterization-v1.md):
  canonical `crawler-v1`, flat ground, its pinned timestep/gravity and spawn
  conditions, two fresh constructions, and descriptive observations only.
  Reuse its exact protocol and authorization; this design does not extend
  either. No calibration run is authorized by this disposition.
- The complete read-only declared/effective inventory is recorded in
  [`lab/research/physics3d/mujoco-effective-model-audit.md`](../../../lab/research/physics3d/mujoco-effective-model-audit.md)
  with its machine-readable report. Keep `missing`, `implicit`, and
  `provisional` findings explicit. Do not add mappings, velocity clamps, or
  tune parameters in response to these findings.
- For this first descriptive stage, record effective compiled solver/contact
  values; do not change them or turn them into pass/fail requirements. The
  already-frozen crawler protocol's stop rule and parameters remain unchanged.
- The passive crawler/flat-ground contact observations remain descriptive.
  Driven contact/material cases, additional morphologies/environments, and
  vision characterization are deferred to separate scopes. Vision remains
  provisional and is not part of this first stage.
- No measured physical reference is currently specified. Accordingly, this
  stage is apparatus characterization only and supports no physical-fidelity
  or calibration claim. Any later empirical calibration needs an identified
  reference source, its own owner/reviewer decisions, and a separately
  reviewed/frozen protocol.

These dispositions close preparation only for reusing the existing crawler
characterization protocol. They do not freeze a broader calibration protocol
or authorize any additional run, parameter change, or scientific campaign.

### Owner-supplied numeric choices (intentionally unset here)

The owner/reviewer must provide and pin every numeric choice used in the
eventual plan, as applicable: timestep and substeps; gravity; integrator,
solver, solver iteration/tolerance and contact settings; body-specific spawn
pose and joint state; settling duration/window and convergence/residual
tolerances; contact-case geometry, approach speed/impact energy, actuation,
measurement interval and acceptable ranges; vision scene dimensions, receptor
sampling setup, albedo/light/background values and comparison tolerance;
repeat counts, seeds, replay horizon and any acceptance limits. The list is a
completeness prompt, not a recommendation or proposed value. Where a quantity
is descriptive only, say so and do not turn it into a threshold after seeing
results. Do not reuse A7/PyBullet values without a separately justified owner
decision; the old values are not transferable.

## 6. Evidence and artifact contract

Each scenario must have a machine-readable manifest that pins repository
revision, dirty/clean state, body descriptor and schema revision, MuJoCo and
Python/package versions, platform, seed, initial state, declared inputs,
effective compiled model settings, scenario configuration, and the exact
owner-approved criterion version. Keep declared and compiled values distinct:
MuJoCo compiles model descriptions into `mjModel`, while evolving state and
measurements live in `mjData`; the compiled representation is the source for
reporting what the simulator actually received. See the official
[MuJoCo XML reference](https://mujoco.readthedocs.io/en/stable/XMLreference.html)
and [API types reference](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html).

Preserve, at minimum, the source/configuration inputs; the compiled-model
inventory (including body/joint/geom identifiers, root mobility, timestep,
gravity/integrator/solver, masses/inertias, joint limits/damping, actuator
parameters and geom/contact settings); the selected `mjData` observables and
contact records at the declared sampling points; vision ray hit/miss/range and
luminance records; criterion-by-criterion outcome with observed values and
units; and an index mapping every planned case to artifacts. Record hashes
for immutable inputs and outputs, plus explicit missing-artifact reasons.
Distinguish source declarations, compiled/effective settings, runtime
measurements and reviewer interpretation in both schema and report.

MuJoCo's contact semantics make direct value comparison important: friction
coefficients and solver parameters are combined across contacting geoms using
engine-defined rules; the official [contact parameter documentation](https://mujoco.readthedocs.io/en/stable/modeling.html#contact-parameters)
describes these rules. Therefore do not infer pair behavior solely from either
geom's declaration; retain the actual contact parameters and relevant pair
identity used for each measurement.

### Non-numeric completeness criteria for review

This checklist assesses whether a later execution protocol is complete enough
to review, not whether the apparatus passes calibration. A review-ready protocol
must have: every owner choice above either filled in or explicitly deferred;
each scenario mapped to observables and artifact fields; each criterion
classified as owner-selected pass/fail, descriptive-only, or not-evaluable;
all bodies and required controls accounted for; evidence lineage and hashes
specified; and a named disposition path for deviations. No apparatus or
scientific success conclusion follows from satisfying these documentation
completeness conditions.

## 7. Governance and exit

Record the project owner's design approval (2026-10-05) under repository
governance. It covers only this bounded apparatus plan; it does not freeze an
execution protocol or authorize its execution, parameter changes, or a
scientific campaign. Record calibrated apparatus scope separately from any
later experiment and retain the historic A7 evidence unchanged.

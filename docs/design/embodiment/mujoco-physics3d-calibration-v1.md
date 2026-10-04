---
id: design.embodiment.mujoco-physics3d-calibration-v1
title: "MuJoCo Physics3D Apparatus Calibration v1"
document_type: design
domain: embodiment
status: proposed
canonical: false
implementation_status: not_started
language: en
---
# MuJoCo Physics3D Apparatus Calibration v1

**State:** exploratory apparatus-calibration proposal; not approved, frozen, or
implemented. It authorizes no parameter changes, runs, or scientific campaign.

## 1. Purpose and limits

Specify a reviewable calibration plan for the MuJoCo Physics3D substrate and
independent analytic vision ray caster introduced by
[ADR-0066](../../adr/ADR-0066-mujoco-physics-engine-and-engine-independent-vision.md).
The work assesses apparatus behavior and observability, not organism
competence, biological robustness, or equivalence with the retired PyBullet
apparatus. The closed A7 PyBullet protocol and its numerical settings are
historical and non-transferable.

This proposal does not authorize experiments. Any later scientific study
requires its own reviewed and frozen protocol plus explicit owner
authorization. Calibration results must not be presented as scientific
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
failure.

### Fixed-base robotic arm requirement

The planned robotic arm is a **fixed-base** embodiment: its root is anchored to
the world and is not a floating/free joint. Its six rotational axes actuate
only the articulated links; they must not translate or rotate the root. The
arm model and any later characterization must declare this base constraint
explicitly. This requirement does not select a mounting transform, link
geometry, actuator limits, tool/gripper, calibration scenario, or acceptance
threshold.

The current articulated-body implementation creates a free root joint
unconditionally. Supporting the arm therefore requires an explicit base
mobility contract while preserving the existing floating-base behavior of
current bodies. Before an arm model is added, implementation-level tests must
show that a fixed-root model has no free root joint, that root pose remains
unchanged under joint actuation, and that state export/restore and kinematic
observations work for both fixed- and floating-base models. These are
mechanical software-contract tests, not apparatus calibration or scientific
evidence. This design remains proposed; the requirement does not authorize
that implementation, parameter changes, calibration runs, or experiments.

## 3. Proposed staged work

Run stages independently and preserve their inputs and outputs:

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

## 5. Governance and exit

Classify and publish this design under the repository's scientific governance
process. A proposal approval, if granted, covers only this bounded apparatus
plan; it does not freeze a scientific protocol or authorize its execution.
Record calibrated apparatus scope separately from any later experiment and
retain the historic A7 evidence unchanged.

---
id: design.embodiment.crawler-passive-characterization-v1
title: "Crawler Passive Characterization v1"
document_type: design
domain: embodiment
status: proposed
canonical: false
implementation_status: not_started
language: en
---
# Crawler Passive Characterization v1

**State:** proposed exploratory apparatus characterization protocol. It is not
approved or frozen and authorizes no run, parameter change, or scientific claim.

## 1. Question and scope

Characterize whether the current crawler model can passively settle in the
current MuJoCo Physics3D scene and report its resulting support/contact
observables. This is a software-apparatus smoke characterization, not physical
calibration, locomotion evaluation, organism competence, or a comparison to the
retired PyBullet apparatus. No body, material, solver, or organism parameters
may be tuned in response to the observations.

Empirical physical calibration is out of scope: no physical reference
measurements are currently specified. MuJoCo's system-identification tooling
describes fitting simulated outputs against recorded sensor data; this protocol
has no such measured reference ([official documentation](https://github.com/google-deepmind/mujoco/blob/main/python/mujoco/sysid/README.md)).

## 2. Fixed conditions

- Body: canonical `crawler-v1`, built by the current `CrawlerPhysics` factory.
- Scene: fresh `PhysicsScene(timestep=1/240)` with standard ground and gravity
  `(0, 0, -9.81)`; use the repository defaults for all other scene/solver
  settings and record their effective compiled values.
- Initial condition: factory-provided spawn state; no additional perturbation,
  actuator input, environment resource, sensor feedback, or organism loop.
- Seeds: none; there is no stochastic input in this passive setup. Record the
  source commit, dependency versions, body descriptor, and model settings.
- Repeats: two independent fresh scene/body constructions under identical
  conditions. They are an apparatus reproducibility check, not independent
  biological replicates.

## 3. Procedure

1. Before stepping, archive declared descriptor/material inputs and effective
   compiled model values (timestep, gravity, body/joint/geom counts, masses,
   inertias, joint limits/damping, contact dimensions, friction, `solref`, and
   `solimp`). Record any declaration-to-runtime mapping discrepancy without
   repairing it.
2. Call the existing `settle_passive_body` with its unmodified defaults: at
   most 2400 steps; 48 consecutive stable samples; base linear speed at most
   0.025 m/s, base angular speed at most 0.05 rad/s, and joint displacement
   speed at most 0.08 rad/s. These are the implementation's operational stop
   rule, not evidence of physical validity.
3. If convergence is reported, collect 480 additional steps (2 simulated
   seconds) with effectors kept empty. If it does not converge, stop that
   replicate and report `not_evaluable` for the post-settle window; do not
   extend the budget or alter thresholds.
4. Repeat from a fresh construction once. Preserve the complete raw trace and
   per-step output for both replicates; do not select a favorable repeat.

## 4. Required observables and disposition

Record settling convergence, steps and residual velocities; joint positions and
velocities; base pose, velocity and displacement; center-of-mass height/drift;
ground-contact count and normal reaction; body weight and reaction/weight
ratio; maximum/mean ground penetration; peak base/joint velocities; and
finite-state checks. Include time series and summary statistics for the full
post-settle window, not just a final frame. Record artifacts and their hashes.

The protocol sets no physical pass/fail thresholds for these observations.
Report raw values and between-repeat differences descriptively. A run is
mechanically reportable only if its pinned inputs and required artifacts are
complete and numeric outputs are finite; otherwise mark it `not_evaluable`
with the reason. Do not infer that convergence, finite values, or repeat
similarity establish contact realism or calibration.

## 5. Governance and next gate

This protocol must receive the required external scientific review and explicit
owner approval, then be frozen with its execution revision before any run.
Execution requires separate explicit owner authorization and the repository's
`agentctl run` pinned-run workflow. Review or approval of this document alone
does not launch a run. Any later physical calibration, parameter fitting,
additional body, actuation, or scientific study requires its own scope and
evidence contract.

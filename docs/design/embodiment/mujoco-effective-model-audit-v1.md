---
id: design.embodiment.mujoco-effective-model-audit-v1
title: "MuJoCo Effective Model Audit v1"
document_type: design
domain: embodiment
status: implemented
canonical: false
implementation_status: complete
language: en
---

# MuJoCo Effective Model Audit v1

## 1. Purpose

Establish a complete, read-only mapping from Physics3D declarations to the
compiled MuJoCo model that actually governs simulation.

The audit answers:

> For every relevant physical declaration, what did MuJoCo actually compile,
> and is the relationship exact, transformed, runtime-enforced, implicit,
> missing, provisional, or mismatched?

It does **not** calibrate MuJoCo, alter parameters, compare trajectories with
PyBullet, or feed information to an organism. It is apparatus instrumentation.

Implementation:

- `lab/src/lab/physics3d/effective_model_audit.py`
- `lab/src/lab/physics3d/effective_model_audit_cli.py`
- `lab/tests/unit/lab/physics3d/test_effective_model_audit.py`
- `lab/tests/integration/test_physics3d_effective_model_audit.py`

## 2. Scope

The runner covers every canonical Physics3D morphology:

- `anthropomorphic-v6`
- `anthropomorphic-v6-vision`
- `crawler-v1`
- `asymmetric-v1`
- `hexapod-v1`
- `robotic-arm-v1`

and every canonical environment in `ENVIRONMENT_NAMES`.

Each scenario is built from a fresh `PhysicsScene`, canonical ground, canonical
environment recipe, physical resource and selected body. The final report is
read from `mjModel` and apparatus declarations without changing physical or
sensor state.

## 3. Source-to-effective classification

| Relation | Meaning |
|---|---|
| `exact` | Compiled value matches the declaration within tolerance. |
| `transformed` | A documented deterministic transformation exists. |
| `runtime` | Enforced by runtime mechanics rather than represented directly in `mjModel`. |
| `implicit` | Effective value comes from MuJoCo defaults or another undeclared source. |
| `missing` | A declared property has no active mapping. |
| `provisional` | Active value explicitly pending apparatus qualification. |
| `mismatch` | Compiled value contradicts the expected declared/transformed value. |

`mismatch` is an implementation failure. `missing`, `implicit` and
`provisional` are explicit unresolved contract surfaces and are reported, not
silently converted into behavior.

## 4. Effective model inventory

Every scenario records:

- scene options: timestep, gravity, integrator, solver, iterations, tolerances,
  cone, Jacobian mode, impedance ratio, density, viscosity, wind and magnetic
  field when available;
- bodies: id, stable name, mass, principal inertia, inertial position, DoF count
  and mocap binding;
- joints: id, stable name, type, limited flag, effective range, DOF damping,
  limit `solref` and `solimp`;
- geoms: id, stable name, owner, type, size, local position, complete friction
  vector, RGBA and collision masks.

## 5. Declared-vs-effective checks

### Scene

`timestep` and `gravity` must match exactly. Integrator, solver, iteration
counts, tolerances, contact cone, Jacobian mode and impedance ratio are reported
as `implicit` while they remain engine defaults. Governed runs still pin the
engine version; this is a contract-explicitness gap, not a claim that existing
runs are unreproducible.

### Joints

- anatomical range is deterministically inset by the existing mechanical guard
  and compared with `mjModel.jnt_range`;
- `passive_damping` must match effective DOF damping;
- `max_motor_torque` is `runtime` because `apply_effectors` bounds torque and
  writes `qfrc_applied` without a MuJoCo actuator;
- `max_velocity` is `missing/warning` because it remains declared but is not
  enforced by current MuJoCo dynamics;
- effective limit solver parameters are recorded from `mjModel`.

The audit does not add a velocity clamp.

### Segments

Declared mass must match `mjModel.body_mass`. Inertia is `transformed`: the
report preserves source geometry/origin alongside MuJoCo's compiled
principal-inertia representation.

### Materials

Body, ground and resource three-component MuJoCo friction vectors are compared
directly. Declared `restitution`, `linear_damping` and `angular_damping` are
reported as `missing/warning` because they currently have no active mapping.
The audit does not emulate former PyBullet semantics.

### Environment fixtures

Static recipes declare lateral friction only. The audit checks that component
and records torsional/rolling friction as `implicit/warning`. Moving visual-only
fixtures must compile with both collision masks disabled.

### Vision

The engine-independent analytic visual apparatus is inspected without sampling
it. Receptor-topology completeness is checked. Background luminance, ambient
fraction and light direction are recorded as `provisional/warning` pending
apparatus qualification.

## 6. Determinism and provenance

Each scenario report contains audit schema version, body kind, MuJoCo version,
Python/platform identity, complete compiled inventory, sorted findings, summary
counts and SHA-256 over canonical JSON.

The suite report contains the selected body/environment sets, every scenario,
aggregate counts and a suite SHA-256. These hashes establish report-content
identity; they do not replace governed-run provenance.

## 7. Command

Full canonical matrix:

```bash
python -m lab.physics3d.effective_model_audit_cli \
  --output lab/research/physics3d/mujoco-effective-model-audit.json
```

One morphology/environment:

```bash
python -m lab.physics3d.effective_model_audit_cli \
  --body crawler-v1 \
  --environment contact-garden-v1
```

Strict declared-vs-compiled gate:

```bash
python -m lab.physics3d.effective_model_audit_cli --fail-on-mismatch
```

`--fail-on-mismatch` exits `2` only for actual `mismatch` findings. Known
`missing`, `implicit` and `provisional` surfaces remain visible for owner
disposition instead of being hidden behind implementation choices.

## 8. Acceptance contract

Implementation is complete when:

1. every canonical body is auditable;
2. every canonical environment is auditable;
3. the complete body × environment matrix can be constructed;
4. masses, joint damping, ranges and active friction are checked against compiled truth;
5. solver/contact defaults are exposed;
6. declared-but-unmapped material fields are explicit;
7. unenforced joint velocity declarations are explicit;
8. fixture partial-friction semantics are explicit;
9. visual provisional constants are explicit;
10. no MuJoCo physical state or sensor state is mutated by the audit;
11. output is JSON serializable and deterministically hashed;
12. tests fail on actual source-to-compiled mismatches.

## 9. Explicit non-goals

This work does not choose physical values, restore PyBullet semantics, add
velocity clamps, map restitution, add per-link damping, alter friction
combination, change solver/integrator settings, change geometry, change vision
constants, claim apparatus calibration success, or claim biological/cognitive
validity.

Those decisions belong to subsequent Physics3D apparatus qualification using
this audit as its source-of-truth instrument.

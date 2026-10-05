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

The audit answers one question:

> For every relevant physical declaration, what did MuJoCo actually compile,
> and is the relationship exact, transformed, runtime-enforced, implicit,
> missing, provisional, or mismatched?

It does **not** calibrate MuJoCo, alter parameters, compare trajectories with
PyBullet, or feed information to an organism. It is apparatus instrumentation.

Implementation:

- `lab/src/lab/physics3d/effective_model_audit.py`
- `scripts/audit_mujoco_effective_model.py`
- `lab/tests/unit/lab/physics3d/test_effective_model_audit.py`

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
read from `mjModel` and `mjData` without changing physical state.

## 3. Source-to-effective classification

Every finding uses one of these relations.

| Relation | Meaning |
|---|---|
| `exact` | Compiled value matches the declaration within the audit tolerance. |
| `transformed` | A documented deterministic transformation exists between source and compiled value. |
| `runtime` | The declaration is enforced by runtime mechanics rather than represented directly in `mjModel`. |
| `implicit` | The effective value comes from MuJoCo defaults or another undeclared source. |
| `missing` | A declared property has no active mapping in the current apparatus. |
| `provisional` | The value is active but explicitly pending apparatus qualification. |
| `mismatch` | The compiled value contradicts the expected declared or transformed value. |

`mismatch` is an implementation failure. `missing`, `implicit` and
`provisional` are not automatically failures; they are explicit unresolved
contract surfaces.

## 4. Effective model inventory

Every scenario records the compiled model inventory required to reconstruct
what the simulator received:

### Scene options

- timestep;
- gravity;
- integrator;
- solver;
- iteration counts;
- solver tolerances;
- contact cone;
- Jacobian mode;
- impedance ratio;
- density;
- viscosity;
- wind;
- magnetic field, when exposed by the installed MuJoCo version.

### Bodies

- MuJoCo body id and stable name;
- mass;
- principal inertia;
- inertial-frame position;
- degree-of-freedom count;
- mocap binding.

### Joints

- id and stable name;
- joint type;
- limited flag;
- effective range;
- effective DOF damping;
- limit `solref`;
- limit `solimp`.

### Geometry

- id and stable name;
- owning body;
- geometry type;
- size;
- local position;
- full MuJoCo friction vector;
- RGBA;
- collision masks.

## 5. Declared-vs-effective checks

### 5.1 Scene

`timestep` and `gravity` must match exactly.

The active MuJoCo defaults for integrator, solver, iteration counts, tolerances,
cone, Jacobian and impedance ratio are recorded as `implicit` until an owner
makes them explicit apparatus contract values.

This is not a reproducibility claim failure: governed runs already pin the
package lock and engine version. It is a contract-explicitness gap.

### 5.2 Joint range

Canonical anatomical limits are transformed into mechanical limits by the
existing guard band. The audit independently recomputes that deterministic
transformation and compares it with `mjModel.jnt_range`.

Any disagreement is `mismatch/error`.

### 5.3 Passive damping

`JointSpec.passive_damping` must appear as the effective MuJoCo DOF damping.
Any disagreement is `mismatch/error`.

### 5.4 Motor torque

`JointSpec.max_motor_torque` is classified as `runtime`: the apparatus applies
bounded torque through `qfrc_applied`; no MuJoCo actuator is created.

### 5.5 Maximum velocity

`JointSpec.max_velocity` is classified as `missing/warning` because it is
present in source/URDF but is not enforced by current MuJoCo dynamics.

The audit does not add a clamp and does not decide whether the field should
become a physical mechanism or be renamed as descriptive metadata.

### 5.6 Segment mass and inertia

Declared segment mass must match `mjModel.body_mass`.

Inertia is recorded as `transformed`: source geometry and inertial origin are
converted through URDF and MuJoCo's compiled principal-inertia representation.
The report preserves both source values and the compiled inertia/frame values.

### 5.7 Body, ground and resource materials

The three active MuJoCo friction components are compared directly with the
source declarations.

The following currently declared fields are intentionally reported as
`missing/warning` because there is no active mapping:

- restitution;
- linear damping;
- angular damping.

The audit does not silently emulate their former PyBullet behavior.

### 5.8 Environment fixtures

Static fixture recipes declare one scalar `friction`; the implementation maps
that scalar only to MuJoCo lateral friction. The audit therefore reports:

- lateral friction as `exact` or `mismatch`;
- torsional and rolling friction as `implicit/warning`.

Kinematic visual-only sources must compile with both collision masks disabled.
Any violation is `mismatch/error`.

### 5.9 Vision

The engine-independent analytic visual apparatus is checked as a separate
apparatus surface. Its active luminance constants are reported as
`provisional/warning` pending qualification:

- background luminance;
- ambient fraction;
- light direction.

No visual observation is injected into an organism by this audit.

## 6. Determinism and provenance

Every per-scenario report includes:

- audit schema version;
- body kind;
- engine name and version;
- Python version;
- platform identity;
- complete compiled inventory;
- sorted findings;
- summary counts;
- SHA-256 over canonical JSON content.

The suite report additionally records:

- selected body set;
- selected environment set;
- every scenario report;
- aggregate counts;
- suite SHA-256.

The hash is evidence of report-content identity, not a replacement for governed
run provenance.

## 7. Command

Full matrix:

```bash
python scripts/audit_mujoco_effective_model.py \
  --output lab/research/physics3d/mujoco-effective-model-audit.json
```

One morphology/environment:

```bash
python scripts/audit_mujoco_effective_model.py \
  --body crawler-v1 \
  --environment contact-garden-v1
```

Strict declared-vs-compiled check:

```bash
python scripts/audit_mujoco_effective_model.py \
  --fail-on-mismatch
```

`--fail-on-mismatch` exits with status `2` only for actual `mismatch`
findings. It deliberately does not fail for known `missing`, `implicit` or
`provisional` surfaces because those require owner disposition rather than a
hidden implementation choice.

## 8. Acceptance contract

The implementation is complete when all of the following hold:

1. every canonical body can be audited;
2. every canonical environment can be audited;
3. the complete body × environment matrix is constructible;
4. compiled masses, joint damping, ranges and active friction are checked;
5. solver/contact defaults are exposed rather than hidden;
6. declared-but-unmapped material fields are explicit;
7. unenforced joint velocity declarations are explicit;
8. fixture partial-friction semantics are explicit;
9. visual provisional constants are explicit;
10. the audit does not mutate MuJoCo physical state;
11. the report is JSON serializable and deterministically hashed;
12. tests fail on actual source-to-compiled mismatches.

## 9. Explicit non-goals

This work does not:

- choose new physical parameter values;
- restore PyBullet semantics;
- add velocity clamps;
- add restitution;
- add per-link damping;
- change friction combination behavior;
- change solver or integrator settings;
- change body geometry;
- change visual luminance constants;
- claim apparatus calibration success;
- claim biological or cognitive validity.

Those decisions belong to the subsequent Physics3D apparatus-qualification
work, using this audit as its source-of-truth instrument.

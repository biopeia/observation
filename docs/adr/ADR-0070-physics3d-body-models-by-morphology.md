# ADR-0070 — Physics3D body models by morphology

- **Status:** Accepted
- **Date:** 2026-10-05
- **Decision owner:** project owner
- **Relates to:** ADR-0055, ADR-0066, ADR-0067, `docs/design/embodiment/mujoco-physics3d-calibration-v1.md`
- **Scope:** source-level Physics3D morphology models and deterministic mechanical-contract tests. This ADR does not approve apparatus calibration, select calibrated parameters, authorize a calibration run or scientific experiment, or claim locomotion/manipulation capability.

## Context

The Physics3D package already provides a shared articulated-body implementation and separate files for the anthropomorphic and four-legged crawler bodies. A combined alternative-body module had been split into morphology-specific crawler and asymmetric modules. The project now needs distinct hexapod and robotic-arm models without duplicating common mechanics or conflating their body-specific state contracts.

The project owner has separately requested that the crawler remain identified as four-legged, that a hexapod also be available, that each morphology be distinguishable by source file, and that the robotic arm have a fixed base. The proposed MuJoCo calibration design remains **Proposed** and does not authorize calibration or experiments.

## Decision

1. Each distinct Physics3D morphology has its own module under `embodiment.physics3d`; body-specific joint topology, geometry declarations, contact regions, and model identity live with that morphology. Shared engine behavior remains in `articulated.py` and shared mechanics types/constants remain in `mechanics.py`. `bodies.py` is the catalog/descriptor boundary, not the implementation home for multiple morphologies.

2. Add `hexapod.py` as `hexapod-v1`: six bilateral front/middle/rear legs, each with three revolute axes (coxa yaw and two pitch axes), totaling 18 motor DoF. Each leg includes distinct coxa, femur, tibia and passive foot links. The chosen dimensions and actuator values are provisional model inputs only.

3. Add `robotic_arm.py` as `robotic-arm-v1`: a six-revolute-axis serial arm with `fixed_base=True`, so its root is world-anchored and joint actuation moves only articulated links. Include a passive tool-flange link, not a gripper or task-level end-effector controller. The mounting transform, geometry and actuator values in this initial model are provisional structural inputs only.

4. Register both bodies through the existing `BodyDescriptor` contract, deriving opaque receptor and effector channel counts from each body specification. Human-readable morphology names remain apparatus/observer-side metadata; they do not become organism-side semantic labels.

5. Keep each body's state schema versioned and independent. A body-specific physical checkpoint or competence is not portable evidence for another morphology; any such use requires body-specific revalidation consistent with Constitution §§9–10.

6. Deterministic tests may validate URDF/model structure, DoF and channel counts, link presence, loading, root anchoring, settling, replay, and checkpoint restoration. These are software/mechanical-contract checks only. They do not establish calibration, physical realism, stable gait, reachability, manipulation, organism competence, or transfer.

## Alternatives considered

- **Keep adding morphologies to a combined alternative-bodies module.** Rejected: it obscures ownership and makes the requested per-body separation harder to maintain.
- **Duplicate the MuJoCo/articulated implementation for each body.** Rejected: it needlessly forks shared mechanics and increases the risk of inconsistent checkpoint and actuator behavior.
- **Treat 18 DoF as evidence of hexapod locomotion or six axes as evidence of useful manipulation.** Rejected: degree-of-freedom count is a structural property, not a capability result.
- **Select calibrated geometry or actuator parameters now.** Rejected: there is no approved calibration protocol or evidence supporting such claims; current values remain explicitly provisional.

## Consequences

- The catalog can expose the hexapod and fixed-base arm as distinct selectable bodies while shared mechanics remain centralized.
- Each body has its own schema identity and opaque channel surface; downstream consumers must use the descriptor rather than assume another body's dimensions.
- The fixed-base arm uses the existing generic fixed-root option; floating-root behavior for existing bodies remains unchanged.
- The calibration design remains Proposed. No calibration execution, experiment, organism change, or cross-body competence transfer is authorized by this ADR.

## Acceptance

The project owner accepted this bounded decision on 2026-10-05. Acceptance covers only the source-level morphology models and deterministic software/mechanical-contract tests described above. The governed CONSTITUTIONAL candidate still requires external review before promotion under repository policy.

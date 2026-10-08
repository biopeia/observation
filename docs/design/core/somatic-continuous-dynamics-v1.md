# Somatic Continuous Dynamics v1

**State:** Proposed / Implemented Candidate (Phase M2.1)  
**Date:** 2026-10-08  
**Scope:** Continuous, physical-duration-aware integration of thermal relaxation, fatigue recovery, and autonomous repair in the Living Body homeostatic controller.  
**Authority:** Subordinate to [Mathematical Foundations and Temporal Scales v1](mathematical-foundations-and-temporal-scales-v1.md) and [Temporal Scales and Clock Separation v1](temporal-scales-and-clock-separation-v1.md).  
**Non-goals:** Growth, senescence, reproduction, memory decay, recency, sensor maturity, controllability, and informational metrics remain outside M2.1.

---

## 1. Problem

Before M2, three somatic mechanisms advanced once per organism call with no explicit physical duration:

- thermal relaxation toward the constitutional setpoint;
- fatigue recovery;
- autonomous structural repair.

The equations therefore depended on scheduler-call count rather than the physical time represented by those calls.

The canonical Physics3D runtime already has a deterministic interval:

\[
\Delta t_p = `time_step` \times `physics_substeps_per_tick`
\]

with the historical default

\[
\Delta t_{\mathrm{ref}} = \frac{1}{240}\times 10 = \frac{1}{24}\;\mathrm{s}.
\]

M2.1 makes that interval an explicit Embodiment-owned input to somatic physiology. It is never exposed to Cognition.

## 2. Dimensional contract

| Quantity | Runtime representation | M2.1 interpretation |
| --- | --- | --- |
| `PhysicalDuration` | seconds | deterministic physical interval |
| `temperature` | normalized [0,1] | model state, not Celsius |
| `fatigue` | normalized [0,1] | dimensionless model state |
| `structural_integrity` | normalized [0,1] | dimensionless model state |
| `embodied_work` | non-negative interval quantity | current legacy converted physical-work cost; not relabelled as Joules |
| `thermal_relaxation_rate` | 0.02 | relaxation fraction over the reference interval |
| `fatigue_recovery_rate` | 0.02 | fatigue decrement over the reference interval |
| `autonomous_repair_rate` | 0.02 | integrity increment over the reference interval, subject to reserve |

M2.1 does not claim that normalized temperature is a physical temperature or that maintenance reserve is SI energy. The change is temporal, not a unit relabelling.

## 3. Ownership and data flow

\[
\boxed{\text{Physics3D / Embodiment owns }T_p}
\]

Physics3D computes the interval from substep duration and count and registers a typed `PhysicalDuration` through `OrganismRuntime.set_physical_duration_for_tick()` immediately before the organism cycle. The value is transient execution context consumed once by Physiology; it is not part of the cognitive `tick()` API.

Permitted:

\[
\text{Physics3D}\rightarrow\text{Orchestration carrier}\rightarrow\text{PhysiologyDomain}\rightarrow\text{HomeostaticController}
\]

Prohibited:

\[
T_p\not\rightarrow\text{Cognition}.
\]

`PhysicalDuration` is not checkpointed as acquired organism state. A new embodiment may legitimately provide a different physical integration interval.

For runtimes with no explicit physical apparatus, absence of a registered duration selects the historical reference interval, preserving pre-M2 behavior rather than introducing host wall time. `PrivateModelOrganismRuntime` requires no physical-time parameter and remains unaware of `PhysicalDuration`.

## 4. Mathematical migration

### 4.1 Thermal relaxation

Legacy:

\[
T_{n+1}=T_n+(T^*-T_n)r_T.
\]

Define

\[
k_T = -\frac{\ln(1-r_T)}{\Delta t_{\mathrm{ref}}}.
\]

Then:

\[
T_{\mathrm{relaxed}}(t+\Delta t)
=
T^*+(T(t)-T^*)e^{-k_T\Delta t}.
\]

This has the semigroup property and exactly reproduces the legacy relaxation step when the duration equals the reference interval.

### 4.2 Thermal forcing from embodied work

`embodied_work` is treated as an interval quantity with uniform forcing inside that interval. Let

\[
\phi(x)=\frac{1-e^{-x}}{x}.
\]

The work scale is

\[
S_W(\Delta t)=
\frac{\phi(k_T\Delta t)}
{\phi(k_T\Delta t_{\mathrm{ref}})}.
\]

Then

\[
T(t+\Delta t)=T_{\mathrm{relaxed}}(t+\Delta t)+g_T W S_W(\Delta t).
\]

At the historical reference interval, \(S_W=1\), preserving the legacy work contribution exactly.

### 4.3 Fatigue

The current recovery term is a fixed decrement rather than proportional relaxation. M2 preserves that semantics and converts it into a physical-time rate:

\[
F(t+\Delta t)
=
\operatorname{clip}_{[0,1]}
\left(
F(t)+g_F W-r_F\frac{\Delta t}{\Delta t_{\mathrm{ref}}}m_{\mathrm{rest}}
\right)
\]

where \(m_{\mathrm{rest}}=2\) while resting and \(1\) otherwise.

No exponential fatigue law is asserted without evidence.

### 4.4 Autonomous repair

\[
\Delta I
=
\min\left(
1-I,
r_I\frac{\Delta t}{\Delta t_{\mathrm{ref}}},
r_{I,\max}\frac{\Delta t}{\Delta t_{\mathrm{ref}}},
E_{\mathrm{available}}
\right).
\]

The maintenance ledger remains the limiting resource. M2.1 does not reinterpret it as SI energy.

## 5. Compatibility invariant

At

\[
\Delta t_p=\Delta t_{\mathrm{ref}}=\frac{1}{24}\;\mathrm{s}
\]

the migrated equations must reproduce the pre-M2 single-step result for thermal relaxation, thermal work forcing, fatigue gain/recovery, and autonomous repair.

This is migration equivalence, not biological calibration.

## 6. Gate G1 — Somatic substep invariance

Hold constant:

- initial `LivingBodyState`;
- total physical duration;
- total embodied-work amount and its rate profile;
- resting profile;
- initial metabolic reserve.

Execute the same somatic path with 4, 8, and 16 partitions of the same interval.

Acceptance for the isolated deterministic integrator:

\[
|T_A-T_B|,\;|F_A-F_B|,\;|I_A-I_B|\le 10^{-12}.
\]

This test intentionally excludes metabolism replenishment, cognition, ontogeny, and scheduler opportunity effects.

## 7. Implementation traceability

| Design item | Code | Evidence |
| --- | --- | --- |
| reference interval | `core/embodiment/physiology_config.py` | reference-equivalence test |
| physical-duration type | `core/embodiment/duration.py` | M1.1 fail-closed contract |
| duration carrier | `core/orchestration/runtime.py` | transient typed registration consumed once per cycle |
| physiology ownership | `core/domains/physiology.py` | only Homeostasis consumes duration |
| continuous equations | `core/embodiment/homeostasis.py` | M2 unit/G1 tests |
| Physics3D binding | `lab/physics3d/runtime.py` | duration = time_step × substeps |
| Gate G1 | `symbiont/tests/unit/core/test_somatic_continuous_m2.py` | reference equivalence + partition invariance |

## 8. Explicitly deferred

M2.1 does not change `aging_ticks`, `growth_rate_per_tick`, `senescence_start_ticks`, `senescence_rate_per_tick`, `waste_ticks`, reproduction gates, sensor maturity, social recency, predictive-credit horizons, or motor controllability.

## 9. Acceptance state

M2.1 may be promoted only when:

1. reference-duration compatibility passes;
2. Gate G1 partition invariance passes;
3. existing homeostasis/runtime suites remain green;
4. architecture-integrity confirms Cognition does not consume `PhysicalDuration`;
5. docs/governance validation passes;
6. external SCIENTIFIC review accepts the bounded evidence.

No broader physical-fidelity or biological-validity claim follows from those gates.

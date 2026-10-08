# Temporal Scales and Clock Separation v1

**State:** Reviewed / Implemented (Phase M1 Technical Baseline)  
**Date:** 2026-10-08  
**Scope:** Formal decoupling of temporal scales ($T_p, T_s, T_e, T_d$), elimination of overloaded `tick` semantics, and establishment of clock authority boundaries across the Symbiont organism runtime.  
**Authority:** Subordinate to [docs/governance/constitution.md](../../governance/constitution.md) and [docs/design/core/mathematical-foundations-and-temporal-scales-v1.md](mathematical-foundations-and-temporal-scales-v1.md).  
**Implementation State:** Implemented (Verified via G-M1.1–G-M1.7).

---

## 1. Executive Summary and Problem Statement

Phase M0 ([Mathematical Constants and Mechanisms Inventory v1](mathematical-constants-inventory-v1.md)) cataloged 76 active runtime constants and identified that the single identifier `tick` is overloaded across the codebase to mean four fundamentally distinct concepts:

1. **Physical continuous duration** ($T_p$): duration of physical simulation sub-steps and somatic dissipation ($\Delta t_p$ in seconds).
2. **Cycle / Scheduler iteration** ($T_s$): sequential integer execution step of the organism control loop (`OrganismRuntime.tick()`).
3. **Experiential event count** ($T_e$): effective observation count, evidence accumulation, and sensorimotor interaction opportunities.
4. **Developmental / Somatic history** ($T_d$): biological wear, metabolic turnover, and irreversible ontogenetic progression.

This conflation creates grave architectural and scientific failure modes:

- A change in simulation sub-stepping or scheduling cadence inadvertently accelerates or decelerates biological aging, Hebbian memory decay, and epistemic maturity.
- Somatic dissipation equations (Newton cooling, tissue repair) are discretized assuming an implicit $\Delta t_p = 1\text{ tick}$, violating physical invariance (Gate G1).
- Cognitive subsystems risk consuming raw physical durations or host wall-clock time, violating constitutional host isolation and cognitive causality.

### Cardinal Rule of Phase M1

$$\boxed{\text{M1 does not alter organism behavioral equations.}}$$
M1 is purely an **architectural typing, semantic boundary, and clock separation** milestone. If a refactoring changes temperature, fatigue, memory retention, prediction weights, or agency commitments, it has crossed into Phase M2, M3, or M4.

---

## 2. Operational Definitions of Temporal Scales

The organism recognizes four mutually incommensurable temporal scales, each with a single authoritative owner domain:

$$\begin{aligned}
T_p &\in \mathbb{R}^+ \quad [\text{seconds}] && \text{Physical duration; owned strictly by Embodiment / Physics apparatus} \\
T_s &\in \mathbb{N} \quad [\text{cycles}] && \text{Cycle / Scheduler step; owned by Organism Orchestration} \\
T_e &\in \mathbb{N} \quad [\text{observations}] && \text{Experiential evidence count; owned locally by perceptual and cognitive estimators} \\
T_d &\in \mathcal{S}_{\text{ontogeny}} && \text{Developmental state; owned by Living Body Physiology}
\end{aligned}$$

```mermaid
flowchart TD
    subgraph Host_Plane ["Host Plane (Non-Deterministic)"]
        WallTime["Host Wall Time (time.monotonic())"]
        HostTel["HostTelemetry.observe_tick()"]
        WallTime -.-> HostTel
    end

    subgraph Embodiment_Domain ["Embodiment Domain"]
        Tp["Physical Time Tp (Δtp seconds)"]
        Physics["MuJoCo / Physics3D Substrate"]
        Somatic["Constitutive Physiology (Thermal, Fatigue, Repair)"]
        Physics --> Tp
        Tp --> Somatic
    end

    subgraph Orchestration_Domain ["Orchestration Domain"]
        Ts["Cycle Step Ts (Integer Execution Loop)"]
        Loop["OrganismRuntime.tick()"]
        Limits["Consolidation & Replay Ceilings"]
        Loop --> Ts
        Ts --> Limits
    end

    subgraph Epistemic_Domain ["Perception & Cognition Domain"]
        Te["Experiential Count Te (Sample Opportunities)"]
        Sensors["Transducer Evidence & Normalizers"]
        Credit["Predictive Credit (EWMA / Weighting)"]
        Graph["Hebbian Traces & Plastic Edges"]
        Te --> Sensors
        Te --> Credit
        Te --> Graph
    end

    subgraph Somatic_Domain ["Living Body State"]
        Td["Developmental State Td (Cumulative Work & Senescence)"]
        Ontogeny["Growth & Senescence State"]
        Td --> Ontogeny
    end

    %% Prohibitions
    WallTime x-.-x|PROHIBITED| Loop
    Tp x-.-x|CONSTITUTIONAL BARRIER| Epistemic_Domain
    Ts x-.-x|SEPARATION| Te
```

### 2.1 Physical Duration ($T_p$)
- **Definition:** The continuous metric time elapsed in the physical environment.
- **Unit:** Physical seconds $[\text{s}]$ ($\Delta t_p$).
- **Authority:** Strictly owned by **Embodiment**.
- **Constitutional Boundary:** **Strictly prohibited inside Cognition.** The cognitive graph, concept formation, prospective agency, and social relations must never inspect $T_p$, clock frequencies, or wall time. Cognition operates purely on causal sequences and experiential opportunities.

### 2.2 Cycle Step ($T_s$)
- **Definition:** The discrete integer iteration of the organism control cycle.
- **Unit:** Non-negative integers $[\text{cycles}]$.
- **Authority:** Strictly owned by **Organism Orchestration** (`OrganismRuntime`).
- **Semantics:** Monotonically increasing counter of scheduler evaluations. Governs operational cadence: structural graph consolidation intervals, episodic replay batch triggering, and checkpoint synchronization.

### 2.3 Experiential Count ($T_e$)
- **Definition:** The discrete count of actual empirical samples, transductions, or interaction opportunities observed by a specific subsystem or receptor.
- **Unit:** Integer sample count $[\text{samples}]$.
- **Authority:** Owned locally by **Perception, Sensory Systems, and Cognitive Estimators**.
- **Semantics:** $T_e \neq T_s$. A dormant or unobserved sensor experiences $\Delta T_s > 0$ while its experiential count remains $\Delta T_e = 0$. Epistemic estimators (prediction gain, credit assignment, confidence) update solely upon experiential arrival ($T_e$).

### 2.4 Developmental History ($T_d$)
- **Definition:** The irreversible ontogenetic, metabolic, and viability state of the living organism.
- **Unit:** Multidimensional biological state $\mathcal{S}_{\text{ontogeny}}$ (not a simplistic scalar clock).
- **Authority:** Owned strictly by **Living Body Physiology** (`core/embodiment/physiology.py`).
- **Architectural Boundary:** **No universal scalar `DevelopmentalTime` clock is introduced in M1.** Developmental maturity and senescence are derived somatic states shaped by cumulative metabolic work, structural wear, and tissue history. M1 formalizes the boundary; M2 and M4 will refine the specific ontogenetic estimators.

---

## 3. Subsystem Consumption and Authority Boundaries

| Subsystem | Physical $T_p$ | Cycle Step $T_s$ | Experiential $T_e$ | Developmental $T_d$ | Host Wall Time |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Physics / Embodiment** | **OWNER** (rw) | Consumer (ro) | Prohibited | Consumer (ro) | Prohibited |
| **Living Body Homeostasis** | Consumer (ro) | Consumer (ro) | Prohibited | **OWNER** (rw) | Prohibited |
| **Metabolism & Energy** | Consumer (ro) | Consumer (ro) | Prohibited | Consumer (ro) | Prohibited |
| **Organism Orchestration** | Prohibited | **OWNER** (rw) | Prohibited | Consumer (ro) | Prohibited |
| **Sensory Transducers** | Prohibited | Consumer (ro) | **OWNER** (rw) | Consumer (ro) | Prohibited |
| **Predictive Credit Assignment** | Prohibited | Prohibited | **OWNER** (rw) | Prohibited | Prohibited |
| **Cognitive Graph (Hebbian)** | Prohibited | Consumer (ro) | **OWNER** (rw) | Prohibited | Prohibited |
| **Prospective Deliberation** | Prohibited | Consumer (ro) | Consumer (ro) | Prohibited | Prohibited |
| **Social & Cultural Relations** | Prohibited | Consumer (ro) | **OWNER** (rw) | Prohibited | Prohibited |
| **Host Telemetry Adapter** | Prohibited | Prohibited | Prohibited | Prohibited | **OWNER** (isolated) |

### 3.1 Forensic Trace of Special Clocks
1. **Host Wall Time (`time.monotonic()`):**
   - *Current Path:* In [`core/orchestration/runtime.py:2187`](../../../symbiont/src/symbiont/core/orchestration/runtime.py#L2187), `tick_start = time.monotonic()` is computed and passed down to [`core/domains/lifecycle.py:191`](../../../symbiont/src/symbiont/core/domains/lifecycle.py#L191) to compute `tick_latency`.
   - *Consumer Audit:* `tick_latency` is passed exclusively to `self._host_telemetry.observe_tick(tick_latency)` in [`sensory/interoception.py:73`](../../../symbiont/src/symbiont/sensory/interoception.py#L73).
   - *Verification:* It is **never** stored in organism state, **never** exposed as an interoceptive percept, and **never** influences deterministic state. M1 formally locks this isolation: wall time remains strictly confined to host telemetry profiling.
2. **`IDLE_GRACE_TICKS = 20` in Host Self-Model:**
   - *Current Path:* [`core/cognition/host_self_model.py:27`](../../../symbiont/src/symbiont/core/cognition/host_self_model.py#L27).
   - *Consumer Audit:* Computed as `idle_ticks = max(0, current_tick - state.last_observed_tick)` (lines 131, 140, 172).
   - *Finding:* Despite the label "IDLE", this is **not** host wall time. It is literally the count of organism scheduler cycles ($T_s$) since a host capability was last sampled. M1 renames this semantically to `UNOBSERVED_CYCLES_GRACE` to prevent false wall-time inferences.

---

## 4. Forensic Classification Matrix of Current `tick` Usages

Every temporal usage across `symbiont/src/symbiont/` is classified into:

$$\text{CURRENT CLOCK} \longrightarrow \text{SEMANTIC DOMAIN} \longrightarrow \text{ALLOWED OWNER} \longrightarrow \text{M1 ACTION}$$

Where allowed `M1 ACTION` is strictly one of:
- `PRESERVE`: Valid usage of the scale; retain as canonical.
- `RENAME`: Valid semantic scale, but currently mislabeled as `tick`.
- `TYPE`: Encapsulate with explicit typed domain primitive.
- `ISOLATE`: Enforce architectural barrier preventing outward leakage.
- `DEFER_TO_M2`: Physical/somatic continuous formulation deferred to Phase M2.
- `DEFER_TO_M3`: Decay and memory kernel reformulation deferred to Phase M3.
- `DEFER_TO_M4`: Statistical maturity and epistemic estimator deferred to Phase M4.
- `REMOVE_HOST_TIME_LEAK`: Eradicate non-deterministic host timing from deterministic logic.

| Module & Location | Current Symbol / Usage | Real Semantic Domain | Allowed Owner | M1 Action | Rationale / Target Resolution |
| :--- | :--- | :--- | :--- | :--- | :--- |
| [`runtime.py:2161`](../../../symbiont/src/symbiont/core/orchestration/runtime.py#L2161) | `OrganismRuntime.tick()` | Scheduler execution cycle | Orchestration | `TYPE` | Represent cycle step as explicit `CycleStep` ($T_s$). |
| [`runtime.py:2187`](../../../symbiont/src/symbiont/core/orchestration/runtime.py#L2187) | `tick_start = time.monotonic()` | Host profiler wall clock | Host Telemetry | `ISOLATE` | Retain strictly inside host profiling; prohibit export to deterministic organism state. |
| [`homeostasis.py:108`](../../../symbiont/src/symbiont/core/embodiment/homeostasis.py#L108) | `constitutive_step()` | Somatic continuous advance | Embodiment | `DEFER_TO_M2` | Somatic integration must take $\Delta t_p$ in M2; M1 documents the interface requirement without altering Euler steps yet. |
| [`physiology_config.py:40`](../../../symbiont/src/symbiont/core/embodiment/physiology_config.py#L40) | `aging_ticks = 16` | Chronological ontogenetic cadence | Physiology | `DEFER_TO_M2` | Conflates $T_s$ with ontogeny; defer replacement by metabolic/turnover state to M2. |
| [`physiology_config.py:45`](../../../symbiont/src/symbiont/core/embodiment/physiology_config.py#L45) | `senescence_start_ticks = 2048` | Biological senescence onset | Physiology | `DEFER_TO_M2` | Uses $T_s$ for somatic degradation; defer to M2 somatic wear integration. |
| [`physiology.py:129`](../../../symbiont/src/symbiont/core/embodiment/physiology.py#L129) | `LivingBodyState.age_ticks` | Biological body lifespan | Physiology | `TYPE` / `ISOLATE` | Body-local biological cycle count ($T_s^{\text{body}}$), independent of Symbiont persistent tick; preserve behavior and defer replacement by continuous wear state to M2. |
| [`limits.py:20`](../../../symbiont/src/symbiont/cognition/limits.py#L20) | `consolidation_interval_ticks = 32` | Structural graph maintenance cadence | Cognition | `PRESERVE` | Legitimate usage of $T_s$; keep as cycle interval. |
| [`structure.py:474`](../../../symbiont/src/symbiont/cognition/structure.py#L474) | `edge.age_ticks` | Tentative edge lifespan | Cognition | `PRESERVE` | Edge lifecycle age in $T_s$ (`edge.age_ticks += 1` on each lifecycle check); defer co-activation opportunity count to M4. |
| [`sensor.py:30`](../../../symbiont/src/symbiont/sensory/sensor.py#L30) | `sensor.age_ticks` | Transducer sample history | Sensory | `DEFER_TO_M4` | Increments only when readings exist across all sources (`system.py:295`). Epistemic maturity proxy; defer replacement by sample count $N_{\text{eff}}$ to M4. |
| [`sensor.py:157`](../../../symbiont/src/symbiont/sensory/sensor.py#L157) | `self.age_ticks / 16.0` | Heuristic maturity factor | Sensory | `DEFER_TO_M4` | Conflates registration cycles with epistemic confidence; defer to M4. |
| [`predictive_credit.py:11`](../../../symbiont/src/symbiont/sensory/predictive_credit.py#L11) | `_SELECTION_FORGETTING = 0.97` | Geometric weight discount per step | Sensory | `DEFER_TO_M3` | Defer unification with continuous $\tau$ to M3; in M1 classify as experiential step ($T_e$). |
| [`predictive_credit.py:69`](../../../symbiont/src/symbiont/sensory/predictive_credit.py#L69) | `effective_weight` accumulation | Observation arrival event | Sensory | `TYPE` | Explicitly classify as experiential arrival count $T_e$ (`EvidenceCount`). |
| [`host_self_model.py:27`](../../../symbiont/src/symbiont/core/cognition/host_self_model.py#L27) | `IDLE_GRACE_TICKS = 20` | Cycles without observation | Host Self-Model | `RENAME` | Rename to `UNOBSERVED_CYCLES_GRACE` ($T_s$) with backward-compatible alias `IDLE_GRACE_TICKS`; not host wall-time. |
| [`relations.py:40`](../../../symbiont/src/symbiont/core/social/relations.py#L40) | `freshness(current_tick, half_life=32.0)` | Social evidence recency | Social Ledger | `DEFER_TO_M3` | Actual calculation is $T_s$ (`current_tick - last_tick`); intended candidate is experiential recency $T_e?$. Defer continuous $\tau$ to M3. |
| [`culture.py:1274`](../../../symbiont/src/symbiont/modeling/culture.py#L1274) | `freshness(current_tick, half_life=32.0)` | Cultural composite retention | Modeling | `DEFER_TO_M3` | Actual calculation is $T_s$; intended candidate is experiential recency $T_e?$. Defer continuous $\tau$ to M3. |
| [`telemetry.py:183`](../../../symbiont/src/symbiont/modeling/telemetry.py#L183) | `max_age_ticks` | Telemetry buffer capacity | Telemetry | `RENAME` | Rename to `retention_cycles` ($T_s$) with backwards-compatible alias and serialization support for `max_age_ticks`. |

---

## 5. Architectural Typing and Boundary Plan for M1

Rather than creating a monolithic `foundation/time.py` that erroneously puts physical duration into the Symbiont core, M1 enforces the boundary where the concepts live:

### 5.1 Orchestration & Scheduling ($T_s$)
- **Domain:** `symbiont.core.orchestration`
- **Type Primitive:** `CycleStep(int)` (immutable, non-negative integer wrapper preventing accidental arithmetic with physical seconds or float rates).
- **Semantics:** Replaces untyped `int` in scheduling loops, consolidation intervals, and cycle-based checkpoints.

### 5.2 Perception & Evidence Arrival ($T_e$)
- **Domain:** `symbiont.sensory` and `symbiont.cognition`
- **Type Primitive:** `EvidenceCount(int)` / `SampleCount(int)`.
- **Semantics:** Represents discrete counts of empirical observations, transductions, and prediction evaluations. Independent of scheduler clock speed.

### 5.3 Physical Duration ($T_p$)
- **Domain:** `symbiont.core.embodiment`
- **Type Primitive:** Stays strictly in Embodiment. Cognition and Foundation do not import or see $T_p$.
- **Semantics:** Explicitly represents physical time steps $\Delta t_p$ in seconds for physical simulation and somatic dynamics (preparing for Phase M2).

### 5.4 Developmental State ($T_d$)
- **Domain:** `symbiont.core.embodiment.physiology`
- **Semantics:** No premature universal scalar `DevelopmentalTime` is created. `LivingBodyState` retains somatic viability attributes without pretending that biological development is a scalar counter.

---

## 6. Phase M1 Gate and Invariant Criteria

The M1 milestone is closed only when all seven invariants pass technical verification:

| Invariant Gate | Formal Condition | Verification Method |
| :--- | :--- | :--- |
| **G-M1.1: Cognitive Isolation** | $T_p \not\rightarrow \text{Cognition}$ | Static AST import check asserting no module in `symbiont.cognition` imports physical duration or physics interfaces. |
| **G-M1.2: Host Non-Leakage** | $\text{host wall-time} \not\rightarrow \text{organism state}$ | Determinism regression test asserting identical trajectory across arbitrary synthetic CPU sleep delays. |
| **G-M1.3: Scale Separation** | $T_s \neq T_e$ | Contract test demonstrating that idling cycles ($\Delta T_s > 0$) with zero observations do not advance $T_e$. |
| **G-M1.4: Checkpoint Continuity** | Separated persisted markers retain exact values and types across their owning serialization boundaries. | Organism checkpoint roundtrip for $T_s$ and body-local biological cycles plus `PairwisePredictiveEvidence` checkpoint roundtrip for typed $T_e$. |
| **G-M1.5: Deterministic Replay** | Identical deterministic configuration and input history produce identical checkpoints and tick traces. | Independent-run equality under identical deterministic setup. This bounded gate does not claim universal quantification over every possible seed. |
| **G-M1.6: Bounded Equation Preservation** | Behavior-bearing equations touched by M1 retain their pre-M1 numerical semantics. | Numerical regression over predictive-credit accumulation and renamed grace-period semantics; broader causal equivalence remains a separate governed evidence suite. |
| **G-M1.7: Semantic Equivalence & Backwards Compatibility** | Typed primitives preserve primitive JSON representation and legacy aliases remain unambiguous. | Roundtrip tests plus fail-closed rejection of contradictory legacy/new telemetry retention fields. |

---

## 7. Traceability Matrix and Verification Evidence

All seven Phase M1 invariant gates have been implemented and verified via automated contract tests in [`tests/unit/core/test_temporal_scales_m1.py`](../../../symbiont/tests/unit/core/test_temporal_scales_m1.py):

| Gate Code | Gate Name | Target Mechanism / Invariant | Verification Test | Status | Evidence Summary |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **G-M1.1** | Cognitive Isolation | $T_p \not\rightarrow \text{Cognition}$ | `test_g_m1_1_cognitive_isolation_ast` | **PASSED** | Static AST inspection across all modules in `symbiont.cognition` and `symbiont.core.cognition` confirms zero imports of `PhysicalDuration`, `duration`, `mujoco`, or `physics3d`. |
| **G-M1.2** | Host Non-Leakage | $\text{wall-time} \not\rightarrow \text{state}$ | `test_g_m1_2_host_non_leakage_across_synthetic_delays` | **PASSED** | Trajectories run under arbitrary synthetic host CPU sleep delays produce bitwise-identical checkpoints (`assert ckpt1 == ckpt2`). |
| **G-M1.3** | Scale Separation | $T_s \neq T_e$ | `test_g_m1_3_scale_separation_cycle_vs_experiential` | **PASSED** | Advancing scheduler cycles ($T_s$) with zero sensor observations leaves `PairwisePredictiveEvidence.observations` ($T_e$) strictly stationary at 0 until observations arrive. |
| **G-M1.4** | Checkpoint Continuity | Persisted temporal markers preserve exact value/type at their owning boundary | `test_g_m1_4_checkpoint_continuity_separated_scales` | **PASSED** | Organism checkpoint roundtrip preserves $T_s$ and $T_s^{\text{body}}$; predictive-evidence checkpoint roundtrip preserves typed $T_e$ as `EvidenceCount`. |
| **G-M1.5** | Deterministic Replay | Identical deterministic configuration/input $\Rightarrow$ identical result | `test_g_m1_5_deterministic_replay_trace_equality` | **PASSED** | Independent runs under the same deterministic setup produce identical checkpoints. No universal all-seeds claim is made by this gate. |
| **G-M1.6** | Bounded Equation Preservation | Touched M1 behavior-bearing mechanisms preserve numerical semantics | `test_g_m1_6_zero_equation_drift` | **PASSED** | Predictive-credit accumulation remains the same geometric recursion and host grace remains exactly 20. Full causal-equivalence snapshots are governed separately. |
| **G-M1.7** | Semantic Equivalence & Backwards Compatibility | Primitive serialization remains stable; aliases are fail-closed when contradictory | `test_g_m1_7_semantic_equivalence_and_backwards_compatibility` + M1.1 alias-conflict tests | **PASSED** | Typed primitives serialize as native JSON numbers; legacy/new telemetry retention aliases roundtrip when equal and are rejected when contradictory. |

### Summary of Source-Level Implementation

1. **Embodiment Physical Duration ($T_p$):** Added [`symbiont.core.embodiment.PhysicalDuration`](../../../symbiont/src/symbiont/core/embodiment/duration.py), strictly confined to Embodiment.
2. **Orchestration Cycle Step ($T_s$):** Added [`symbiont.core.orchestration.CycleStep`](../../../symbiont/src/symbiont/core/orchestration/cycle.py) and typed `_tick_count` in [`OrganismRuntime`](../../../symbiont/src/symbiont/core/orchestration/runtime.py).
3. **Sensory Experiential Count ($T_e$):** Added [`symbiont.sensory.EvidenceCount`](../../../symbiont/src/symbiont/sensory/evidence.py) (and alias `SampleCount`), typed `PairwisePredictiveEvidence.observations` in [`symbiont.sensory.predictive_credit`](../../../symbiont/src/symbiont/sensory/predictive_credit.py).
4. **Host Self-Model Semantics:** Renamed `IDLE_GRACE_TICKS` to `UNOBSERVED_CYCLES_GRACE` with backward-compatible alias in [`symbiont.core.cognition.host_self_model`](../../../symbiont/src/symbiont/core/cognition/host_self_model.py).
5. **Telemetry Buffer Semantics:** Supported `retention_cycles` with bidirectional `max_age_ticks` serialization in [`symbiont.modeling.telemetry`](../../../symbiont/src/symbiont/modeling/telemetry.py).
6. **Living Body State Semantics:** Formalized Body-local biological cycle count ($T_s^{\text{body}}$) docstrings in [`LivingBodyState`](../../../symbiont/src/symbiont/core/embodiment/physiology.py).

---

## 8. M1.1 Temporal Contract Hardening

A post-M1 review identified that the initial nominal types and evidence wording were more permissive than the semantic boundary they were intended to enforce. M1.1 hardens the baseline without changing any behavioral equation.

### 8.1 Fail-closed temporal scalar construction

- `CycleStep` accepts only non-negative integer cycle counts. Boolean, string, and fractional inputs are rejected rather than silently coerced.
- `EvidenceCount` / `SampleCount` accept only non-negative integer observation counts. Boolean, string, and fractional inputs are rejected.
- `PhysicalDuration` accepts only finite numeric durations and rejects booleans, strings, NaN, infinities, and negative values.

These checks prevent cross-scale ambiguity from being hidden by Python numeric coercion.

### 8.2 Fail-closed telemetry migration alias

`CommunicationTelemetry` continues to accept legacy `max_age_ticks` and canonical `retention_cycles`, but when both are supplied they MUST carry the same value. Conflicting constructor arguments or checkpoint fields are rejected instead of selecting one silently.

### 8.3 Evidence-scope clarification

The focused M1 contract suite establishes the bounded invariants documented above. It does **not** by itself constitute the broader causal-equivalence suite across established, private-model, promotion, re-embodiment, and developed-cognition snapshots. Those governed equivalence snapshots remain a separate evidence surface and must not be inferred from G-M1.1–G-M1.7.

M1.1 therefore strengthens the implementation and narrows claims to the evidence actually exercised; it does not alter temperature, fatigue, memory decay, maturity, agency, or any M2–M4 equation.

Publication of M1.1 uses the repository's governed CI branch contract; the candidate branch must match an enabled `ci.yml` push prefix so validation is attached to the candidate SHA before review.

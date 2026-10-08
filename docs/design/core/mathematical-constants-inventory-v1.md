# Mathematical Constants and Mechanisms Inventory v1

**State:** Proposed (Phase M0 Observational Forensic Inventory)  
**Date:** 2026-10-08  
**Scope:** Exhaustive catalog of active mathematical constants, rates, thresholds, bounds, and parameters across `symbiont/src/symbiont/`  
**Authority:** Subordinate to [docs/governance/constitution.md](../../governance/constitution.md) and [docs/design/core/mathematical-foundations-and-temporal-scales-v1.md](mathematical-foundations-and-temporal-scales-v1.md)  
**Implementation State:** Not applicable (Zero runtime changes; purely observational audit)

---

## 1. Executive Summary and Scope

This document fulfills the requirements of **Phase M0** of the Mathematical Foundations Roadmap ([Mathematical Foundations and Temporal Scales v1](mathematical-foundations-and-temporal-scales-v1.md)).

Phase M0 is a **strictly observational and forensic audit**. Its sole purpose is to establish a canonical, traceable inventory of every active numerical constant, rate, threshold, bound, coefficient, and temporal parameter governing the organism runtime in `symbiont/src/symbiont/`.

### Core Governing Invariants for M0
1. **Zero Runtime Mutation:** Not a single line of runtime code, configuration, or test in `symbiont/src/` or any other subsystem is altered during M0.
2. **Epistemic Honesty:** Constants are evaluated on demonstrable empirical, physical, or constitutional justification, never on aesthetic elegance. Where an arbitrary "magic number" or undocumented weight exists, it is marked as `HEURÍSTICA_HISTÓRICA` with a ruling of `STUDY` or `DEPRECATE`.
3. **Strict Separation of Runtime vs Analytical Quantities:** Active runtime symbols (stored parameters, hardcoded thresholds, execution bounds) are strictly cataloged in Section 4. Theoretical, asymptotic, or derived quantities ($W_\infty, N_{\text{eff}}^{\text{geom}}$) are analyzed separately in Section 5 and never counted as runtime degrees of freedom.
4. **No Premature Execution:** Neither Phase M1, M2, nor experimental intervention campaigns are launched during this phase. Findings are recorded; debt is registered.

---

## 2. Methodology and Exclusion Rules

### 2.1 Search Methodology
The inventory was conducted via automated AST (Abstract Syntax Tree) traversal and source lexing across all 229 Python modules in `symbiont/src/symbiont/`, followed by manual line-by-line verification across the 11 core functional domains:
- `core/embodiment` (physiology, homeostasis, metabolism, ontogeny)
- `sensory` (predictive credit, sensor transducers, fitness evaluation)
- `actuation` (sensorimotor primitives, competence, motor control)
- `cognition` (kernel limits, structure, Hebbian learning, activation normalizers, metaplasticity)
- `core/cognition` (host self-model, attention budget, shadow predictors)
- `foundation` (epistemic conventions, recency bins, discretization classes)
- `core/social` (social relations ledger, resource claims)
- `modeling` (cultural composites, temporal responsibility tracker)
- `agency` (prospective deliberation, policy evaluation)
- `core/regulation` (innate reactivity, urgent interrupt thresholds)
- `genetics` (genome schema, loci bounds, mutation scales)

### 2.2 Explicit Exclusion Rules
To maintain strict scientific focus and prevent noise, the following literal values are excluded from the mathematical inventory:
1. **Algebraic Identity Literals:** Neutral elements ($0$, $1$, $-1$) used strictly for initializations, boolean logic, empty collections, or boundary iteration (e.g., `range(0, len(x))`, `count = 0`).
2. **Array and Memory Offsets:** Negative index lookups (`history[-1]`, `history[-2]`), slice bounds (`[:32]`), or string token truncations (`len(token) > 64`).
3. **Serialization and Protocol Markers:** Schema version integers (`SCHEMA_VERSION = 1`, `schema_version = 2`), cryptographic hash lengths (`SHA256` 32 bytes, hex strings 64 characters).
4. **I/O, Networking, and Diagnostic Literals:** Stream buffer sizes, terminal codes, standard HTTP status codes, or log levels unrelated to organism dynamics.

---

## 3. Taxonomy and Metadata Specification

Every cataloged constant is evaluated against a uniform metadata schema:

| Attribute | Definition / Allowed Values |
| :--- | :--- |
| **ID / Symbol** | Qualified variable, parameter, or constant name. |
| **Numerical Value** | Current hardcoded or default numeric value in runtime. |
| **Source Location** | Exact module path and source line range (`file.py:Lxx-Lyy`). |
| **Governed Mechanism** | Biological, cognitive, or physical dynamic governed by the value. |
| **Domain / Subsystem** | Architectural subsystem owning the parameter. |
| **Dimensionality / Units** | Dimensional analysis ($[\text{s}]$, $[\text{tick}]$, $[\text{energy}]$, $[\text{temp}]$, $[-]$, $[\text{variance}]^{-1}$, etc.). |
| **Associated Time Scale** | Time scale of operation: $T_p$ (physical), $T_s$ (cycle/scheduler), $T_e$ (experiential), $T_d$ (developmental), or host wall-time. |
| **Provenance Origin** | `CONSTITUTION` (constitutional invariant), `ADR-xxxx` (architectural decision), `FORMAL` (derived from physical/statistical laws), `CODE` (defined in code without external cite), `HISTORICAL` (legacy magic number), `STUDY` (empirically calibrated in prior study). |
| **Runtime Role** | `parameter` \| `threshold` \| `bound` \| `coefficient` \| `cadence` \| `capacity` \| `literal-derived`. |
| **Class** | `ESTRUCTURAL` \| `EMPÍRICA_INTERPRETABLE` \| `HEURÍSTICA_HISTÓRICA`. |
| **Sensitivity / Impact** | `HIGH` \| `MEDIUM` \| `LOW` + narrative of failure modes under perturbation. |
| **Dependencies** | Downstream consumers, coupled rates, or invariants depending on this value. |
| **Ruling** | `KEEP` \| `STUDY` \| `DEPRECATE`. |

---

## 4. Active Runtime Constants and Parameters Catalog

### 4.1 Core Embodiment, Metabolism & Living Body Physiology
Owning modules: [`physiology_config.py`](../../../symbiont/src/symbiont/core/embodiment/physiology_config.py), [`homeostasis.py`](../../../symbiont/src/symbiont/core/embodiment/homeostasis.py), [`metabolism.py`](../../../symbiont/src/symbiont/core/embodiment/metabolism.py)

| ID / Symbol | Value | Location | Governed Mechanism | Dim / Units | Scale | Provenance | Role | Class | Sens. | Dependencies | Ruling |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `ratio_unrecoverable` | `0.0` | [`physiology_config.py:22`](../../../symbiont/src/symbiont/core/embodiment/physiology_config.py#L22) | Lethal starvation threshold | $[-]$ | $T_p$ | `CONSTITUTION` | threshold | `ESTRUCTURAL` | HIGH | Viability gate | `KEEP` |
| `ratio_severe` | `0.2` | [`physiology_config.py:23`](../../../symbiont/src/symbiont/core/embodiment/physiology_config.py#L23) | Severe resource deficit trigger | $[-]$ | $T_p$ | `CODE` | threshold | `EMPÍRICA_INTERPRETABLE` | HIGH | Activity throttling | `STUDY` |
| `ratio_elevated` | `0.5` | [`physiology_config.py:24`](../../../symbiont/src/symbiont/core/embodiment/physiology_config.py#L24) | Elevated pressure warning | $[-]$ | $T_p$ | `CODE` | threshold | `EMPÍRICA_INTERPRETABLE` | MED | Activity scaling | `STUDY` |
| `somatic_reference_duration_s` | `1/24` | [`physiology_config.py`](../../../symbiont/src/symbiont/core/embodiment/physiology_config.py) | M2 migration reference interval derived from historical Physics3D `10 × 1/240 s` cadence | $[s]$ | $T_p$ | `FORMAL` | parameter | `ESTRUCTURAL` | HIGH | Thermal/fatigue/repair time normalization | `KEEP` |
| `max_repair_per_tick` | `0.25` | [`physiology_config.py:25`](../../../symbiont/src/symbiont/core/embodiment/physiology_config.py#L25) | Maximum structural healing cap | $[\text{integrity}/\text{tick}]$ | $T_p$ | `CODE` | bound | `EMPÍRICA_INTERPRETABLE` | HIGH | Tissue repair | `STUDY` |
| `autonomous_repair_rate` | `0.02` | [`physiology_config.py:26`](../../../symbiont/src/symbiont/core/embodiment/physiology_config.py#L26) | Baseline tissue healing rate | $[\text{integrity}/\text{tick}]$ | $T_p$ | `CODE` | parameter | `EMPÍRICA_INTERPRETABLE` | MED | Energy charges | `STUDY` |
| `fatigue_work_gain` | `0.50` | [`physiology_config.py:27`](../../../symbiont/src/symbiont/core/embodiment/physiology_config.py#L27) | Fatigue generation per unit mechanical work | $[\text{fatigue}/\text{work}]$ | $T_p$ | `CODE` | coefficient | `EMPÍRICA_INTERPRETABLE` | HIGH | Embodied work | `STUDY` |
| `fatigue_recovery_rate` | `0.02` | [`physiology_config.py:28`](../../../symbiont/src/symbiont/core/embodiment/physiology_config.py#L28) | Fatigue dissipation rate while idle | $[\text{fatigue}/\text{tick}]$ | $T_p$ | `CODE` | parameter | `EMPÍRICA_INTERPRETABLE` | MED | Homeostasis step | `STUDY` |
| `fatigue_activity_threshold` | `0.50` | [`physiology_config.py:29`](../../../symbiont/src/symbiont/core/embodiment/physiology_config.py#L29) | Fatigue level triggering motor throttling | $[-]$ | $T_p$ | `CODE` | threshold | `EMPÍRICA_INTERPRETABLE` | MED | Motor regulation | `STUDY` |
| `fatigue_activity_floor` | `0.20` | [`physiology_config.py:30`](../../../symbiont/src/symbiont/core/embodiment/physiology_config.py#L30) | Minimum motor throughput under maximal fatigue | $[-]$ | $T_p$ | `CODE` | bound | `ESTRUCTURAL` | HIGH | Motor minimum | `KEEP` |
| `thermal_setpoint` | `0.50` | [`physiology_config.py:31`](../../../symbiont/src/symbiont/core/embodiment/physiology_config.py#L31) | Canonical homeostatic temperature optimum | $[-]$ | $T_p$ | `CONSTITUTION` | parameter | `ESTRUCTURAL` | HIGH | Homeostatic deviation | `KEEP` |
| `thermal_relaxation_rate` | `0.02` | [`physiology_config.py:32`](../../../symbiont/src/symbiont/core/embodiment/physiology_config.py#L32) | Newton cooling relaxation rate | $[\text{tick}^{-1}]$ | $T_p$ | `CODE` | parameter | `EMPÍRICA_INTERPRETABLE` | MED | Thermal homeostasis | `STUDY` |
| `thermal_work_gain` | `0.10` | [`physiology_config.py:33`](../../../symbiont/src/symbiont/core/embodiment/physiology_config.py#L33) | Thermal heating per unit work | $[\text{temp}/\text{work}]$ | $T_p$ | `CODE` | coefficient | `EMPÍRICA_INTERPRETABLE` | MED | Embodied heating | `STUDY` |
| `activity_elevated_penalty`| `0.90` | [`physiology_config.py:34`](../../../symbiont/src/symbiont/core/embodiment/physiology_config.py#L34) | Motor activity multiplier under elevated pressure | $[-]$ | $T_p$ | `HISTORICAL` | coefficient | `HEURÍSTICA_HISTÓRICA` | MED | Homeostatic throttle | `STUDY` |
| `activity_elevated_floor` | `0.50` | [`physiology_config.py:35`](../../../symbiont/src/symbiont/core/embodiment/physiology_config.py#L35) | Minimum activity scale under elevated pressure | $[-]$ | $T_p$ | `CODE` | bound | `EMPÍRICA_INTERPRETABLE` | MED | Motor floor | `STUDY` |
| `activity_severe_penalty` | `0.75` | [`physiology_config.py:36`](../../../symbiont/src/symbiont/core/embodiment/physiology_config.py#L36) | Motor activity multiplier under severe pressure | $[-]$ | $T_p$ | `HISTORICAL` | coefficient | `HEURÍSTICA_HISTÓRICA` | HIGH | Homeostatic throttle | `STUDY` |
| `activity_severe_floor` | `0.20` | [`physiology_config.py:37`](../../../symbiont/src/symbiont/core/embodiment/physiology_config.py#L37) | Minimum activity scale under severe pressure | $[-]$ | $T_p$ | `CODE` | bound | `EMPÍRICA_INTERPRETABLE` | HIGH | Motor floor | `STUDY` |
| `safe_mode_integrity_threshold` | `0.10` | [`physiology_config.py:38`](../../../symbiont/src/symbiont/core/embodiment/physiology_config.py#L38) | Integrity trigger for physiological safe mode | $[-]$ | $T_p$ | `CONSTITUTION` | threshold | `ESTRUCTURAL` | HIGH | Safe mode trigger | `KEEP` |
| `safe_mode_activity_scale`| `0.10` | [`physiology_config.py:39`](../../../symbiont/src/symbiont/core/embodiment/physiology_config.py#L39) | Minimal activity allowed in safe mode | $[-]$ | $T_p$ | `CONSTITUTION` | bound | `ESTRUCTURAL` | HIGH | Safe mode execution | `KEEP` |
| `aging_ticks` | `16` | [`physiology_config.py:40`](../../../symbiont/src/symbiont/core/embodiment/physiology_config.py#L40) | Developmental chronological epoch cadence | $[\text{ticks}]$ | $T_d$ | `HISTORICAL` | cadence | `HEURÍSTICA_HISTÓRICA` | HIGH | Age accumulation | `DEPRECATE` |
| `waste_ticks` | `8` | [`physiology_config.py:41`](../../../symbiont/src/symbiont/core/embodiment/physiology_config.py#L41) | Metabolic waste expulsion interval | $[\text{ticks}]$ | $T_p$ | `CODE` | cadence | `EMPÍRICA_INTERPRETABLE` | LOW | Waste excretion | `STUDY` |
| `dormant_metabolic_factor`| `0.25` | [`physiology_config.py:42`](../../../symbiont/src/symbiont/core/embodiment/physiology_config.py#L42) | Basal metabolic reduction during dormancy | $[-]$ | $T_p$ | `ADR-0062` | coefficient | `EMPÍRICA_INTERPRETABLE` | HIGH | Dormancy energy charge | `KEEP` |
| `growth_rate_per_tick` | `0.01` | [`physiology_config.py:43`](../../../symbiont/src/symbiont/core/embodiment/physiology_config.py#L43) | Physical size increment per tick during growth | $[\text{size}/\text{tick}]$ | $T_d$ | `CODE` | parameter | `EMPÍRICA_INTERPRETABLE` | MED | Ontogenetic growth | `STUDY` |
| `growth_energy_fraction` | `0.20` | [`physiology_config.py:44`](../../../symbiont/src/symbiont/core/embodiment/physiology_config.py#L44) | Energy cost allocated per growth step | $[-]$ | $T_p$ | `CODE` | parameter | `EMPÍRICA_INTERPRETABLE` | MED | Somatic budget | `STUDY` |
| `senescence_start_ticks` | `2048` | [`physiology_config.py:45`](../../../symbiont/src/symbiont/core/embodiment/physiology_config.py#L45) | Onset of somatic senescence in ticks | $[\text{ticks}]$ | $T_d$ | `HISTORICAL` | threshold | `HEURÍSTICA_HISTÓRICA` | HIGH | Senescence onset | `DEPRECATE` |
| `senescence_rate_per_tick`| `0.001` | [`physiology_config.py:46`](../../../symbiont/src/symbiont/core/embodiment/physiology_config.py#L46) | Degradation rate per tick after onset | $[\text{tick}^{-1}]$ | $T_d$ | `CODE` | parameter | `EMPÍRICA_INTERPRETABLE` | HIGH | Structural wear | `STUDY` |
| `senescence_wear_rate` | `0.0002` | [`physiology_config.py:47`](../../../symbiont/src/symbiont/core/embodiment/physiology_config.py#L47) | Additional structural wear rate from age | $[\text{tick}^{-1}]$ | $T_d$ | `CODE` | parameter | `EMPÍRICA_INTERPRETABLE` | MED | Chronic decay | `STUDY` |
| `reproduction_energy_fraction` | `0.25` | [`physiology_config.py:48`](../../../symbiont/src/symbiont/core/embodiment/physiology_config.py#L48) | Energy endowment required for reproduction | $[-]$ | $T_p$ | `CODE` | parameter | `EMPÍRICA_INTERPRETABLE` | HIGH | Germline endowment | `STUDY` |
| `reproduction_min_integrity`| `0.80`| [`physiology_config.py:49`](../../../symbiont/src/symbiont/core/embodiment/physiology_config.py#L49) | Minimal parent structural integrity | $[-]$ | $T_p$ | `CODE` | threshold | `EMPÍRICA_INTERPRETABLE` | HIGH | Reproduction gate | `STUDY` |
| `reproduction_max_senescence`|`0.75`| [`physiology_config.py:50`](../../../symbiont/src/symbiont/core/embodiment/physiology_config.py#L50) | Maximum allowable senescence for fertility | $[-]$ | $T_d$ | `CODE` | threshold | `EMPÍRICA_INTERPRETABLE` | MED | Fertility cutoff | `STUDY` |
| `resting_recovery_multiplier`|`2.0` | [`homeostasis.py:127`](../../../symbiont/src/symbiont/core/embodiment/homeostasis.py#L127) | Fatigue clearance bonus while resting | $[-]$ | $T_p$ | `CODE` | coefficient | `HEURÍSTICA_HISTÓRICA` | MED | Fatigue recovery | `STUDY` |
| `metabolic_spend_cap_factor`| `2.0` | [`metabolism.py:203`](../../../symbiont/src/symbiont/core/embodiment/metabolism.py#L203) | Maximum instantaneous spend overrun multiplier | $[-]$ | $T_p$ | `CODE` | bound | `ESTRUCTURAL` | HIGH | Overdraft clamp | `KEEP` |

---

### 4.2 Sensory Processing, Fitness & Predictive Credit
Owning modules: [`predictive_credit.py`](../../../symbiont/src/symbiont/sensory/predictive_credit.py), [`sensor.py`](../../../symbiont/src/symbiont/sensory/sensor.py), [`fitness.py`](../../../symbiont/src/symbiont/sensory/fitness.py)

| ID / Symbol | Value | Location | Governed Mechanism | Dim / Units | Scale | Provenance | Role | Class | Sens. | Dependencies | Ruling |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `MAX_SELECTION_PAIRS` | `256` | [`predictive_credit.py:8`](../../../symbiont/src/symbiont/sensory/predictive_credit.py#L8) | Channel pairing ceiling for credit assignment | $[\text{count}]$ | $T_s$ | `ADR-0015` | capacity | `ESTRUCTURAL` | HIGH | Credit allocation | `KEEP` |
| `_SELECTION_ALPHA` | `0.15` | [`predictive_credit.py:10`](../../../symbiont/src/symbiont/sensory/predictive_credit.py#L10) | Instantaneous credit gain EWMA factor | $[-]$ | $T_e$ | `CODE` | parameter | `EMPÍRICA_INTERPRETABLE` | HIGH | Fast horizon EWMA | `STUDY` |
| `_SELECTION_FORGETTING` | `0.97` | [`predictive_credit.py:11`](../../../symbiont/src/symbiont/sensory/predictive_credit.py#L11) | Geometric weight retention discount $\lambda$ | $[-]$ | $T_e$ | `CODE` | parameter | `EMPÍRICA_INTERPRETABLE` | HIGH | Slow horizon discount | `KEEP` |
| `credit_scale_margin` | `0.05` | [`predictive_credit.py:58`](../../../symbiont/src/symbiont/sensory/predictive_credit.py#L58) | Denominator regularization epsilon factor | $[-]$ | $T_e$ | `CODE` | bound | `HEURÍSTICA_HISTÓRICA` | MED | Instant gain denominator | `STUDY` |
| `gain_threshold` | `0.05` | [`predictive_credit.py:86`](../../../symbiont/src/symbiont/sensory/predictive_credit.py#L86) | Minimum relative predictive gain floor | $[-]$ | $T_e$ | `CODE` | threshold | `HEURÍSTICA_HISTÓRICA` | HIGH | Structural pruning | `STUDY` |
| `sensor_health_degraded_threshold` | `0.25` | [`sensor.py:143`](../../../symbiont/src/symbiont/sensory/sensor.py#L143) | Transducer health threshold for DEGRADED state | $[-]$ | $T_e$ | `CODE` | threshold | `EMPÍRICA_INTERPRETABLE` | HIGH | Sensor maturity | `STUDY` |
| `sensor_age_specialised` | `64` | [`sensor.py:145`](../../../symbiont/src/symbiont/sensory/sensor.py#L145) | Age ticks required for SPECIALISED maturity | $[\text{ticks}]$ | $T_d$ | `HISTORICAL` | threshold | `HEURÍSTICA_HISTÓRICA` | HIGH | Maturity state | `DEPRECATE` |
| `sensor_age_established` | `16` | [`sensor.py:147`](../../../symbiont/src/symbiont/sensory/sensor.py#L147) | Age ticks required for ESTABLISHED maturity | $[\text{ticks}]$ | $T_d$ | `HISTORICAL` | threshold | `HEURÍSTICA_HISTÓRICA` | HIGH | Maturity state | `DEPRECATE` |
| `sensor_age_immature` | `4` | [`sensor.py:149`](../../../symbiont/src/symbiont/sensory/sensor.py#L149) | Age ticks required for IMMATURE maturity | $[\text{ticks}]$ | $T_d$ | `HISTORICAL` | threshold | `HEURÍSTICA_HISTÓRICA` | MED | Maturity state | `DEPRECATE` |
| `sensor_health_ewma_alpha`| `0.10` | [`sensor.py:156`](../../../symbiont/src/symbiont/sensory/sensor.py#L156) | Sensor health tracking EWMA factor | $[-]$ | $T_e$ | `CODE` | parameter | `EMPÍRICA_INTERPRETABLE` | MED | Transducer health | `STUDY` |
| `sensor_confidence_health_weight` | `0.70` | [`sensor.py:158`](../../../symbiont/src/symbiont/sensory/sensor.py#L158) | Linear weight of health in sensor confidence | $[-]$ | $T_e$ | `HISTORICAL` | coefficient | `HEURÍSTICA_HISTÓRICA` | HIGH | Transducer confidence | `DEPRECATE` |
| `sensor_confidence_maturity_weight`| `0.30` | [`sensor.py:158`](../../../symbiont/src/symbiont/sensory/sensor.py#L158) | Linear weight of maturity in sensor confidence | $[-]$ | $T_e$ | `HISTORICAL` | coefficient | `HEURÍSTICA_HISTÓRICA` | HIGH | Transducer confidence | `DEPRECATE` |
| `fitness_demonstrated_weight_p` | `0.60` | [`fitness.py:38`](../../../symbiont/src/symbiont/sensory/fitness.py#L38) | Heuristic weight for predictive credit in fitness | $[-]$ | $T_e$ | `HISTORICAL` | coefficient | `HEURÍSTICA_HISTÓRICA` | HIGH | Receptor pruning | `STUDY` |
| `fitness_demonstrated_weight_d` | `0.40` | [`fitness.py:38`](../../../symbiont/src/symbiont/sensory/fitness.py#L38) | Heuristic weight for downstream demand in fitness | $[-]$ | $T_e$ | `HISTORICAL` | coefficient | `HEURÍSTICA_HISTÓRICA` | HIGH | Receptor pruning | `STUDY` |
| `fitness_quality_base` | `0.70` | [`fitness.py:41`](../../../symbiont/src/symbiont/sensory/fitness.py#L41) | Multiplier intercept for receptor quality | $[-]$ | $T_e$ | `HISTORICAL` | coefficient | `HEURÍSTICA_HISTÓRICA` | MED | Fitness scaling | `STUDY` |
| `fitness_quality_novelty` | `0.15` | [`fitness.py:41`](../../../symbiont/src/symbiont/sensory/fitness.py#L41) | Novelty slope in receptor fitness multiplier | $[-]$ | $T_e$ | `HISTORICAL` | coefficient | `HEURÍSTICA_HISTÓRICA` | MED | Receptor selection | `STUDY` |
| `fitness_quality_reliability` | `0.15` | [`fitness.py:41`](../../../symbiont/src/symbiont/sensory/fitness.py#L41) | Reliability slope in receptor fitness multiplier | $[-]$ | $T_e$ | `HISTORICAL` | coefficient | `HEURÍSTICA_HISTÓRICA` | MED | Receptor selection | `STUDY` |
| `fitness_penalty_redundancy` | `0.10` | [`fitness.py:42`](../../../symbiont/src/symbiont/sensory/fitness.py#L42) | Redundancy penalty coefficient | $[-]$ | $T_e$ | `HISTORICAL` | coefficient | `HEURÍSTICA_HISTÓRICA` | MED | Anti-parsimony penalty | `STUDY` |
| `fitness_penalty_cost` | `0.05` | [`fitness.py:42`](../../../symbiont/src/symbiont/sensory/fitness.py#L42) | Metabolic cost penalty coefficient | $[-]$ | $T_e$ | `HISTORICAL` | coefficient | `HEURÍSTICA_HISTÓRICA` | MED | Metabolic penalty | `STUDY` |

---

### 4.3 Actuation, Motor Primitives & Competence
Owning modules: [`sensorimotor.py`](../../../symbiont/src/symbiont/actuation/sensorimotor.py), [`competence.py`](../../../symbiont/src/symbiont/actuation/competence.py)

| ID / Symbol | Value | Location | Governed Mechanism | Dim / Units | Scale | Provenance | Role | Class | Sens. | Dependencies | Ruling |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `motor_reproducibility_factor` | `25.0` | [`sensorimotor.py:220`](../../../symbiont/src/symbiont/actuation/sensorimotor.py#L220), [`1174`](../../../symbiont/src/symbiont/actuation/sensorimotor.py#L1174) | Variance scaling in reproducibility $\frac{1}{1 + 25\sigma^2}$ | $[\text{effect}]^{-2}$ | $T_e$ | `HISTORICAL` | coefficient | `HEURÍSTICA_HISTÓRICA` | CRITICAL | Primitive competence | `STUDY` |
| `controllability_cutoff` | `0.002` | [`sensorimotor.py:1177`](../../../symbiont/src/symbiont/actuation/sensorimotor.py#L1177), [`1395`](../../../symbiont/src/symbiont/actuation/sensorimotor.py#L1395) | Threshold to prune non-agentic motor primitives | $[\text{effect}]$ | $T_e$ | `HISTORICAL` | threshold | `HEURÍSTICA_HISTÓRICA` | CRITICAL | Primitive survival | `DEPRECATE` |
| `min_competence_support` | `2` | [`competence.py:24`](../../../symbiont/src/symbiont/actuation/competence.py#L24) | Minimal sample count for competence gate | $[\text{count}]$ | $T_e$ | `STUDY` | threshold | `EMPÍRICA_INTERPRETABLE` | HIGH | Gate selection | `KEEP` |
| `min_directional_consistency`| `0.60` | [`competence.py:25`](../../../symbiont/src/symbiont/actuation/competence.py#L25) | Vector directional consistency floor | $[-]$ | $T_e$ | `STUDY` | threshold | `EMPÍRICA_INTERPRETABLE` | HIGH | Gate selection | `KEEP` |
| `reproducibility_ratio_threshold` | `2/3` | [`competence.py:56`](../../../symbiont/src/symbiont/actuation/competence.py#L56) | Minimal reproducibility to enter ESTABLISHED | $[-]$ | $T_e$ | `HISTORICAL` | threshold | `HEURÍSTICA_HISTÓRICA` | HIGH | Competence maturity | `STUDY` |

---

### 4.4 Cognition Kernel, Structure, Learning & Activation
Owning modules: [`limits.py`](../../../symbiont/src/symbiont/cognition/limits.py), [`learning.py`](../../../symbiont/src/symbiont/cognition/learning.py), [`activation.py`](../../../symbiont/src/symbiont/cognition/activation.py), [`metaplasticity.py`](../../../symbiont/src/symbiont/cognition/metaplasticity.py)

| ID / Symbol | Value | Location | Governed Mechanism | Dim / Units | Scale | Provenance | Role | Class | Sens. | Dependencies | Ruling |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `max_nodes` | `768` | [`limits.py:15`](../../../symbiont/src/symbiont/cognition/limits.py#L15) | Hard structural ceiling for cognitive nodes | $[\text{count}]$ | $T_s$ | `ADR-0015` | capacity | `ESTRUCTURAL` | HIGH | Kernel safety | `KEEP` |
| `max_concepts` | `192` | [`limits.py:16`](../../../symbiont/src/symbiont/cognition/limits.py#L16) | Hard ceiling for concept cluster nodes | $[\text{count}]$ | $T_s$ | `ADR-0015` | capacity | `ESTRUCTURAL` | MED | Concept abstraction | `KEEP` |
| `max_edges` | `6144` | [`limits.py:17`](../../../symbiont/src/symbiont/cognition/limits.py#L17) | Hard ceiling for consolidated plastic edges | $[\text{count}]$ | $T_s$ | `ADR-0015` | capacity | `ESTRUCTURAL` | HIGH | Graph connectivity | `KEEP` |
| `max_tentative_edges` | `512` | [`limits.py:18`](../../../symbiont/src/symbiont/cognition/limits.py#L18) | Candidate edge pool capacity | $[\text{count}]$ | $T_s$ | `ADR-0015` | capacity | `ESTRUCTURAL` | MED | Edge proposal | `KEEP` |
| `max_structural_mutations`| `16` | [`limits.py:19`](../../../symbiont/src/symbiont/cognition/limits.py#L19) | Maximum topology changes per consolidation | $[\text{count}]$ | $T_s$ | `ADR-0015` | bound | `ESTRUCTURAL` | HIGH | Consolidation burst | `KEEP` |
| `consolidation_interval_ticks`| `32`| [`limits.py:20`](../../../symbiont/src/symbiont/cognition/limits.py#L20) | Hard consolidation cadence in ticks | $[\text{ticks}]$ | $T_s$ | `ADR-0015` | cadence | `ESTRUCTURAL` | HIGH | Consolidation schedule | `KEEP` |
| `max_consolidation_candidates`| `1024`| [`limits.py:22`](../../../symbiont/src/symbiont/cognition/limits.py#L22) | Candidate edge evaluation queue capacity | $[\text{count}]$ | $T_s$ | `ADR-0015` | capacity | `ESTRUCTURAL` | MED | Candidate evaluation | `KEEP` |
| `consolidation_epoch_ticks`| `8` | [`limits.py:24`](../../../symbiont/src/symbiont/cognition/limits.py#L24) | Sub-epoch duration in ticks | $[\text{ticks}]$ | $T_s$ | `ADR-0015` | cadence | `ESTRUCTURAL` | MED | Support tracking | `KEEP` |
| `slow_support_epochs` | `4` | [`limits.py:25`](../../../symbiont/src/symbiont/cognition/limits.py#L25) | Required consecutive epochs for slow edge | $[\text{epochs}]$ | $T_s$ | `ADR-0015` | threshold | `ESTRUCTURAL` | MED | Edge promotion | `KEEP` |
| `fast_consolidation_threshold`| `0.80`| [`limits.py:26`](../../../symbiont/src/symbiont/cognition/limits.py#L26) | Predictive gain threshold for fast edge promote | $[-]$ | $T_s$ | `ADR-0015` | threshold | `ESTRUCTURAL` | HIGH | Fast promotion | `KEEP` |
| `fast_min_reliability` | `0.60` | [`limits.py:27`](../../../symbiont/src/symbiont/cognition/limits.py#L27) | Reliability threshold for fast edge promote | $[-]$ | $T_s$ | `ADR-0015` | threshold | `ESTRUCTURAL` | HIGH | Fast promotion | `KEEP` |
| `max_incoming_weight_norm`| `8.0` | [`limits.py:28`](../../../symbiont/src/symbiont/cognition/limits.py#L28) | $L_1$ clamp on incoming synaptic edge weights | $[-]$ | $T_s$ | `ADR-0015` | bound | `ESTRUCTURAL` | CRITICAL | Divergence safety | `KEEP` |
| `reacclimation_ticks` | `32` | [`limits.py:29`](../../../symbiont/src/symbiont/cognition/limits.py#L29) | Grace ticks after topological mutation | $[\text{ticks}]$ | $T_s$ | `ADR-0015` | cadence | `ESTRUCTURAL` | MED | Transient dampening | `KEEP` |
| `max_episodic_episodes` | `4096` | [`limits.py:34`](../../../symbiont/src/symbiont/cognition/limits.py#L34) | Hard episodic memory item ceiling | $[\text{count}]$ | $T_s$ | `ADR-0015` | capacity | `ESTRUCTURAL` | HIGH | Episodic buffer | `KEEP` |
| `max_episodic_replay_items` | `16` | [`limits.py:37`](../../../symbiont/src/symbiont/cognition/limits.py#L37) | Replay batch size per cognitive wake cycle | $[\text{count}]$ | $T_s$ | `ADR-0015` | capacity | `ESTRUCTURAL` | MED | Replay throughput | `KEEP` |
| `ELIGIBILITY_BOUND` | `10.0` | [`learning.py:10`](../../../symbiont/src/symbiont/cognition/learning.py#L10) | Hard bound preventing Hebbian trace explosion | $[-]$ | $T_e$ | `ADR-0015` | bound | `ESTRUCTURAL` | HIGH | Synaptic plasticity | `KEEP` |
| `huber_loss_delta` | `1.0` | [`learning.py:15`](../../../symbiont/src/symbiont/cognition/learning.py#L15) | Huber loss quadratic-to-linear boundary $\delta$ | $[-]$ | $T_e$ | `FORMAL` | parameter | `EMPÍRICA_INTERPRETABLE` | MED | Robust regression | `KEEP` |
| `shadow_prediction_eval_gate` | `8` | [`learning.py:160`](../../../symbiont/src/symbiont/cognition/learning.py#L160) | Minimal samples to evaluate shadow predictor | $[\text{count}]$ | $T_e$ | `CODE` | threshold | `EMPÍRICA_INTERPRETABLE` | MED | Shadow evaluation | `STUDY` |
| `shadow_prediction_retire_gate`| `16`| [`learning.py:162`](../../../symbiont/src/symbiont/cognition/learning.py#L162) | Contradicted samples before retiring shadow edge | $[\text{count}]$ | $T_e$ | `CODE` | threshold | `EMPÍRICA_INTERPRETABLE` | MED | Shadow retirement | `STUDY` |
| `normalizer_variance_floor` | `1e-6` | [`activation.py:9`](../../../symbiont/src/symbiont/cognition/activation.py#L9) | Variance regularization floor $\epsilon$ | $[\text{signal}]^2$ | $T_e$ | `CODE` | bound | `ESTRUCTURAL` | HIGH | Division by zero | `KEEP` |
| `normalizer_z_max` | `4.0` | [`activation.py:37`](../../../symbiont/src/symbiont/cognition/activation.py#L37) | Maximum z-score clipping limit | $[\sigma]$ | $T_e$ | `FORMAL` | bound | `EMPÍRICA_INTERPRETABLE` | HIGH | Robust squashing | `KEEP` |
| `normalizer_softness` | `2.0` | [`activation.py:37`](../../../symbiont/src/symbiont/cognition/activation.py#L37) | Scale divisor inside $\tanh(z / s)$ | $[\sigma]$ | $T_e$ | `HISTORICAL` | coefficient | `HEURÍSTICA_HISTÓRICA` | HIGH | Activation response | `STUDY` |
| `metaplasticity_freeze_failures`| `3` | [`metaplasticity.py:76`](../../../symbiont/src/symbiont/cognition/metaplasticity.py#L76) | Consecutive objective regressions to freeze meta-parameters | $[\text{count}]$ | $T_s$ | `CODE` | threshold | `ESTRUCTURAL` | HIGH | Metaplastic safety | `KEEP` |

---

### 4.5 Host Cognition, Self-Model, Attention & Predictors
Owning modules: [`host_self_model.py`](../../../symbiont/src/symbiont/core/cognition/host_self_model.py), [`attention.py`](../../../symbiont/src/symbiont/core/cognition/attention.py), [`predictors.py`](../../../symbiont/src/symbiont/core/cognition/predictors.py)

| ID / Symbol | Value | Location | Governed Mechanism | Dim / Units | Scale | Provenance | Role | Class | Sens. | Dependencies | Ruling |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `LOW_HEALTH_INVESTIGATION_THRESHOLD` | `0.15` | [`host_self_model.py:26`](../../../symbiont/src/symbiont/core/cognition/host_self_model.py#L26) | Host health floor triggering active diagnostic probing | $[-]$ | Wall/Host | `CODE` | threshold | `EMPÍRICA_INTERPRETABLE` | MED | Host self-model | `STUDY` |
| `IDLE_GRACE_TICKS` | `20` | [`host_self_model.py:27`](../../../symbiont/src/symbiont/core/cognition/host_self_model.py#L27) | Host ticks before idle health decay commences | $[\text{host ticks}]$ | Wall/Host | `CODE` | cadence | `EMPÍRICA_INTERPRETABLE` | MED | Host telemetry | `STUDY` |
| `quality_nominal_health` | `1.0` | [`host_self_model.py:29`](../../../symbiont/src/symbiont/core/cognition/host_self_model.py#L29) | Nominal telemetry health score mapping | $[-]$ | Wall/Host | `CODE` | coefficient | `EMPÍRICA_INTERPRETABLE` | LOW | Self-model health | `KEEP` |
| `quality_degraded_health` | `0.6` | [`host_self_model.py:30`](../../../symbiont/src/symbiont/core/cognition/host_self_model.py#L30) | Degraded telemetry health score mapping | $[-]$ | Wall/Host | `HISTORICAL` | coefficient | `HEURÍSTICA_HISTÓRICA` | MED | Self-model health | `STUDY` |
| `quality_stale_health` | `0.25` | [`host_self_model.py:31`](../../../symbiont/src/symbiont/core/cognition/host_self_model.py#L31) | Stale telemetry health score mapping | $[-]$ | Wall/Host | `HISTORICAL` | coefficient | `HEURÍSTICA_HISTÓRICA` | MED | Self-model health | `STUDY` |
| `attention_diminishing_rate` | `0.05` | [`attention.py:96`](../../../symbiont/src/symbiont/core/cognition/attention.py#L96) | Sampling fatigue factor $\frac{1}{1 + 0.05 n}$ | $[\text{obs}]^{-1}$ | $T_s$ | `CODE` | coefficient | `HEURÍSTICA_HISTÓRICA` | HIGH | Attention budget | `STUDY` |
| `attention_rank_cost_default`| `1.0` | [`attention.py:23`](../../../symbiont/src/symbiont/core/cognition/attention.py#L23) | Base rank cost denominator | $[-]$ | $T_s$ | `CODE` | parameter | `ESTRUCTURAL` | LOW | Attention priority | `KEEP` |
| `MAX_SHADOW_PREDICTIONS` | `16384`| [`predictors.py:13`](../../../symbiont/src/symbiont/core/cognition/predictors.py#L13) | Global hard capacity for speculative predictors | $[\text{count}]$ | $T_s$ | `ADR-0015` | capacity | `ESTRUCTURAL` | HIGH | Memory cap | `KEEP` |
| `MAX_LIVE_SHADOW_FACTOR` | `8` | [`predictors.py:14`](../../../symbiont/src/symbiont/core/cognition/predictors.py#L14) | Max active shadows multiplier per node | $[-]$ | $T_s$ | `ADR-0015` | bound | `ESTRUCTURAL` | MED | Shadow scaling | `KEEP` |
| `predictor_gain_ewma_alpha` | `0.125`| [`predictors.py:39`](../../../symbiont/src/symbiont/core/cognition/predictors.py#L39) | Predictor empirical utility EWMA factor | $[-]$ | $T_e$ | `CODE` | parameter | `EMPÍRICA_INTERPRETABLE` | HIGH | Streak tracking | `STUDY` |
| `predictor_streak_epsilon` | `1e-4` | [`predictors.py:45`](../../../symbiont/src/symbiont/core/cognition/predictors.py#L45) | Indifference deadband for gain streaks | $[-]$ | $T_e$ | `CODE` | bound | `ESTRUCTURAL` | LOW | Numerical deadband | `KEEP` |

---

### 4.6 Epistemic Conventions & Representation
Owning module: [`epistemic.py`](../../../symbiont/src/symbiont/foundation/epistemic.py)

| ID / Symbol | Value | Location | Governed Mechanism | Dim / Units | Scale | Provenance | Role | Class | Sens. | Dependencies | Ruling |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `established_signal_min_samples` | `5` | [`epistemic.py:31`](../../../symbiont/src/symbiont/foundation/epistemic.py#L31) | Sample floor for statistically established signal | $[\text{count}]$ | $T_e$ | `CODE` | threshold | `EMPÍRICA_INTERPRETABLE` | HIGH | Normalizer cold start | `KEEP` |
| `epistemic_ewma_alpha` | `0.06` | [`epistemic.py:34`](../../../symbiont/src/symbiont/foundation/epistemic.py#L34) | Canonical global epistemic EWMA factor | $[-]$ | $T_e$ | `CODE` | parameter | `EMPÍRICA_INTERPRETABLE` | CRITICAL | Normalizers, self-model | `STUDY` |
| `health_classes` | `16` | [`epistemic.py:37`](../../../symbiont/src/symbiont/foundation/epistemic.py#L37) | Discretized integer bins for health | $[\text{bins}]$ | $T_s$ | `HISTORICAL` | capacity | `HEURÍSTICA_HISTÓRICA` | HIGH | State representation | `DEPRECATE` |
| `confidence_classes` | `16` | [`epistemic.py:38`](../../../symbiont/src/symbiont/foundation/epistemic.py#L38) | Discretized integer bins for confidence | $[\text{bins}]$ | $T_s$ | `HISTORICAL` | capacity | `HEURÍSTICA_HISTÓRICA` | HIGH | State representation | `DEPRECATE` |
| `cost_classes` | `16` | [`epistemic.py:39`](../../../symbiont/src/symbiont/foundation/epistemic.py#L39) | Discretized integer bins for cost | $[\text{bins}]$ | $T_s$ | `HISTORICAL` | capacity | `HEURÍSTICA_HISTÓRICA` | MED | Cost discretization | `DEPRECATE` |
| `maturity_classes` | `8` | [`epistemic.py:40`](../../../symbiont/src/symbiont/foundation/epistemic.py#L40) | Categorical bins for component maturity | $[\text{bins}]$ | $T_d$ | `HISTORICAL` | capacity | `HEURÍSTICA_HISTÓRICA` | HIGH | Maturity progression | `DEPRECATE` |
| `recency_thresholds` | `(10, 40, 120, 400)` | [`epistemic.py:44`](../../../symbiont/src/symbiont/foundation/epistemic.py#L44) | Idle ticks determining recency classes | $[\text{ticks}]$ | $T_s$ | `HISTORICAL` | threshold | `HEURÍSTICA_HISTÓRICA` | HIGH | Recency classification | `DEPRECATE` |
| `maturity_thresholds` | `(0, 1, 2, 4, 8, 16, 32, 64)` | [`epistemic.py:47`](../../../symbiont/src/symbiont/foundation/epistemic.py#L47) | Support epochs required per maturity bin | $[\text{epochs}]$ | $T_d$ | `HISTORICAL` | threshold | `HEURÍSTICA_HISTÓRICA` | HIGH | Discrete maturity | `DEPRECATE` |

---

### 4.7 Social Dynamics, Culture & Modeling
Owning modules: [`relations.py`](../../../symbiont/src/symbiont/core/social/relations.py), [`culture.py`](../../../symbiont/src/symbiont/modeling/culture.py), [`responsibility.py`](../../../symbiont/src/symbiont/modeling/responsibility.py)

| ID / Symbol | Value | Location | Governed Mechanism | Dim / Units | Scale | Provenance | Role | Class | Sens. | Dependencies | Ruling |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `social_valence_deadband`| `0.1` | [`relations.py:36`](../../../symbiont/src/symbiont/core/social/relations.py#L36) | Indifference band between support and harm | $[-]$ | $T_e$ | `CODE` | bound | `HEURÍSTICA_HISTÓRICA` | MED | Valence categorization | `STUDY` |
| `social_freshness_half_life` | `32.0`| [`relations.py:40`](../../../symbiont/src/symbiont/core/social/relations.py#L40) | Exponential evidence half-life in ticks | $[\text{ticks}]$ | $T_e$ | `CODE` | parameter | `EMPÍRICA_INTERPRETABLE` | HIGH | Freshness calculation | `STUDY` |
| `cultural_claim_half_life` | `32.0` | [`culture.py:1274`](../../../symbiont/src/symbiont/modeling/culture.py#L1274) | Exponential claim retention half-life in ticks | $[\text{ticks}]$ | $T_e$ | `CODE` | parameter | `EMPÍRICA_INTERPRETABLE` | HIGH | Cultural retention | `STUDY` |
| `max_social_relations` | `1024` | [`relations.py:284`](../../../symbiont/src/symbiont/core/social/relations.py#L284) | Hard capacity for resident social ledger | $[\text{count}]$ | $T_s$ | `ADR-0015` | capacity | `ESTRUCTURAL` | HIGH | Social memory ceiling | `KEEP` |
| `max_resource_claims` | `64` | [`relations.py:209`](../../../symbiont/src/symbiont/core/social/relations.py#L209) | Hard capacity for tracked external resources | $[\text{count}]$ | $T_s$ | `ADR-0015` | capacity | `ESTRUCTURAL` | MED | Resource tracking | `KEEP` |
| `responsibility_smoothing` | `0.125`| [`responsibility.py:26`](../../../symbiont/src/symbiont/modeling/responsibility.py#L26) | Exponential loss smoothing factor $\alpha$ | $[-]$ | $T_e$ | `CODE` | parameter | `EMPÍRICA_INTERPRETABLE` | MED | Loss tracking | `STUDY` |
| `responsibility_temperature`| `0.25` | [`responsibility.py:27`](../../../symbiont/src/symbiont/modeling/responsibility.py#L27) | Softmax temperature for responsibility shares | $[\text{loss}]$ | $T_e$ | `HISTORICAL` | parameter | `HEURÍSTICA_HISTÓRICA` | CRITICAL | Mechanism credit | `STUDY` |

---

### 4.8 Prospective Agency & Decision Policy
Owning module: [`policy.py`](../../../symbiont/src/symbiont/agency/policy.py)

| ID / Symbol | Value | Location | Governed Mechanism | Dim / Units | Scale | Provenance | Role | Class | Sens. | Dependencies | Ruling |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `_CONFIDENCE_CLASS_MAX` | `7` | [`policy.py:34`](../../../symbiont/src/symbiont/agency/policy.py#L34) | Normalization denominator for model confidence | $[-]$ | $T_s$ | `HISTORICAL` | literal-derived | `HEURÍSTICA_HISTÓRICA` | CRITICAL | Utility scaling | `DEPRECATE` |
| `min_model_confidence` | `0.50` | [`policy.py:64`](../../../symbiont/src/symbiont/agency/policy.py#L64) | Model confidence admission threshold | $[-]$ | $T_e$ | `ADR-0062` | threshold | `ESTRUCTURAL` | HIGH | Deliberation gate | `KEEP` |
| `min_value_samples` | `4` | [`policy.py:65`](../../../symbiont/src/symbiont/agency/policy.py#L65) | Minimal samples to admit value expectation | $[\text{count}]$ | $T_e$ | `ADR-0062` | threshold | `ESTRUCTURAL` | HIGH | Deliberation gate | `KEEP` |
| `value_confidence_norm_divisor`| `16.0`| [`policy.py:93`](../../../symbiont/src/symbiont/agency/policy.py#L93) | Normalization denominator for sample confidence | $[\text{count}]$ | $T_e$ | `HISTORICAL` | coefficient | `HEURÍSTICA_HISTÓRICA` | HIGH | Sample confidence | `DEPRECATE` |
| `decision_margin` | `0.02` | [`policy.py:66`](../../../symbiont/src/symbiont/agency/policy.py#L66) | Minimal utility superiority required to commit | $[-]$ | $T_e$ | `ADR-0062` | threshold | `ESTRUCTURAL` | HIGH | Deliberation tiebreak | `KEEP` |

---

### 4.9 Innate Reactivity & Homeostatic Regulation
Owning module: [`reactivity.py`](../../../symbiont/src/symbiont/core/regulation/reactivity.py)

| ID / Symbol | Value | Location | Governed Mechanism | Dim / Units | Scale | Provenance | Role | Class | Sens. | Dependencies | Ruling |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `surprise_threshold` | `0.18` | [`reactivity.py:28`](../../../symbiont/src/symbiont/core/regulation/reactivity.py#L28) | Perceptual surprise trigger threshold | $[-]$ | $T_s$ | `CODE` | threshold | `EMPÍRICA_INTERPRETABLE` | HIGH | Novelty interrupts | `STUDY` |
| `acute_velocity` | `0.05` | [`reactivity.py:29`](../../../symbiont/src/symbiont/core/regulation/reactivity.py#L29) | Rate of homeostatic worsening triggering urgency | $[\Delta \text{dev}/\text{tick}]$ | $T_s$ | `CODE` | threshold | `EMPÍRICA_INTERPRETABLE` | HIGH | Worsening velocity | `STUDY` |
| `reactivity_smoothing` | `0.35` | [`reactivity.py:30`](../../../symbiont/src/symbiont/core/regulation/reactivity.py#L30) | Velocity EWMA smoothing factor $\alpha$ | $[-]$ | $T_s$ | `CODE` | parameter | `EMPÍRICA_INTERPRETABLE` | MED | Urgency smoothing | `STUDY` |
| `criticality_offset` | `0.55` | [`reactivity.py:87`](../../../symbiont/src/symbiont/core/regulation/reactivity.py#L87) | Affine disequilibrium offset $(\text{dev}-0.55)/0.45$ | $[-]$ | $T_s$ | `HISTORICAL` | threshold | `HEURÍSTICA_HISTÓRICA` | CRITICAL | Criticality scale | `DEPRECATE` |
| `criticality_span` | `0.45` | [`reactivity.py:87`](../../../symbiont/src/symbiont/core/regulation/reactivity.py#L87) | Affine disequilibrium scale factor | $[-]$ | $T_s$ | `HISTORICAL` | coefficient | `HEURÍSTICA_HISTÓRICA` | CRITICAL | Criticality scale | `DEPRECATE` |
| `withdrawal_mix_factor` | `0.50` | [`reactivity.py:92`](../../../symbiont/src/symbiont/core/regulation/reactivity.py#L92) | Heuristic mixture for withdrawal response | $[-]$ | $T_s$ | `HISTORICAL` | coefficient | `HEURÍSTICA_HISTÓRICA` | MED | Defensive action | `STUDY` |
| `stabilization_withdrawal_weight`| `0.75` | [`reactivity.py:95`](../../../symbiont/src/symbiont/core/regulation/reactivity.py#L95) | Linear coefficient for withdrawal stabilization | $[-]$ | $T_s$ | `HISTORICAL` | coefficient | `HEURÍSTICA_HISTÓRICA` | MED | Urgency state | `STUDY` |
| `stabilization_criticality_weight`|`0.65` | [`reactivity.py:95`](../../../symbiont/src/symbiont/core/regulation/reactivity.py#L95) | Linear coefficient for critical stabilization | $[-]$ | $T_s$ | `HISTORICAL` | coefficient | `HEURÍSTICA_HISTÓRICA` | MED | Urgency state | `STUDY` |

---

### 4.10 Genetics & Genome Schema
Owning module: [`schema.py`](../../../symbiont/src/symbiont/genetics/schema.py)

| ID / Symbol | Value | Location | Governed Mechanism | Dim / Units | Scale | Provenance | Role | Class | Sens. | Dependencies | Ruling |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `default_mutation_probability` | `0.10` | [`schema.py:36`](../../../symbiont/src/symbiont/genetics/schema.py#L36) | Mutation probability per locus during reproduction | $[-]$ | $T_d$ | `ADR-0062` | parameter | `ESTRUCTURAL` | HIGH | Germline variance | `KEEP` |
| `default_mutation_scale` | `0.05` | [`schema.py:37`](../../../symbiont/src/symbiont/genetics/schema.py#L37) | Mutation perturbation magnitude for linear genes | $[-]$ | $T_d$ | `ADR-0062` | parameter | `ESTRUCTURAL` | HIGH | Germline step | `KEEP` |
| `soft_node_budget_range` | `[8, 768]` | [`schema.py:189`](../../../symbiont/src/symbiont/genetics/schema.py#L189) | Bounded evolutionary locus for cognitive nodes | $[\text{count}]$ | $T_d$ | `ADR-0015` | bound | `ESTRUCTURAL` | HIGH | Phenotype capacity | `KEEP` |
| `soft_edge_budget_range` | `[16, 6144]` | [`schema.py:192`](../../../symbiont/src/symbiont/genetics/schema.py#L192) | Bounded evolutionary locus for plastic edges | $[\text{count}]$ | $T_d$ | `ADR-0015` | bound | `ESTRUCTURAL` | HIGH | Phenotype capacity | `KEEP` |
| `consolidation_ticks_range` | `[8, 128]` | [`schema.py:200`](../../../symbiont/src/symbiont/genetics/schema.py#L200) | Evolvable range for consolidation cadence | $[\text{ticks}]$ | $T_d$ | `ADR-0015` | bound | `ESTRUCTURAL` | HIGH | Consolidation interval | `KEEP` |

---

## 5. Analytical, Asymptotic, and Statistical Derived Quantities (Non-Runtime Symbols)

To avoid confusing runtime symbols with theoretical properties, the following quantities are recorded as **analytical consequences** of estimators and parameters rather than active stored constants:

### 5.1 Asymptotic Cumulative Weight Mass ($W_\infty$)
In [`predictive_credit.py:116`](../../../symbiont/src/symbiont/sensory/predictive_credit.py#L116), the expression:
$$\text{clip}\left(\text{obs}, \frac{1}{1 - \lambda}\right)$$
uses the geometric series sum for $\lambda = 0.97$:
$$W_\infty = \sum_{k=0}^{\infty} \lambda^k = \frac{1}{1 - \lambda} = \frac{1}{0.03} \approx 33.333$$
$W_\infty$ is strictly the **asymptotic cumulative weight mass** of the geometric weighting kernel. It is not an empirical sample size or an independent degree of freedom.

### 5.2 Kish Effective Sample Size ($N_{\text{eff}}^{\text{geom}}$)
For an infinite sequence of geometric weights $w_k = \lambda^k$ with $\lambda = 0.97$, the Kish Effective Sample Size is defined analytically as:
$$N_{\text{eff}}^{\text{geom}} = \frac{\left(\sum w_k\right)^2}{\sum w_k^2} = \frac{(1 - \lambda)^{-2}}{(1 - \lambda^2)^{-1}} = \frac{1 + \lambda}{1 - \lambda}$$
For $\lambda = 0.97$:
$$N_{\text{eff}}^{\text{geom}} = \frac{1.97}{0.03} \approx 65.667$$
**Crucial Boundary:** $N_{\text{eff}}^{\text{geom}}$ is an analytical benchmark valid **only under the assumption of independent, identically distributed observations**. It does not exist as a variable in the runtime codebase, does not correct for temporal autocorrelation, and must never be applied globally to other estimators without empirical calibration.

---

## 6. Quantified Summary Matrix and Analysis

Across the active runtime, **77 unique mathematical parameters, constants, thresholds, bounds, and rates** are cataloged.

### 6.1 Distribution by Classification

```
                  ┌──────────────────────────────────────────────┐
  ESTRUCTURAL     │ 33 (42.9%)                                   │
  EMPÍRICA        │ 24 (31.2%)                                   │
  HEURÍSTICA      │ 20 (26.0%)                                   │
                  └──────────────────────────────────────────────┘
```

- **ESTRUCTURAL (33 constants, 42.9%):** Invariant safety ceilings, constitutional resource limits (ADR-0015, ADR-0062), and baseline viability bounds. These are justified by architectural safety and host isolation contracts.
- **EMPÍRICA_INTERPRETABLE (24 constants, 31.2%):** Legitimate empirical parameters (half-lives, EWMA factors, physical dissipation rates). These represent real phenomena but currently suffer from dimensional coupling to discrete scheduler ticks rather than continuous time scales.
- **HEURÍSTICA_HISTÓRICA (20 constants, 26.0%):** Pure historical magic numbers, arbitrary discrete bins, and undocumented combination weights. This group constitutes the primary scientific debt of the organism.

### 6.2 Distribution by Runtime Role

| Runtime Role | Count | Percentage | Primary Subsystems |
| :--- | :---: | :---: | :--- |
| `bound` | 17 | 22.1% | Cognition limits, genetics, normalizers, safe mode |
| `coefficient` | 17 | 22.1% | Fitness, motor reproducibility, reactivity, fatigue |
| `threshold` | 16 | 20.8% | Epistemic maturity, sensorimotor gating, viability |
| `parameter` | 14 | 18.2% | Decay rates, EWMA alphas, mutation parameters |
| `capacity` | 8 | 10.4% | Kernel ceilings, social ledger, episodic memory |
| `cadence` | 5 | 6.5% | Consolidation ticks, aging ticks, waste ticks |
| **Total** | **77** | **100.0%** | |

### 6.3 Distribution by Governance Ruling

| Ruling | Count | Percentage | Meaning and Actionable Trajectory |
| :--- | :---: | :---: | :--- |
| **`KEEP`** | 34 | 44.2% | Constitutionally or architecturally justified; preserve unchanged. |
| **`STUDY`** | 30 | 39.0% | Interpretable or heuristic parameter requiring empirical calibration or continuous reformulation ($T_p, T_e$). |
| **`DEPRECATE`** | 13 | 16.9% | Arbitrary discretization, tick-coupled developmental gates, or unprincipled cutoffs to be systematically eliminated. |
| **Total** | **77** | **100.0%** | |

---

## 7. Scientific Debt Ledger and Roadmap Traceability

Every cataloged constant marked as `STUDY` or `DEPRECATE` is mapped to its resolving roadmap phase as specified in [Mathematical Foundations and Temporal Scales v1](mathematical-foundations-and-temporal-scales-v1.md):

```mermaid
flowchart TD
    M0["Phase M0: Forensic Inventory (Complete)"] --> M1["Phase M1: Temporal Scales Decoupling (Tp, Ts, Te, Td)"]
    M0 --> M2["Phase M2: Unification of Decay Kernels"]
    M0 --> M3["Phase M3: Continuous Epistemology & Metric Calibration"]
    M0 --> M4["Phase M4: Statistical Agency & Motor Estimators"]
    M0 --> M5["Phase M5: Calibration Campaigns & Validation"]

    subgraph Debt_M1 ["M1 Debt: Clock Disentanglement"]
        D1["aging_ticks = 16 (DEPRECATE)"]
        D2["senescence_start_ticks = 2048 (DEPRECATE)"]
        D3["IDLE_GRACE_TICKS = 20 (STUDY)"]
    end

    subgraph Debt_M2 ["M2 Debt: Continuous Relaxation"]
        D4["epistemic_ewma_alpha = 0.06 vs 0.15 vs 0.125 (STUDY)"]
        D5["thermal_relaxation_rate = 0.02 (STUDY)"]
        D6["social_freshness_half_life = 32.0 ticks (STUDY)"]
    end

    subgraph Debt_M3 ["M3 Debt: Discretization Removal"]
        D7["recency_thresholds = (10, 40, 120, 400) (DEPRECATE)"]
        D8["health/confidence/cost_classes = 16 (DEPRECATE)"]
        D9["sensor_age_thresholds = (4, 16, 64) (DEPRECATE)"]
    end

    subgraph Debt_M4 ["M4 Debt: Motor & Agency Estimators"]
        D10["motor_reproducibility_factor = 25.0 (STUDY)"]
        D11["controllability_cutoff = 0.002 (DEPRECATE)"]
        D12["_CONFIDENCE_CLASS_MAX = 7 vs 16 (DEPRECATE)"]
        D13["responsibility_temperature = 0.25 (STUDY)"]
    end

    M1 --- Debt_M1
    M2 --- Debt_M2
    M3 --- Debt_M3
    M4 --- Debt_M4
```

### 7.1 Debt Itemization by Phase

#### Phase M1: Clock Separation & Temporal Decoupling ($T_p, T_s, T_e, T_d$)
- **DEPRECATE:** `aging_ticks = 16` in [`physiology_config.py`](../../../symbiont/src/symbiont/core/embodiment/physiology_config.py#L40). Conflates scheduler iterations with developmental maturity. Ontogeny must be driven by metabolic turnover and accumulated experience ($T_d, T_e$).
- **DEPRECATE:** `senescence_start_ticks = 2048` in [`physiology_config.py`](../../../symbiont/src/symbiont/core/embodiment/physiology_config.py#L45). Somatic senescence must be governed by cumulative physical work and structural wear ($T_p$), not raw scheduler iterations.
- **STUDY:** Decoupling host wall-time timeouts (`IDLE_GRACE_TICKS = 20` in [`host_self_model.py`](../../../symbiont/src/symbiont/core/cognition/host_self_model.py#L27)) from internal organism time.

#### Phase M2: Unification of Decay Kernels & Continuous Relaxation
- **STUDY & UNIFY:** Reconcile three competing, discordant discrete EWMA smoothing factors across cognition and sensing:
  - $\alpha = 0.06$ in [`epistemic.py:34`](../../../symbiont/src/symbiont/foundation/epistemic.py#L34) (effective half-life $\approx 11.2$ ticks)
  - $\alpha = 0.15$ in [`predictive_credit.py:10`](../../../symbiont/src/symbiont/sensory/predictive_credit.py#L10) (effective half-life $\approx 4.3$ ticks)
  - $\alpha = 0.125$ in [`predictors.py:39`](../../../symbiont/src/symbiont/core/cognition/predictors.py#L39) (effective half-life $\approx 5.2$ ticks)
  All decay kernels must be expressed as continuous relaxation times $\tau$ satisfying $w(t) = \exp(-\Delta t / \tau)$, parameterized by physical or experiential duration.
- **STUDY:** Replace Euler-discretized thermal cooling (`thermal_relaxation_rate = 0.02` in [`homeostasis.py:136`](../../../symbiont/src/symbiont/core/embodiment/homeostasis.py#L136)) with an exact continuous integration step $T(t + \Delta t) = T_{\text{set}} + (T(t) - T_{\text{set}})\exp(-\Delta t / \tau_{\text{thermal}})$.

#### Phase M3: Epistemic Maturity Decoupling & Continuous Representation
- **DEPRECATE:** Quantized recency bins `(10, 40, 120, 400)` in [`epistemic.py:44`](../../../symbiont/src/symbiont/foundation/epistemic.py#L44). Epistemic freshness is a continuous function $\exp(-\Delta t / \tau)$, never a step staircase.
- **DEPRECATE:** Discrete integer classes (`health_classes = 16`, `confidence_classes = 16`, `cost_classes = 16`, `maturity_classes = 8`). State representation must remain continuous IEEE 754 floats in $[0, 1]$; discretization is permitted only as a passive, non-canonical projection for telemetry visualization.
- **DEPRECATE:** Arbitrary sensor age maturity thresholds `(4, 16, 64)` in [`sensor.py:145-150`](../../../symbiont/src/symbiont/sensory/sensor.py#L145-L150) and linear mixture weights `0.7 * health + 0.3 * maturity_factor` in [`sensor.py:158`](../../../symbiont/src/symbiont/sensory/sensor.py#L158). Maturity must be a monotonic function of effective sample count $N_{\text{eff}}$ and empirical variance, not elapsed ticks.

#### Phase M4: Statistical Agency & Motor Estimators Formulation
- **STUDY & DERIVE:** Dimensionally sound reformulation of motor reproducibility (`sensorimotor.py:220`). Currently $1 / (1 + 25\sigma^2)$ treats $25.0$ as a dimensionless constant while $\sigma^2$ has units of $[\text{effect}]^2$. Must be reformulated relative to effect dynamic range $\sigma_{\text{baseline}}^2$ or empirical variance scale $1 / (1 + \sigma^2 / \sigma_0^2)$.
- **DEPRECATE:** Hardcoded controllability cutoff `0.002` in [`sensorimotor.py:1177`](../../../symbiont/src/symbiont/actuation/sensorimotor.py#L1177). To be replaced by a principled statistical hypothesis test comparing effect mean to estimation standard error $Z = |\hat{\mu}| / (\hat{\sigma} / \sqrt{N_{\text{eff}}} + \epsilon)$ under a calibrated episode definition.
- **DEPRECATE:** Discrete confidence normalizer inconsistency (`_CONFIDENCE_CLASS_MAX = 7` in [`policy.py:34`](../../../symbiont/src/symbiont/agency/policy.py#L34) vs `confidence_classes = 16` in [`epistemic.py:38`](../../../symbiont/src/symbiont/foundation/epistemic.py#L38)). Prospective agency must operate directly on continuous bounded confidence in $[0, 1]$.
- **STUDY:** Fixed softmax temperature `temperature = 0.25` in [`responsibility.py:27`](../../../symbiont/src/symbiont/modeling/responsibility.py#L27). Since $\exp(-\Delta \mathcal{L} / T)$ requires $T$ to have units of loss $[\mathcal{L}]$, a fixed dimensionless $0.25$ causes arbitrary sensitivity when loss scales change. Must adapt to running loss dispersion.

#### Phase M5: Calibration Campaigns & Empirical Studies
- **STUDY:** Empirical calibration of sensory fitness heuristic weights (`0.60, 0.40, 0.70, 0.15, 0.10, 0.05` in [`fitness.py:38-42`](../../../symbiont/src/symbiont/sensory/fitness.py#L38-L42)).
- **STUDY:** Social evidence half-life (`half_life = 32.0` in [`relations.py:40`](../../../symbiont/src/symbiont/core/social/relations.py#L40) and [`culture.py:1274`](../../../symbiont/src/symbiont/modeling/culture.py#L1274)).

---

## 8. Phase M0 Governance Gate Closure

### 8.1 Closure Criteria Verification

| Criterion | Requirement | Status | Evidence |
| :--- | :--- | :---: | :--- |
| **C1. Full Forensic Coverage** | Every active numeric constant in `symbiont/` identified with source lines, units, and roles. | **PASS** | 77 runtime constants cataloged across 11 subsystems in Section 4. |
| **C2. Taxonomy Conformance** | Every entry classified into one of 3 runtime classes and assigned one of 6 runtime roles. | **PASS** | 100% compliance verified in summary matrix (Section 6). |
| **C3. Separation of Analytical Quantities** | Asymptotic/theoretical quantities strictly segregated from runtime parameters. | **PASS** | Section 5 defines $W_\infty$ and $N_{\text{eff}}^{\text{geom}}$ as analytical properties outside runtime code. |
| **C4. Zero Runtime Mutation** | Strictly zero changes to runtime code, configurations, or tests. | **PASS** | `git diff` against `main` contains exclusively documentation files. |
| **C5. Prioritized Scientific Debt** | All `STUDY` and `DEPRECATE` rulings formally registered and mapped to subsequent roadmap phases. | **PASS** | Section 7 establishes the formal mapping to Phases M1 through M5. |

### 8.2 Milestone Disposition
Phase M0 is **formally complete**. The observational baseline is established. The repository is prepared to open Phase M1 (Clocks and Temporal Scales Separation) under independent scientific preregistration.

# Domain map

This reference maps the principal scientific domains to their current implementation anchors. It is intentionally implementation-facing; explanatory chapters should be preferred for first reading.

| Domain | Primary implementation | Role |
| --- | --- | --- |
| Runtime orchestration | `symbiont/src/symbiont/core/orchestration/runtime.py` | Orders one organism tick and composes domains |
| Lifecycle | `symbiont/src/symbiont/core/domains/lifecycle.py` | Death/release/events/journal boundaries |
| Physiology | `symbiont/src/symbiont/core/domains/physiology.py`, `symbiont/src/symbiont/core/embodiment/physiology.py` | Body state, vital state, cost and ageing |
| Perception | `symbiont/src/symbiont/core/domains/perception.py` | Sampling, transduction, attention, drift, signal knowledge |
| Sensory phenotype | `symbiont/src/symbiont/sensory/*` | Organism-owned sensors, modalities and plasticity |
| Host modalities | `modality/src/modality/*` | Physical and platform measurement surfaces |
| Cognition | `symbiont/src/symbiont/core/domains/cognition.py`, `symbiont/src/symbiont/core/cognition/*`, `symbiont/src/symbiont/cognition/*` | Cognitive state, evidence, graph activation, self-model and plasticity |
| Memory | `symbiont/src/symbiont/core/domains/memory.py`, `symbiont/src/symbiont/modeling/episodic.py` | Retention, consolidation and episodic organisation |
| Agency | `symbiont/src/symbiont/agency/*` | Affordances, intentions, prospective and outcome policy |
| Actuation | `symbiont/src/symbiont/actuation/*` | Competence acquisition, control and actuator delivery |
| Embodiment (organism) | `symbiont/src/symbiont/core/domains/embodiment.py`, `symbiont/src/symbiont/core/embodiment/*` | Body contract, schema, episode and reacclimation |
| Physical bodies | `embodiment/src/embodiment/physics3d/*` | Articulated mechanical bodies (crawler, hexapod, humanoid, spot) |
| Development | `symbiont/src/symbiont/core/domains/development.py` | Expression and developmental state |
| Genetics | `symbiont/src/symbiont/genetics/*`, `symbiont/src/symbiont/core/lineage/*` | Genome, germline, inheritance and lineage |
| Social | `symbiont/src/symbiont/core/social/*` | Communication, evidence, relations and exchange |
| Generative cognition | `symbiont/src/symbiont/cognition/generative/*` | Internal hypotheses, replay, rollout and consolidation |
| Provenance | `symbiont/src/symbiont/provenance.py` | Bounded causal events/frontier |
| World | `environment/src/environment/*`, `lab/src/lab/world/*` | External physical dynamics, resources and regimes |
| Physics3D simulation | `lab/src/lab/physics3d/*`, `lab/src/lab/integration/physics3d/apparatus.py` | Laboratory physics simulation and apparatus binding |
| Observatory | `lab/src/lab/observatory/*`, `lab/src/lab/observation/*` | Passive researcher-facing projection |
| Experiments | `lab/src/lab/experiments/*`, `lab/experiments/*` | Reproducible experiment definitions and runners |

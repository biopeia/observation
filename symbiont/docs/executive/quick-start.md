# Quick Start — Five-Minute Reading Guide

<!-- Epistemic Demarcation: Executive Synthesis Layer -->
<!-- Invariant: This document synthesizes canonical concepts for human reviewer orientation. It does not introduce new architectural or scientific authority. Authoritative definitions reside in the canonical corpus (symbiont/docs/) and reference registries (symbiont/docs/reference/). -->

## 1. Introduction for Reviewers

Symbiont is a longitudinal digital organism, not an agent wrapper, prompt pipeline, or stateless simulation episode.

The five architectural domains of the repository structure the system:
- **`symbiont`**: The computational subject, owning its bounded internal state, inherited capacity, acquired cognition, agency, memory, and persistent identity.
- **`environment`** & **`embodiment`**: The spatial habitat and physical body coupling that condition and interact with the organism, but never substitute for its identity.
- **`modality`**: Physical transduction channels connecting sensory surfaces to the world.
- **`lab`**: The observer, researcher apparatus, ground truth, and evaluation metrics that evaluate the subject without leaking evaluative knowledge into the subject's internal experience.

Knowledge, competences, and causal representations in Symbiont must emerge from the organism's own lived experience and sensorimotor interactions.

For detailed foundations and architectural demarcations, see [Foundations and Epistemology](../00-foundations-and-epistemology.md) and [System and Boundaries](../01-system-and-boundaries.md).

---

## 2. Five Rules Before Reading

Before evaluating implementation code, metrics, or architecture chapters, apply these five foundational reading distinctions:

### Rule 1: Separated States
$$\text{Technical} \neq \text{Scientific} \neq \text{Canonical} \neq \text{Integration} \neq \text{Behavioral relevance}$$

A component may be technically compiled without being behaviorally active; an integration contract may be verified without proving a scientific hypothesis; and engineering stability does not imply empirical causal efficacy.

### Rule 2: Epistemic Hierarchy
$$\text{Fact} \neq \text{Evidence} \neq \text{Model} \neq \text{Hypothesis} \neq \text{Claim}$$

Internal predictions, counterfactual simulations, and generative hypotheses never acquire factual authority through internal confidence, repetition, or rollout convergence. Only closed, observed environmental outcomes constitute empirical evidence for the organism. See [Generative Cognition](../09-generative-cognition.md).

### Rule 3: Capability vs. Physical Body
$$\text{Competence} \in \text{Organism}, \quad \text{Execution Binding} \in \text{Embodiment Coupling}$$

A *Competence* (`SYM-COMP`) is a reusable, acquired capability that belongs strictly to the organism. An *Execution Binding* (`SYM-CBIND`) expresses that competence through a specific, interchangeable physical *Body* (`SYM-BODY`). Re-embodiment decouples bodily morphology without resetting cognitive competence. See [World, Body and Embodiment](../03-world-body-and-embodiment.md) and [Agency, Action and Motor Learning](../07-agency-action-and-motor-learning.md).

### Rule 4: Regulation vs. External Reward
$$\text{Homeostasis} \neq \text{External Reward} \neq \text{Action Directives}$$

Homeostatic regulation (`SYM-HOM`, `SYM-PHYS`) measures internal viability deviation relative to physiological survival boundaries. It does not act as an externally supplied reward scalar, objective function, or optimization target given by an environment designer. See [Physiology, Homeostasis and Cost](../05-physiology-homeostasis.md).

### Rule 5: Code vs. Causal Efficacy
$$\text{Implemented} \neq \text{Wired} \neq \text{Behaviorally Effective}$$

Technical unit tests prove that an algorithm executes without runtime exceptions. Level 2 engineering traceability demonstrates an auditable software path. Neither constitutes scientific proof of causal emergence, behavioral autonomy, or cognitive learning in empirical environments. Consult [docs/governance/constitution.md](../../../docs/governance/constitution.md).

---

## 3. Recommended Reading Path for Reviewers

External and technical reviewers should follow this sequential trajectory through the repository:

1. **Executive Architecture Overview**: [overview.md](overview.md) — One-page synthesis, architectural layers, and canonical organism flow.
2. **Foundations & Epistemology**: [Foundations](../00-foundations-and-epistemology.md) and [Boundaries](../01-system-and-boundaries.md) — System invariants, identity preservation, and epistemic demarcation.
3. **Existence & Time**: [Lifecycle and Time](../02-lifecycle-and-time.md) — Temporal scales, checkpoints, and longitudinal survival.
4. **Physical Decoupling**: [World, Body and Embodiment](../03-world-body-and-embodiment.md) and [Perception](../04-perception-and-sensory-development.md) — Opaque signal mapping, sensorimotor boundaries, and embodiment transitions.
5. **Physiology & Regulatory Baseline**: [Physiology and Homeostasis](../05-physiology-homeostasis.md) — Energetic costs and somatic viability.
6. **Cognition, Agency & Generative Dynamics**: [Cognition](../06-cognition-and-internal-organization.md), [Agency](../07-agency-action-and-motor-learning.md), [Learning](../08-learning-memory-and-plasticity.md), and [Generative Cognition](../09-generative-cognition.md) — The causal cycle of internal representations, affordances, and memory consolidation.
7. **Quantitative Registries**:
   - [components.yaml](../reference/components.yaml): 48 canonical `SYM-*` components with explicit state ownership and authority boundaries.
   - [parameters.yaml](../reference/parameters.yaml): Mathematical and architectural parameter contracts.
   - [metrics.yaml](../reference/metrics.yaml): Observable metrics partitioned across epistemic classes.
   - [notation.yaml](../reference/notation.yaml): Formal notation symbols and disambiguation.
   - [coverage.yaml](../coverage.yaml): Traceability between implementation, design, tests, and ADRs.
8. **Permanent Governance**: [docs/governance/constitution.md](../../../docs/governance/constitution.md) — Architectural, host-safety, and scientific boundary invariants.

---

## 4. Minimal Organic Vocabulary (Orientation)

This table provides operational orientations for biological and cognitive terms used across the codebase. Authoritative definitions reside in the component fiches ([components.yaml](../reference/components.yaml)) and canonical references.

| Term | Operational Meaning in Symbiont | Primary Canonical Owner |
|:---|:---|:---|
| **Genome** | Inherited, immutable constitution establishing initial architecture and capacities; contains zero acquired experiential knowledge. | `component.genome` (`SYM-GEN`) |
| **Germline** | Reproductive and lineage channel restricting which information can be inherited across generations. | `component.germline` (`SYM-GERM`) |
| **Epigenetics** | Persistent modulation of phenotypic expression over development without altering underlying constitutional code. | `component.epigenetics` (`SYM-EPI`) |
| **Ontogeny** | Quantitative somatic and physical development of the organism over longitudinal time. | `component.ontogeny` (`SYM-ONT`) |
| **Homeostasis** | Continual monitoring and regulation of physiological deviations from internal viability envelopes; never an external reward signal. | `component.homeostasis` (`SYM-HOM`) |
| **Competence** | Reusable, acquired capability learned through lived experience, evidence, and outcome verification; decoupled from specific actuators. | `component.competence` (`SYM-COMP`) |
| **Embodiment** | Dynamic coupling between the computational subject and a physical body substrate; distinct from organism identity. | `concept.embodiment` |
| **Episode** | Concrete, spatio-temporally bounded lived experience stored and retrievable as an episodic trace; never a universal predictive model. | `component.episodic-memory` (`SYM-EPI-M`) |
| **Private Model** | Internal forward predictive model ($\text{state} \times \text{action} \to \text{next-state}$); predicts probable dynamics without declaring ground truth. | `component.private-model` (`SYM-PM`) |
| **Provenance** | Structured trace documenting causal origins, dependencies, and transformation chains of an internal state or claim; origin $\neq$ truth. | `component.provenance` (`SYM-PROV`) |

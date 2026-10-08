# Quick Start — Five-Minute Reading Guide

<!-- Epistemic Demarcation: Executive Synthesis Layer -->
<!-- Invariant: This document synthesizes canonical concepts for human reviewer orientation. It does not introduce new architectural or scientific authority. Authoritative definitions reside in symbiont/docs/ and symbiont/docs/reference/. -->

## 1. Introduction for Reviewers

Symbiont is a longitudinal digital organism, not an agent wrapper, prompt pipeline, or stateless simulation episode.

The five architectural domains of the repository structure the system:
- **`symbiont`**: the computational subject, owning its bounded internal state, inherited capacity, acquired cognition, agency, memory, and persistent identity.
- **`environment`**: the external spatial and causal substrate.
- **`embodiment`**: the physical coupling layer that exposes body-specific receptor and effector contracts without owning organism identity.
- **`modality`**: transduction channels that expose bounded signals without injecting external semantics.
- **`lab`**: the observer and scientific apparatus, which may hold ground truth and evaluator-only information that must not leak into organism cognition.

Acquired cognition must arise from organism-accessible evidence admitted through legitimate sensory, physiological, social, and action-consequence channels. Laboratory ground truth and evaluator-only labels are never shortcuts into organism knowledge.

For detailed foundations and architectural demarcations, see [Foundations and Epistemology](../00-foundations-and-epistemology.md) and [System and Boundaries](../01-system-and-boundaries.md).

---

## 2. Five Rules Before Reading

Before evaluating implementation code, metrics, or architecture chapters, apply these five foundational reading distinctions.

### Rule 1: Separated States

$$\text{Technical} \neq \text{Scientific} \neq \text{Canonical} \neq \text{Integration} \neq \text{Behavioral relevance}$$

A component may be technically implemented without being behaviorally effective; an integration contract may be verified without proving a scientific hypothesis; and engineering stability does not imply empirical causal efficacy.

### Rule 2: Epistemic Hierarchy

$$\text{Fact} \neq \text{Evidence} \neq \text{Model} \neq \text{Hypothesis} \neq \text{Claim}$$

Predictions, counterfactual simulations, and generative hypotheses never acquire factual authority through confidence, repetition, or rollout convergence. Factual revision requires admitted observations or observed consequences with valid provenance; generated content cannot manufacture its own evidence. See [Generative Cognition](../09-generative-cognition.md).

### Rule 3: Competence vs. Execution Binding

A *Competence* (`SYM-COMP`) is an organism-owned, reusable capability learned from evidence. A *Competence Execution Binding* (`SYM-CBIND`) is also organism-owned state: it maps an abstract competence to the actuators exposed by the current embodiment and must be revalidated or rebound when embodiment changes.

The physical **Body** is external to the `SYM-*` component catalogue. Re-embodiment may replace the body and invalidate body-specific execution authority without erasing organism-level competence. See [World, Body and Embodiment](../03-world-body-and-embodiment.md) and [Agency, Action and Motor Learning](../07-agency-action-and-motor-learning.md).

### Rule 4: Regulation vs. External Reward

$$\text{Homeostasis} \neq \text{External Reward} \neq \text{Action Directives}$$

Homeostatic regulation (`SYM-HOM`, `SYM-PHY`) measures internal deviation from viable physiological conditions. It must not become an externally supplied reward scalar, environment-authored objective, or direct motor selector. See [Physiology, Homeostasis and Cost](../05-physiology-homeostasis.md).

### Rule 5: Code vs. Causal Efficacy

$$\text{Implemented} \neq \text{Wired} \neq \text{Behaviorally Effective}$$

A passing implementation test establishes only the contract that test actually discriminates. Traceable integration does not by itself establish scientific emergence, autonomous behaviour, or causal learning in empirical environments. Consult [docs/governance/constitution.md](../../../docs/governance/constitution.md).

---

## 3. Recommended Reading Path for Reviewers

1. **Executive Architecture Overview**: [overview.md](overview.md) — transversal synthesis and a traceable component relationship view.
2. **Foundations & Epistemology**: [Foundations](../00-foundations-and-epistemology.md) and [Boundaries](../01-system-and-boundaries.md).
3. **Existence & Time**: [Lifecycle and Time](../02-lifecycle-and-time.md).
4. **Physical Decoupling**: [World, Body and Embodiment](../03-world-body-and-embodiment.md) and [Perception](../04-perception-and-sensory-development.md).
5. **Physiology & Regulation**: [Physiology and Homeostasis](../05-physiology-homeostasis.md).
6. **Cognition, Agency & Generative Dynamics**: [Cognition](../06-cognition-and-internal-organization.md), [Agency](../07-agency-action-and-motor-learning.md), [Learning](../08-learning-memory-and-plasticity.md), and [Generative Cognition](../09-generative-cognition.md).
7. **Canonical registries**:
   - [components.yaml](../reference/components.yaml): component authority, ownership, lifecycle, inputs, outputs, and consumers.
   - [parameters.yaml](../reference/parameters.yaml): quantitative parameter contracts.
   - [metrics.yaml](../reference/metrics.yaml): metrics partitioned by epistemic class.
   - [notation.yaml](../reference/notation.yaml): formal notation and forbidden meanings.
   - [coverage.yaml](../coverage.yaml): implementation, test, design, ADR, dependency, and Master traceability.
8. **Permanent Governance**: [docs/governance/constitution.md](../../../docs/governance/constitution.md).

---

## 4. Minimal Organic Vocabulary (Orientation)

This table is an orientation layer only. Canonical authority remains in the registries and linked chapters.

| Term | Operational Meaning in Symbiont | Primary Canonical Owner |
|:---|:---|:---|
| **Genome** | Heritable constitutional representation defining genetic loci and capacities; it must not contain acquired cognitive knowledge or learned competences. | `component.genome` (`SYM-GEN`) |
| **Germline** | Heritable reproductive transmission package and lineage boundary; it must not transport acquired memories or learned competences. | `component.germline` (`SYM-GRM`) |
| **Epigenetic State** | Persistent regulatory modulation without genomic alteration; cognitive experience cannot be converted directly into genetic loci. | `component.epigenetic-state` (`SYM-EPI-G`) |
| **Ontogeny / Development** | Organism-owned developmental stage and maturation state that survives restart and re-embodiment. | `component.ontogeny-development` (`SYM-DEV`) |
| **Physiology** | Somatic physiological state and metabolic internal conditions. | `component.physiology` (`SYM-PHY`) |
| **Homeostasis** | Measurement of deviation from viable physiological conditions; never an external reward oracle or direct action selector. | `component.homeostasis` (`SYM-HOM`) |
| **Competence** | Acquired reusable capability that does not assume executability on every embodiment. | `component.competence` (`SYM-COMP`) |
| **Competence Execution Binding** | Organism-owned, embodiment-local mapping from competence to concrete actuators; re-embodiment requires rebinding rather than overwriting competence identity. | `component.competence-binding` (`SYM-CBIND`) |
| **Embodiment** | The bounded relation between a Symbiont and a particular perceptual, actuator, and timing contract; distinct from the physical body and organism identity. | `concept.embodiment` |
| **Episode** | Sequential lived experience retained as episodic memory; it must not contain ungrounded world truth. | `component.episodic-memory` (`SYM-EPI-M`) |
| **Private Model** | Organism-owned predictive transition model from state and action to probable next state; it may predict but must not assert factual truth. | `component.private-model` (`SYM-PM`) |
| **Causal Provenance** | Trace of causal origin and references for organism events or claims; provenance records origin, not truth. | `component.causal-provenance` (`SYM-PROV`) |

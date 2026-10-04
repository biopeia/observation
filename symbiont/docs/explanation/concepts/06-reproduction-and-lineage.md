---
id: explanation.web.06-reproduccion-y-linaje
title: "06 Reproduction And Lineage"
document_type: explanation
domain: concepts
status: unclassified
canonical: false
implementation_status: unknown
migrated_on: 2026-09-25
last_reviewed: null
language: en
---
# Reproduction and lineage

<a id="que-es"></a>

## What it is

A Symbiont can reproduce, but reproduction here does not mean copying a process nor deploying a new instance at will. It means creating a distinct organism identity, with its own inherited genome and its own independent cognitive development — subject to explicit habitat authorization and carrying capacity, never as uncontrolled propagation.

<a id="mecanismo"></a>

## Mechanism

Reproductive pressure does not depend on age nor on hitting a punctual limit: it activates only if, during several sustained consecutive ticks, the organism is viable, adaptive and its phenotypic capacity is saturated against growth that remained blocked due to lack of space. Only then the organism becomes `REPRODUCTIVELY_READY`.

The first asexual mechanism is clonal budding: the progenitor **does not die nor divide**. The descendant receives the same Genome v2 (without recombination or allele mutation) but a new and unique organism identity, and a newly initialized CognitiveGraph. It does not inherit acquired synaptic weights, sensory baselines, beliefs, or the parent's somatic `EpigeneticPrior`. Separately, germline marks may be captured and transmitted only when the explicit `EpigeneticProtocol` permits it; those marks can affect the child's birth expression. This is a mechanical inheritance path, not evidence of adaptive benefit. Thus, acquired cognitive knowledge and somatic adaptation are not passed on as such, while the protocol-gated Genome v2 germline channel is distinct.

Materializing a descendant is never a free operation: `HabitatBirthAuthority` turns birth into an atomic transaction. If the carrying capacity of the habitat is full, the birth is denied as a whole and the reproductive reserve accumulated by the progenitor is reverted intact — it is not partially lost, it is not consumed by a failed attempt. A successful birth consumes the pressure that justified it, so that the same historical saturation event does not generate descendants indefinitely.

The organism lineage is a separate structure from the genome lineage: two clonal descendants can share exactly the same `genome_id` and still have distinct `organism_id` and completely independent life histories.

<a id="implementado"></a>

## What is implemented

- Reproductive pressure based on sustained saturation, not on age — **[implemented]**.
- Clonal budding with empty germinal CognitiveGraph and no inherited cognitive memory or weights — **[implemented]**; protocol-gated Genome v2 germline marks are a separate inherited channel.
- Transactional habitat authority: denied birth reverts the progenitor's reserve entirely — **[implemented]**.
- Separation of organism lineage and genome lineage — **[implemented]**.
- Genome v2 recombination between compatible parents — **[not implemented]**. Resident budding is clonal and does not mutate alleles.

<a id="evidencia"></a>

## Evidence

It is proven that reproductive pressure requires sustained persistence before enabling a bud, and that this bud consumes the pressure exactly once. It is proven that a birth denied due to a full habitat capacity **does not** consume the accumulated reproductive pressure of the progenitor — the rejection is atomic and complete. Tests also establish an empty child CognitiveGraph and a protocol-gated Genome v2 germline capture → checkpoint/restore → resident-budding → child-expression path. These are mechanical results only; they do not establish adaptive benefit or ecological advantage.

<a id="abierto"></a>

## What remains open (from this mechanism)

- The measurable divergence between progenitor and descendant under different experiences is designed as an expected property of the system, but its long-term quantitative characterization belongs to laboratory studies, not to this description of the mechanism.
- Cognitive inheritance, somatic `EpigeneticPrior`, protocol-gated Genome v2 germline marks, and social/cultural claims have separate owners and contracts. Their combined effects under ecological pressure are not established by the mechanical tests described here.

<a id="respaldo-formal"></a>

## Formal backing

This chapter describes a transaction machine and a discrete life cycle, not a formal mathematical development of its own in the compendium. The complete normative design — including the recombination of inheritable loci, bounded epigenetic inheritance and the separation of inheritance channels — is in
[`docs/history/design/fisiologia-y-reproduccion.md`](../../../../docs/history/design/fisiologia-y-reproduccion.md).

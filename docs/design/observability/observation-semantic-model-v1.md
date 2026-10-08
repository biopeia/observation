# Observation Semantic Model v1

**Status:** Proposed / In progress.  
**Implementation state:** Not started; no implementation is authorized.  
**Scope:** Transport-independent conceptual model for semantic observations in Observation Architecture v1.  
**Authority:** This document derives from the approved [Target Design](observation-architecture-target-design-v1.md) and accepted [Design Inputs](observation-architecture-design-inputs-v1.md). It does not amend either, authorize implementation, or approve a wire/API/transport contract.

## 1. Purpose

Define the shared semantic concepts needed to describe admitted observations across authority domains, before selecting concrete record layouts or delivery mechanisms.

The model is **observation-oriented and event-delivered where needed, not event-owned**. A semantic observation is distinct from an event, transport message, snapshot, materialized view, query result or UI projection.

This is a conceptual model, not a Python type system, JSON/protobuf schema, envelope, API, topic hierarchy or endpoint design.

## 2. Governing boundaries

- Each authority domain has one intentional observation boundary containing multiple typed semantic families.
- A semantic claim has one unambiguous primary semantic authority and epistemic interpretation.
- A producer, measurement source, Observation Plane host or consumer does not acquire authority by handling a claim.
- Context may be supplied by other roles, but its issuer/source must remain explicit when material.
- A delivery batch or composed view may contain heterogeneous claims without assigning them shared authority.
- Identity, domain time, transport order and lineage are distinct concepts.
- Unknown or contradictory context blocks only interpretation or joins that depend on it; independent source claims remain valid within their evidenced scope.
- Unknown/implicit physical units do not conform to a declared physical semantic contract. The affected capability remains excluded until its unit is explicitly declared or converted.

## 3. Conceptual observation

An observation is a bounded semantic assertion about a subject or source-scoped state, made under a domain meaning and an acquisition/derivation basis.

At minimum, the conceptual model must let a reader answer:

1. What claim is being made?
2. What subject or scope does it concern?
3. Which domain owns the claim's meaning?
4. Is the claim source state, apparatus measurement, domain-derived, Lab-derived, or another explicitly distinguished epistemic kind?
5. When was it valid, sampled, derived or applied, using which domain clock/revision?
6. What source, transformation or configuration lineage is material to interpreting it?
7. Is it available and complete enough for the intended use?

These are interpretability requirements, not a requirement to repeat every item on every primitive value. Homogeneous subrecords may share context; mixed claims must preserve distinctions explicitly.

## 4. Core concepts to define

The v1 model must refine the following concepts without assuming every concept is a mandatory field:

| Concept | Meaning to preserve | Open design question |
|---|---|---|
| Semantic claim | One bounded assertion with a primary authority and epistemic interpretation. | What makes a claim atomic for each retained family? |
| Subject/scope | The entity, relationship, or source scope the claim concerns. | Which claims concern an entity versus an Environment location or run scope? |
| Authority | Domain that defines the meaning of the claim. | Datum-level assignments remain subject to domain-owner disposition. |
| Acquisition/derivation basis | How the asserted value was obtained or produced. | Which distinctions are needed in operational records versus trace documentation? |
| Domain time | Typed source-domain clock or revision, not a universal `tick`. | Which clocks/revisions are needed per retained family? |
| Provenance/lineage | Material source claims, transformations and effective configuration. | How are multi-input and configured derivations referenced without bloating records? |
| Availability/completeness | Whether absence, partiality, staleness or unsupported capability changes interpretation. | Which statuses are source semantics and which describe plane delivery? |
| Semantic family/contract revision | Meaning namespace and compatible semantic definition. | How are family and version identities represented independently of transport? |
| Measurement source | Apparatus or sensing source for a measured/simulated claim. | When is source identity necessary for interpretation versus audit only? |
| Producer/asserter | Component that materializes or asserts a representation. | How is it distinguished from the semantic authority and identifier issuer? |

## 5. Conditional context

The model should attach context conditionally when it affects meaning or valid association:

- subject identity and explicit identity links;
- domain clock or revision;
- units, frames and semantic physical-contract reference;
- source/measurement identity;
- derivation parents and effective transformation/configuration;
- Run/orchestration context;
- availability/completeness.

Context is not a hidden additional semantic claim. For example, an explicit Lab run association does not assert that a source-domain organism identifier equals a Lab catalog reference.

## 6. Distinctions the model must retain

```text
semantic authority       != producer
semantic authority       != measurement source
semantic authority       != transport host
semantic authority       != consumer
derivation               != Lab ownership
source observation       != derived observation
domain time              != observation-plane sequence
subject identity         != alias without an explicit link
observation              != event/message/snapshot/projection
operational observation  != scientific evidence
```

## 7. Explicit non-goals

This document does not define:

- concrete record or envelope fields;
- language-level interfaces or data classes;
- serialization, schema encoding or wire compatibility;
- event names, topics, subscription syntax or delivery cadence;
- snapshot coherence, watermarks, replay, retention or gap recovery;
- endpoints, HTTP/SSE/WebSocket/broker, storage or transport;
- final publication scope or implementation.

Those are later decisions. The macro architecture is frozen as recorded in the Target Design; this semantic model may refine common concepts but must not silently reopen that architecture.

## 8. Checklist

Work one bounded item at a time. Mark only the current item `IN PROGRESS`; do not treat the first unchecked item as current focus. Completion of this conceptual model does not authorize a record schema or transport.

- [ ] **IN PROGRESS — Establish model vocabulary and scope.** Reconcile the core concepts in §§3–6 with the approved authority, identity, time, provenance and availability boundaries; distinguish universal interpretability needs from conditional context.
- [ ] **QUEUED — Test the model against retained semantic cases.** Use Body Pose, Environment logical resource-pool state, Body-local modeled physiology and Symbiont affordance as cases; preserve their distinct readiness status and exclude nonconforming physical capability.
- [ ] **QUEUED — Record unresolved common-model choices.** Identify decisions that belong in this semantic model versus family contracts or the later access/delivery design.
- [ ] **QUEUED — Review for accidental wire/transport design.** Remove any prescriptive field layout, encoding, event, endpoint or delivery guarantee.
- [ ] **QUEUED — Obtain architecture-owner disposition.** Keep the model Proposed until reviewed; domain-owner dispositions remain necessary for datum-level meanings.

**Current focus:** Establish the conceptual vocabulary and scope only. No implementation, schema or transport is authorized.

## 9. Related documents

- [Observation Architecture v1 — Target Design](observation-architecture-target-design-v1.md)
- [Observation Architecture — Design Inputs v1](observation-architecture-design-inputs-v1.md)
- [Observation Architecture — Current-State Assessment v1](observation-architecture-current-state-assessment-v1.md)

# Observation Semantic Model v1

**Status:** Approved conceptual model (Architecture Owner decision, 2026-10-09).
**Implementation state:** Semantic-family and concrete record/delivery implementations are not authorized by this conceptual model. Transport-neutral primitives may be integrated when they preserve this model and do not freeze a wire/API/transport contract.
**Scope:** Transport-independent conceptual semantics for observations in Observation Architecture v1.
**Authority:** This model refines the approved [Target Design](observation-architecture-target-design-v1.md) and accepted [Design Inputs](observation-architecture-design-inputs-v1.md). It does not amend the macro-architecture or authorize a concrete schema, wire format, API, transport, storage mechanism, or cutover.

## 1. Purpose and approval boundary

This document defines the approved shared semantics needed to describe observations across authority domains. It closes the conceptual model gate and authorizes work to proceed to semantic-family contracts, followed later by record/envelope design. Those are subsequent design steps: this approval does not select a concrete representation or delivery technology.

The model is observation-oriented and event-delivered where needed, not event-owned. A semantic claim is distinct from a delivery record, event, transport message, snapshot, materialized view, query result, or UI projection. Observation remains a passive projection: observing or delivering a claim must not change the organism's life or confer authority on Observation, its host, or its consumers.

This is a conceptual model, not a Python type system, JSON/protobuf schema, envelope layout, API, topic hierarchy, endpoint design, or transport contract. Future family and record designs must preserve these semantics and identify their own narrower scope and omissions explicitly.

## 2. Semantic claim and atomicity

The minimum semantic unit is a **SemanticClaim**: exactly one semantically interpretable assertion under one primary semantic authority and one epistemic basis.

A claim may carry a structured value when its components share semantic authority, epistemic basis, subject/scope, and effective domain time/revision, and the family contract defines them as meaningful together. Examples may include Body Pose, a Resource Pool State, Body Temperature, or a joint transform. Do not split a semantically indivisible quantity into artificial scalar claims.

Conversely, claims with different authorities, epistemic bases, subjects/scopes, or effective times/revisions remain independent even if they are delivered together. For example, an Embodiment-authoritative body pose, a Lab-derived confidence claim, and an Environment-authoritative terrain claim are separate claims. Therefore:

```text
delivery record != SemanticClaim
```

A delivery may contain multiple claims without making them one semantic assertion.

## 3. Subject, scope, and identity

Every claim identifies unambiguously what it is about. Depending on the family, a subject or scope may be an Organism, Embodiment episode, Body, Body part, World, World presence, Environment, Environment location/region, relationship, run/experiment scope, or another explicitly typed semantic subject.

There is no implicit universal identity. Identities are typed, issuer-scoped, and authority-aware. Cross-domain identity associations must be explicit. For example, `OrganismId`, `BodyId`, and `PresenceId` are distinct even when a temporary one-to-one association exists. A physical-part claim identifies the applicable Body/Embodiment identity, part identity, and morphology revision when relevant. List position is not persistent part identity unless an explicit morphology contract guarantees its stability.

Identity of an observation, when needed, is distinct from subject identity, event identity, and transport-message identity. Not every claim requires a globally permanent observation identity; replay, deduplication, lineage, or scientific evidence may require a stable identity within an explicitly declared issuer/scope.

## 4. Semantic authority, producer, and asserter

Each SemanticClaim has exactly one primary semantic authority: the domain that defines the claim's meaning and the authoritative state or contract that supports it. The currently recognized primary authorities are:

```text
ORGANISM
EMBODIMENT
ENVIRONMENT
WORLD
```

Observation does not become an authority by observing. Lab does not become an authority by recording. Modality does not automatically become an authority by transducing. A producer may materialize a representation whose meaning belongs to another authority when the relevant contract allows it.

Distinguish these roles:

- **Authority:** domain that defines the claim's meaning and supports its authoritative status.
- **Producer:** component that materializes or emits the representation.
- **Semantic asserter:** authority or contract boundary that backs the correctness of the represented domain meaning.
- **Measurement source:** phenomenon-facing source, instrument, sensor, receptor, or estimator involved in measurement.
- **Transport:** mechanism that carries a representation.
- **Consumer:** component that interprets or uses the claim.

Producer and semantic asserter may coincide, but this is not presumed. For example, Embodiment may own authoritative body state, an Observation adapter may produce its projection, and the Embodiment boundary may remain the semantic asserter. Lab may produce a `LAB_DERIVED` claim and be authority for that derivation without becoming authority for its source claims.

## 5. Epistemic basis and availability

Every claim preserves an explicitly distinguishable epistemic basis. The conceptual model recognizes at least:

```text
AUTHORITATIVE_STATE
DIRECT_MEASUREMENT
TRANSDUCED_MEASUREMENT
DOMAIN_DERIVED
LAB_DERIVED
ESTIMATE
INFERENCE
DECLARED_EXTERNAL_INPUT
```

Future contracts need not encode these names literally, but must preserve the distinctions relevant to interpretation. An estimate or inference must not be presented as authoritative state merely because its value agrees numerically with that state.

`NO_DATA`, `UNKNOWN`, `UNAVAILABLE`, and `NOT_APPLICABLE` are interpretability/availability states, not ordinary values of a magnitude. Do not encode absence by inventing numeric sentinel values.

Availability must distinguish at least:

```text
AVAILABLE
PARTIAL
STALE
UNAVAILABLE
UNSUPPORTED
UNKNOWN
```

`PARTIAL` identifies the covered or missing scope when material. `STALE` states the time/revision against which it is stale. Source unavailability and Observation-delivery unavailability are different: a delivery-plane failure does not make the source state ontologically unknown, and lost delivery is not semantic absence.

## 6. Domain time and revision

There is no universal `tick`. A claim is associated with the time and/or revision of the domain that determines its validity. Depending on a family, relevant context may include World causal tick, physics step/substep, Organism causal/developmental time, Embodiment episode/revision, Environment revision, or generation.

Host wall-clock time has no causal authority. It may be retained as observation, collection, or transport timestamp, or as performance metadata, but remains distinct from domain time. When interpretation depends on structural or semantic revision, that revision is explicit in the family semantics (for example, morphology revision, Environment revision, or semantic-contract revision). A claim must not silently be applied to a different effective time or revision.

## 7. Provenance and derivation lineage

Provenance must permit material reconstruction of the source state/input, transformation, effective configuration, and producer involved in a claim. A full provenance graph need not be embedded in the claim; stable references to provenance records are permitted.

For derived claims, preserve material parent claim/reference identities, source revisions, transformation identity/version, and effective configuration identity/hash. Semantic derivation lineage is distinct from a transport delivery path. Provenance may be scoped to what materially affects interpretation and reproducibility; it need not duplicate irrelevant history.

## 8. Semantic family, revision, units, and frames

Each semantic family has a stable identity independent of transport and a semantic revision identifying changes to its meaning. A revision change is compatible only when a consumer of the prior revision can continue to interpret the relevant claims correctly without semantic reinterpretation. Changes to meaning, units, reference-frame semantics, subject semantics, authority, epistemic interpretation, or required identity linkage are incompatible. Family/revision identity does not depend on HTTP, SSE, protobuf, or another transport.

Every physical magnitude has explicit units defined by its semantic family. Implicit or undocumented context-dependent units are not allowed. Dimensionless quantities are declared as such when not self-evident. Unit conversion is an explicit transformation from a source claim to a derived/transformed representation; it does not silently change source semantics.

Frame-dependent quantities identify the semantic frame necessary for interpretation, such as World, body, part-local, sensor, or Environment-local frame. Frame transformations preserve sufficient provenance and revision context to be reproducible. No global frame is assumed across authorities.

Physical parts use identity stable within the applicable morphology revision, such as a part identity together with that revision or an equivalent stable semantic identity. A list index is not a persistent identity unless the morphology contract explicitly guarantees that stability.

## 9. Measurement source

When measurement or transduction is involved, distinguish the phenomenon/subject, measurement source, transducer/instrument, producer, and semantic authority. Identify the measurement source when changing it could change claim meaning or comparability; examples include camera/sensor identity, Body receptor identity, simulated apparatus, or configured estimator. Source identity is not mandatory where it is irrelevant to the family semantics.

## 10. Snapshot and replay semantics

A snapshot is not, by default, a globally atomic snapshot of all Biopeia state. It declares its coherence scope. Conceptual scopes may include authority-coherent, World-causal-cut-coherent, or best-available composite views.

A snapshot may be called coherent with respect to a World causal cut only when every included claim is linked to the same committed cut or to revisions explicitly compatible with it. A composite without a common causal cut preserves the individual claim times/revisions and must not imply false simultaneity.

Observation replay means reproducing preserved observational claims/events according to their semantics. It does not imply causal re-execution of World or full deterministic simulation replay. Replay preserves claim identity when applicable, domain time/revision, semantic family/revision, provenance, and only the ordering guarantees actually provided. Scientific replay and causal runtime replay remain separate contracts.

## 11. Delivery guarantees

The semantic model does not mandate a transport. Any future stream/subscription delivery contract declares its ordering scope, duplication semantics, gap detection, completeness, and resume/replay capability. Global exactly-once delivery is not assumed.

For reliable streaming where required by a family, the default target is at-least-once capability, stable observation identity or sequence within a declared scope, explicit gap detection, and idempotent consumer support. Ephemeral/UI projections may use latest-value/lossy delivery if declared. Delivery loss is never reinterpreted as source-state absence.

## 12. Scientific evidence boundary

Observation produces or transports observations but does not thereby own scientific evidence custody. When an observation is admitted as scientific evidence, the distinct flow is:

```text
Observation claim
    -> Lab/scientific evidence admission
    -> provenance/evidence record
```

Scientific admission may add study, run, arm, protocol, or apparatus-configuration context without modifying the source claim.

## 13. Non-goals and subsequent design gates

This approval does not define concrete record/envelope fields or layouts, language interfaces, serialization, schema encoding, wire compatibility, event names/topics, subscription syntax, endpoints, cadence, storage, retention, or a transport. It does not authorize implementation or publication. Those choices require the subsequent semantic-family and record/envelope design work, which must preserve this model and remain consistent with the approved Target Design.

The approved macro-architecture remains:

```text
authoritative domain
    -> passive observation projection
    -> transport/presentation
```

## 14. Resolution record and checklist

The Architecture Owner resolved the conceptual choices in §§2–12 on 2026-10-09. The model gate is closed; this does not close family-specific contracts or the later record/envelope and delivery design gates.

- [x] Define claim atomicity, including structured values and separation of heterogeneous claims.
- [x] Define typed subject/scope and explicit cross-domain identity linkage.
- [x] Distinguish semantic authority, producer, asserter, measurement source, transport, and consumer.
- [x] Preserve epistemic basis, availability, domain time/revision, provenance, and lineage.
- [x] Define transport-independent family/revision, units, reference frames, and part identity semantics.
- [x] Distinguish snapshot coherence, observation replay, causal replay, and delivery guarantees.
- [x] Preserve the scientific evidence admission boundary and passive-observation invariant.
- [x] Confirm that this conceptual approval does not authorize concrete schema/API/transport/storage or family-specific implementation; compatible transport-neutral primitives remain separately reviewable.

**Current status:** Approved conceptual model. Next work may define semantic-family contracts. A later record/envelope design remains a separate gate; no transport is selected by this document.

## 15. Related documents

- [Observation Architecture v1 — Target Design](observation-architecture-target-design-v1.md)
- [Observation Architecture — Design Inputs v1](observation-architecture-design-inputs-v1.md)
- [Observation Architecture — Current-State Assessment v1](observation-architecture-current-state-assessment-v1.md)

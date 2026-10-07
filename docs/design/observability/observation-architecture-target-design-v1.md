# Observation Architecture v1 — Target Design

**Status:** Approved with refinements (architecture-owner disposition, 2026-10-07).
**Authoring authorization:** Project owner, 2026-10-07. This authorizes this target-architecture document only.  
**Implementation state:** Not started; no implementation is authorized.  
**Source inputs:** [Current-State Assessment](observation-architecture-current-state-assessment-v1.md) and [Design Inputs](observation-architecture-design-inputs-v1.md).  
**Scope:** Target architecture for operational observation. This is not a record/API specification, event taxonomy, endpoint/transport design, implementation plan, scientific evidence protocol, or cutover authorization.

## 1. Purpose and decision boundary

This document defines the architecture direction and boundaries approved to replace the current Lab-mediated operational observation path. It deliberately does not preserve legacy payloads, endpoints, replay behavior, snapshots, or frontend assumptions as compatibility contracts. The current implementation is evidence about source paths and failure modes, not a template for the target.

The target is **observation-oriented and event-delivered where consumers need live changes, not event-owned**. A semantic observation is distinct from its event delivery, snapshot inclusion, materialized/query projection, and UI representation. This design establishes architectural boundaries and leaves exact record schemas, delivery mechanics, endpoints and implementation for later gates.

The architecture owner approved this target architecture with refinements on 2026-10-07. That approval covers the architecture direction and boundaries recorded here only. It does not approve datum-level authority, final v1 publication, semantic record schemas, an envelope, event/snapshot/replay/delivery specifications, endpoints, transport, implementation or cutover.

## 2. Goals

The target architecture should:

1. Give each source domain authority over the meaning of the facts it owns.
2. Let the Lab observe, coordinate and derive explicitly Lab-owned analytical claims without silently rewriting source facts.
3. Preserve enough subject identity, domain time and lineage to interpret retained observations and their material derivations.
4. Support coherent current-state views and live delivery only to the extent justified by retained operational consumers.
5. Bound operational observation cost and isolate source behavior from observer load, failure, replay and UI activity.
6. Keep operational observation separate from private/debug access and durable scientific evidence.
7. Replace the current operational path completely after separate contract, implementation and cutover approvals.

## 3. Non-goals

This document does not:

- define concrete JSON/protobuf/Python record fields, an envelope, event names, or schema versioning rules;
- select HTTP, SSE, WebSocket, a broker, a database, or another transport/storage technology;
- require a durable event log or event-sourcing architecture;
- assign final semantic authority to unresolved physiological, physical, Environment, affordance or prediction fields;
- declare any blocked candidate family publishable;
- redesign organism interoception, action, physiology, scientific protocols or evaluator paths;
- authorize code changes, experiments, deployment, legacy deletion or cutover.

## 4. Governing architecture

### 4.1 Authority domains and subjects

For this Observation Architecture v1 design, the accepted governing authority domains are:

```text
Symbiont
Embodiment
Modality
Environment
bounded Lab-created semantics
```

These are domains that may define semantic claims. They do not assign ownership of each candidate datum. `Organism`, `Body`, `EmbodimentEpisode`, `EnvironmentInstance`/`World`, `Resource`, `Signal` and `Run` are subjects or context identities, not authority domains. UI is a consumer/presentation layer, not an authority for source facts.

The architecture keeps these roles distinct even where one component occupies more than one role:

```text
subject
semantic authority
measurement source
producer
observation-plane coordinator/host
consumer
```

An apparatus can supply a measured/simulated value without becoming an authority domain. A transport host can serve a record without owning its semantics. A derivation can remain domain-authoritative even when its inputs cross domains. Lab is authoritative only for semantic distinctions it creates (for example, a versioned analytical classification); hosting or presenting another domain's claim does not transfer that authority.

### 4.2 Source-to-consumer layers

The target separates five architectural layers:

```text
Source domains and apparatus
        ↓
Domain-owned observation production
        ↓
Semantic observation records
        ↓
Observation-plane coordination and access
        ↓
Lab projections and operational consumers
```

1. **Source domains** own their canonical state and semantic definitions. **Apparatus and sensors** simulate or measure values under an applicable domain contract; they are attributed measurement sources/producers, not additional authority domains. Physics3D/MuJoCo is an apparatus implementation, not a sixth authority domain.
2. **Domain-owned observation production** exposes bounded, intentional observations of domain state. It is not a raw object dump and must not require the Lab to reach into private runtime internals.
3. **Semantic observation records** express claims with an unambiguous primary semantic authority and epistemic interpretation. Explicit context (identity, time, measurement source, provenance) may be supplied by other roles, but must be attributed rather than hidden in the claim.
4. **Observation-plane coordination and access** composes eligible observations for operational consumers, manages the declared consistency/availability guarantees, and offers the access patterns justified by those consumers. It does not become the semantic owner of source observations.
5. **Lab projections and consumers** may join, classify, aggregate, compare or render inputs. Any newly introduced meaning is a separate Lab-derived claim with explicit inputs/configuration sufficient to interpret it; source observations remain available as distinct claims when retained.

### 4.3 Semantic observation is not delivery

The semantic observation model is the canonical representation **within the operational observation plane**; it does not supersede source-domain state or durable scientific evidence. An observation may be:

- delivered live as an event/update when a retained consumer requires it;
- included in a coherent or explicitly partial snapshot;
- materialized as current operational state;
- queried over bounded operational history;
- consumed by a Lab-derived projection.

These are access/materialization choices, not different authorities. A delivery batch or snapshot may contain heterogeneous observations so long as each member retains its own semantic claim and provenance. The target does not infer a durable event log, universal stream, broker, or exactly-once delivery from event-delivered updates.

## 5. Target invariants

The following constraints govern subsequent design. They derive from the accepted Design Inputs and must remain subject to the Constitution; they do not amend it.

1. **No hidden authority transfer.** Producer, measurement source, host and consumer do not acquire semantic authority by location or serialization.
2. **No heterogeneous semantic claim.** A record-level claim has one clear primary authority and epistemic interpretation. Context may be separately attributed. Batches/snapshots may group distinct claims.
3. **No implicit identity joins.** Similar field names or identifiers do not prove equality. An unresolved/conflicting link invalidates only the dependent association; independent observations remain valid in their evidenced scopes.
4. **Domain time is not delivery order.** Organism cycles, embodiment cycles, simulation steps/time and transport sequence are distinct unless an explicit relation is defined.
5. **Derivation preserves lineage.** Material domain- or Lab-derived claims must preserve or resolve the inputs and effective transformation/configuration needed for interpretation. Cross-domain inputs do not automatically make the result Lab-owned.
6. **No consumer-side hidden semantics.** A record must not depend on undocumented adapter/UI assumptions for its meaning, subject, clock, units, frames or transformation.
7. **Operational is not scientific evidence.** Operational history/materialization does not become durable, protocol-governed evidence by containing similar values.
8. **Passive external observation.** Observation remains read-only with bounded cost, isolated backpressure/failure and no observer-to-organism causal feedback. Organism-owned interoception/regulation is a distinct path.
9. **Full replacement.** The target creates no permanent legacy adapters, aliases, dual publication or compatibility promise. Differential comparison is allowed to classify intentional and unintended changes, not to require parity.

## 6. Approved ownership boundary for the Observation Plane

### 6.1 Alternatives considered

Three viable infrastructure boundaries were considered before the owner disposition:

| Option | Boundary | Benefits | Costs/risks |
|---|---|---|---|
| A. Lab-owned plane | Lab owns domain adapters, coordination, materialization and delivery. | Fits the current host and keeps operational machinery near consumers. | Risks reproducing current semantic reach-through and making Lab projections look source-canonical unless domain contracts are enforced. |
| B. Independent shared infrastructure | A standalone shared service/package owns coordination, materialization and delivery. | Separates observation infrastructure from Lab and could serve multiple hosts. | Adds deployment/dependency surface before multi-host need is established; may centralize concepts prematurely. |
| C. Domain producers with Lab coordination | Domains own semantic observation production; Lab owns operational composition, materialization and delivery for its consumers. | Preserves authority while reusing current Lab operational boundary; can later extract infrastructure without changing source semantics. | Requires explicit domain-facing observation contracts and careful limits on Lab composition; remains a Lab-hosted operational plane. |

### 6.2 Approved v1 boundary — Option C

**Decision — APPROVED FOR OBSERVATION ARCHITECTURE V1:** use Option C: source domains define and produce their own observations; Lab owns operational coordination, materialization and delivery for its consumers, plus explicitly Lab-derived claims. Infrastructure extraction into a standalone service/package is deferred until demonstrated deployment or multi-host value justifies it. Do not create an independent Observation service merely for conceptual purity.

This boundary does not authorize APIs or code changes. Lab coordination must not imply ownership of Symbiont, Embodiment, Modality or Environment semantics. Lab may create only its own attributed analytical meaning. The boundary is reversible at the infrastructure-host level without transferring semantic authority.

### 6.3 Domain-owned observation boundary

Each source domain should expose an intentional, bounded observation producer/port for retained claims. The Lab must not reconstruct canonical observations by inspecting arbitrary private runtime objects. This is a target architectural boundary, not authorization to add ports or APIs yet.

## 7. Cross-cutting models required by this architecture

These are architectural responsibilities. Their exact structures and specifications remain subsequent work.

### 7.1 Identity and association

Each retained observation must refer to a subject within an evidenced identity scope. Identity evidence must distinguish identifier kind/namespace, issuer, asserter, scope/lifetime, persistence/restore behavior and explicit links to other identities where such links are required. Identity resolution is a separate association operation; it must not silently replace an assertion with a preferred alias.

The current evidence distinguishes physical Body identity, Organism identity, EmbodimentEpisode identity, Lab run/catalog references, durable Environment instance identity, observer-session identity, projection-local entities and sample-local contacts. None may be collapsed by legacy field name. The target identity model must preserve conflicts and fail closed only for joins that depend on the unresolved link.

### 7.2 Time and ordering

The target uses typed domain-clock concepts rather than a context-free `tick`. Candidate clocks include organism cycle, embodiment cycle, simulation step, simulation time and Environment revision. A record may carry only clocks established for its source and family. Any cross-clock relation (same-cycle, sampled-after, applied-on-next-cycle, etc.) must be explicit and evidenced. Observation-plane ordering/sequence, if later required, is transport metadata and cannot substitute for a domain clock.

### 7.3 Provenance and derivation

Provenance is represented at the smallest level needed to avoid ambiguity, with inheritance only for demonstrably homogeneous subrecords. A material derivation may need links to multiple inputs and to an effective transformation/configuration revision. For causal conversion, distinguish source estimate, conversion, delivered causal input, application time and resulting domain state. This architecture does not require every intermediate scalar to be public; final publication is a scope decision.

### 7.4 Physical semantics

Retained physical observations must refer to an Embodiment-owned, backend-neutral semantic contract defining applicable quantity kinds, units, axis and reference-frame conventions, orientation representation, sampling/integration windows, part/joint identity and semantic version. Physics3D is the initial implementation to assess for conformance; simulator-specific values remain separately attributed. A second-backend conformance gate activates only when another concrete backend exists and applies per published capability. No family is made universal by being available in MuJoCo.

### 7.5 Availability and completeness

Consumers must be able to distinguish applicable states such as not observed, unavailable, unsupported, not applicable, partial, stale and lost due to a delivery gap. Exact status vocabulary and placement depend on later semantic record and delivery design. Missing fields must not be interpreted differently by hidden consumer conventions.

## 8. Coherence and operational access

Coherence is consumer-driven; the architecture does not provide a globally coherent snapshot by default. `ObservedFrame` is neither retained as a target type nor treated as a consistency oracle. It is evidence that some consumers may need a composed current-state view.

The proposed model is to distinguish:

- **independent observations**, valid within their own subject and domain-time scope;
- **composed views**, which state which inputs/revisions were combined and whether the view is coherent, partial or unresolved;
- **identity-dependent joins**, which are unavailable when a required identity link conflicts or is unresolved, without suppressing their independent inputs.

Before specifying any composed view, each retained consumer must state its participating observations, clocks/revisions, maximum acceptable skew, missing/partial behavior, and whether unresolved identity blocks composition. If no defensible common cut exists, expose the view as partial, asynchronous or unresolved rather than manufacturing coherence. Snapshot atomicity, watermarks, history bounds, replay and gap recovery remain later specification work; no current frame/replay guarantee is inherited.

## 9. Consumers and projections

Mind, Body, Development and operational diagnostics are consumers, not source authorities. Each retained consumer must declare the observations and explicitly attributed Lab derivations it needs. It must be rebuildable without direct runtime inspection, legacy payload assumptions or hidden identity/clock interpretation.

Lab may compute visual layout, labels, summaries, classifications, comparisons and aggregates where a legitimate operational need exists. If a projection introduces semantic meaning, retain its derivation inputs and classifier/transformation revision as appropriate, and label it as Lab-created semantics. A presentation-only arrangement need not become a public semantic observation.

The bounded frozen evidence scope is a test set, not an approved publication list:

| Candidate family | Current target-design treatment |
|---|---|
| Physical Body Pose / Joint Kinematics | Separate candidate claims by default. Body Pose has a proposed backend-neutral semantic contract in §9.1.1; it remains blocked pending Embodiment semantic-owner disposition, concrete test criteria and Physics3D conformance. Joint Kinematics remains separate and is not covered by §9.1.1. |
| Environment resource state | Candidate; blocked pending Environment/resource identity links, units/meaning and source mapping. |
| Body-local modeled physiology | Embodiment-authoritative, Body-scoped candidate by semantic-owner disposition; individual fields remain blocked for units, clock, lineage, consumer need and record readiness. No distinct portable Symbiont physiology claim is retained for v1. |
| Symbiont affordance state | Candidate; blocked pending subject/context identity, clock, lineage and domain-owner review. |
| Lab prediction-error band | Deferred/excluded from v1 by Lab semantic-owner disposition; may be reopened only on demonstrated retained operational need and the conditions in Design Inputs. |

Required cross-cutting identity, time, conditional provenance and run context are evaluated separately from these semantic families. This document does not freeze any field or final v1 family.

### 9.1 Candidate semantic-record boundaries (proposed; domain review pending)

The architecture owner authorized this bounded next activity: propose semantic boundaries for the frozen families and identify context that is conditional rather than part of the semantic claim. These are design candidates, not approved records, schemas, fields or publication commitments. A semantic record may group values that jointly express one domain-owned claim under one contract; it is not restricted to one primitive value.

| Frozen candidate | Proposed claim boundary | Primary authority candidate | Boundary/context rule | Required disposition before record freeze |
|---|---|---|---|---|
| Physical pose/kinematics | **Proposed split within this frozen family:** (a) Body pose claim for base/link position and orientation under one declared frame, orientation convention and sample; (b) joint-kinematics claim for position/velocity values keyed by stable joint identity and one declared sample. Do not imply that the two claims share a coherent sample merely because the current runtime emits them during one tick. Do not include COM, mass, force, contact, torque or work by implication. | Embodiment | Body pose context: identified Body/part, measurement source, physical-contract version, units, axes/frame, orientation convention and sampling reference. Joint-kinematics context: identified Body/joint, quantity kind, unit, axis/sign convention, physical-contract version and sampling reference. The current Physics3D trace establishes distinct acquisition paths/cadences and does not embed a sample clock in tick-end physical state; see [Current-State Assessment §9.5](observation-architecture-current-state-assessment-v1.md#95-physical-body--embodiment--environment-trace-first-upstream-pass). | This is a boundary proposal, not a record approval. Embodiment semantic owner must approve the claim grouping and backend-neutral meanings; Physics3D conformance, reliable Body/joint identity and per-claim temporal context remain required. Merge the groups only if the approved Embodiment contract defines a common coherent sample and interpretation. |
| Environment resource state | **Proposed boundary:** Environment-owned logical resource state (for example availability/remaining material, if its domain meaning is approved) is separate from (a) recipe/configuration identity and geometry, (b) apparatus-sampled physical realization, (c) Lab-derived organism-to-resource distance/progress, and (d) offered/accepted transfer or study/nursery support. Do not combine these into a single resource observation. | Environment for the logical resource-state claim; authority of any physical realization depends on its measured quantity contract. | Subject must be an explicitly identified EnvironmentInstance and Resource. Recipe fixture IDs, generated `fixture.N`, rebuild-unstable MuJoCo handles and observer `entity.N` are not interchangeable identities. Include a world revision/clock only when the claim's validity depends on it. The current source path exposes no explicit durable mapping from recipe/resource identity to observer entity; see [Current-State Assessment §9.5](observation-architecture-current-state-assessment-v1.md#95-physical-body--embodiment--environment-trace-first-upstream-pass) and [§9.6](observation-architecture-current-state-assessment-v1.md#96-physiology-homeostasis-and-metabolism-trace-first-upstream-pass). | This is a candidate-boundary proposal, not a resource record approval. Environment semantic owner must define which logical quantities constitute resource state and approve subject/link rules. Identity mapping, quantity meaning/units, revision/time and source conformance remain required; unsupported or unresolved quantities stay out. |
| Organism physiology state | A claim covers only a coherent group of physiological state values with the same semantic authority and lifecycle. Separate external embodied-work/resource inputs and apparatus measurements from resulting physiology state. Do not revive a heterogeneous `vitals` record. | Unresolved between Symbiont and Embodiment, potentially split by state | Organism/Body/EmbodimentEpisode association, applicable clock, units and re-embodiment lifecycle are conditional context and cannot be inferred from a shared container. | Domain-semantic owner(s) must determine ownership, lifecycle and grouping for each retained value before record freeze. |
| Symbiont affordance state | A claim represents affordance state produced within the Symbiont model for an explicitly bounded organism-in-context, not Environment opportunity or a Lab-computed affordance. | Symbiont | Include the relevant embodiment/context identity and domain clock; lineage may cross domains without transferring authority to Lab. | Symbiont semantic owner must confirm meaning, scope, clock and material inputs/lineage. |
| Lab prediction-error band | A Lab-created classification claim for a specified input value/window and classifier revision. Keep distinct from the underlying prediction error and from any Symbiont knowledge. | Lab | Subject is the analyzed observation/prediction context; input identity, window/clock and classifier revision are required when material. This remains a stress case only. | Lab owner must justify an operational consumer and finite-value/classifier behavior; otherwise exclude from v1. |

The table proposes boundaries, not final atomicity. If domain review shows a row contains multiple claims or lifecycles, split it. If it cannot be interpreted with explicit context and lineage, narrow or defer it. A record may include identity, time, measurement-source or provenance references from other roles, provided those references are explicitly attributed and do not become hidden semantic claims.

#### 9.1.1 Proposed Embodiment Physical Body Pose semantic contract

**Status: Proposed for Embodiment semantic-owner disposition; not approved and not record-ready.** This proposal is limited to the backend-neutral meaning of `embodiment.body_pose`. It does not define a wire schema, envelope, event, endpoint, transport, implementation or publication mechanism.

**Claim and authority.** Body Pose is an Embodiment-authoritative point-state claim of the physical position and orientation of exactly one identified Physical Body or one identified Physical Body part, at an identified Embodiment physical sampling instant and relative to an explicitly identified physical reference frame. A part pose is scoped to a Body. Part identity is meaningful only under that Body's physical-contract identity/revision; array order and backend indices are not semantic identity.

**Position and frames.** Position is the location of the origin of the subject's declared local physical frame relative to the origin of the declared reference frame. The proposed canonical quantity is length in metres (`m`); backends using other internal units must convert. The proposed external frame is the active Embodiment physical-world frame where the apparatus is instantiated. It is not implicitly equal to an Environment frame. The frame contract must state handedness, positive axes and up direction; this proposal selects right-handed Cartesian coordinates and `+Z` up, while leaving `+X`/`+Y` orientation to the concrete frame definition. Each Body/part's local-frame origin and orientation must be declared; center of mass is not implied.

**Orientation.** Orientation is the rotation from the subject's local physical frame into the declared reference frame. The proposed canonical representation is a normalized unit quaternion in `(x, y, z, w)` order, with `w` scalar; `q` and `-q` are equivalent. The contract must still set normalization tolerance and invalid/unavailable behavior. Euler angles are not canonical. Backends may convert from another internal representation.

**Sampling and time.** The claim is a point sample of physical state, not an interval average, command, intention, prediction, trajectory or presentation interpolation. It must identify an Embodiment-domain sampling reference. Organism cycle, transport sequence and presentation frame are distinct clocks; any relation to organism cycle is explicit and does not replace physical sample time. If derived/interpolated pose is ever admitted, it must be distinguishable from sampled physical state; the v1 candidate is sampled state. The concrete contract must define the sample clock/reference and any applicable freshness/availability limits.

**Identity and revision.** Body identity is stable for that physical Body's lifetime: same-Body restore preserves it; replacement/re-embodiment creates a new Body identity. Part identity is stable within the applicable physical Body contract. EmbodimentEpisode may be contextual but does not replace Body identity. No Lab alias or fallback may silently fill unresolved identity. Body Pose must reference a physical semantic-contract revision covering quantity meaning, units, frames, orientation, local frames, part identities and sampling semantics; checkpoint/state-schema versions are not substitutes.

**Availability and composition.** The semantic model must distinguish at least available, unsupported, not applicable, not observed, temporarily unavailable and stale; exact representation remains record design. A requested nonexistent part is not applicable; backend inability is unsupported; absent current sample is temporarily unavailable. Composed Body/part views must not combine samples from different instants while implying atomicity. Preserve individual sample references or mark the view asynchronous/partial.

**Epistemic limits and exclusions.** For a simulator-backed embodiment, the claim describes physical state represented by that apparatus, not independently measured external-world ground truth. Body Schema, Self Model, Environment entities, intended/predicted pose, joint kinematics, velocity, center of mass, mass, contact, force, torque, actuator effort, work and resource position are excluded and require separate admitted claims.

**Conformance proposal.** A backend may publish `embodiment.body_pose` only when it demonstrates compatible subject and local-frame identity, metres, explicit compatible reference frame, right-handed `+Z`-up axes, canonical quaternion semantics, explicit physical sampling reference, sampled-versus-interpolated distinction, physical-contract revision and availability behavior. Backend internals need not match. Undefined or non-conforming quantities are not published under this family.

**Readiness sequencing correction.** Identity and availability are prerequisites of conformance, so conformance cannot be assessed before their concrete contract/test criteria are resolved. After semantic-owner disposition, the bounded sequence is: (1) resolve concrete frame, quaternion-tolerance, sample-reference, identity and availability criteria; (2) map and test Physics3D against them; (3) decide final Body Pose record readiness. The proposal leaves quaternion tolerance, exact frame orientation and freshness limits open; they must not be inferred from MuJoCo or the existing World observer. No second backend is required.

The prior Embodiment disposition approves the authority boundary and separates Body Pose from Joint Kinematics, but does not approve these proposed units, frames, axes, orientation conventions, identities, clocks, availability semantics or contract revision. **No semantic-owner approval is inferred here.**

### 9.2 Conditional cross-cutting context

Cross-cutting context is attached only where needed to interpret or associate a claim; it is not a universal payload checklist and does not itself assign source authority.

| Context | Required when | Design constraint |
|---|---|---|
| Subject identity and links | Claim names an organism, Body, Environment instance, resource, signal, run or other entity; a consumer composes claims across namespaces. | Preserve identifier kind/namespace, issuer and asserter as needed. Explicit links are required for cross-namespace joins; unresolved/conflicting links invalidate only dependent composition. |
| Domain clock/revision | Meaning depends on when a source state was valid, sampled, derived or applied. | Use a typed clock/revision reference; distinguish source time from transport order. State cross-clock relations when material. |
| Measurement source and physical contract | Claim is measured/simulated or depends on physical units, frames, anatomy, sampling or integration. | Attribute apparatus separately from semantic authority and reference the contract that defines the quantity. |
| Derivation lineage/configuration | Claim is derived and inputs, transformation, effective configuration or application boundary materially affect interpretation. | Preserve/resolve all material parents and transformation identity; do not publish every intermediate merely to make lineage explicit. |
| Run/orchestration context | Operational interpretation or consumer association depends on a managed run/session. | Keep orchestration identity distinct from source subject identity; do not use a Lab run reference to silently assert domain identity. |
| Availability/completeness | Absence, unsupported capability, partial acquisition, stale state or delivery loss changes interpretation. | Represent the relevant condition explicitly in the later record/access specification rather than relying on consumer-specific omission rules. |

The candidate boundary activity is not complete until the proposed groups and conditional context have been reviewed against their domain semantics. Architecture approval does not substitute for those domain-semantic dispositions.

## 10. Non-interference and operational isolation

The implementation derived from this architecture must demonstrate, not merely declare:

- read-only access to source state, except for explicitly domain-owned internal observation mechanisms that are not the external Lab plane;
- bounded sampling, serialization, queues, history and per-consumer work;
- slow or disconnected consumers cannot block organism, physics or Environment progression;
- observer, logger, projection or transport failure cannot alter source state or future decisions;
- observation frequency and UI activity do not create a causal input to organism behavior;
- access control and data classification prevent private/debug or evaluator/ground-truth information from being presented as ordinary source observation.

Concrete budgets, tests and failure contracts are implementation/specification work. Constitution §§1–2 and §13 remain controlling, including Lab as apparatus, source/ground-truth separation and passive Observatory requirements.

## 11. Replacement and cutover boundary

The target is a complete replacement of the current operational observation path. The following are not compatibility commitments: `/api/organism`, `body`/`cognition`/`vitals` as canonical families, legacy Mind snapshots, `ObservedFrame`, existing replay/cursor rules, or current frontend assumptions. No production dual truth source or permanent adapter is planned.

Before a later cutover proposal can be approved, it must define and validate:

1. retained consumers can be reconstructed from approved target observations/projections;
2. source authority, identity, domain time, units/frames and required lineage are interpretable for every retained record;
3. coherent/partial view guarantees match consumer needs;
4. replay/loss/rebase behavior is explicit for consumers that need it;
5. observational non-interference and bounded failure isolation are tested;
6. operational materialization remains distinct from scientific evidence;
7. differential tests explain intentional semantic changes and identify accidental losses without requiring old/new parity;
8. all live legacy routes, payload assumptions and projections scheduled for removal have no remaining target consumer.

Passing these criteria would support a cutover proposal; it would not itself authorize implementation or deletion.

## 12. Decisions, proposals and open questions

### Accepted inputs governing this proposal

- Role distinctions, five-domain authority model for this design, event-delivered/not event-owned direction, identity conflict behavior, full replacement, operational/scientific separation, and non-interference are accepted as scoped inputs in Design Inputs §3.
- Candidate evidence scope is frozen in Design Inputs §4.2, but final semantic publication scope is not.

### Architecture-owner disposition — 2026-10-07

The architecture owner **approved the target architecture with refinements** on 2026-10-07. The accepted scope is architecture direction and boundaries only; it does not approve record schemas, datum-level authority assignments, final publication scope, event/snapshot/replay/delivery schemas, endpoints, transport, implementation, deployment, legacy deletion, cutover or scientific use.

The approved decisions are:

1. Adopt the five-layer source-to-consumer structure in §4.2 and the distinction among semantic authority, measurement source, producer, host/coordinator and consumer.
2. Treat semantic observation as the primary operational unit; deliver events only where required, without implying event sourcing, a durable log, broker or universal stream.
3. Let a semantic record express one primary claim/authority/epistemic interpretation, while permitting a coherent group of values; explicit context may have separately attributed origins.
4. Adopt **Option C for v1**: domain-owned semantics and observation production with Lab-owned operational coordination, materialization and delivery. Defer a standalone service/package until demonstrated deployment or multi-host value.
5. Require intentional domain observation boundaries; Lab must not reconstruct canonical claims by inspecting arbitrary private runtime objects. This is an architecture boundary, not API authorization.
6. Use explicit identity kinds, issuer/asserter, links, conflict visibility and fail-closed dependent joins; independent observations remain valid.
7. Use typed domain time and explicit material cross-clock relations; do not invent a universal tick.
8. Preserve material derivation lineage and effective transformation/configuration where needed for interpretation; intermediate values need not all be public.
9. Require backend-neutral physical semantics for retained physical families, with Physics3D as the first conformance implementation; the multi-backend gate remains dormant until a second backend exists.
10. Make coherence consumer-driven, not a global snapshot guarantee. Consumers must specify participants, clocks/revisions, skew, partial behavior and identity requirements; expose partial/asynchronous/unresolved views rather than manufacturing coherence.
11. Distinguish relevant availability/completeness conditions; exact vocabulary is later specification work.
12. Treat operational consumers as consumers of source observations plus explicit Lab derivations; do not permit hidden assumptions or implicit joins.
13. Permit Lab analytical claims only for a legitimate operational need, with explicit meaning, known inputs, material revision, clear Lab attribution, and no presentation as organism knowledge. The prediction-error band remains a stress case only.
14. Require demonstrated observational non-interference under the Constitution.
15. Keep operational observation separate from durable scientific evidence.
16. Fully replace the existing operational path; legacy interfaces are not compatibility commitments. Differential comparison is validation only.
17. Ratify the bounded families in §9 as a design test set, not a publication catalog.

Accordingly, target architecture status is **Approved** for the scope above. The next authorized activity is candidate semantic-record boundary/context design and domain-semantic review. Record-level readiness, final v1 records, transport, implementation and cutover remain separate gates.

### Approved direction and remaining record work

- Option C is approved for v1 as stated in §6.2. Standalone infrastructure extraction is deferred pending demonstrated need.
- Semantic observation is the primary operational model; delivery/snapshot/query/projection are access or composition mechanisms.
- Coherence is consumer-driven. Partial/asynchronous/unresolved composition is required where a defensible coherent cut cannot be supported.

### Deliberately unresolved

- Datum-level semantic authorities and final v1 family/field publication.
- Exact observation-record atomicity and mandatory versus conditional metadata.
- Concrete identifier formats, issuers, link authority and conflict representation.
- Concrete typed clock representation and cross-clock relation rules.
- Physical quantity catalog and Physics3D conformance results.
- Physiology ownership and re-embodiment fate for each retained state.
- Public representation of causal conversions and their effective configuration provenance.
- Concrete consumer requirements for any composed view, including participants, clocks/revisions, skew and partial behavior.
- Availability vocabulary, operational retention, materialization, replay/gap recovery and delivery guarantees.
- Concrete privacy/access policy, performance budgets, tests, endpoint/transport and cutover plan.

An unresolved issue may narrow or defer a family; it must not be filled by assuming current code is normative.

## 13. Consequences and risks

### Expected benefits

- Source-domain meaning is not conflated with adapters, Lab hosting or UI presentation.
- Identity, time and derivation ambiguity are treated as architectural concerns before records are frozen.
- Multiple access patterns can share semantic observations without making events the source of truth.
- The target remains reversible at the infrastructure-host boundary and does not require a broker or second backend.

### Costs and risks

- Domain observation ports and semantic contracts require explicit ownership and additional tests.
- Lab coordination remains a potential semantic choke point unless source claims and Lab derivations stay distinguishable.
- Cross-source coherent views may be expensive or impossible at some required skew; consumers may need partial views or reduced scope.
- Full replacement requires deliberate consumer reconstruction and intentional loss/change review; parity cannot be assumed.
- Without final datum-level authority and record-level lineage, this proposal is not ready to become a contract specification.

## 14. Next gates

The sequence is intentionally staged:

```text
Approved target architecture
    → candidate semantic-record boundaries/context and domain-owner review
    → record-level evidence/interpretability and final v1 scope
    → Envelope Readiness
    → event/snapshot/materialization/replay/delivery/transport specification
    → separate implementation authorization
    → implementation and validation
    → separately approved full replacement/cutover
```

Target architecture approval does not require final datum-level authority or record readiness, and does not approve records, transport or implementation. Record readiness does not authorize code. Implementation validation does not imply scientific acceptance.

## 15. Checklist

Work one bounded item at a time. `Current focus` is explicitly marked; it is not inferred from the first unchecked item. Keep one sequential item `IN PROGRESS` at most. New evidence or out-of-scope defects discovered while working should be added to the relevant checklist/future-analysis notes without silently widening the active item.

- [x] **DONE (2026-10-07) — Record target-design authorization and boundaries.** Project owner authorized authoring this architecture document only. No record/API, endpoint, transport, implementation or cutover authorization is implied.
- [x] **DONE (2026-10-07) — Perform internal consistency review of the target draft.** Clarified that source domains own semantic state while apparatus/sensors are measurement sources or producers, and that the observation model is canonical only within the operational plane, not a replacement for domain state or scientific evidence. This is document review, not owner disposition.
- [x] **DONE (2026-10-07) — Record architecture-owner disposition of the target architecture.** Approved with refinements: Option C for v1, domain-owned observation boundaries, semantic observation as primary unit, consumer-driven coherence, explicit identity/time/lineage, and full replacement. Approval is limited to architecture direction/boundaries; record schemas, datum authority, final publication, transport, implementation and cutover remain unapproved.
- [x] **DONE (2026-10-07) — Assess physical pose/kinematics claim boundary.** Against Assessment §9.5, propose separate Body-pose and joint-kinematics claims by default because current acquisition paths and sampling semantics differ. This is only a within-family boundary proposal; it does not approve fields, units/frames, datum authority, publication, physical-contract readiness or Body/joint identity links.
- [x] **DONE (2026-10-07) — Assess Environment resource claim boundary.** Against Assessment §§9.5–9.6, separate logical Environment resource state from recipe/configuration, apparatus realization, Lab-derived spatial metrics, transfer, and study/nursery support. This proposal does not approve a resource field set, units, canonical resource identity/link, or publication.
- [x] **DONE (2026-10-07) — Draft backend-neutral Physical Body Pose semantics.** §9.1.1 records a proposed Embodiment contract for claim, subject/frame, units, orientation, sampling/time, identity/revision, availability, exclusions and conformance. This is a proposal only; its semantic choices remain unapproved.
- [ ] **IN PROGRESS — Obtain Embodiment semantic-owner disposition for Physical Body Pose v1.** Review §9.1.1 and explicitly accept, revise or reject its proposed semantic choices and identify unresolved criteria. The earlier authority-boundary approval is not approval of this contract.
- [ ] **QUEUED — Assess Physics3D conformance and final Body Pose record readiness.** After semantic-owner disposition, resolve concrete test criteria (frame orientation, quaternion tolerance, sample reference, identity and availability), map/test Physics3D, then assess interpretability and retain only conforming quantities. No second backend is required.
- [ ] **QUEUED — Continue candidate semantic-record boundaries for the next family.** Resume the bounded evidence scope only after the current Body Pose disposition/conformance item is closed; obtain relevant domain-semantic dispositions without inferring final schemas or publication.
- [ ] **QUEUED — Establish record readiness and final v1 scope.** Complete record-level evidence and interpretability review: resolve or exclude ambiguous identity, clocks, units/frames, availability and derivation/configuration lineage; confirm consumer need; remove, split or defer unresolved records. This precedes Envelope Readiness.
- [ ] **QUEUED — Establish Envelope Readiness.** Demonstrate representative cases, consumer sufficiency, consumer-driven coherent/partial view requirements, scientific separation and non-interference against the approved models.
- [ ] **QUEUED — Specify event, snapshot, materialization, replay, gap recovery and transport.** Begin only after record semantics and Envelope Readiness are dispositioned. Do not revive the superseded Symbiont Telemetry Event API without an explicit reopening decision.
- [ ] **QUEUED — Prepare implementation and cutover proposal.** Separate authorization, implementation validation, consumer migration, legacy deletion and operational cutover.

**Current focus:** Obtain Embodiment semantic-owner disposition for the proposed Physical Body Pose contract in §9.1.1. The architecture is approved only for its direction and boundaries; this focus does not authorize record schemas, transport, implementation or cutover.

### Dormant future gate

- **BLOCKED / dormant — Validate multi-backend semantic conformance.** Activate only when another concrete Embodiment backend is ready to publish a family defined by the backend-neutral physical contract. Evaluate conformance per overlapping capability; internal simulator equivalence is not required. This is not on the v1 critical path and requires no synthetic backend.

### Future analysis notes (outside current target-architecture drafting focus)

- No new source-code defect is asserted by this target proposal. Defects identified during the AS-IS investigation remain recorded in the Current-State Assessment future-analysis notes and are not implementation authorization.
- **Documentation reconciliation:** The candidate table and Design Inputs still contain older candidate statuses in places, including generic physiology ownership and the Lab prediction-error stress case. Reconcile those summaries against the recorded Embodiment/Symbiont and Lab semantic-owner dispositions before considering the broader candidate table closed; this is outside the current Body Pose contract-disposition item.

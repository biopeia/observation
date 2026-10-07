# Observation Architecture v1 — Target Design

**Status:** Proposed; architecture-owner review pending.  
**Authoring authorization:** Project owner, 2026-10-07. This authorizes this target-architecture document only.  
**Implementation state:** Not started; no implementation is authorized.  
**Source inputs:** [Current-State Assessment](observation-architecture-current-state-assessment-v1.md) and [Design Inputs](observation-architecture-design-inputs-v1.md).  
**Scope:** Target architecture for operational observation. This is not a record/API specification, event taxonomy, endpoint/transport design, implementation plan, scientific evidence protocol, or cutover authorization.

## 1. Purpose and decision boundary

This document proposes the architecture that replaces the current Lab-mediated operational observation path. It deliberately does not preserve legacy payloads, endpoints, replay behavior, snapshots, or frontend assumptions as compatibility contracts. The current implementation is evidence about source paths and failure modes, not a template for the target.

The target is **observation-oriented and event-delivered where consumers need live changes, not event-owned**. A semantic observation is distinct from its event delivery, snapshot inclusion, materialized/query projection, and UI representation. This design establishes architectural boundaries and leaves exact record schemas, delivery mechanics, endpoints and implementation for later gates.

The design remains Proposed. The architecture-owner disposition in Design Inputs accepts scoped constraints; it does not approve this target architecture. No datum-level authority, final v1 publication set, protocol, implementation or cutover is approved here.

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

## 6. Proposed ownership boundary for the Observation Plane

### 6.1 Alternatives

Three viable infrastructure boundaries remain under target review:

| Option | Boundary | Benefits | Costs/risks |
|---|---|---|---|
| A. Lab-owned plane | Lab owns domain adapters, coordination, materialization and delivery. | Fits the current host and keeps operational machinery near consumers. | Risks reproducing current semantic reach-through and making Lab projections look source-canonical unless domain contracts are enforced. |
| B. Independent shared infrastructure | A standalone shared service/package owns coordination, materialization and delivery. | Separates observation infrastructure from Lab and could serve multiple hosts. | Adds deployment/dependency surface before multi-host need is established; may centralize concepts prematurely. |
| C. Domain producers with Lab coordination | Domains own semantic observation production; Lab owns operational composition, materialization and delivery for its consumers. | Preserves authority while reusing current Lab operational boundary; can later extract infrastructure without changing source semantics. | Requires explicit domain-facing observation contracts and careful limits on Lab composition; remains a Lab-hosted operational plane. |

### 6.2 Proposed direction (not approved)

**Proposal:** use Option C for the first operational target increment: source domains define and produce their own observations; Lab coordinates and serves only the observations needed by its retained operational consumers, plus explicitly Lab-derived claims. Keep infrastructure extraction as a deployment choice, not a prerequisite for semantic separation.

This is a proposal, not an architecture-owner disposition. It is motivated by the accepted domain boundaries, the absence of demonstrated need for a standalone service, and reversibility: an in-process Lab coordinator can later be moved without transferring semantic authority. Before approval, review that Lab composition cannot leak evaluator/ground-truth labels into organism-facing paths or feed observation-derived semantics back into the organism.

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

The architecture requires an explicit consistency promise only for consumers that demonstrate a need for it. The target should not preserve `ObservedFrame` as a structure merely because it exists today; preserve the requirement it evidences: some consumers may need a coherent multi-source cut.

The proposed model is to distinguish:

- **independent observations**, valid within their own subject and domain-time scope;
- **composed views**, which state which inputs/revisions were combined and whether the view is coherent, partial or unresolved;
- **identity-dependent joins**, which are unavailable when a required identity link conflicts or is unresolved, without suppressing their independent inputs.

Before specifying snapshots/watermarks, each retained consumer must state the maximum acceptable skew or consistency requirement and the source clocks/revisions involved. If no defensible common cut exists, expose a partial/asynchronous view rather than claiming coherence. Snapshot atomicity, watermarks, history bounds, replay and gap recovery remain to be specified after record readiness; no current frame/replay guarantee is inherited.

## 9. Consumers and projections

Mind, Body, Development and operational diagnostics are consumers, not source authorities. Each retained consumer must declare the observations and explicitly attributed Lab derivations it needs. It must be rebuildable without direct runtime inspection, legacy payload assumptions or hidden identity/clock interpretation.

Lab may compute visual layout, labels, summaries, classifications, comparisons and aggregates where a legitimate operational need exists. If a projection introduces semantic meaning, retain its derivation inputs and classifier/transformation revision as appropriate, and label it as Lab-created semantics. A presentation-only arrangement need not become a public semantic observation.

The bounded frozen evidence scope is a test set, not an approved publication list:

| Candidate family | Current target-design treatment |
|---|---|
| Physical pose/kinematics | Candidate; blocked pending backend-neutral semantics, Physics3D conformance and identity/context readiness. |
| Environment resource state | Candidate; blocked pending Environment/resource identity links, units/meaning and source mapping. |
| Organism physiology state | Candidate; blocked pending domain-semantic disposition, re-embodiment/lifecycle rules, units/clocks/lineage. |
| Symbiont affordance state | Candidate; blocked pending subject/context identity, clock, lineage and domain-owner review. |
| Lab prediction-error band | Architecture stress case only; not approved for publication and may be excluded if need/semantics/readiness do not justify it. |

Required cross-cutting identity, time, conditional provenance and run context are evaluated separately from these semantic families. This document does not freeze any field or final v1 family.

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

### Proposed target direction requiring review

- Domain-owned observation semantics and producers, coordinated/materialized/served by Lab for its operational consumers (Option C in §6).
- Semantic observation as primary model; delivery/snapshot/query/projection as derived access mechanisms.
- Explicit partial/asynchronous composed views where a defensible coherent cut is unavailable.

### Deliberately unresolved

- Datum-level semantic authorities and final v1 family/field publication.
- Exact observation-record atomicity and mandatory versus conditional metadata.
- Concrete identifier formats, issuers, link authority and conflict representation.
- Concrete typed clock representation and cross-clock relation rules.
- Physical quantity catalog and Physics3D conformance results.
- Physiology ownership and re-embodiment fate for each retained state.
- Public representation of causal conversions and their effective configuration provenance.
- Observation Plane ownership approval and whether its host is Lab or extracted infrastructure.
- Which consumers require coherent cuts and their skew/consistency bounds.
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
Proposed target architecture
    → architecture-owner review/disposition
    → refine target architecture from review
    → candidate semantic record definitions and domain-owner review
    → record-level evidence/interpretability and final v1 scope
    → Envelope Readiness
    → event/snapshot/materialization/replay/delivery/transport specification
    → separate implementation authorization
    → implementation and validation
    → separately approved full replacement/cutover
```

Architecture approval does not approve records, transport or implementation. Record readiness does not authorize code. Implementation validation does not imply scientific acceptance.

## 15. Checklist

Work one bounded item at a time. `Current focus` is explicitly marked; it is not inferred from the first unchecked item. Keep one sequential item `IN PROGRESS` at most. New evidence or out-of-scope defects discovered while working should be added to the relevant checklist/future-analysis notes without silently widening the active item.

- [x] **DONE (2026-10-07) — Record target-design authorization and boundaries.** Project owner authorized authoring this architecture document only. No record/API, endpoint, transport, implementation or cutover authorization is implied.
- [x] **DONE (2026-10-07) — Perform internal consistency review of the target draft.** Clarified that source domains own semantic state while apparatus/sensors are measurement sources or producers, and that the observation model is canonical only within the operational plane, not a replacement for domain state or scientific evidence. This is document review, not owner disposition.
- [ ] **IN PROGRESS — Review and disposition the proposed target architecture.** Review the layer boundaries, Option C infrastructure proposal, coherence approach and replacement gates. Record accepted/revised/rejected choices and scope; do not infer approval from the authorization to author.
- [ ] **QUEUED — Define candidate semantic record boundaries and conditional context.** Use only the frozen evidence scope; each record must state one primary semantic claim and explicit cross-cutting context. Obtain domain-semantic dispositions for retained source-domain claims.
- [ ] **QUEUED — Complete record-level evidence and interpretability review.** Resolve or exclude ambiguous identity, clocks, units/frames, availability and derivation/configuration lineage; freeze final v1 semantic scope only after gates pass.
- [ ] **QUEUED — Establish Envelope Readiness.** Demonstrate representative cases, consumer sufficiency, coherent/partial view requirements, scientific separation and non-interference against the proposed models.
- [ ] **QUEUED — Specify event, snapshot, materialization, replay, gap recovery and transport.** Begin only after record semantics and Envelope Readiness are dispositioned. Do not revive the superseded Symbiont Telemetry Event API without an explicit reopening decision.
- [ ] **QUEUED — Prepare implementation and cutover proposal.** Separate authorization, implementation validation, consumer migration, legacy deletion and operational cutover.

**Current focus:** Review and disposition the proposed target architecture. This document remains Proposed; the TO-BE authoring authorization does not constitute architecture approval or implementation permission.

### Dormant future gate

- **BLOCKED / dormant — Validate multi-backend semantic conformance.** Activate only when another concrete Embodiment backend is ready to publish a family defined by the backend-neutral physical contract. Evaluate conformance per overlapping capability; internal simulator equivalence is not required. This is not on the v1 critical path and requires no synthetic backend.

### Future analysis notes (outside current target-architecture drafting focus)

- No new source-code defect is asserted by this target proposal. Defects identified during the AS-IS investigation remain recorded in the Current-State Assessment future-analysis notes and are not implementation authorization.

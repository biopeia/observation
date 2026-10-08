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

**Macro-architecture status:** Frozen for Observation Architecture v1 by project-owner disposition on 2026-10-08. This freeze covers the source-domain observation boundaries, domain-to-plane publication, Lab-hosted operational Observation Plane, consumer access direction, and the observation-oriented/event-delivered-where-needed distinction in §§4–8. It does not freeze semantic records, family conformance, identity/clock/provenance representations, availability vocabulary, snapshot/replay/delivery contracts, or transport. Those remain subsequent design work and do not reopen the macro-architecture absent an explicit owner decision.

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

Each source domain should expose one intentional observation boundary for retained claims. That boundary may contain multiple explicitly typed semantic families; it is not one aggregate record and does not determine their transport or storage. The Lab must not reconstruct canonical observations by inspecting arbitrary private runtime objects. This is a target architectural boundary, not authorization to add ports or APIs yet.

### 6.4 Source publication and consumer access

**Architecture-owner disposition — ACCEPTED, SCOPED (2026-10-07).** Source publication and consumer access are independent directional contracts:

```text
source publication: domain → Observation Plane
consumer access:    consumer ↔ Observation Plane
```

Source-to-plane publication is bounded, non-blocking and independent of active consumer demand. A UI opening/closing, subscriber count, logger presence or consumer polling frequency must not start, stop or alter source observation semantics or cadence. This does not require every family to publish every tick: a family may define an appropriate change-, cadence-, lifecycle- or revision-based rule, but that rule cannot be derived from downstream demand.

Consumers access observations through the plane using a later-specified mode such as current/materialized state, point query, bounded history, subscription, composed view or export. A subscription requests delivery from the plane; it is not an observation, source command, permission to activate domain work or organism stimulus. Periodic Lab polling of private source state is not the default update path.

A read followed by subscription is not presumed atomic or gap-free. The later delivery design must provide a watermark/reconciliation guarantee or expose the possible race. Zero consumers do not require unlimited retention; materialization, coalescing, short history and eviction remain bounded policy decisions. Source-to-plane queues and failure behavior must ensure slow/unavailable consumers or plane failure cannot block source progression, change source state or create unbounded memory.

Normal operational consumers do not establish independent paths into private source internals. The approved path is domain observation boundary → Observation Plane → consumers. Private/debug access remains separately governed. This disposition does not select callback/queue mechanics, sync/async interfaces, process boundary, broker, protocol, file format, buffering, history duration or delivery guarantee; it authorizes no API or implementation.

### 6.5 Semantic namespace, not transport namespace

The domain observation boundary may organize retained claims under semantic families and subtypes, for example `embodiment.body_pose` or `environment.resource_state`. Such names classify meaning and authority scope; they do not prescribe URLs, broker topics, subscription syntax, file paths or endpoint structure. One boundary may expose many typed families. Delivery and storage mechanisms remain outside this semantic namespace.

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
| Physical Body Pose / Joint Kinematics | Separate candidate claims by default. Body Pose has an Embodiment-accepted backend-neutral semantic contract in §9.1.1; it remains blocked pending Physics3D conformance and record-readiness review. Joint Kinematics remains separate and is not covered by §9.1.1. |
| Environment resource state | Candidate; blocked pending Environment/resource identity links, units/meaning and source mapping. |
| Body-local modeled physiology | Embodiment-authoritative, Body-scoped candidate by semantic-owner disposition; individual fields remain blocked for units, clock, lineage, consumer need and record readiness. No distinct portable Symbiont physiology claim is retained for v1. |
| Symbiont affordance state | Candidate; blocked pending subject/context identity, clock, lineage and domain-owner review. |
| Lab prediction-error band | Deferred/excluded from v1 by Lab semantic-owner disposition; may be reopened only on demonstrated retained operational need and the conditions in Design Inputs. |

Required cross-cutting identity, time, conditional provenance and run context are evaluated separately from these semantic families. This document does not freeze any field or final v1 family.

### 9.1 Candidate semantic-record boundaries (proposed; domain review pending)

The architecture owner authorized this bounded next activity: propose semantic boundaries for the frozen families and identify context that is conditional rather than part of the semantic claim. These are design candidates, not approved records, schemas, fields or publication commitments. A semantic record may group values that jointly express one domain-owned claim under one contract; it is not restricted to one primitive value.

| Frozen candidate | Proposed claim boundary | Primary authority candidate | Boundary/context rule | Required disposition before record freeze |
|---|---|---|---|---|
| Physical pose/kinematics | **Proposed split within this frozen family:** (a) Body pose claim for base/link position and orientation under one declared frame, orientation convention and sample; (b) joint-kinematics claim for position/velocity values keyed by stable joint identity and one declared sample. Do not imply that the two claims share a coherent sample merely because the current runtime emits them during one tick. Do not include COM, mass, force, contact, torque or work by implication. | Embodiment | Body pose context: identified Body/part, measurement source, physical-contract version, units, axes/frame, orientation convention and sampling reference. Joint-kinematics context: identified Body/joint, quantity kind, unit, axis/sign convention, physical-contract version and sampling reference. The current Physics3D trace establishes distinct acquisition paths/cadences and does not embed a sample clock in tick-end physical state; see [Current-State Assessment §9.5](observation-architecture-current-state-assessment-v1.md#95-physical-body--embodiment--environment-trace-first-upstream-pass). | Body Pose semantic meaning and claim boundary are accepted by Embodiment in §9.1.1. Physics3D conformance and Body Pose record readiness are not demonstrated. Joint Kinematics remains outside that disposition. Keep each capability out of a canonical record until its own contract, identity and temporal context pass readiness. |
| Environment resource state | **Proposed boundary:** Environment-owned logical resource state (for example availability/remaining material, if its domain meaning is approved) is separate from (a) recipe/configuration identity and geometry, (b) apparatus-sampled physical realization, (c) Lab-derived organism-to-resource distance/progress, and (d) offered/accepted transfer or study/nursery support. Do not combine these into a single resource observation. | Environment for the logical resource-state claim; authority of any physical realization depends on its measured quantity contract. | Subject must be an explicitly identified EnvironmentInstance and Resource. Recipe fixture IDs, generated `fixture.N`, rebuild-unstable MuJoCo handles and observer `entity.N` are not interchangeable identities. Include a world revision/clock only when the claim's validity depends on it. The current source path exposes no explicit durable mapping from recipe/resource identity to observer entity; see [Current-State Assessment §9.5](observation-architecture-current-state-assessment-v1.md#95-physical-body--embodiment--environment-trace-first-upstream-pass) and [§9.6](observation-architecture-current-state-assessment-v1.md#96-physiology-homeostasis-and-metabolism-trace-first-upstream-pass). | This is a candidate-boundary proposal, not a resource record approval. Environment semantic owner must define which logical quantities constitute resource state and approve subject/link rules. Identity mapping, quantity meaning/units, revision/time and source conformance remain required; unsupported or unresolved quantities stay out. |
| Body-local modeled physiology | A claim covers only a coherent group of modeled physiological values describing one physical Body, with a common authority and lifecycle. Separate external embodied-work/resource inputs and apparatus measurements from resulting Body physiology. Do not revive a heterogeneous `vitals` record. | Embodiment | Body identity, applicable clock, units/meaning, lineage and any necessary EmbodimentEpisode association are conditional context. Same-Body restore preserves state; replacement Body does not inherit prior current physiology. | Semantic ownership/lifecycle are accepted by Embodiment and portable Symbiont physiology is excluded/deferred. Individual values remain blocked until quantity meaning, units, clock, lineage, operational consumer need and record readiness are resolved. Checkpoint placement does not transfer authority. |
| Symbiont affordance state | A claim represents affordance state produced within the Symbiont model for an explicitly bounded organism-in-context, not Environment opportunity or a Lab-computed affordance. | Symbiont | Include the relevant embodiment/context identity and domain clock; lineage may cross domains without transferring authority to Lab. | Symbiont semantic owner must confirm meaning, scope, clock and material inputs/lineage. |
| Lab prediction-error band | Legacy Lab-created classification claim, not retained in v1. Keep distinct from the underlying prediction error and from any Symbiont knowledge. | Lab, only if explicitly reopened | Any future proposal must identify the analyzed observation/prediction context, inputs, clock and classifier revision where material. | Deferred/excluded by Lab semantic-owner disposition because a retained operational consumer need was not demonstrated. Reopen only under the conditions in Design Inputs §3; no current category or threshold is approved. |

The table proposes boundaries, not final atomicity. If domain review shows a row contains multiple claims or lifecycles, split it. If it cannot be interpreted with explicit context and lineage, narrow or defer it. A record may include identity, time, measurement-source or provenance references from other roles, provided those references are explicitly attributed and do not become hidden semantic claims.

#### 9.1.1 Embodiment Physical Body Pose semantic contract v1

**Status: Accepted by the Embodiment semantic owner with refinements on 2026-10-07; not record-ready.** This section records the backend-neutral meaning of `embodiment.body_pose`. It does not define a record schema, wire fields, envelope, event, endpoint, transport, implementation or publication mechanism.

**Claim and authority.** Body Pose is an Embodiment-authoritative point-state claim of the physical position and orientation of exactly one identified Physical Body or one identified Physical Body part, at an identified Embodiment physical-state instant and relative to an explicitly identified physical reference frame. A part pose is scoped to a Body. Body identity, part identity and compatible physical-contract revision are independent identity/context dimensions; part identity is interpreted within the applicable contract. Array order and backend indices are not semantic identity.

**Position and frames.** Position is the location of the origin of the subject's declared local physical frame relative to the origin of the declared reference frame. Quantity kind is length and the canonical observation unit is metre (`m`); backends using other internal units must explicitly convert. Every claim identifies an Embodiment Physical Reference Frame, which need not be called a world frame. For the normal external v1 representation this is the active Embodiment physical reference frame in which the apparatus Body is instantiated. It is not implicitly identical to an Environment frame. The canonical observation convention is right-handed Cartesian coordinates with `+Z` up; the concrete frame definition must state positive `+X` and `+Y`. Backend internals may differ if converted explicitly. Each Body/part local-frame origin and orientation must be declared; center of mass is not implied.

**Orientation.** Orientation is the rotation from the subject's declared local physical frame into the declared reference frame. The canonical representation is a unit quaternion in `(x, y, z, w)` order, with `w` scalar; `q` and `-q` are equivalent, so a sign change alone is not a physical orientation change. The contract must set normalization tolerance and invalid/unavailable behavior. Euler angles are not canonical. Backends may convert from another internal representation if semantics are preserved.

**Sampling and time.** The claim is a point sample of physical state, not an interval average, trajectory, intended/commanded/predicted pose or render interpolation. It must identify an Embodiment Physical Sample Reference sufficient to establish when the physical state was valid; it does not require every backend to have a simulation step or simulation time. Organism cycle, presentation frame and observation-plane sequence are distinct. Any material relationship is explicit and does not replace physical sample time. Derived/interpolated pose, if later exposed, is distinguishable from sampled state; the v1 canonical candidate is sampled state.

**Identity and revision.** Body identity is stable for that physical Body's lifetime: same-Body restore preserves it; replacement Body/re-embodiment creates a new Body identity. Part identity is stable within the applicable physical Body contract and Body instance. Compatibility across contract revisions must be declared; absent that declaration, same names do not prove same semantics. EmbodimentEpisode may be contextual but does not replace Body or part identity. No Lab alias or fallback may silently fill unresolved identity. Body Pose references a physical semantic-contract revision covering quantity meaning, units, frames, orientation, local frames, part identity semantics and sampling semantics; checkpoint/state-schema versions are not substitutes.

**Availability and composition.** The semantic model distinguishes materially different states including available, unsupported, not applicable, not observed, temporarily unavailable and stale; these are conceptual categories, not approved record enum values. A requested nonexistent part is not applicable; backend inability is unsupported; absence of an otherwise expected current sample is temporarily unavailable. A claim must not silently combine values from different physical sample instants. A composed Body/part view may contain independently sampled poses only when their sample references and coherence status remain interpretable; a shared container does not imply an atomic sample.

**Epistemic limits and exclusions.** For simulator-backed Embodiment, the claim describes the modeled physical state represented by that apparatus, not independently validated external-world ground truth. A physical/hardware Embodiment may use a measured-state source while preserving the same semantic contract. Body Schema, Self Model, Environment entity pose, intended/commanded/predicted pose, joint kinematics, velocity, center of mass, mass, contacts, force, torque, actuator effort, work and resource position are excluded and require separate admitted claims.

**Conformance rule.** Conformance is capability-specific. A backend may publish a supported Body/part-pose capability only when it demonstrates identifiable subjects, compatible local-frame definition, position semantics and conversion to metres, explicit compatible reference frame, conversion to right-handed `+Z`-up canonical coordinates with defined `+X`/`+Y`, canonical `xyzw` unit-quaternion semantics, an Embodiment physical sample reference, sampled-versus-derived distinction where material, applicable physical-contract revision and defined availability behavior. A backend may support Body pose while marking part poses unsupported. Backend internals need not match; undefined or non-conforming values are not published as canonical `embodiment.body_pose`.

**Record-readiness boundary.** This accepted semantic contract does not approve a record schema, exact serialization, publication, cadence or transport. Concrete identity implementation, availability behavior and Physics3D conformance remain readiness gates. No second backend is required for the v1 conformance assessment; multi-backend conformance remains a dormant future gate.

The Embodiment semantic-owner disposition of 2026-10-07 accepts this contract with the refinements recorded above. Its decision approves semantic meaning and conformance boundary only; record readiness and publication remain unapproved.

#### 9.1.2 Physics3D Body Pose conformance assessment — refreshed 2026-10-07

**Result: NOT DEMONSTRATED. Body Pose is not record-ready.** This is a source-to-contract assessment against the Embodiment semantic-owner disposition accepted with refinements on 2026-10-07. It is not a finding that the simulated values are numerically wrong. The latest disposition resolves the semantic authority, claim boundary and backend-neutral meaning; the remaining gaps are the concrete Physics3D binding/conformance evidence and record-readiness behavior. This is local to the Body Pose capability and does not block the frozen macro architecture or the transport-independent semantic-model work. The evidence below is limited to the current Physics3D implementation; it does not infer requirements from `PhysicsWorldObserver` metadata or presentation behavior.

**Project-owner unit disposition — 2026-10-08.** Physics3D may claim canonical Body Pose only where the source unit is explicitly declared as metres or an explicitly declared other unit is converted to metres before publication. Generic geometry/pose coordinates whose unit remains implicit or unknown are not conformant. The affected Body Pose capability is excluded from canonical publication until that declaration/conversion and the other applicable conformance requirements are demonstrated. This is a family/capability-local readiness decision: it does not block or reopen the frozen macro Observation Architecture. It does not establish that current coordinates are numerically wrong, select a code change, or authorize implementation.

| Contract requirement | Physics3D evidence | Assessment |
|---|---|---|
| Embodiment authority and Body Pose claim boundary | The accepted semantic-owner disposition assigns retained physical Body-state pose semantics to Embodiment. `base_pose()` exposes base position/orientation; exported links expose position/orientation separately from joints. | **PASS — semantic disposition and source availability only.** This does not approve fields or publication. |
| Position meaning and local-frame origin | [`base_pose()`](../../../embodiment/src/embodiment/physics3d/articulated.py#L403-L412) reads MuJoCo root-body `xpos` for fixed-base bodies and free-joint `qpos` position for floating-base bodies. [`export_physical_state()`](../../../embodiment/src/embodiment/physics3d/articulated.py#L604-L629) exports link `xpos`. [`build_articulated_urdf()`](../../../embodiment/src/embodiment/physics3d/articulated.py#L175-L245) defines link names and joint-origin offsets; `SegmentSpec.origin` is written as an inertial origin, not a declared public pose origin. These paths indicate which simulator transforms are read, but the repository does not bind fixed/free base or exported link transforms to the accepted versioned public local-frame contract or explicitly approve the origin represented for each semantic Body/part subject. | **PARTIAL source mapping; NOT DEMONSTRATED conformance.** Need explicit mapping for fixed/free base origins and each published part frame; an URDF/MuJoCo frame or engine body index/name is not by itself an approved semantic part/local-frame contract. |
| Metres | Pose values are numeric MuJoCo coordinates. `ArticulatedBodySpec`, `SegmentSpec`, and `JointTopology` define numeric `size`, `origin`, topology offsets, and spawn height without a unit field or referenced physical-unit contract; the generic dataclasses are in [`mechanics.py`](../../../embodiment/src/embodiment/physics3d/mechanics.py#L63-L78) and the values are serialized directly into URDF numeric attributes by [`build_articulated_urdf()`](../../../embodiment/src/embodiment/physics3d/articulated.py#L175-L245). This remains true across the concrete body-spec modules inspected. The generated description is imported with `MjSpec.from_string()` without an explicit unit declaration or conversion. Tests assert configured spawn-height values are preserved, but do not establish a generic unit/scale contract. There is local metre intent in selected body-specific source comments: the Spot-inspired geometry comments label approximate dimensions in metres, and the vision head-mount offset is labelled metres. Those comments do not type the generic geometry contract or demonstrate a scale mapping for every exported pose/body kind. The separate world-scene observer's metre declaration applies only to its projection. ROS publishes an SI convention (metres for length) in [REP 103](https://github.com/ros-infrastructure/rep/blob/master/rep-0103.rst), and its [URDF tutorial](https://docs.ros.org/en/rolling/Tutorials/Intermediate/URDF/Building-a-Movable-Robot-Model-with-URDF.html) uses metres for prismatic length. This is relevant convention evidence, but not proof that Symbiont's generic dataclasses adopt that convention: the inspected path emits URDF for direct MuJoCo parsing and declares no ROS/REP 103 conformance. | **NOT DEMONSTRATED.** Generic Physics3D geometry/pose inputs have no typed unit contract or explicit conversion; selected comments, tests and external ROS conventions are insufficient to establish metre conformance for every exported Body Pose capability. Do not infer units from scene-observer metadata or `-9.81`. Focused source tracing is complete; the remaining gap is an authoritative domain/source contract or other direct conformance evidence, not more broad path tracing. |
| Reference frame and axes | [`PhysicsScene`](../../../embodiment/src/embodiment/physics3d/scene.py#L20-L33) creates an `MjSpec`, applies numeric gravity and compiles it. Runtime constructs it with the default `(0, 0, -9.81)` gravity ([runtime construction](../../../lab/src/lab/physics3d/runtime.py#L296-L306)); `add_ground()` creates the ground plane on the MuJoCo world body with a z-axis normal. This supports the current apparatus convention `+Z = up`. [`ArticulatedBody._add_to_scene()`](../../../embodiment/src/embodiment/physics3d/articulated.py#L298-L301) attaches the generated root body to `worldbody` through a frame translated by `spawn_height` and does not declare a frame identity or axis transform. [`base_pose()`](../../../embodiment/src/embodiment/physics3d/articulated.py#L403-L412) reads fixed-base `data.xpos`/`data.xquat` or floating-base free-joint `qpos`; [`link_pose()`](../../../embodiment/src/embodiment/physics3d/articulated.py#L414-L418) returns link `data.xpos`/`data.xmat`; exported link poses likewise use `xpos` and `xquat` ([export](../../../embodiment/src/embodiment/physics3d/articulated.py#L619-L629)). MuJoCo documentation identifies `worldbody` as the root of the kinematic tree/world frame and describes spatial frames as right-handed ([Modeling: coordinate frames](https://mujoco.readthedocs.io/en/stable/modeling.html#coordinate-frames), [XML Reference: `worldbody`](https://mujoco.readthedocs.io/en/2.3.3/XMLreference.html#body)). Thus source outputs are better characterized as MuJoCo global/world-frame transforms; this strengthens source mapping but does not bind them to an approved Embodiment Physical Reference Frame. Environment recipe comments also say metre/Z-up, but do not establish Environment-frame identity/equality with this Embodiment frame. | **PARTIAL source mapping; NOT DEMONSTRATED contract conformance.** MuJoCo world-frame/root and right-handed convention are evidenced, and `+Z = up` is supported for the current apparatus configuration. A concrete Physics3D binding proposal is therefore an identity transform from MuJoCo model-world coordinates (worldbody origin and model-world axes) to the active Embodiment Physical Reference Frame, with `+X`/`+Y` defined as the corresponding model-world axes. The repository does not yet declare that frame identity/binding, so this remains a target mapping proposal, not demonstrated conformance; any Environment-frame relationship remains unresolved. |
| Quaternion component order | [`base_pose()`](../../../embodiment/src/embodiment/physics3d/articulated.py#L403-L412) and [`export_physical_state()`](../../../embodiment/src/embodiment/physics3d/articulated.py#L619-L629) explicitly convert MuJoCo scalar-first `(w,x,y,z)` values to `(x,y,z,w)`. | **PASS — serialization order only.** Local-to-reference meaning, canonical frame semantics, unit norm tolerance and invalid/non-finite behavior are not demonstrated. |
| Quaternion validity | The accessor converts components to floats but does not enforce finite components or the semantic contract's normalization tolerance. | **NOT DEMONSTRATED.** No conformance behavior for invalid values is established. |
| Body/part identity and local frames | Runtime mints `body.<random>` for a new Physics3D Body and restores the identifier from its physical checkpoint ([mint/restore](../../../lab/src/lab/physics3d/runtime.py#L367-L374)); restoring an episode fails closed if its `body_id` contradicts the physical checkpoint ([episode consistency check](../../../lab/src/lab/physics3d/runtime.py#L691-L695)). Episode identity is separately created and the episode is initialized with Symbiont and Body references ([episode construction](../../../lab/src/lab/physics3d/runtime.py#L724-L746)). Exported `link_index` values are assigned from topology ordering and then resolved to scene-local engine IDs ([topology mapping](../../../embodiment/src/embodiment/physics3d/articulated.py#L255-L263), [engine binding](../../../embodiment/src/embodiment/physics3d/articulated.py#L363-L370)); exported `link_name` is the spec's implementation vocabulary ([link export](../../../embodiment/src/embodiment/physics3d/articulated.py#L619-L629)). `state_schema_version` is used to validate physical-state restore, not to assert public physical-part semantics ([export/restore checks](../../../embodiment/src/embodiment/physics3d/articulated.py#L633-L667)); `BodyDescriptor.version` is populated from that state schema in the registered Physics3D descriptors ([descriptor definitions](../../../embodiment/src/embodiment/physics3d/bodies.py#L146-L172)). No canonical cross-system Body issuer/link, stable semantic part ID, physical-contract revision or cross-revision part-compatibility declaration is evidenced. | **PARTIAL for same-runtime Body continuity and checkpoint/episode contradiction detection; NOT DEMONSTRATED for canonical Body/part identity mapping.** The restore check is a local integrity guard, not proof of cross-domain identity equivalence. Topology indices, link names, descriptor versions and state-schema versions must not be promoted implicitly to canonical identity/semantic revision. |
| Physical semantic-contract revision | Exported `schema_version` is `ArticulatedBodySpec.state_schema_version` ([physical-state export](../../../embodiment/src/embodiment/physics3d/articulated.py#L633-L636)), used for physical-state/checkpoint representation. No distinct physical semantic-contract revision is referenced. | **NOT DEMONSTRATED.** State schema version is not a substitute. |
| Point-sample reference | Tick-end physical state/checkpoint is paired out-of-band with `_last_physical_tick`, which is `tick_count`/organism tick ([runtime physical-state access](../../../lab/src/lab/physics3d/runtime.py#L956-L989)); the state payload itself carries no Embodiment Physical Sample Reference. The presentation counter `_presentation_substep` increments after every physics substep, but a pose frame is captured only when presentation cadence fires ([counter and frame construction](../../../lab/src/lab/physics3d/runtime.py#L1495-L1514)). That counter is initialized to zero for each runtime construction ([initialization](../../../lab/src/lab/physics3d/runtime.py#L426-L433)), including restore, and is not part of the physical checkpoint; `simulation_time_s` is therefore runtime-instance-relative and cannot identify a durable sample across restore. Presentation frames remain a separate cadence-limited path, not the tick-end canonical sampled-state path. | **NOT DEMONSTRATED.** Source evidence now establishes the counter's lifecycle and sampling order, but neither organism tick nor runtime-local presentation time is an accepted Embodiment Physical Sample Reference. No explicit mapping binds the tick-end export to a physical step/time. |
| Sampled versus derived/interpolated nature | The source distinguishes physical-state export from presentation pose frames, but exported Body Pose does not carry an acquisition-nature declaration. | **PARTIAL.** A source path exists for sampled state; the contract distinction is not represented in the export. |
| Availability/completeness and capability | [`ArticulatedBody.base_pose()`](../../../embodiment/src/embodiment/physics3d/articulated.py#L403-L412) has fixed/free-base access paths but returns a pose tuple, not an explicit capability/availability result. [`link_pose()`](../../../embodiment/src/embodiment/physics3d/articulated.py#L414-L418) resolves a requested name through the current topology mapping; an unknown name raises `KeyError`. [`export_physical_state()`](../../../embodiment/src/embodiment/physics3d/articulated.py#L604-L680) exports base pose and enumerates registered links, but carries no per-capability or per-sample availability/completeness state. The `BodyDescriptor.available` value in the body registry describes body-factory/catalog availability, not pose capability. No explicit stale, temporarily-unavailable, not-observed, unsupported or partial-composition result is present in these paths. | **NOT DEMONSTRATED.** Current source behavior is characterized, but it does not implement the accepted semantic availability distinctions. Contract readiness must define how each claimed capability handles absent parts, unavailable samples and incomplete/stale data; unknown-name exceptions must not be mistaken for semantic `not_applicable` without an explicit mapping. |
| Simulator epistemic status | Pose values are produced from MuJoCo state through Physics3D, not an independent external-world measurement. | **PASS — source characterization.** Describe only as simulated apparatus state, not ground truth. |

**Capability disposition.** Physics3D currently has source data for base pose and link pose. Neither capability is yet conformant as a canonical `embodiment.body_pose` claim. Base and part capabilities may receive separate readiness outcomes later; lack of part support need not invalidate base-pose conformance, but it must be explicit. `link_pose()` returns a rotation matrix while `export_physical_state().links` serializes orientation as `xyzw`; this difference must be resolved by the eventual producer contract, not hidden by consumers.

**Readiness decision.** The semantic-owner disposition and project-owner unit rule are complete; do not request another generic semantic approval for those decisions. Close this refreshed source-conformance assessment with outcome **NOT DEMONSTRATED**. Keep Body Pose in the bounded candidate scope, but do not mark any capability record-ready until it has an explicit metre declaration or conversion plus all other applicable mappings. Remaining conformance/readiness evidence includes: bind the configured MuJoCo frame to a concrete Embodiment Physical Reference Frame (origin, +X/+Y, handedness and conversion); demonstrate the declared unit/conversion for each retained capability; map fixed/free base and link frames to the contract; define stable Body and part identity/linkage plus physical-contract revision; provide an Embodiment physical sample reference for the sampled-state path; specify and enforce quaternion validity behavior; and define capability/availability behavior. These are family-local target/source conformance tasks, not unresolved macro-architecture decisions. No API, record schema, implementation or transport is authorized.

**Bounded root-origin test evidence — 2026-10-07.** Existing fixed-base Crawler and floating-base Spot tests both assert `base_pose()[0][2] == spawn_height`; the fixed-base test also checks the root remains anchored under actuation. The two focused tests pass. This supports only the current tested Z-translation behavior. It does not establish metres, the semantic point represented by the root local frame, the complete reference-frame mapping, or conformance for other bodies/parts. Thus the accepted Position meaning still has no complete Physics3D semantic mapping.

**Frame/unit evidence note.** The default gravity vector is evidence about one configured scene only. MuJoCo explicitly does not prescribe basic physical units; its MKS-like default gravity does not establish that model coordinates are metres ([MuJoCo Overview](https://mujoco.readthedocs.io/en/stable/overview.html)). MuJoCo's [coordinate-frame documentation](https://mujoco.readthedocs.io/en/stable/modeling.html#coordinate-frames) describes right-handed spatial frames, and its [XML reference](https://mujoco.readthedocs.io/en/2.3.3/XMLreference.html#body) identifies `worldbody` as the world-frame root for the kinematic tree. Repository pose exports read global/world transforms, but conformance still requires an explicit mapping of those transforms to the accepted Body/part and Embodiment Physical Reference Frame semantics. No independent implementation defect was established in this review; these are contract/conformance gaps. Any future source defect found while implementing the mapping should be recorded in Future analysis notes, not silently folded into this design task.

**Unit-provenance trace — closed for current source path (2026-10-07).** A targeted search of the Physics3D Body-spec and model-generation path found no unit metadata on `ArticulatedBodySpec`, `SegmentSpec` or `JointTopology`, and no unit declaration/conversion between those numeric dimensions/origins and the generated URDF imported by MuJoCo. Recipe-level Environment units and the separate scene-observer annotation are not evidence for the Body contract. This closes the source-tracing question, not the conformance blocker: metres remain unproven until an authoritative unit meaning or explicit conversion is established. No code was changed and no unit was inferred.

**Reference-frame source trace — closed for current Body Pose acquisition paths (2026-10-07).** A targeted trace of scene construction, Body attachment and pose access confirms that Physics3D obtains pose values from MuJoCo world transforms (fixed base/link) or the floating-base free-joint position, with the Body root attached under `worldbody` at `spawn_height`. Official MuJoCo documentation identifies `worldbody` as the kinematic tree's world-frame root and spatial frames as right-handed ([Modeling: coordinate frames](https://mujoco.readthedocs.io/en/stable/modeling.html#coordinate-frames), [XML Reference: `worldbody`](https://mujoco.readthedocs.io/en/2.3.3/XMLreference.html#body)). The inspected paths do not attach a named Embodiment Physical Reference Frame, complete axis/origin contract, or explicit canonical-frame conversion. The default gravity `(0, 0, -9.81)` is configuration evidence only and does not close those semantic mappings. This closes source-frame characterization. A direct identity-transform binding from MuJoCo model-world origin/axes to the active Embodiment Physical Reference Frame is the minimal Physics3D mapping candidate, with canonical `+X`/`+Y` taken from the model-world axes and the apparatus's configured `+Z = up`; this follows the implementation's direct global-transform access without asserting an Environment-frame relationship. Conformance is still not established because no frame identity/binding is declared by the source contract, and metre scale, Body/part local frames and other readiness requirements remain unresolved. No code was changed and no frame equivalence was inferred.

**Body/part local-frame source trace — closed for current generated-link pose paths (2026-10-07).** `ArticulatedBodySpec.base_link_name` names the generated root link; `joint_topology` and `fixed_link_topology` name child links and their parent/child offsets. `build_articulated_urdf()` emits each such link and its joint-origin relationship, while `_link_index_by_name` maps those spec names to internal ordinals and `_body_id_by_link` resolves ordinals to scene-local MuJoCo body IDs. `link_pose()` and `export_physical_state()` then read the corresponding MuJoCo body's global `xpos` and orientation (`xmat` or `xquat`). Thus the source path identifies which generated link-frame transform is sampled. It does not establish that a spec link name/ordinal is a stable semantic part identity, nor that the current generated link frame has been accepted as the contract's declared local physical frame for that subject. In particular, `SegmentSpec.origin` is emitted as the inertial origin, not as an explicit public pose-frame declaration; joint-topology origins place child links relative to parents but do not themselves create a stable part-identity or physical-contract revision. Source-to-generated-frame mapping is therefore characterized, while canonical part IDs, local-frame contract bindings and cross-revision compatibility remain unresolved. No independent implementation defect was established.

**Body/part local-frame source trace — closed for the current generated-model path (2026-10-07).** `build_articulated_urdf()` emits named links, joint-origin offsets and inertial origins; `SegmentSpec.origin` specifically populates the URDF inertial origin. Pose accessors then read MuJoCo body transforms for root/link frames, while floating-base root position comes from its free-joint coordinates. The code therefore exposes simulator frame state, but does not attach an Embodiment physical-contract revision that declares the public local-frame origin/orientation for each Body/part identity or compatibility of those identities across morphology revisions. This closes source tracing only; it does not authorize promoting a URDF link name/frame or MuJoCo index into canonical part semantics. No code was changed and no canonical part mapping was inferred.

**Body/part identity source trace — closed for the current Physics3D path (2026-10-07).** `Physics3DRuntime` mints `body.<random>` for a new Body and restores that ID from the physical checkpoint. When restoring the same EmbodimentEpisode, it rejects a disagreement between the episode's `body_id` and the physical checkpoint Body ID. Episode identity is separate and relates a Symbiont, Body, epoch and lifecycle; it is not a Body alias. Within `ArticulatedBody`, `link_index` is assigned from base/joint/fixed-link topology order, then mapped to scene-local engine body IDs; exported `link_name` comes from the selected body spec. The state schema version gates checkpoint restore and is copied into `BodyDescriptor.version`; neither is a physical semantic-contract revision. This establishes same-runtime Body continuity and a fail-closed restore consistency check, but not a canonical issuer/namespace or an explicit link to Lab `body_ref` or Environment identity. It also establishes no stable public part IDs or compatibility declaration across morphology/contract revisions. The source trace is closed; cross-system identity mapping, canonical part identity and semantic revision remain unresolved and block record readiness. No identity equivalence is inferred from matching names, topology order or checkpoint compatibility.

**Quaternion-validation source trace — closed for current Physics3D pose paths (2026-10-07).** `base_pose()` reads MuJoCo `xquat` for fixed-base bodies or the floating-base quaternion components from `qpos`, then reorders scalar-first values to `(x, y, z, w)`; `export_physical_state()` similarly reorders each link's `xquat`. Neither export path explicitly checks component finiteness, quaternion norm/tolerance or a Body-Pose-specific invalid/unavailable policy. Physical-state restore checks that `qpos`, `qvel` and `warmstart` values are finite, but does not separately validate floating-base quaternion normalization against the accepted semantic contract before assigning state and forwarding the scene. This is evidence that project-level contract validation is not implemented in these paths; it does not establish that MuJoCo emitted an invalid quaternion or that the simulation is numerically defective. Source tracing is closed, while conformance behavior and the semantic tolerance/policy remain unresolved. No independent code defect was established; do not classify this contract gap as a bug without a failing or invalid state example.

**Physical sample-reference source trace — closed for current tick-end and checkpoint paths (2026-10-07).** A normal `step()` reads the apparatus before the organism tick, advances the physics scene through `physics_substeps_per_tick`, then exports physical state after integration and stores it with `_last_physical_tick = self.tick_count`. `tick_count` delegates to the organism cycle, so this is an organism-tick association for the completed physical state, not an independent Embodiment physical sample reference. The constructor also initializes the cached state at tick 0. `physical_checkpoint()` may refresh the physical state and tag it with the current organism tick when requested, but the payload has no acquisition timestamp/step of its own. Separately, `_presentation_substep` increments after every scene step, but presentation pose frames (including `physics_step` and `simulation_time_s`) are captured only when presentation cadence fires, together with a within-tick substep index. The counter resets to zero whenever a runtime is constructed, including restore, and is not persisted in the physical checkpoint; its time is runtime-instance-relative, not a durable physical sample identity. These frames do not define the tick-end Body Pose sample. The source therefore establishes sample points in execution order, an organism-cycle association, and a runtime-local substep counter, but not a stable canonical physical sample clock or a formal mapping between tick-end sample instant, physics step and organism cycle. Do not substitute the presentation counter or organism tick without an explicit relation. The focused source trace is closed; a target Physical Sample Reference and Physics3D binding remain unresolved. No timing defect was established.

**Capability/availability source trace — closed for current base/link pose paths (2026-10-07).** `base_pose()` returns base coordinates through fixed- or free-base access paths without an explicit capability/status wrapper. `link_pose()` looks up the requested spec link name and raises `KeyError` when it is absent from the current topology mapping; it does not classify absence as `not_applicable`, `unsupported` or another semantic state. The physical-state export enumerates the available mapped links and emits no per-part completeness or freshness status. The registry's `BodyDescriptor.available` flag concerns whether a Body descriptor/factory is available, not whether a pose capability is supported. This closes source tracing only: the accepted Body Pose availability categories are not represented by these exports, and no capability-specific conformance is demonstrated. The exception behavior is a contract gap, not an independently confirmed implementation defect; no invalid or missing runtime pose was shown.

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
13. Permit Lab analytical claims only for a legitimate operational need, with explicit meaning, known inputs, material revision, clear Lab attribution, and no presentation as organism knowledge. The current prediction-error band is deferred/excluded from v1; legacy use does not establish retained consumer need.
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
- [x] **DONE (2026-10-07) — Record source-publication and consumer-access disposition.** §6.4 records the accepted separation of domain-to-plane publication from consumer-to-plane access, including demand-independent bounded publication, subscription/query semantics, non-atomic bootstrap caveat, bounded zero-consumer retention and failure/backpressure isolation. No API, delivery mechanism, transport or implementation is approved.
- [x] **DONE (2026-10-07) — Assess physical pose/kinematics claim boundary.** Against Assessment §9.5, propose separate Body-pose and joint-kinematics claims by default because current acquisition paths and sampling semantics differ. This is only a within-family boundary proposal; it does not approve fields, units/frames, datum authority, publication, physical-contract readiness or Body/joint identity links.
- [x] **DONE (2026-10-07) — Assess Environment resource claim boundary.** Against Assessment §§9.5–9.6, separate logical Environment resource state from recipe/configuration, apparatus realization, Lab-derived spatial metrics, transfer, and study/nursery support. This proposal does not approve a resource field set, units, canonical resource identity/link, or publication.
- [x] **DONE (2026-10-07) — Obtain Embodiment disposition of Physical Body Pose Semantic Contract v1.** §9.1.1 records acceptance with refinements for claim, independent identity/context dimensions, canonical quantity/unit/frame/orientation semantics, sampling/time, availability, composition, epistemic limits and capability-specific conformance. This approves semantics only, not a record or publication.
- [x] **DONE (2026-10-07) — Assess Physics3D against the accepted Body Pose contract.** Refreshed §9.1.2 requirement by requirement after the semantic-owner disposition. Result: **NOT DEMONSTRATED**; no record-readiness. Assessment distinguishes accepted semantics from unproven Physics3D binding/conformance, including unit/frame mapping, sample reference, physical-contract revision, Body/part identity, quaternion validity and capability/availability behavior.
- [x] **DONE (2026-10-07) — Trace Physics3D Body Pose reference-frame source path and candidate binding.** Closed the source investigation: pose access uses MuJoCo global/world transforms; official MuJoCo documentation identifies `worldbody` as the kinematic-tree world-frame root and spatial frames as right-handed; the configured gravity/ground plane supports `+Z = up`. Recorded the minimal target binding proposal: identity transform from model-world origin/axes to the active Embodiment Physical Reference Frame, taking `+X`/`+Y` from the model-world axes. This proposal does not create a source-declared frame ID or imply an Environment-frame link, so conformance remains blocked pending explicit contract binding and other readiness requirements. No defect or frame equivalence is inferred.
- [x] **DONE (2026-10-07) — Trace Physics3D Body/part local-frame acquisition.** Confirmed generated spec link names map to scene-local MuJoCo body IDs and pose access reads those generated links' global transforms. This identifies the source transform but does not establish stable semantic part IDs, accepted local-frame meaning, a physical-contract revision, or compatibility across revisions; `SegmentSpec.origin` is an inertial origin, not a public pose-frame declaration. No independent defect was established.
- [x] **DONE (2026-10-07) — Trace Physics3D Body/part local-frame source path.** Closed the focused investigation of generated URDF link/joint/inertial origins and fixed/free-base/link pose access. Physics3D exports simulator frame state, but no physical semantic-contract revision declares public Body/part local-frame meanings or cross-morphology identity compatibility. Source tracing is closed; semantic mapping and conformance remain blocked.
- [x] **DONE (2026-10-07) — Trace Physics3D Body/part identity source path.** Confirmed runtime-local Body ID mint/restore and fail-closed consistency with a restored EmbodimentEpisode; confirmed episode identity is distinct, link indices derive from topology ordering/scene binding, link names are body-spec vocabulary, and descriptor/state-schema versions are checkpoint-format versions rather than physical semantic revisions. This closes source tracing only; canonical cross-system Body links, semantic part IDs and revision compatibility remain unresolved.
- [x] **DONE (2026-10-07) — Trace Physics3D quaternion validation on Body Pose paths.** Confirmed `base_pose()` and link export reorder MuJoCo quaternion values but do not explicitly enforce finite/unit-quaternion tolerance; restore validates finiteness of state vectors but not a separate Body Pose quaternion policy. This closes source tracing only and does not show that invalid quaternions occur. Conformance/policy remain unresolved; no independent implementation defect was established.
- [x] **DONE (2026-10-07) — Trace Physics3D Body Pose sample-reference source path.** Confirmed end-of-tick physical state is exported after physics substeps and cached with organism `tick_count`; on-demand checkpoint refresh also associates an export with that organism tick. Presentation frames separately carry a substep counter/time, but are cadence-limited and not the tick-end sample contract. The counter resets on runtime construction/restore and is not checkpointed. This closes acquisition-path tracing only; neither path supplies a canonical Embodiment sample reference or explicit cross-clock relation. No timing defect was established.
- [x] **DONE (2026-10-07) — Trace Physics3D Body Pose capability and availability paths.** `base_pose()` exposes fixed/free-base access without explicit capability status; `link_pose()` raises `KeyError` for an unknown mapped name; physical-state export enumerates mapped links without per-part completeness/freshness status. `BodyDescriptor.available` is body-catalog availability, not pose capability. This closes source tracing only; accepted availability distinctions and capability-specific conformance remain unimplemented/unproven. No independent defect was established.
- [x] **DONE (2026-10-07) — Trace body-specific metre annotations.** Confirmed explicit metre comments for selected Spot-inspired geometry and the vision head-mount offset. These local comments do not establish a generic unit contract or prove metre scale for every Body Pose export; see Assessment §9.5 and the conformance matrix below.
- [x] **DONE (2026-10-07) — Trace generic Physics3D geometry units for Body Pose.** Confirmed `ArticulatedBodySpec`, `SegmentSpec` and `JointTopology` carry numeric dimensions/offsets without unit metadata, values are emitted to URDF without explicit conversion, and inspected spawn-height tests assert configured values rather than unit semantics. Selected metre comments do not generalize. This closes source tracing with result **NOT DEMONSTRATED** for canonical metre conformance; it does not establish a numerical defect or authorize implementation.
- [x] **DONE (2026-10-07) — Trace Physics3D vertical-axis convention.** Confirmed the default scene gravity is negative Z and the ground plane uses a Z-axis normal, supporting `+Z = up` for the current apparatus. This does not establish a named Embodiment frame, its origin, `+X`/`+Y`, handedness or full public pose mapping; see Assessment §9.5 and the conformance matrix below.
- [x] **DONE (2026-10-07) — Verify existing Physics3D base-origin test evidence.** Ran the fixed-base Crawler root-anchor/checkpoint test and floating-base Spot initial-pose test; both pass and assert root Z equals configured `spawn_height`. This closes only the test-evidence trace, not semantic origin/unit/frame mapping or Body Pose conformance.
- [x] **DONE (2026-10-08) — Record project-owner unit disposition for Physics3D Body Pose.** Generic coordinates may conform only with an explicit metre declaration or explicit conversion from a declared unit to metres. Unknown/implicit units are non-conformant; exclude the affected capability from canonical publication until demonstrated. This resolves the owner decision, not Physics3D conformance or Body Pose readiness.
- [ ] **QUEUED — Resolve Physics3D Body Pose capability readiness.** Address the Embodiment Physical Reference Frame binding, Body/part local frames and stable part IDs/revision compatibility, Embodiment Physical Sample Reference, quaternion validity, and capability/availability. Assess only capabilities with demonstrated unit declaration/conversion; keep other capabilities excluded. This is family-local and does not gate macro architecture or other semantic-model work. No implementation is authorized.
- [ ] **QUEUED — Continue candidate semantic-record boundaries for retained families.** Use the conceptual Observation Semantic Model and frozen evidence scope; obtain relevant domain-semantic dispositions without inferring final schemas or publication. Body Pose readiness is tracked independently.
- [ ] **QUEUED — Establish record readiness and final v1 scope.** Complete record-level evidence and interpretability review: resolve or exclude ambiguous identity, clocks, units/frames, availability and derivation/configuration lineage; confirm consumer need; remove, split or defer unresolved records. This precedes Envelope Readiness.
- [ ] **QUEUED — Establish Envelope Readiness.** Demonstrate representative cases, consumer sufficiency, consumer-driven coherent/partial view requirements, scientific separation and non-interference against the approved models.
- [ ] **QUEUED — Specify event, snapshot, materialization, replay, gap recovery and transport.** Begin only after record semantics and Envelope Readiness are dispositioned. Do not revive the superseded Symbiont Telemetry Event API without an explicit reopening decision.
- [ ] **QUEUED — Prepare implementation and cutover proposal.** Separate authorization, implementation validation, consumer migration, legacy deletion and operational cutover.

**Current focus:** The macro architecture is frozen. The next conceptual activity is tracked in [Observation Semantic Model v1](observation-semantic-model-v1.md). Physics3D Body Pose unit disposition is complete; its capability-specific conformance remains **NOT DEMONSTRATED** and is a separate readiness track. No record schema, transport, implementation or cutover is authorized by the current disposition.

### Dormant future gate

- **BLOCKED / dormant — Validate multi-backend semantic conformance.** Activate only when another concrete Embodiment backend is ready to publish a family defined by the backend-neutral physical contract. Evaluate conformance per overlapping capability; internal simulator equivalence is not required. This is not on the v1 critical path and requires no synthetic backend.

### Future analysis notes (outside current target-architecture drafting focus)

- No new source-code defect is asserted by this target proposal. Defects identified during the AS-IS investigation remain recorded in the Current-State Assessment future-analysis notes and are not implementation authorization.
- **Candidate-status reconciliation — DONE (2026-10-07):** Design Inputs §4 and Target Design §9.1 now distinguish the original evidence-investigation freeze from retained v1 scope. Body-local modeled physiology is Embodiment-authoritative but remains blocked at value/record readiness; portable Symbiont physiology is excluded/deferred. The Lab prediction-error band is deferred/excluded from v1 and may be reopened only under the Lab semantic-owner conditions. No record or publication is approved by this reconciliation.

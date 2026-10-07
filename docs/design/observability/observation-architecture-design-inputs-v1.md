# Observation Architecture — Design Inputs v1

**Status:** Proposed input package; not an approved target architecture.  
**Progress:** Partial / in progress; candidate evidence-scope freeze, minimum AS-IS evidence sufficiency for TO-BE entry, and architecture-owner disposition are recorded. Domain-semantic assignments and final v1 record/publication scope remain open.  
**Review state:** Substantive draft; adversarial review, scoped architecture-owner disposition, bounded candidate-scope freeze, and TO-BE-entry evidence review are recorded. This is not final v1 record/publication approval.  
**Target Design:** Architecture-owner approved with refinements on 2026-10-07 for direction and boundaries only. Record schemas, datum-level authority, final publication scope, contract/API, event, endpoint, transport, implementation and cutover remain unapproved.
**Source assessment:** [Observation Architecture — Current-State Assessment v1](observation-architecture-current-state-assessment-v1.md).  
**Purpose:** give the future TO-BE design a concise, reviewable set of evidence-backed constraints, requirements, candidate families, and unresolved decisions. This document does not specify an envelope, event taxonomy, endpoint, transport, or implementation plan.

## 1. Lifecycle boundary

The source assessment reconstructs the current implementation (AS-IS). This package distills design inputs from that assessment; it does not replace the source evidence. A separate **Observation Architecture v1 — Target Design** has been authored and received architecture-owner approval with refinements for direction and boundaries. It must define future behavior deliberately and must not treat current payload shapes as compatibility requirements.

Lifecycle:

```text
AS-IS assessment
    → reviewed design inputs and candidate semantic scope
    → separate TO-BE architecture
    → contract specification
    → separately authorized implementation
    → replacement cutover
```

No stage authorizes the next automatically. This package authorizes neither API/code changes nor scientific use.

## 2. Evidence-backed current-state findings

These are findings about inspected code at the assessment baseline, not assertions that every present behavior should remain:

- The operational observation path is currently Lab-mediated: Lab adapters and projections construct payloads, the Lab bus owns stream/history behavior, and Lab API/SSE serves consumers.
- Current payload families and names (`body`, `cognition`, `vitals`, Mind snapshots, `ObservedFrame`, and current cursor/replay behavior) are implementation evidence, not canonical cross-domain contracts.
- The code contains different identity namespaces and lifetimes: physical Body IDs, Embodiment episode IDs, Lab-managed references, durable Environment world IDs, observer-session IDs, projection-local entity IDs, and sample-local contact IDs. Similar field names do not establish identity equivalence.
- No second concrete physical Embodiment backend currently exists. Backend-neutral physical semantics can be specified and Physics3D conformance assessed now; multi-backend conformance remains a later generality gate.
- Re-embodiment currently replaces active Body-associated physiological state while retaining selected, lossy organism/episode history. The active physiology bundle is serialized in the portable organism checkpoint, while apparatus physical state is stored separately; normal restore rejects missing or mismatched organism/Body ticks, and explicit `--fresh-body` selects re-embodiment. This is observed artifact/lifecycle behavior, not domain-owner approval of public semantic ownership or desired target policy for each field. The tick check is not an atomic pair-persistence guarantee or a semantic ownership decision.
- Shared downstream physiology mutation does not imply one source or one observation family: Environment-resource acquisition, protected support, clean-World material exchange, legacy acquisition, and study-controlled ledger injections have distinct causes and lineage. Study refill/support is an intervention, not an Environment resource fact.
- Symbiont's `InteroceptionProvider` is an organism-internal sensing path: its derived readings are sampled into perception and can widen the percept snapshots used by sensorimotor mechanisms. This is not the Lab's passive observation plane and is not evidence that publishing the same signals externally is non-interfering. Physiological ownership, signal lineage and organism-clock binding remain unresolved.
- Current UI projections combine source state, observer-derived values, and presentation choices. Their existence does not make those projections source-authoritative.
- Operational observation and durable, protocol-governed scientific evidence are separate concerns and must not be treated as interchangeable stores.
- A cross-domain causal transformation may depend on effective configuration that is not recoverable from its input/output values alone. Where a retained operational observation requires that relationship to be interpretable, the target must preserve or resolve the transformation/configuration provenance; this does not transfer scientific-artifact reproducibility obligations into the operational plane.

See the assessment for code paths, tests, limits, and the evidence behind each finding.

## 3. Adversarial review of proposed constraints

The adversarial review table below records the challenge-stage assessment before owner disposition; it is not the current approval state. On 2026-10-07, the architecture owner dispositioned the guardrails as scoped inputs to Observation Architecture v1 in the following subsection. This does not assign authority to individual data, approve a record schema or transport, amend the Constitution, authorize implementation, or replace domain-semantic owner review.

| # | Proposed constraint | Adversarial disposition | Reason and boundary for TO-BE |
| --- | --- | --- | --- |
| 1 | Keep `subject`, `semantic authority`, `measurement source`, `producer`, `transport host`, and `observer/consumer` distinct. | **Carry forward** | These are different roles even when one component occupies several of them. The distinction prevents implementation location or serialization from being mistaken for authority. Assigning a role for any datum still requires evidence/owner review. |
| 2 | Keep semantic authority, epistemic nature, derivation scope, causal role/responsibility, acquisition method, measurement source, fidelity, identity, clock, and lineage conceptually independent. | **Refine** | This is a tracing discipline, not a requirement to place every axis in every record. The TO-BE should carry only the metadata needed to make each published observation interpretable and traceable; it must not inherit the entire audit vocabulary as wire fields. |
| 3 | Treat `Symbiont`, `Embodiment`, `Modality`, `Environment`, and bounded `Lab`-derived semantics as candidate authority domains. `Body` and `World`/Environment instance are subjects/entities, not authority domains. | **Refine** | The current architecture supports these as candidate boundaries, but domain-owner confirmation is not complete. Lab may author semantics it creates (e.g. an explicit classification or join), not reinterpret source facts. “Five domains” is an organizing hypothesis for review, not a closed ontology. |
| 4 | A domain-internal derivation may remain authoritative in that domain; cross-domain lineage does not itself transfer authority to Lab. Lab-created derivations are separately attributed and linked to material inputs. Where needed to interpret a retained derivation, lineage must also identify or resolve its effective transformation/configuration and application boundary. | **Carry forward (scoped)** | Derivation location/scope and semantic authority are independent. Preserve source facts and mark newly introduced semantics as a derived observation with lineage. A traced work-to-metabolic-cost path shows that the output may not be reconstructible from input/output values when the effective coefficient is absent from inspected run configuration. This raises a separate scientific-artifact reproducibility question, not automatically an Observation Plane defect. Exact lineage representation and publication scope are deferred to TO-BE. |
| 5 | An atomic semantic observation record must not hide mixed authority or epistemic nature. Transport batching may group records without asserting common semantic ownership. | **Refine** | Apply homogeneity to the semantic record, not the delivery batch or snapshot. A mixed snapshot/batch is valid if its member records retain their own semantics and provenance. “Atomic record” boundaries remain to be tested against candidate families. |
| 6 | A candidate record must not rely on consumer inference for meaning, identity, clock, units, coordinate frame, or transformation. | **Carry forward** | This follows from the record's public interpretability. It is a record-level readiness gate: unresolved fields are omitted, split, or block that record; do not force a whole family into v1. For physical samples interpreted with static morphology metadata, the sample must identify a compatible semantic descriptor or carry sufficient self-describing semantics; a body-state/checkpoint schema version alone is not evidence of physical-observation semantic compatibility. |
| 7 | Distinguish public operational observation, private/debug data, and durable scientific evidence. | **Carry forward** | The systems have different retention, reproducibility, access, and governance purposes. A shared physical quantity does not make operational materialization a scientific artifact. Concrete publication/retention policy remains for TO-BE and applicable owners. |
| 8 | The operational cutover is full replacement, not backward-compatible extension; differential tests may classify semantic changes but do not require parity or production dual publication. | **Carry forward** | This is an explicit design direction, not an inference from current code. It removes legacy constraints while preserving useful migration validation. It applies only to the operational observation plane, not scientific evidence. |
| 9 | The observation plane must not create an organism feedback dependency; non-interference must be demonstrated, not asserted by a flag. | **Carry forward; operationalize** | This is already a constitutional invariant (Constitution §13, items 95–102; also items 86 and 93), not a new proposal. Scope it to observer/telemetry, UI, logging and derived-observation paths: it does not prohibit the organism's own interoception or other explicitly owned internal physiology/regulation-to-cognition loops. The TO-BE must turn the boundary into testable causal and bounded-cost criteria; any distinct external control path remains outside this observation contract. |
| 10 | Resolve identity links explicitly; do not join by matching names or silently applying fallback precedence. | **Refine** | Fail closed for an identity-dependent association/join when assertions conflict or the link is unresolved. This need not suppress independent source observations: preserve the conflicting assertions and expose the conflict/status rather than choosing silently. |
| 11 | The target is **observation-oriented and event-delivered where live change delivery is needed, not event-owned**. | **Carry forward (scoped)** | This is an explicit architectural input: live-change consumers must have an event-delivery access mode, but the primary semantic unit remains an observation, not an event envelope. Not every observation must be emitted as an event; an observation may instead or additionally be included in a snapshot, materialized, queried, or consumed by a projection. This does not imply event sourcing, a durable event log, a broker, or a fixed transport. Which consumers/families require live delivery remains part of the frozen v1 scope and TO-BE. |

### Architecture-owner disposition — passed (2026-10-07)

The architecture owner reviewed these constraints against the Current-State Assessment, the frozen candidate evidence scope, and governing Symbiont architecture. The dispositions apply only to target-architecture inputs for Observation Architecture v1. They do not approve concrete records, datum-level authority, API/envelope/events/endpoints/transport, implementation or cutover; amend the Constitution; or replace domain-semantic owner review.

| # | Constraint | Architecture-owner disposition | Scope / required refinement |
| --- | --- | --- | --- |
| 1 | Distinguish subject, semantic authority, measurement source, producer, transport host and consumer. | **ACCEPT** | These roles remain distinct even when one component occupies several roles. Datum-level assignment still requires evidence. |
| 2 | Keep classification axes independent. | **ACCEPT — SCOPED** | Preserve distinctions in analysis and contract design; they are not mandatory wire fields. Emit only metadata needed to make published observations interpretable and traceable. |
| 3 | Candidate authority domains and entity/subject distinction. | **ACCEPT — FOR OBSERVATION ARCHITECTURE V1** | Use `Symbiont`, `Embodiment`, `Modality`, `Environment` and bounded `Lab`-created semantics as the governing authority-domain model for this design. `Body`, `Organism`, `EmbodimentEpisode`, `EnvironmentInstance`/`World`, `Resource`, `Signal` and `Run` are subjects/context identities, not additional authority domains. No individual datum ownership is assigned. |
| 4 | Domain derivation does not itself transfer authority to Lab; preserve material lineage. | **ACCEPT — SCOPED** | A derivation may remain authoritative in the domain whose model defines it, including with cross-domain inputs. Lab owns semantics it creates. Material derivations must preserve or resolve lineage and effective transformation/configuration required for interpretation. |
| 5 | Semantic records must not hide heterogeneous authority or epistemic nature; delivery batches may group records. | **ACCEPT — REFINED** | The requirement applies to the semantic claim, not mechanically to contextual fields. A semantic record has one unambiguous primary semantic authority and epistemic interpretation. Explicitly identified identity, time and provenance context may originate elsewhere. Batches, snapshots and delivery containers may group heterogeneous records. |
| 6 | Public records must not rely on implicit consumer interpretation. | **ACCEPT** | This is a record-readiness requirement applied after the TO-BE defines observation, identity, temporal and provenance models. Undocumented meaning must be described, split or excluded. |
| 7 | Keep operational observation, private/debug data and scientific evidence distinct. | **ACCEPT** | These are separate publication/governance classes. Operational replay/materialization does not become scientific evidence by containing similar quantities. Concrete retention/access policy remains a TO-BE decision. |
| 8 | Replace the current operational path completely; differential testing need not preserve parity. | **ACCEPT** | Full replacement is the target direction. Legacy payloads, snapshots, frames, replay/cursor behavior, endpoints and UI assumptions are not compatibility contracts. Differential comparison is validation only. |
| 9 | Demonstrate observational non-interference. | **ACCEPT — REQUIRED** | Apply the existing constitutional non-interference boundary; this is not a new constitutional rule. Operationalize read-only observation, bounded cost, backpressure/failure isolation and no observer-to-organism feedback. Organism-owned interoception/regulation remains distinct. |
| 10 | Use explicit identity links and fail closed for unresolved identity-dependent joins. | **ACCEPT — REFINED** | A conflict/unresolved link blocks only the dependent join or association, not valid independent observations. Preserve conflicting assertions with issuer/asserter provenance and expose unresolved/conflict status; do not silently select precedence. |
| 11 | Observation-oriented, event-delivered where needed, not event-owned. | **ACCEPT — SCOPED** | The observation model is the semantic source of truth. Live event delivery is required only where retained consumers need it. This does not imply event sourcing, durable event log, broker, fixed transport or universal streaming. |

#### Authority-domain clarification

For this design, the five-domain model is accepted as the governing authority model, distinct from datum-level semantic ownership. For example, physical Body pose is an Embodiment candidate; learned Body Schema is a Symbiont candidate; signal semantics are a Modality candidate; Environment resource state is an Environment candidate; and a prediction-error classification created by Lab is Lab-authoritative only for that classification. Lab hosting, coordinating, transporting, materializing or presenting observations does not make it a universal authority.

#### Semantic-record and identity clarifications

The homogeneity requirement applies to each semantic claim: a record must make one unambiguous semantic claim, while explicit context may refer to separately owned identity, time and provenance. A batch or snapshot may contain heterogeneous records. This neither requires one primitive per record nor preselects record boundaries.

An unresolved or contradictory identity link invalidates only a dependent semantic join. Independent source observations remain valid within their evidenced identity scope. Conflicting assertions must remain visible with issuer/asserter provenance rather than being reconciled by hidden precedence.

#### Derivation and causal-conversion clarification

The embodied-work trace requires the target to preserve or resolve material transformation/configuration provenance when needed to interpret a retained derived observation. It does not require every intermediate causal scalar to be public. In particular, `metabolic_work_cost` is not approved for v1 publication by this disposition.

The architecture-owner disposition gate is passed, but it does not replace domain-semantic disposition, assign datum-level meaning, authorize contract specification, implementation or cutover. TO-BE authoring was separately authorized, and the resulting target architecture has now received its own architecture-owner disposition. The candidate evidence-scope freeze is recorded in §4.2.

The following target choices have since been dispositioned or remain open as stated:

- **Observation Plane infrastructure ownership — DISPOSITIONED:** Option C is approved for v1 in Target Design §6.2: domain-owned semantics/producers with Lab-owned operational coordination, materialization and delivery. Standalone extraction is deferred until demonstrated deployment or multi-host value.
- **Snapshot consistency model:** the requirement for coherent reads must be derived from retained consumers and source clocks; the existing `ObservedFrame` shape is not mandated.
- **Delivery/replay mechanics:** event delivery is a target access mode, but cursor shape, retention, replay guarantees, gap recovery, and whether all candidate families are streamed remain undecided.
- **Datum-level authority:** the governing five-domain model is accepted for this design, but semantic authority for individual data remains evidence- and domain-owner-dependent.

## 4. Candidate semantic cases — evidence scope frozen in §4.2

This is the bounded stress-test list for v1 evidence review, not a commitment to include any case in final v1 records. The rows are not all the same architectural kind: some are source-domain observation families, some are derived-observation families, and orchestration identity is cross-cutting context rather than a semantic observation family. Do not force them into one taxonomy merely to keep six review cases. §4.2 records the separate freeze of semantic-family candidates and cross-cutting context. Fields and transport schema remain out of scope here.

| Candidate case | Kind | Candidate authority | Subject | Evidence state / gate |
| --- | --- | --- | --- |
| Physical pose/kinematics | Source-domain observation family | Embodiment candidate | Body | Blocked: Physics3D evidence now distinguishes revolute joint radians/radians-per-second, command-derived effort (not torque measurement), xyzw pose representation, world-frame base velocity, and fixed-base zero values. Tick-end physical-state exports and render-cadence presentation-frame samples are separate acquisition paths; retained samples need explicit sample-clock and cross-clock semantics rather than an inferred shared tick. This remains backend-specific evidence: backend-neutral quantity/unit/frame/sampling semantics, contract reference, and v1 identity links are open. Any retained velocity record must distinguish fixed-base constrained zero from measured zero motion or unavailable data. Physics3D is the only current concrete backend. |
| Environment resource state | Source-domain observation family | Environment candidate; exact source semantics require review | Resource in a World/EnvironmentInstance | Blocked: recipe fixture IDs are not mapped into the observer's session-local `entity.N` records; the separate `PhysicalResource` has no persisted Resource ID and exposes only a rebuild-unstable engine handle. Establish an explicit identity link and semantic subject, or narrow/defer the family. Keep acquired material distinct from nursery support and study interventions. |
| Organism physiology state | Source-domain observation family (ownership unresolved) | Unresolved; possible split between Body-substrate and Symbiont regulation | Body and/or Organism | Blocked: owner review, per-state re-embodiment fate, units, clocks, and causal lineage remain open. |
| Organism affordance state | Domain-derived observation family | Symbiont candidate | Organism-in-context | Partial: source-owned runtime derivation is traced, and current Mind cognitive-live and Body Self Model views consume the projected list. This supports present operational use, not target publication approval. Context identity, typed clocks, input lineage, owner review, and v1 publication scope remain open. |
| Lab-derived prediction-error band | Observer-derived observation family | Lab, only for the classification it creates | Predictor/target observation; exact subject key unresolved | Partial: the current Lab projection classifies absolute signed residuals using fixed thresholds, and Mind map/history consumers use the categories. The target key can be `target_id` or fall back to `predictor_id`; finite-value validation, classifier version/meaning, source clock and stable subject identity remain unresolved. |
| Orchestration/run identity | Cross-cutting identity/context capability, not a semantic observation family | Lab orchestration candidate | Run and linked runtime subjects | Partial: namespaces and fallback risks are traced; explicit issuer/asserter/link and conflict behavior remain required. Decide whether v1 needs this context and what identity assertions may be exposed; do not treat metadata as source-domain state. |

Do not infer readiness from this table. A family may be deferred or excluded if its evidence does not pass.

### 4.1 Candidate v1 evidence-scope disposition

This proposal underpins the bounded evidence-scope freeze in §4.2, not target-contract or publication approval. “Include” means retain the semantic family as a v1 candidate for evidence review; it does not mean that any field is ready or guaranteed to ship. “Blocked” means the candidate is worth testing against the architecture, but current evidence prevents readiness. “Defer” means do not spend v1 evidence effort on it unless an operational need is established. “Exclude” means it is outside the operational observation contract as currently understood.

#### Semantic observation families

| Disposition | Candidate family | Rationale and evidence condition |
| --- | --- | --- |
| **Include — blocked** | Physical pose/kinematics | Strong operational need for Body/Mind consumers and a useful apparatus-measurement case. Blocked until backend-neutral Embodiment quantity/frame/sampling semantics and v1 Body/Embodiment identity links are defined and Physics3D conformance is demonstrated. Limit the candidate initially to a minimal pose/kinematics record; do not presume every force, contact, joint, or work-derived field belongs in it. |
| **Include — blocked** | Environment resource state | Needed to represent an external-domain fact and exercise Environment identity. The current Physics3D path has two distinct sources: recipe fixtures whose IDs are dropped when engine names `fixture.N` are created, and a standalone `PhysicalResource` whose checkpoint has no Resource ID. The observer exposes only session-local `entity.N` keys and no explicit mapping to either source. Blocked until EnvironmentInstance/Resource identity, source-to-runtime links, and units/meaning of retained quantities are established; otherwise narrow or defer this family. Exclude study interventions and nursery support. |
| **Include — blocked** | Organism physiology state | Needed to test Symbiont/Body ownership and state publication. Blocked pending per-state authority and re-embodiment disposition, unit/clock/lineage evidence, and owner review. Current physiology is stored in the organism checkpoint, while apparatus physical state is separate; restore enforces tick alignment but that does not settle ownership or per-value Body linkage. Include only resolved state observations; do not include intermediate `metabolic_work_cost` merely because legacy `vitals` exposes it. |
| **Include — blocked** | Symbiont affordance state | Valuable domain-internal derived case, distinct from Lab derivation. The current resolver path is traced, but the candidate remains blocked on stable subject/context identity, typed temporal references, derivation inputs/lineage, owner review and a legitimate operational consumer. |
| **Include — blocked** | Lab-derived prediction-error band (absolute signed residual classified into a category) | This is a bounded single-input Lab-derived case with existing Mind map/history uses, making it a concrete test of observer-created semantics without forcing a multi-source join into the same record. Current code uses fixed unversioned cutoffs and accepts non-finite floats as `extreme`; the key falls back from `target_id` to `predictor_id`. Block publication until the intended prediction-error definition, finite-value handling, thresholds/classifier revision, source clock, subject identity and a legitimate target consumer are resolved. Preserve the raw signed residual as a distinct source-owned candidate only if its own gates pass; the category must never stand in for organism knowledge. Do not add a cross-domain Lab join to v1 implicitly. |
| **Defer** | Body Schema, Self Model, raw/internal prediction and agency detail beyond the separately listed Lab-derived prediction-error band candidate, Cognitive Atlas, broad cognition/topology inventories, and detailed contact/force/work families | These have unresolved semantic boundaries, identity/time/provenance or publication scope, and are not required to prove the initial observation model. Reconsider only if an operational need is demonstrated and the relevant tracing can pass the same gates. |
| **Exclude** | Durable scientific evidence, evaluator/ground-truth labels, and observer-to-organism control/feedback | These belong to separately governed scientific/evaluation or control paths, not the operational observation contract. A shared underlying quantity does not make the scientific artifact and operational observation interchangeable. |

#### Required cross-cutting context (not semantic families)

| Disposition | Context capability | Rationale and evidence condition |
| --- | --- | --- |
| **Include — blocked** | Subject identity and explicit identity links | Required to interpret every included family. Preserve distinct Organism, Body, EmbodimentEpisode, EnvironmentInstance, Resource and Run namespaces. Block identity-dependent joins until issuer/asserter, lifetime, restore behavior and conflict handling are evidenced; never infer identity from matching legacy field names. |
| **Include — blocked** | Domain time references | Required for time-varying candidates. Carry only clocks actually established for the retained records; resolve organism cycle, embodiment cycle, simulation step/time and their relationships per family. Do not substitute transport sequence for domain time. |
| **Include — conditional** | Provenance/lineage and transformation configuration | Required when a record is derived, measured through an apparatus, joined across sources, or depends on effective configuration. Source facts need not carry redundant provenance where a homogeneous record-level contract suffices. Block records whose interpretation cannot resolve required lineage/configuration. |
| **Include — conditional** | Run/orchestration context | Include only where needed to scope an observation, distinguish execution instances, or resolve a subject link. Treat Run as orchestration context, not as an organism or domain fact; issuer and asserter must be explicit before using it in semantic joins. |
| **Defer** | Transport sequence, stream incarnation, replay cursor and delivery-gap context | These are transport/recovery decisions, not semantic scope. Design them only after the target observation and consumer requirements are approved. |
| **Defer** | UI layout, labels, display aggregation and presentation-only metadata | These remain consumer projections unless a separately justified Lab-derived analytical observation is selected. They are not required semantic context for the initial contract. |

This frozen evidence scope deliberately retains a small but heterogeneous test set: apparatus measurement, Environment state, Symbiont-owned state, Symbiont-domain derivation, Lab derivation, and cross-cutting identity/time/provenance. Evidence gates may narrow or defer candidates; they do not authorize adding unreviewed families. No field, record shape, event, endpoint, or transport is selected here.

### 4.2 Architecture-owner candidate-scope freeze — 2026-10-07

The owner review freezes the following bounded **candidate evidence scope**, not the final set of public v1 records. The dispositions below answer which cases to investigate against the target architecture; `Include — blocked` remains conditional and does not promise publication. A failed evidence/readiness gate may narrow, defer or exclude a candidate. Adding or materially changing a family or required context reopens evidence review for the affected scope.

#### Frozen semantic-family candidates

| Candidate disposition for evidence review | Family | Frozen boundary |
| --- | --- | --- |
| **Include — blocked** | Physical pose/kinematics | Minimal pose/kinematics only; do not silently add forces, contacts, work or all joint fields. Backend-neutral semantics and identity links remain evidence/design gaps. |
| **Include — blocked** | Environment resource state | External resource/environment facts only; keep organism acquisition, nursery support and study interventions distinct. |
| **Include — blocked** | Organism physiology state | Candidate only; do not presume Symbiont versus Embodiment ownership or publish unresolved state. Exclude the intermediate `metabolic_work_cost` absent a separate justified decision. |
| **Include — blocked** | Symbiont affordance state | Domain-derived candidate; identity/context, clocks, input lineage and domain-owner review remain open. |
| **Include — blocked** | Lab-derived prediction-error band | Retained as an architecture stress case only. It may be excluded from final public v1 unless operational need, semantics, finite-value behavior, identity, clock and classifier revision are justified. It must not stand in for Symbiont knowledge. |
| **Defer** | Body Schema, Self Model, raw/internal prediction and broader agency detail, Cognitive Atlas, broad cognition/topology inventories, detailed contact/force/work | Not required for the initial architecture test; reopen only with demonstrated operational need and bounded source evidence. |
| **Exclude** | Durable scientific evidence, evaluator/ground-truth labels, observer-to-organism feedback/control | Outside this operational observation candidate scope; separate scientific and control governance remains in force. |

#### Frozen cross-cutting context candidates

| Context disposition for evidence review | Capability | Frozen boundary |
| --- | --- | --- |
| **Include — blocked** | Subject identity and explicit identity links | Required for all retained families; keep Organism, Body, EmbodimentEpisode, EnvironmentInstance, Resource and Run identities distinct until explicit links are evidenced. |
| **Include — blocked** | Domain time references | Include only clocks demonstrated for retained records; do not substitute transport ordering for domain time. |
| **Include — conditional** | Provenance/lineage and transformation configuration | Required where apparatus measurement, derivation, join or configuration materially affects interpretation; exact representation is a TO-BE decision. |
| **Include — conditional** | Run/orchestration context | Include only when needed to scope records or resolve a subject link; never treat Run as source-domain fact. |
| **Defer** | Transport sequence, stream incarnation, replay cursor and delivery-gap context | Not part of the frozen semantic/context evidence scope; decide after target record semantics and consumer requirements. |
| **Defer** | UI layout, labels, display aggregation and presentation metadata | Consumer projection unless separately justified as an analytical Lab-derived observation. |

This freeze bounds the evidence pass and permits the TO-BE entry gate to be evaluated. It does not settle per-record authority, domain-semantic approval, field inclusion, record readiness, Envelope Readiness, delivery, transport, or implementation authorization.

## 5. Candidate scope and evidence gates

Keep the candidate set deliberately small; its purpose is to stress the architecture across distinct provenance/derivation cases, not to inventory all Symbiont state. The bounded candidate evidence scope is frozen in §4.2: semantic families and cross-cutting context are listed separately and must not be conflated.

Use this sequence to avoid requiring a contract before the TO-BE has designed it:

```text
candidate v1 semantic families + required cross-cutting context (freeze separately)
        → minimum source evidence and explicit gaps
        → TARGET ARCHITECTURE ENTRY
        → separate TO-BE defines observation, identity, time, provenance and coherence models
        → candidate semantic record definitions
        → record-level evidence and interpretability gates
        → final v1 record scope / Envelope Readiness
        → event, snapshot, delivery and transport specification
```

Before TO-BE entry, AS-IS evidence must be sufficient to identify source paths, known ambiguities and risks for the frozen candidate families; it need not define the future record fields or pass record-level interpretability. The TO-BE is where the semantic observation and cross-cutting models are deliberately designed. After those models exist, no proposed record may pass Envelope Readiness if a field depends on implicit consumer knowledge for authority, subject/identity link, clock, units/frame or transformation. Remove, split or defer unresolved fields; if no coherent record remains, defer the family.

The recorded candidate freeze bounds TO-BE inputs but does not freeze fields, records or transport. The TO-BE may explicitly narrow or defer families based on its record-level design and readiness review; adding a materially new family requires renewed evidence review for that scope. Readiness is record-specific: a family does not pass merely because its headline meaning is understood if an included field still has unresolved identity, time, units/frame or transformation semantics.

## 6. Required design-input topics

The TO-BE must resolve these topics from the approved candidate scope and source evidence:

- **Identity:** identifier kind, issuer, asserter, scope/lifetime, restore behavior, explicit links, contradiction handling.
- **Time:** typed domain clocks and their relation (if any); transport ordering must not masquerade as domain time.
- **Physical semantics:** backend-neutral quantity kinds, units, axes, frames, sampling semantics, versioning, and per-backend conformance.
- **Lineage/provenance:** source facts, apparatus measurements, domain derivations, observer derivations, and multi-input derivation graphs.
- **Coherence:** what constitutes a coherent cross-source snapshot/cut and how its limits are represented.
- **Availability/completeness:** absent, unavailable, not observed, not applicable, partial, and explicit loss/gap semantics where relevant.
- **Consumer sufficiency:** Mind, Body, Development, and operational diagnostics must be rebuildable from approved observations without source-internal inspection or legacy projections.
- **Persistence boundary:** bounded operational materialization/replay must remain distinct from durable scientific artifacts.
- **Non-interference:** read-only behavior, bounded resource use, and no observer-to-organism feedback dependency.
- **Replacement:** remove the old operational API/stream/projection assumptions at cutover; no compatibility alias or second live truth source.

## 7. Remaining design decisions and evidence gates

The target architecture has been approved for its direction and boundaries, but its semantic records and operational mechanisms are not specified. This section separates **approved architectural direction**, **remaining record/contract choices**, and **evidence conditions that must be met before candidate scope and records can be frozen**. Current implementation behavior informs these choices but is not their default answer.

The distinction is:

```text
constraint / design input: what the future design must respect, subject to owner disposition
architectural decision: what the future design deliberately chooses among viable options
evidence gate: what must be demonstrated before a scope or record can be frozen
```

The scoped architecture-owner disposition in §3 and the subsequent Target Design disposition accept the architecture direction: role separation, the five-domain authority model, observation-oriented semantics with event delivery only where needed, domain-owned observation production with Lab coordination (Option C), explicit identity links and fail-closed dependent joins, consumer-driven coherence, separation of operational observation from scientific evidence, full operational replacement, and demonstrable non-interference. These are not permanent constitutional amendments, datum-level assignments or implementation specifications. The AS-IS findings do not decide their implementation.

Remaining choices concern record boundaries and concrete representations, datum-level authority, final publication scope, consumer-specific coherence requirements, delivery/replay mechanics and the physical/physiological semantics of retained records. Infrastructure ownership is no longer open for v1: Option C is approved in Target Design §6.2. The coherence policy is also decided: consumer-driven, with no global coherent-snapshot guarantee. These choices must not be made by treating current implementation behavior as the default.

### 7.1 Remaining record and access design decisions

The target architecture direction is approved. The following record, publication and access choices remain open unless explicitly dispositioned below.

1. **Final v1 semantic scope** — Decide which frozen candidate families are included or deferred in final records. Keep required cross-cutting context (identity, clocks, provenance and run context) separately dispositioned. Inclusion must follow operational need and evidence sufficiency, not current Lab fields.
2. **Datum-level authority assignments** — The five-domain governing model is accepted for this design (§3), but authority for individual data remains unresolved. Confirm assignments from domain evidence/owner review and decide how retained domain-internal and cross-domain derivations preserve authority and lineage without making Lab the implicit universal owner.
3. **Canonical semantic observation model** — Decide the semantic atomicity boundary, metadata intrinsic to every record versus conditional by family, representation of derived inputs/lineage, and how records may be grouped without implying common authority. The design input is observation-oriented and event-delivered where live changes require it, not event-owned.
4. **Identity model** — Decide identifier kinds, issuer/asserter, scope and lifetime, restore/re-embodiment behavior, explicit alias/link relationships, conflict representation, and fail-closed behavior for identity-dependent joins. Do not inherit equality from legacy names such as `body_id` or `world_id`.
5. **Temporal model** — Decide which typed domain clocks are public and how (or whether) they relate, including organism cycle, embodiment cycle, simulation step/time and world/projection revision. Keep transport ordering distinct from domain time.
6. **Backend-neutral physical observation contract** — Define the Embodiment-owned quantity semantics required by retained physical families: quantity kind, unit, axis convention, coordinate/reference frame, orientation representation, sampling/integration window, joint/part identity and semantic contract version. Physics3D must demonstrate conformance. Multi-backend semantic conformance is a separate future generality gate, not a prerequisite for this contract, TO-BE or v1. Activate it only when a second concrete backend is ready to publish a family already defined by the backend-neutral contract. Evaluate per overlapping published capability: require equivalent semantic meaning, units, frames/axes, sampling/time, subject identity and availability/completeness; backend-specific assumptions must remain separately attributed. Unsupported families are declared unsupported. Backend implementations need not be equivalent, and no synthetic backend is required.
7. **Physiology and re-embodiment ownership** — Decide ownership and lifecycle semantics for retained physiology: Body-local, portable with Symbiont, reset, initialized from a new Body, derived, or historical-only. Resolve modeled Body physiology, organism regulation, external embodied-work/resource inputs and retained history.
8. **Cross-domain causal-conversion model** — Decide how converted inputs are attributed and represented (for example physical work estimate → configured conversion → embodied-work input → later physiology change), including semantic ownership, effective configuration/version provenance, source/application clocks and whether the intermediate input is public.
9. **Provenance and lineage model** — Decide the minimum provenance needed to interpret source-owned state, apparatus measurements, domain-/Lab-derived observations, multi-input joins and configured transformations. The target must preserve or resolve required lineage without mechanically copying the audit vocabulary into wire fields.
10. **Observation-plane infrastructure ownership — DISPOSITIONED** — Option C is approved for v1: domain-owned semantics/producers with Lab-owned operational coordination, materialization and delivery. Standalone extraction is deferred until demonstrated deployment or multi-host value. See Target Design §6.2.
11. **Consumer-specific composed-view requirements — ARCHITECTURE POLICY ACCEPTED; CONSUMER NEEDS OPEN** — Coherence is consumer-driven, with no global coherent-snapshot guarantee. Each retained consumer must specify participating observations, clocks/revisions, maximum skew, partial behavior and identity requirements. `ObservedFrame` is not a target structure or consistency oracle.
12. **Event and delivery model** — Decide which retained families/consumers need live delivery, change semantics, batching, ordering, duplication/idempotency expectations and how delivery refers to or carries semantic observations. Event delivery must not become the semantic source of truth.
13. **Materialization, query, replay and gap recovery** — Decide operational current-state retention, bounded history, replay guarantees, stream incarnation/sequence, gap detection, snapshot rebase and reset behavior. These mechanisms remain distinct from scientific evidence storage.
14. **Availability and completeness** — Decide how to distinguish absent, unavailable, not observed, not applicable, unsupported, partial, stale and data lost through a delivery gap, without consumer-specific interpretation of omitted fields.
15. **Publication and visibility** — Decide the concrete boundary among public operational observations, private/debug data and scientific evidence. Minimize publication and justify it by legitimate consumers; internal availability alone is not a reason for public-contract inclusion.
16. **Consumer contracts** — Decide what Mind, Body, Development and operational diagnostics may assume. Consumers must be reconstructible from approved observations and explicitly attributed Lab derivations without direct runtime inspection, hidden adapter knowledge, legacy payloads or implicit joins.
17. **Observational non-interference — PRINCIPLE ACCEPTED** — The architecture requires passive/read-only observation, bounded cost, backpressure/failure isolation and no observer-to-organism feedback, without prohibiting organism-owned interoception/regulation. The testable budgets and failure contracts remain specification/implementation gates.
18. **Replacement and cutover — DIRECTION ACCEPTED** — Full replacement is approved; no backward-compatibility contract, permanent adapters/aliases or production dual truth source. Differential testing is validation only and does not require parity. Concrete acceptance/deletion tests remain a later cutover decision.

### 7.2 Evidence and readiness gates

These are prerequisites, not architecture choices. Distinguish the evidence needed to enter the TO-BE from the stricter gates applied later to proposed records. Unrelated AS-IS traces need not be completed before v1 can proceed.

1. **Scope-freeze gate — PASSED for the current bounded set (2026-10-07)** — §4.2 freezes candidate semantic families and required cross-cutting context for evidence investigation only. This does not freeze records or publication. Adding or materially changing a candidate restarts evidence review for that scope.
2. **TO-BE-entry evidence gate — PASSED for the frozen candidate set (2026-10-07)** — The Current-State Assessment contains bounded source-to-consumer traces sufficient to identify current paths and explicit limitations: physical pose/kinematics and physical/Environment identity (§9.5); Environment resource and acquisition/work-to-physiology paths (§9.6); Symbiont affordance derivation and bounded Lab prediction-error classification (§9.8); and current identity issuer/asserter and clock namespaces (§9.1–§9.2, §9.5 and §9.8). These traces expose rather than resolve missing backend-neutral units/frames/sampling semantics, canonical identity links, physiological ownership, typed public clocks, classifier semantics and lineage. Those gaps are inputs to target design or reasons to narrow records, not missing AS-IS tracing prerequisites. This gate does not pass record-level interpretability or authorize publication.
3. **Owner-disposition gate — ARCHITECTURE DISPOSITION PASSED (2026-10-07); DOMAIN DISPOSITION OPEN** — Keep two approval kinds explicit, even if one person currently holds both roles:
   - **Architecture owner:** approves, refines or rejects architecture-level constraints and decisions (for example observation-oriented/event-delivered scope, identity-join policy, and bounded candidate-family/context freeze). This role does not assign domain meaning to data or approve individual records.
   - **Domain semantic owner:** confirms or rejects the meaning and semantic authority of records originating in that domain (for example whether a physiological quantity is Symbiont- or Embodiment-authoritative). This disposition does not approve the overall architecture or transport.

   Lab-created analytical semantics require an explicit Lab-side semantic disposition. A person may hold multiple roles, but record each disposition by role and scope. The architecture-owner disposition in §3 passes that part of the TO-BE entry gate. Domain-semantic dispositions are required before affected source-domain records can be frozen, and unresolved assignments must remain explicit. Code location, legacy names and projection labels are insufficient evidence.
4. **Record-level interpretability gate (after TO-BE model design)** — Every proposed record field must be interpretable under the TO-BE observation, identity, time and provenance models without undocumented adapter/UI/consumer knowledge. Remove, split or defer unresolved fields/records.
5. **Representative end-to-end trace gate (for retained records)** — Provide a complete trace for each semantic case retained after TO-BE record design, covering applicable apparatus measurement, Environment state, Symbiont source-owned and domain-derived state, Lab-derived observation if retained, cross-domain conversion and identity/context. A cross-domain Lab join is outside this proposal unless separately added and reviewed.
6. **Consumer-sufficiency gate** — Rebuild retained operational consumers from approved observations and explicitly attributed derivations, without legacy source inspection.
7. **Coherence gate** — Demonstrate which consumers require coherent multi-source views and the guarantee they need. Do not infer that current `ObservedFrame` provides the target model. The existing checkpoint restore tick comparison is a narrow cross-artifact alignment guard; it does not establish atomic pair persistence or a general observation snapshot/watermark guarantee.
8. **Scientific-separation gate** — Preserve the boundary between operational materialization/replay and durable scientific evidence, including their distinct provenance and reproducibility obligations.
9. **Non-interference gate** — Demonstrate that observation does not change organism behavior or create causal dependence through sampling frequency, backpressure, failure, logging or UI activity.

### 7.3 Target-design entry condition

The Target Design entry gate **PASSED** on 2026-10-07. The separate **Observation Architecture v1 — Target Design** is now architecture-owner approved with refinements for direction and boundaries. The next activity is candidate semantic-record boundary/context design and domain-semantic review. Target entry did not require final record definitions or record-level interpretability; those are subsequent gates.
The approved Target Design is at [observation-architecture-target-design-v1.md](observation-architecture-target-design-v1.md). Its approval does not authorize record schemas, transport, implementation or cutover. Missing source evidence is not a substitute for a design decision; unresolved evidence must remain visible and may narrow/exclude a family or field.

## 8. Links and authority limits

- AS-IS evidence and task tracking: [Current-State Assessment](observation-architecture-current-state-assessment-v1.md).
- Lifecycle/status: [Design Status Register](../register.md).
- This package summarizes the assessment; if a claim is disputed, consult source paths and tests cited there.
- This package does not amend permanent architectural invariants, scientific protocols, the roadmap, or implementation authorization.

## 9. Design-input checklist

Track this package one bounded item at a time. Use explicit checklist states: `DONE`, `IN PROGRESS`, `QUEUED`, and `BLOCKED`. The **current focus** is the single item explicitly marked `IN PROGRESS`, never merely the first unchecked item. Only one sequential item may be `IN PROGRESS`; `BLOCKED` is reserved for a genuinely unavailable prerequisite and is not treated as the next actionable item. Dormant future gates are listed separately from the sequential checklist. Completing an item records documentary/source work only; it does not imply owner approval, freeze, TO-BE authorization or implementation permission. Keep the package **Proposed / Partial** until its relevant owner dispositions are recorded.

- [x] **Draft candidate v1 semantic scope proposal — DONE (2026-10-07).** §4.1 separates semantic families from cross-cutting context and records include/defer/exclude/blocked dispositions with reasons; §4.2 freezes that bounded evidence-investigation set. This does not approve final records or publication.
- [x] **Adversarially review proposed constraints and authority boundaries — DONE (2026-10-07).** §3 records the adversarial review and its limits, distinguishing cross-domain design inputs from unresolved choices.
- [x] **Resolve document lifecycle and gate-boundary review — DONE (2026-10-07).** §5 and §7.3 distinguish Target Architecture Entry from later record-level interpretability and Envelope Readiness; §9 tracks the current focus explicitly rather than using the first unchecked item; the multi-backend gate is dormant and off the v1 critical path; the AS-IS checklist remains limited to current-state tracing; and §7.2.3 distinguishes architecture-owner from domain-semantic-owner disposition.
- [x] **Record architecture-owner disposition of proposed constraints — DONE (2026-10-07).** The owner disposition in §3 accepts the 11 constraints as scoped target-architecture inputs with explicit refinements and boundaries. This does not approve individual data semantics, final records/publication, implementation or cutover.
- [x] **Freeze candidate v1 evidence scope — DONE (2026-10-07).** §4.2 freezes the semantic-family and cross-cutting-context investigation set separately, retaining blocked/conditional/deferred/excluded statuses. This bounds evidence work only; it does not approve final records, publication, or TO-BE details. Adding or materially changing a candidate restarts evidence review for that scope.
- [x] **Complete minimum AS-IS evidence for frozen candidates — DONE (2026-10-07).** §7.2.2 links the frozen families to the bounded source traces and records the material unresolved semantics. Physical quantity serialization, constrained-zero velocity and distinct tick-end/presentation sampling paths are traced in Assessment §9.5; resource and causal physiology paths in §9.6; affordance and prediction-error source-to-consumer paths in §9.8; identity issuer/asserter and clock namespaces in §9.1–§9.2, §9.5 and §9.8. This satisfies minimum evidence for TO-BE entry only; it does not close target semantics, final records or publication readiness.
- [x] **DONE (2026-10-07) — Open and obtain disposition of the separate TO-BE.** Project-owner authoring authorization and architecture-owner approval with refinements are recorded in the Target Design. Approval is limited to architecture direction/boundaries and does not approve records, transport, implementation or cutover.
- [ ] **IN PROGRESS — Define candidate semantic-record boundaries and conditional context.** Target Design §9.1–§9.2 proposes boundaries for the frozen evidence families. Obtain required domain-semantic dispositions; do not infer final schemas, datum authority or publication.
- [ ] **QUEUED — Evaluate record-level evidence/readiness and final v1 scope.** Resolve field interpretation, lineage, identity, clocks, units/frames and consumer needs. Remove, split or defer records that fail; only then determine final record scope and Envelope Readiness.
- [ ] **QUEUED — Specify event, snapshot, delivery, replay and transport.** Do this only after semantic records and Envelope Readiness are dispositioned. Preserve full replacement; do not revive legacy compatibility or the superseded Symbiont Telemetry Event API without an explicit reopening decision.

#### Dormant / future generality gates (not on the v1 critical path)

- **BLOCKED — Validate multi-backend semantic conformance (only one concrete physical backend exists).** Activate only when a second concrete Embodiment backend is ready to publish a family already defined by the backend-neutral contract. Evaluate each overlapping capability independently: same semantic contract/version and quantity meaning; compatible canonical units; equivalent frame/axis and explicit sampling/time semantics; valid subject identity; equivalent availability/completeness; no hidden backend assumptions. Keep backend-specific metadata separately attributed and require conformance tests. Backend implementations need not be equivalent; unsupported families are declared unsupported. Do not create a synthetic backend or delay v1 to satisfy this gate.

**Current focus:** Define candidate semantic-record boundaries and conditional context in the Target Design and obtain domain-semantic dispositions. The Target Design is approved only for architecture direction/boundaries; the Design Inputs package remains Proposed / Partial. Record schemas, final publication, transport, implementation and cutover remain gated separately.

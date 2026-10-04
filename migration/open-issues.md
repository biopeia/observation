# Open issues

Classification follows `INSTRUCTIONS.md` §23. Nothing here was fixed silently.

## Requested by the owner during the migration

| Item | State |
| --- | --- |
| Remove import aliases and forwarders | DONE |
| Remove the legacy agent simulation and everything that ran on it | DONE |
| Remove old persisted formats | DONE: checkpoint schemas 1–10, genome schema 1 and `HeritableGenome`, telemetry v3/v4 |
| Remove the desktop workbench | DONE. `lab.app.physics3d` stays: the server uses its run store and session, and the Physics3D engine uses its Qt viewer. |
| Remove the lab demo and the Observatory front-end | DONE |
| Domain packages named after the domain, not after the organism | DONE |
| Move into `modality/` and `embodiment/` what belongs there | DONE for concrete coupling (bodies, vision array, host channels). Intrinsic organism state stays in the organism by decision |
| The four domain libraries are peers with no first-party dependency on each other or on the Lab; the Lab is the only composition root | DONE (Import Linter, hard test gate, per-library isolated tests); the organism builds no concrete source |
| Enforce the boundaries with Import Linter | DONE: three contracts in `pyproject.toml`; runs in CI, pre-commit and the test suite |

## State after the third round

Done and validated (six suites green, Import Linter 3 contracts, each library
installed alone outside the repository, organism identity 13/13):

- every domain owns its tests (`<domain>/tests`) and the organism its
  documentation (`symbiont/docs`); `tests/` holds repository-wide checks only;
- governance covers every path of the five domains; domain `pyproject.toml`
  files and the boundary checks are CONSTITUTIONAL;
- real backends are declared as extras (`embodiment[physics3d]`,
  `modality[vision]`, `environment[physics3d]`) and imported by the package
  that declares them: nothing receives the PyBullet module as a parameter any
  more. The backend ban applies to the organism only;
- returned from the Lab to their owner: the deferred-damage rule and the
  physical resource (Environment), the re-embodiment transition and its
  longitudinal memory (Symbiont);
- **OI-3, the organism and its sense sources, is closed (steps A–G):**
  - the organism resolves which senses it requires in a pure function
    (`symbiont.core.orchestration.sense_requirements`), for a fresh creation
    and for a restore; the Lab does not interpret checkpoint controls;
  - `lab.integration.organism` composes the concrete sources and provides
    explicit first-boot creation and required restore for the canonical
    organism. Every caller in `lab/src`, `lab/tests` and `tests` goes through
    it;
  - `OrganismRuntime()` builds no provider and inspects no platform: on its own
    it is a minimal organism with no host source;
  - the concrete host channels live in `modality.host` with their own record
    types; `lab.integration.organism.host_sources.HostSource` converts them;
  - `symbiont.host.providers` no longer exists, and a test asserts it;
  - interoception is split by provenance: the organism's own channels stay in
    `symbiont.sensory.interoception`; host process measurements are
    `modality.host.process_telemetry` and are no longer called interoception;
  - no test in `symbiont/tests` imports the Lab. A trial with the organism's
    providers removed left 1797 of them passing unchanged; the two that asserted
    what the canonical composition picks per platform moved to `lab/tests`.

Order actually followed: A, B, restore resolution, C, interoception split, D,
F and G, E. F had to precede E: an organism that still built its own providers
could not import them from `modality`.

Equivalence with the organism that built its own sources was checked against
the pre-migration tree through commit `2632ff40e` (nine option sets and 54
restores with overrides, same state hash and checkpoint). The check cannot be
run any more: checkpoint schema 12 is deliberately incompatible with schema 11.

### Decisions and remaining owner work (scientific, not structural)

The migration deferred changes that affect energy trajectories or perception.
The owner subsequently requested resolution of the consolidated audit issues;
the telemetry-cost defect below is fixed, and its unchanged canonical-profile
configuration is covered by an instrumentation-invariance regression test.

- **Host telemetry costs the organism energy — FIXED locally (2026-10-04).**
  Perception metabolism is now charged only for organism-facing readings;
  apparatus process telemetry no longer changes energy. The former strict xfail
  is now a passing invariance test in
  `symbiont/tests/unit/sensory/test_interoception_independence.py` (6 passed).
  Its `test_canonical_profile_v1_is_invariant_to_unperceived_host_telemetry`
  case confirms the approved v1 runtime settings still expose no interoception
  provider and produce the same state hash with process telemetry present or
  absent. No v1 setting or profile-version change is made; historical runs with
  non-canonical interoception settings were not re-audited.
- **Interoception is only offered where host senses are.** The organism's own
  interoception is attached only when `discover_senses` is on and the Lab
  reports the host available. Kept as it was; a minimal `OrganismRuntime()`
  therefore has none.

### Still open

- **Persisted names.** Host telemetry is still published under the source id
  `interoception` and the capability ids `internal.tick_latency` /
  `internal.memory_rss`, because they are written into checkpoints. Same kind
  of debt as `APPARATUS_FIELDS`; nothing in this work touched schema, hashing
  or the envelope.
- **Residue in the organism.** `symbiont.core.embodiment.transition` keeps a
  fallback descriptor naming a concrete body kind for checkpoints older than
  embodiment epochs.
- **Units inside the organism still mix state and coupling.**
  `symbiont.core.embodiment`, `symbiont.actuation`, `symbiont.sensory` and the
  generic machinery in `symbiont.host` were kept in the organism on purpose
  (body schema, physiology, metabolism, homeostasis, sensory and motor
  learning are intrinsic). Only concrete external coupling left.
- **Design documents.** `docs/design/` stays at the root: preregistrations, a
  frozen artefact and a path protected by running work. `embodiment`,
  `modality`, `environment` and `lab` have no documentation of their own beyond
  a README.

The sections below predate this round; where they disagree, this section is
current.

## Architecture debt

**OI-3 — CLOSED.** See "State after the third round".

**OI-4 — What remains in `lab.physics3d` and `lab.world`.** Engine, runtime
and persistence compose organism, body and environment; they are Lab
composition and stay. **Resolved sub-boundary:**
`environment.physics3d.resource` owns its `ContactMaterial`; it does not import
the body's `SurfaceMaterial`. The five-domain import contract prohibits peer
dependencies and is exercised by
`tests/experimental_integrity/test_five_domain_architecture.py`. The
observer-only labels in `observer_semantics` belong to the Lab. `lab.world`
keeps the population runtime, transactions and persistence.

**OI-5 — The Lab still imports organism internals beyond `symbiont.api`.**
This applies to the Lab only. The other three libraries import nothing from
Symbiont, and the fix for them was never to widen the API: code that needed the
organism moved to `lab.integration`. The canonical organism composition,
organism CLI, replay runner, and clonal-budding orchestrator use `symbiont.api`
for lifecycle types and checkpoint entry points. The resident launcher and
advisory evaluator now also use its checkpoint operations. Lab production and
study code still imports organism subsystems directly; deciding
which additional internals (including
`symbiont.modeling` and `symbiont.cognition.generative`) belong in the public
surface remains open.

**OI-17 — Domain contracts are implicit.**
The Physics3D apparatus contract is now owned by `embodiment.physics3d` and
consumed by the Lab adapter; it names receptor sampling, opaque
receptor/effector ids, and motor port pairings. The organism's passive process
telemetry hook is also now a named `ProcessTelemetryObserver` protocol rather
than `Any`, preserving observer-only ownership. Other hand-offs still need an
owner-by-owner contract audit, and `lab.integration.physics3d.apparatus` still
constructs organism types (`SensorReading`, `Capability`,
`ActuatorConstitution`) at the composition boundary. Domain-owned contracts
across those boundaries remain open.

**OI-6 — CLOSED: leaf imports no longer rely on core initialization order.**
Shared epistemic conventions and organism limits now live in the independent
`symbiont.foundation` package, so cognition and host leaf modules do not import
through `symbiont.core`. The top-level `symbiont` package loads its `core`
facade on demand rather than eagerly. Subprocess regressions verify direct
imports of `symbiont.cognition.checkpoint` and `symbiont.host.acclimation`
without initializing `symbiont.core`, and verify the public core facade still
loads on demand. The full Symbiont suite passes.

**OI-15 — `core.cognition.bridge_compat`.**
A 478-line mixin that forwards 42 private attributes of `CognitiveBridge` to
its collaborators. It is internal API indirection, not an old data format: the
organism itself uses it in 25 places, tests in 85. Left as is.

**OI-18 — Cognitive epistemic ownership and evidence lineage.**
The bounded source-and-test audit is complete in
[`Epistemic Ownership and Claim Levels v1`](../docs/design/core/epistemic-ownership-and-claim-levels-v1.md),
but the design remains proposed and several ownership contracts are incomplete.
Keep mechanisms separate; do not unify cognition scores, merge stores, or make
E3/E4 claims from code or persistence. Planned follow-up, in order:

1. Specify the canonical evidence-reference owner and enforce resolution at
   the `note_factual_outcome()` boundary; add a focused regression proving a
   reference must resolve to a recorded `OBSERVED` experience before it can
   reconcile a hypothesis.
2. Complete source/revision/retraction contracts for CognitiveGraph,
   predictor promotion/retirement, causal/sensorimotor evidence, competence
   materialization/revocation, and their checkpoint/restore consumers.
3. Define provenance and contradiction/eviction contracts for episodic
   retrieval/replay and consolidation; do not claim replay changes later
   action choice without a differential engineering test.
4. Specify caller authority, source attribution, and reconciliation for
   social claims and symbol/sequence grounding; preserve the current absence
   of a canonical peer-claim-to-organism-decision path.
5. Keep private-model prediction quality, ancestry utility, replay utility,
   and generative causal contribution as separate scientific questions. Any
   E3/E4 work requires its governing approved protocol and authorization; this
   issue authorizes no experiment.

**Acceptance:** each live owner has the §2 contract fields in the linked design
or an owner-approved successor; production evidence references cannot be
reconciled without resolving to their canonical observed source; targeted
regressions cover invalid, missing, and contradictory evidence paths; no
consolidation or stronger capability claim is made without evidence matching
the relevant level. Scientific utility and causal claims remain outside this
engineering issue.

## Consolidated longitudinal-integrity audit (2026-10-04)

This is a status reconciliation, not a claim that all scientific capabilities
are demonstrated. Statuses below distinguish implemented mechanisms from
unverified semantics and evidence.

| Issue | Current status | Remaining boundary |
| --- | --- | --- |
| SYM-01 continuation-condition integrity | **Implemented locally**; schema 12 verifies a separate condition hash and rejects missing contemporary controls | Hash is unkeyed integrity, not authentication; no publication claim yet |
| SYM-02 silent rebirth on missing checkpoint | **Resolved in this repository**; required restore fails and first-boot creation is explicitly named; the replay CLI uses required restore | External deployments are outside this checkout and cannot be audited here |
| SYM-03 observer telemetry changes organism energy | **Resolved for runtime and canonical profile v1** | Instrumentation invariance passes for intrinsic state in enabled/sham modes and for the approved v1 configuration; no profile setting/version change is required. Historical non-canonical trajectories were not re-audited |
| SYM-04 BodySchema historical knowledge vs current-body authority | **Resolved for the canonical re-embodiment path** | The consumer audit found no active read of archived BodySchema priors; the current schema resets at transition and old content remains historical. No transfer-utility claim follows, and external consumers of exported snapshots are outside the audit scope |
| SYM-05 exact checkpoint schema policy | **Implemented/documented**; only schema 12 restores | Historical checkpoints are archival evidence, not live-restorable organisms |
| SYM-06 continuity register semantic correctness | **Sensory binding and developmental edge cases resolved; broader register audit remains open** | `_sensory_system` and `_adaptive_senses` now have an explicit split: acquired state is retained only as `BodySpecificMemory.sensory_prior`, while active models come from the fresh Body checkpoint. `DevelopmentalTracker.previous_stressed` is reset at re-embodiment so the first active observation of a new Body cannot count as recovery from the closed Body. Regression and composite tests cover these cases; the register-wide semantic audit remains incomplete |
| SYM-07 epistemic ownership | **Bounded audit closed; follow-up tracked as OI-18** | Source/test review and selected consumer paths are documented in the proposed design. Owner approval and complete source/revision contracts remain open; no consolidation or capability claims beyond the scoped E0–E2 evidence follow from this audit |
| SYM-08 broad `OrganismRuntime` | **Open architectural debt** | Defer extraction until stable ownership boundaries justify it |
| SYM-09 budding semantics | **Contract clarified** as clonal budding | No recombination or Genome v2 reproductive inheritance is claimed |
| SYM-10 integrated transgenerational epigenetics | **Open functional gap** | Somatic and germline marks are not an evidenced inheritance chain |
| SYM-11 social learning | **Partial** | Existing communication/claims/evidence do not establish a canonical peer-claim-to-decision policy |
| SYM-12 ancestry utility | **Mechanics only** | Causal learning benefit is not demonstrated |
| SYM-13 generative cognition utility | **Mechanism present; utility unproven** | No causal/adaptive benefit is claimed |
| SYM-14 restart semantics | **Documented intentional behavior** | Semantic continuity is not trajectory equivalence |
| SYM-15 legacy anthropomorphic fallback | **Fail-closed for current-schema re-embodiment**; missing/invalid lifecycle metadata now rejects transition instead of inheriting the legacy profile | Pre-epoch archival payloads still use the bounded v4 assumption. A repository scan found no checkpoint-like JSON artifacts; external/archive populations remain uncensused, so legacy fallback retirement is not justified |
| SYM-16 stale migration descriptions | **Resolved for current outer-checkpoint policy** | Active loaders and restore docs state schema 12 only; historical Living Body, re-embodiment, and ADR migration plans now identify themselves as historical and cannot imply that schemas 1–11 restore. Baseline/validation artifacts remain timestamped historical evidence; subsystem-local migrations are separate contracts |
| SYM-17 composite re-embodiment test | **Resolved for implemented/acquired state** | `lab/tests/integration/test_reembodiment_continuity.py` develops one subject with acquired cognition, sensorimotor, causal, private-model, ancestry, social, relation and grounding state, then checkpoints, restores, re-embodies and advances it. Unsupported acquired epigenetic priors are deliberately absent (SYM-10), so no epigenetic continuity is claimed |
| SYM-18 capability/evidence conflation | **Initial inventory completed** | The proposed ownership design now rates each traced epistemic mechanism at a conservative E0–E2 ceiling and states why no E3/E4 benefit or causal claim is established. Re-rate on implementation changes; this inventory does not replace controlled evaluations |

### BodySchema consumer audit findings

The current BodySchema representation has no per-item body/episode provenance;
it stores learned sensory/cognitive structure and agency-boundary evidence in
one representation. That is not by itself an authority leak in the canonical
path: re-embodiment archives the complete prior schema and resets the active
schema before restore into Body B. The action-domain boundary update uses only
channels from the just-closed transition and agency estimates newer than the
current episode start; integration tests check inference against Body B
identities. Passive runtime snapshots and embodiment adaptation/continuity
summaries were traced; archived `body_schema_prior` is not fed back to the
active engine or execution authority. **SYM-04 is resolved for the canonical
re-embodiment path.** No transfer-utility claim follows, and arbitrary external
consumers of exported checkpoints or snapshots remain outside the audit scope.

The functional-transfer mechanics check now follows this nested policy rather
than requiring byte identity for the entire `body_schema` checkpoint field: it
verifies that the old schema is archived and the active schema is reset. The
frozen scientific protocol constants and campaign claims were not changed.

### Canonical-profile consequence of the telemetry correction

The correction changes the defective instrumentation-coupled behavior, not the
approved profile configuration. The focused invariance suite compares the
approved `CANONICAL.runtime_kwargs()` with process telemetry absent/present and
asserts both no interoception provider and an identical organism state hash.
Canonical Organism Profile v1 remains unchanged; this does not retrospectively
validate historical runs using non-canonical interoception settings.

## Other

**OI-7 — Lab scripts still at the root.** `scripts/bench_*.py`,
`characterize_kernel.py`, `aggregate_e8_*`, `run_e8_*`, `reprofile_performance.py`
are Lab analysis; `scripts/agentctl.py` and `scripts/governance/` are governance.

**OI-8 — CLOSED.** Each domain's tests live in `<domain>/tests`; `tests/` holds repository-wide checks.

**OI-9 — Runner scripts of completed experiments use the old package names.**
`lab/experiments/world/genesis-v1/{run_w01_w02,run_w02_retry,run_w03,view_world}.py`
import `symbiont_lab` / `symbiont_world`. Left unmodified as evidence; they run
only against the source repository.

**OI-10 — No full scientific equivalence campaign.** The equivalence unit and
integration tests pass, but `agentctl`'s equivalence suite was not run.

**OI-11 — Governance tooling is path-rewritten but not exercised.**
`docs/governance/*.toml`, `scripts/governance/`, `scripts/agentctl.py` and
`.github/workflows/` point at the new paths, and their unit tests pass.
Frozen-evidence detection keys on `lab/experiments/`. `agentctl publish` and a
remote CI run have not been performed. A local `agentctl ci-check` against the
branch base fails because all 75 unpublished commits lack `Governance-Class`
trailers; checking the current metadata-bearing documentation commit alone
passes (`agentctl ci-check --base HEAD^ --head HEAD`). The range failure does
not establish that the final changed-file plan is wrong. The `observatory` lane
and CI job names remain as labels for the still-active Lab Observatory
subsystem.

**OI-12 — CLOSED for current documentation navigation.** The obsolete root
`docs/architecture.md` exposition was replaced by a navigation page to the
canonical `symbiont/docs/` description; the portal no longer presents it as a
unified current-state specification. Stale `docs/math/` references were
replaced by the current mathematical map, and the web-source taxonomy now
points to the canonical documentation. Historical design and research records
remain available as history and are not asserted to describe current runtime
behavior. Validation: documentation links and source-trace tests pass.

**OI-13 — Generic top-level import names.** `lab`, `environment`, `modality`
and `embodiment` could collide with a third-party package of the same name.
Inside this workspace they resolve to the local members.

**OI-14 — `git status` was run once in the source repository** before the
no-touch rule was applied strictly (it can refresh the index stat cache). No
file there was created, changed or deleted; its `HEAD` and working tree are as
they were.

**OI-16 — CLOSED: stale web residue removed or accurately described.** The
retired `#lab` and `#experiments` aliases are removed; unrecognized routes
already resolve to Home. The joint-angle interpolation remains as a
presentation-only fallback for sparse pose frames without authoritative link
poses, and its comment now describes that active behavior rather than calling
it legacy/demo telemetry. A smoke assertion covers the route table and wording,
and Node syntax checks plus the unified-app asset smoke test pass; no claim of
interactive browser QA is made.

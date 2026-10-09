# Migration record

## Provenance

- Source repository: `symbiont-lab`
- Source repository SHA: `80d372a186513035f85a769db886e505cabba52d`
- Original source paths:
  - `lab/src/lab/observation/contracts.py`
  - `lab/src/lab/observation/projection.py`
- Source commits:
  - contracts: `e6a704b84349b64bbb2ccd721ac4d429104416d5` (`2026-10-05`, `fix(observation): keep frame compatibility while adding identity contract`)
  - projection: `13720935595fedabec2c376dc933629b0deae5aa` (`2026-10-03`, `Restructure into five domains: symbiont, environment, modality, embodiment, lab`)
- SHA-256 of full source files at extraction:
  - `contracts.py`: `ee760b80b536c0de44bd24045da2eb628cf040042a0cde872758e27da1570b7d`
  - `projection.py`: `1c3ed2c17e9b7fe94c3045c208dc1385faa41a1d1fa1364833ba7e339fea926f`

## Disposition

| Source piece | Disposition | Extracted scope |
| --- | --- | --- |
| `contracts.py` | `MOVE` (copy-first; source retained) | `ObservedFrame` and projection provenance constants, unchanged |
| `projection.py` | `SPLIT` (copy-first; source retained) | `runtime_tick_events` and its private mapping helpers only |
| `mind_snapshot_from_rich_state` | `DEFER` | Excluded because it imports Lab's Atlas implementation and carries a larger cognition-specific view contract |
| Observation bus, delta/wire protocols, World scene, bridge/readers | `DEFER` | Require separate transport, World, or domain-contract review |
| Observatory, provenance journal, studies, UI, controls | `DEFER` / excluded from scope | Scientific evidence custody, application, or intervention responsibilities |

The source repository was not modified. No source history was copied or synthesized; this new repository is a provenance-linked extraction, not a history-preserving path rewrite.

## State and authority boundaries

The migrated functions only map caller-provided telemetry into projection objects/events. They do not write to a runtime, own any source state, resolve transitions, or transport events. `ObservedFrame.provenance.feeds_back` is explicitly false.

This extraction does not assign semantic ownership of every projected field. The mapping may include body, cognition and vital data; the authority that produces each value remains the relevant source-domain owner. Any dynamic state in the upstream system remains owned by its originating authority, not by this projection package. No mutable persistent state is introduced here.

## Known rewrites and limits

- The runtime event projection is copied from the source file; the unrelated `mind_snapshot_from_rich_state` portion is deliberately omitted.
- Imports are local to this package and Python standard library only.
- The package name and public import path are `observation`; the distribution name is `observation`.
- The current payload keys are preserved as compatibility with the selected source slice. They are not ratified as final Biopeia API/schema.
- No operator control, UI, evidence archive/custody, or live transport implementation is included.

## Semantic Observation Plane extraction (2026-10-09)

### Provenance

- Source repository: `symbiont-lab`
- Pinned source repository SHA: `80d372a186513035f85a769db886e505cabba52d`
- Original paths:
  - `lab/src/lab/observation/semantic.py` (source commit `ee91ffc9bc158c115bab9773b955ea01dbda2611`)
  - `lab/src/lab/observation/plane.py` (source commit `9a59346cf66fb9a291ce01c44dbdd133face8436`)
- Target paths: `src/observation/semantic.py`, `src/observation/plane.py`
- Disposition: `MOVE` (copy-first; source retained); the plane import was rewritten from `lab.observation.semantic` to the target-local `.semantic` module. Plane documentation was updated to exclude Lab transport.
- Source SHA-256: semantic `dce7cc317bcf19e8d33cadd6c7c81bc7a7685672799ee70ff0f4f7595b879a56`; plane `166a76630989082fb665658e2d64eaf5a1c30e28c6b06db3918fc43a7103cf93`.

### Bounded scope and limits

The source `semantic.py` is the transport-independent claim/identity/lineage model, not a semantic authority. The source `plane.py` is bounded in-memory current materialization, live subscriber fan-out, replay, and explicit rebase signaling. The plane does not own the meaning or canonical state of claim values. Delivery sequence is local plane metadata, not domain time. This slice does not include `wire.py`, `bus.py`, World-scene materialization, delta encoding, Lab run lifecycle, HTTP/SSE, UI, or scientific evidence custody. No causal runtime API is imported or written. Source semantic tests were copied with import-path updates; plane behavior is tested with neutral semantic fixtures rather than Lab/Embodiment adapters.

Validation: target package suite and wheel/sdist build are recorded with the migration PR. The bounded extraction is integrated in PR #3 (merge commit `64c3226ab3701f748e276c92a852ca4facd74091`); integration does not ratify every copied behavior.

### Review adjustments for the approved conceptual model (2026-10-09)

- Authority vocabulary now names `ORGANISM`, `EMBODIMENT`, `ENVIRONMENT`, and
  `WORLD`; `LAB` is available for Lab-derived claims only. `MODALITY` is not a
  primary authority.
- Current materialization identity includes semantic contract ID and revision,
  epistemic kind, and each subject identity's issuer, scope, and lifetime, so
  distinct semantic, epistemic, contract, or identity contexts cannot replace
  each other's current value.
- `open_stream()` declares global publish-order sequencing, family-filtered
  sequence gaps, and explicit rebase signals for replay/live/bootstrap overflow;
  current-state bootstrap is never silently truncated. The source-era
  `subscribe()` API was a lossy latest-value projection without gap signaling.
  It is historical and superseded by removal in [PR #6](https://github.com/biopeia/observation/pull/6);
  no compatibility API is supported.
- `SubjectScope.key` is only a local scope descriptor, not a stable identity by
  itself; semantic-family contracts define required typed identity linkage.
- In-memory delivery contract: `open_stream()` sequences globally within one
  plane instance; family filters preserve global sequence values. A healthy
  subscription delivers each sequence once, but recovery re-fetch can overlap,
  so consumers deduplicate by sequence. Completeness is bounded to retained
  replay and normal live delivery until overflow; there is no durability or
  cross-restart resume. `subscribe()` is at-most-once/latest-value/lossy, with
  no replay or gap signal.
- `current()` / `current_messages()` expose only the bounded retained latest
  subset. Capacity evicts oldest subjects; absence from this projection is not
  evidence that source state is absent, unavailable, or nonexistent.
- These clarifications do not select a wire format, API, transport, or storage
  mechanism. Stream ordering and bounded loss are in-process plane behavior.

## Pinned-source inventory (2026-10-09)

This is a source-disposition inventory, not approval to import the historical
implementation. It covers every tracked module under
`lab/src/lab/observation/` at source commit
`80d372a186513035f85a769db886e505cabba52d`, plus the direct Observation test
suite and related integration checks listed below. The source repository is
read-only. All dispositions in this inventory are **candidates** unless an
already extracted target file is explicitly identified; this table does not
ratify a wire/API/storage contract. “Blob” is `git rev-parse <pin>:<path>`;
“path commit” is the last commit touching that path at the pin. This provides
stable source provenance without copying source history.

### Source modules

| Source path; path commit / blob | Top-level symbols at pin | Candidate disposition and target/owner; observed consumers/tests and limits |
| --- | --- | --- |
| `lab/src/lab/observation/__init__.py`; `13720935595fedabec2c376dc933629b0deae5aa` / `7c68362376e3d177daf15d86eeed0e916d45702b` | *(empty)* | `DROP` candidate: no behavior or public exports to preserve. Package initialization belongs to Biopeia package layout, not this file. |
| `.../atlas.py`; `13720935595fedabec2c376dc933629b0deae5aa` / `c75dfca22bfb153f759c04bb8fdfd730fc5f67b9` | `ATLAS_SCHEMA_VERSION`, `AtlasNode`, `AtlasEdge`, `CognitiveAtlasSnapshot`, `_topology_nodes`, `_topology_edges`, `_bindings_by_competence`, `_competence_state`, `_motor_competence_nodes`, `_effect_nodes`, `_action_dimension_nodes`, `_intervention_signature_nodes`, `_causal_estimate_edges`, `_action_intent_nodes_and_edges`, `_affordance_overlay_edges`, `_agency_metrics`, `_embodiment_binding_nodes_and_edges`, `_competence_effect_edges`, `_controller_nodes_and_edges`, `_body_schema_nodes_and_edges`, `_motor_capability_metrics`, `_prediction_metrics`, `_knowledge_coverage_metrics`, `build_cognitive_atlas`, `CognitiveAtlasDiff`, `_ratio`, `_edge_strength`, `cognitive_atlas_payload`, `diff_cognitive_atlas` | `SPLIT` candidate to Lab analysis/presentation. Reads Organism/Embodiment structures and derives a cognitive atlas; it is not passive observation or a primary semantic authority. Consumer: Lab Observatory/workbench; `test_atlas.py`. Do not transfer algorithm or external labels into Organism. |
| `.../body_physiology.py`; `bfcef4d7378e8f91b3ca2368f81ea5d08215482e` / `a2f3bc375850779d9d07bfe768c056f106d3ec83` | `LIVING_BODY_SOURCE`, `body_physiology_observation` | `REWRITE` candidate after Embodiment family contract: current adapter turns body readings into claims and labels authority/measurement source. Embodiment must define meaning and back state; Observation must not create authority. Consumer/test: `test_remaining_semantic_families.py`. |
| `.../body_pose.py`; `01fcb1a8c1a2442f3d8f0d47f1ea33a5a1e7a5c1` / `9eda624b2fcbcebaf5759faa9c4ec1b8e2f7cdcc` | `EMBODIMENT_AUTHORITY`, `PHYSICS3D_SOURCE`, `PHYSICS3D_RUNTIME`, `LAB_PRODUCER`, `LAB_RUN_ISSUER`, `body_pose_observation` | `SPLIT` candidate: keep body-pose semantics/authority with Embodiment; any neutral family contract/projection in Observation only after approved family design; Lab runtime/run linkage stays Lab. Consumer/tests: `test_semantic_body_pose_vertical.py`, `test_semantic_delivery.py`, semantic server smoke tests. Its current Physics3D/Lab attribution is not a canonical semantic contract. |
| `.../bus.py`; `2981f219c6af3fc6b5db2b23d4974bdf1c51a2ae` / `f270ded3e9963456eea3d18c94ba0b1d2bfb3e81` | `ObservationMessage`, `_with_rebase_notice`, `ObservationBus` | `DROP` candidate for the old Lab bus API, not preserve compatibility. Lab app may independently need orchestration/delivery. Consumers: Lab server/SSE/session; `test_live_delta.py`, run lifecycle/reconnect tests and server smoke tests. Transport and delivery semantics are not authorized by the extracted semantic model alone. |
| `.../cadence.py`; `13720935595fedabec2c376dc933629b0deae5aa` / `d1b3d23389c659142570b1360b89301be61786a0` | `ExecutionRates` | `DROP` candidate from Observation: schedules host execution/render/observation cadence rather than defining a claim. Any runtime scheduling belongs to the applicable host/runtime owner. Consumers: Lab physics3d run/engine; `test_cadence.py`. Do not treat wall-clock cadence as causal time. |
| `.../contracts.py`; `e6a704b84349b64bbb2ccd721ac4d429104416d5` / `14dd5186a187820d679d88b542c639cf84b57adc` | `PRESENTATION_PROJECTION`, `COMPLETED_FRAME_CONTRACT`, `OBSERVATION_IDENTITY_CONTRACT`, `ObservedFrame` | Existing extraction: `ObservedFrame` plus constants were copied (PR #1 merged). For TARGET, `REWRITE` candidate: the Lab-composed frame is a delivery/composition artifact, not a single semantic claim; no final envelope/API is selected. Consumers: bridge/server/viewer; `test_observability_integrity.py`, runtime stream and browser tests. Keep source provenance; no backward-compatible frame contract is implied. |
| `.../delta.py`; `5028c402738352f33150ddb7f760d77982eabfd6` / `b4573fd49979fd8eee088f3dfa98fe5b0f147c44` | `DELTA_CONTRACT`, `DEFAULT_ANCHOR_INTERVAL`, `COMPRESSIBLE_TYPES`, `_canonical_bytes`, `state_hash`, `_join`, `_equal`, `_diff`, `ObservationDeltaEncoder`, `_split`, `_apply`, `ObservationDeltaDecoder` | `DROP` candidate for Lab's JSON delta/wire mechanism. If later transport requires deltas, design independently under an authorized delivery contract. Consumers: Lab bus/SSE/browser; `test_live_delta.py`, run lifecycle tests. Not a semantic model. |
| `.../development_history.py`; `e474f95d46c79d95e083e2eb56d34ca684813016` / `36e96d6d772b16faf1224efea6994018f7f83e1a` | `_read_json`, `_telemetry_manifest_candidates`, `_number`, `_nodes`, `_edges`, `_body_schema_counts`, `_point`, `_history_snapshot`, `_snapshot_fingerprint`, `_managed_runs`, `build_development_history` | `SPLIT` candidate: run-file discovery and development history/read model belong to Lab apparatus/analysis, while any source claim remains owner-produced. Consumer: Lab server/workbench; `test_development_history.py`, related history UI tests. Do not turn Lab’s historical reconstruction into source truth. |
| `.../environment_resource.py`; `041e3cb30c060c9f7ddebff609fcb4cfec19fc65` / `c849ed5be32744799949d0529a65e37965ace9e2` | `ENVIRONMENT_AUTHORITY`, `WORLD_STATE_ISSUER`, `WORLD_ENVIRONMENT_SOURCE`, `WORLD_RUNTIME_PRODUCER`, `resource_state_observation` | `REWRITE` candidate: Environment owns resource state/meaning; World coordinates causal cut; Lab source adapter must not assert owner semantics. Candidate future Environment family contract/producer; consumer/tests: Lab world runtime, `test_remaining_semantic_families.py`, `test_world_environments.py`. |
| `.../joint_kinematics.py`; `f9f641b9d26cb0b6db885a541141f029930c1ec2` / `6f69da7ae98e638455e85b2833a0ff50071a14b2` | `joint_kinematics_observation` | `REWRITE` candidate after Embodiment part/morphology contract. Stable part identity and morphology revision are required; no list position as persistent identity. Consumer/tests: semantic-family tests, `test_semantic_body_pose_vertical.py`. |
| `.../observatory.py`; `13720935595fedabec2c376dc933629b0deae5aa` / `47c42c8ffa09828989342f7b7f95d6382aefe66c` | `observatory_package_root`, `valid_instance_id`, `_read_json_object`, `_registry_api`, `parse_journal_line`, `read_journal`, `ObservatorySource` | `SPLIT` candidate to Lab apparatus/read-model and evidence tooling. It discovers Lab artifacts and run registries; Observation does not own evidence custody. Consumers: Lab Observatory/server; `test_observatory_source_adapter.py`, `test_provenance_queries.py`. |
| `.../physics3d.py`; `966c32db115227af24caeb2ad39b6e4059ee4282` / `116d19599724ddfb785e7e8ea4eaacfeb0c27a4a` | `_body_descriptor_for_state`, `_optional_text`, `_topology_revision`, `EventSink`, `Physics3DObservationBridge` | `SPLIT` candidate: numerical solver is not authority; body/environment meaning and adoption stay with Embodiment/Environment, World coordinates causal cuts, and Lab hosts any applicable integration. Consumers: Physics3D session/runtime and server; observation integrity/semantic vertical tests and runtime-stream smoke test. Do not migrate the bridge as a generic Observation API. |
| `.../plane.py`; `9a59346cf66fb9a291ce01c44dbdd133face8436` / `a971a49857a562021da909a00a4efd53a0f7e637` | `ObservationKey`, `PlaneMessage`, `PlaneRebaseRequired`, `PlaneStreamSubscription`, `observation_key`, `ObservationPlane` | Existing extraction: bounded in-memory semantic plane copied (PR #3 merged). Candidate `DEFER` review before expanding: current sequence/replay/rebase/loss behavior is in-process, not durable and not a transport/API choice. Consumers: Lab server/SSE and world runtime; target tests `test_plane.py`, source `test_semantic_delivery.py`, semantic server smoke. Keep source-absence distinct from projection eviction or delivery gaps. |
| `.../projection.py`; `13720935595fedabec2c376dc933629b0deae5aa` / `9ee6e8ccd2ebdcd1896ebe17d035f42a0da48655` | `_identity`, `_copy_number`, `_copy_bool`, `runtime_tick_events`, `_prediction_class`, `mind_snapshot_from_rich_state` | Existing extraction: `runtime_tick_events` and local mapping helpers copied (PR #1). TARGET `SPLIT` candidate: raw legacy telemetry mapping is not yet a family contract; `mind_snapshot_from_rich_state` combines cognition with Lab Atlas interpretation and stays out. Consumers: Physics3D bridge/Lab UI; source `test_runtime_stream_adapter.py`; target `test_projection.py`. Payload keys are historical evidence only, not a compatibility promise. |
| `.../provenance_journal.py`; `13720935595fedabec2c376dc933629b0deae5aa` / `e4eb2840dc63c52b95cbfce812dda4e9828b7c3f` | `ProvenanceJournal`, `ProvenanceIndex`, `render_tree` | `SPLIT` candidate to Lab evidence/provenance tooling after defining its custody and scientific admissibility; this journal is not automatically the scientific evidence authority. Consumer: Lab CLI, runtime and server; `test_causal_provenance.py`, `test_provenance_queries.py`. Preserve evidence and history; do not copy artifacts into Observation. |
| `.../semantic.py`; `ee91ffc9bc158c115bab9773b955ea01dbda2611` / `125c906cd4a2d52d797f577172a33133534ef230` | `T`, `_token`, `_text`, `AuthorityDomain`, `IdentityLinkState`, `ConditionDimension`, `ConditionOrigin`, `ActorRef`, `SemanticContractRef`, `SemanticFamily`, `IdentityRef`, `IdentityAssertion`, `IdentityLink`, `SubjectScope`, `DomainTimeRef`, `AcquisitionBasis`, `TransformationRef`, `LineageSourceRef`, `Lineage`, `ObservationCondition`, `OrchestrationContext`, `SemanticClaim`, `SemanticObservation` | Existing extraction: transport-independent model copied (PR #3). Candidate `MOVE` only as capability primitives if package tests continue to conform to approved Semantic Model v1; it grants no authority to Observation and is not a selected record/wire schema. Consumers: plane and Lab adapters; source `test_semantic_model.py`, delivery/semantic family tests; target `test_semantic_model.py`. |
| `.../subsystem_status.py`; `13720935595fedabec2c376dc933629b0deae5aa` / `c20ec51d7c3cd37eb498f1b43d773ed2f30c61f8` | `ABSENT`, `DISABLED`, `NOT_READY`, `IDLE`, `ACTIVE`, `LIFECYCLES`, `generative_status` | `DROP` candidate from Observation: operational readiness/status projection of Lab/runtime internals, not a semantic family. Consumer: Lab API/UI; likely covered by server/workbench status checks rather than Observation-specific tests. Do not infer source-state availability from host subsystem readiness. |
| `.../symbiont_affordance.py`; `0ab93a681181540f4da51e581a5b4793abb36103` / `5e37fbd287cb4c72199d00bf2541d5e0b6580025` | `SYMBIONT_RUNTIME`, `ACTION_DOMAIN_SOURCE`, `_lineage`, `affordance_observation` | `SPLIT` candidate to Organism-owned action semantics and a separately attributed Lab-derived claim if scientifically needed. The adapter reads a runtime view; it does not establish that the organism internally represents developer “affordance” semantics. Consumer/tests: Lab action/Observatory views; `test_remaining_semantic_families.py`, `test_atlas.py`. |
| `.../wire.py`; `69bb7bb8e01241bdcb774a3992456c28eeb7af8f` / `160df024ef608db2ee97603e8d4a326c53718fae` | `SEMANTIC_WIRE_CONTRACT`, `_json_value`, `_actor`, `_identity`, `semantic_observation_payload`, `plane_message_payload` | `DROP` candidate for historical JSON wire payload. Future record/envelope and transport choices remain open; this table does not authorize a replacement. Consumers: Lab SSE/API; `test_semantic_delivery.py`, `test_sse_transport.py`, server smoke tests. |
| `.../world_scene.py`; `13720935595fedabec2c376dc933629b0deae5aa` / `fdf54be9b1dce8c0347c0ea4c40abf2cb6299699` | `SCENE_CONTRACT`, `project_world_scene`, `WorldScenePublisher`, `apply_world_event` | `SPLIT` candidate: environmental truth/projection to Environment, body projection to Embodiment, causal coordination/cuts to World; Lab visualization/composition remains Lab. Consumer: Lab world runtime/Physics3D viewer; `test_world_scene.py`, `test_physics_world_observer.py`, world-environment tests. Its “scene” is not Environment/World authority. |

### Direct source tests and cross-boundary checks

The following files exist at the same pinned repository commit. Their blob is
resolved exactly as `git rev-parse 80d372a...:<path>` and their path commit is
`git log -1 --format=%H 80d372a... -- <path>`; test files are evidence of the
legacy behavior under their exercised conditions, not instructions to preserve
that behavior. **No test implementation is copied by this inventory.**

| Source test path | What it exercises / relevant consumers | Candidate test disposition |
| --- | --- | --- |
| `lab/tests/unit/lab/observation/test_atlas.py` | atlas nodes, edges, cognitive/agency projections | `SPLIT`: Lab tests remain Lab; retain assertions only if still useful to Lab |
| `lab/tests/unit/lab/observation/test_cadence.py` | `ExecutionRates` | `DROP` with historical cadence module |
| `lab/tests/unit/lab/observation/test_development_history.py` | run-artifact history projection | `SPLIT` to Lab tests |
| `lab/tests/unit/lab/observation/test_live_delta.py` | bus/delta serialization, replay | `DROP` for old transport contract; new delivery tests require explicit contract |
| `lab/tests/unit/lab/observation/test_observability_integrity.py` | `ObservedFrame`, bridge, world-scene and non-feedback properties | `SPLIT`: preserve negative boundary assertions in owner-specific target tests, not old frame shape |
| `lab/tests/unit/lab/observation/test_physics_world_observer.py` | Lab `PhysicsWorldObserver` | `SPLIT` to Lab/solver integration; not an Observation target test |
| `lab/tests/unit/lab/observation/test_remaining_semantic_families.py` | physiology, environment resource, kinematics, affordance adapters | `SPLIT` to owning authorities/family contracts; do not port assertions that ratify unapproved semantics |
| `lab/tests/unit/lab/observation/test_run_lifecycle.py` | Lab run lifecycle, bus/delta/history | `SPLIT` to Lab; old payload/replay expectations not preserved |
| `lab/tests/unit/lab/observation/test_run_lifecycle_reconnect.py` | SSE reconnect and replay | `DROP` from Observation package; future transport-specific tests belong with transport owner |
| `lab/tests/unit/lab/observation/test_semantic_body_pose_vertical.py` | body pose adapter -> plane path | `DEFER` test decomposition until family contract and authority boundaries are implemented |
| `lab/tests/unit/lab/observation/test_semantic_delivery.py` | plane, body pose and JSON wire delivery | `SPLIT`: retain semantics-neutral model/plane assertions as applicable; wire assertions are not target contract |
| `lab/tests/unit/lab/observation/test_semantic_model.py` | value/identity/lineage model | `MOVE` candidate only with approved model conformance; target equivalent exists as `tests/test_semantic_model.py` |
| `lab/tests/unit/lab/observation/test_world_environments.py` | World/Environment observation composition | `SPLIT` to World/Environment owners and integration tests |
| `lab/tests/unit/lab/observation/test_world_scene.py` | `WorldScenePublisher`, `apply_world_event` | `SPLIT` to Lab view and World/Environment/Embodiment boundaries |
| `lab/tests/smoke/test_observation_integrity_server.py` | server-level no-feedback/observer integrity | `SPLIT` to Lab and workspace integration; not a package unit test |
| `lab/tests/smoke/test_observatory_source_adapter.py` | Observatory reading source/run artifacts | `MOVE` candidate to Lab tests, not Observation |
| `lab/tests/smoke/test_runtime_stream_adapter.py` | projection, bridge, bus, runtime stream and old payloads | `SPLIT` to Lab adapter/integration tests; do not carry payload as API commitment |
| `lab/tests/smoke/test_semantic_observation_server.py` | semantic plane through Lab HTTP/SSE server | `SPLIT` across package and Lab integration; HTTP/SSE remains undecided here |
| `lab/tests/smoke/test_unified_server.py` | unified Lab server and Observation bus | `MOVE` candidate to Lab tests |
| `lab/tests/experimental_integrity/test_physics3d_observation_independence.py` | confirms observation independence from physical progression under fixture | `DEFER` as a valuable negative invariant; relocate/re-author in workspace/physical integration tests only with equivalent fixture and scope |
| `lab/tests/unit/lab/physics3d/test_observer_semantics.py` | physics observer semantics and ground-truth scene readings | `SPLIT` to Environment/Embodiment/Lab tests; observer ground truth is not Observation authority |
| `lab/tests/unit/lab/physics3d/test_session_observation_identity.py` | bridge/session identity linkage | `SPLIT` to Embodiment/World/Lab integration tests; exact target identity contract must govern |
| `lab/tests/unit/lab/physics3d/test_session.py` | session composition includes observation plane | `SPLIT` to Lab/runtime integration; not Observation package behavior |
| `lab/tests/unit/lab/server/test_api.py` | Lab API materialization from Observation | `MOVE` candidate to Lab tests; endpoint contract not authorized by this inventory |
| `lab/tests/unit/lab/server/test_sse_transport.py` | SSE delivery, replay, gap/rebase transport | `MOVE` candidate to eventual transport owner tests, but `DEFER` until transport contract is authorized |
| `lab/tests/unit/lab/test_provenance_queries.py` | queries of Lab provenance journal | `MOVE` candidate to Lab tests; no evidence-custody semantics inferred |
| `lab/tests/unit/workbench/test_body_observation_boundary.py` | frontend boundary handling for body-observation state | `MOVE` candidate to Lab/workbench tests; presentation assertion only, not Observation package behavior |
| `lab/tests/unit/workbench/test_observability_state.py` | Workbench observation-state presentation | `MOVE` candidate to Lab/workbench tests; no source-state semantics inferred from UI |
| `lab/tests/unit/test_causal_provenance.py` | provenance API / causal evidence integration | `SPLIT` to Lab and causal owners; assertions require review against current World commit contract |

Other Workbench browser/viewer rendering checks are downstream consumers, not direct
Observation tests. They remain Lab-owned and are not candidates to move to this
package. Environment's own `environment.observation` contracts are likewise a
separate owner boundary; this inventory does not absorb them.

### Inventory caveats and closure triggers

- The source pin is a provenance baseline, not a statement that it is the
  latest source or that all files under Lab are Observation-owned. No claim is
  made about untracked/generated files, runtime observations, or historical
  scientific results.
- `MOVE`, `SPLIT`, `REWRITE`, `DROP`, and `DEFER` in the tables are provisional
  candidates except for the bounded copy-first slices explicitly recorded
  above. `DEFER` is not final disposition. Before migration completion, close
  each deferred row with a reviewed disposition and a Biopeia target owner/path.
- Candidate `DROP` means “do not migrate this legacy implementation/API”; it
  does not prohibit designing a distinct capability later where independently
  justified. Candidate `SPLIT`/`REWRITE` means preserve justified meaning only,
  never compatibility shims or copied legacy behavior.
- The next safe Observation slice is contract-only review of the extracted
  `semantic.py`/`plane.py` against approved Semantic Model v1, followed by
  identifying one semantic family with its authority owner. Do not add schema,
  envelope, API, storage, transport, or source-domain adapters until their
  respective design gates are approved. Legacy wire/bus, Lab scene, evidence,
  and cognitive-analysis paths should be dispositioned with their owners rather
  than migrated as bulk code.

### Extracted-slice integration state

The existing copy-first slices are integrated: Observation PR #1 merged as
`8261dda79551a4ad13bf2b91692098f7509c2c9b` (2026-10-09), and PR #3 merged as
`64c3226ab3701f748e276c92a852ca4facd74091` (2026-10-09). Merge records show
integration only; they do not constitute semantic, scientific, transport or
constitutional approval of every copied symbol or legacy behavior. The target
package and tests remain bounded to the copied projections and semantic-plane
slice described above.

#### Direct test provenance (path commit / blob)

The tests above are pinned to the same repository commit; exact path-level provenance follows.

| Test path | Path commit | Blob at pin |
| --- | --- | --- |
| `lab/tests/unit/lab/observation/test_atlas.py` | `282c44eea894faedb57763c3545a1401cf032a86` | `0fa5f707fe46f78d3dda50c652856e72b3eb9198` |
| `lab/tests/unit/lab/observation/test_cadence.py` | `282c44eea894faedb57763c3545a1401cf032a86` | `650fb7b1708067f63351d3ae35cdf916fd461be0` |
| `lab/tests/unit/lab/observation/test_development_history.py` | `c34824713034540f73f1ca3f365ba6e173c7b17a` | `135aa96560e5551990cd98f2c779953e2988d771` |
| `lab/tests/unit/lab/observation/test_live_delta.py` | `a8ab9327608321ddb18ab19c90174e7199d20c3d` | `b356437f98859b69f36025a36d3a443555a4bd42` |
| `lab/tests/unit/lab/observation/test_observability_integrity.py` | `4648916b2b0ac13f2d77358f72294c150dcf969d` | `13245d94df94d4ed60a487632ecb28422d766f35` |
| `lab/tests/unit/lab/observation/test_physics_world_observer.py` | `40adf60c42322c06b225e9169dbb77b126c04257` | `a21b7fa92a71605731470671c8ba27e4db831aa1` |
| `lab/tests/unit/lab/observation/test_remaining_semantic_families.py` | `baca8d35eaff943643db82efb7209410778a4d3d` | `bf0cfc06fbbe01b85308bff344a95bf77523c4c3` |
| `lab/tests/unit/lab/observation/test_run_lifecycle.py` | `8a7479e35ce7fa1b97bed7966d51c7bfbf9c60b0` | `d6ac30c60af46bbad906e24d7fb507f7b2420978` |
| `lab/tests/unit/lab/observation/test_run_lifecycle_reconnect.py` | `ac4b2a17b41841776dc0d5e2f70373c2520cdb31` | `8bb49e2711340881507841caea28c8c56d461927` |
| `lab/tests/unit/lab/observation/test_semantic_body_pose_vertical.py` | `9896d4a7ff4c73742ca1a784de69bd63457f4f34` | `04b573eb01e40ccf5405bc06fe84d54e27a321ac` |
| `lab/tests/unit/lab/observation/test_semantic_delivery.py` | `f83895ddbd10aec56284b076eff5716be0bef7f6` | `033b33588512fa26e1ba3e4ef033f232398b11d1` |
| `lab/tests/unit/lab/observation/test_semantic_model.py` | `d3b21610df2a087348cc236e35570bcd79453b78` | `332580349d8fd41693b1830e2cbd5893c6879c4f` |
| `lab/tests/unit/lab/observation/test_world_environments.py` | `54acefa003f41a324cc285691c62547dc39c4e96` | `bc68c49fd1547dc78521a5fb6cd8d6b6ec1b2c40` |
| `lab/tests/unit/lab/observation/test_world_scene.py` | `282c44eea894faedb57763c3545a1401cf032a86` | `198859f9fcfc1af6547d7657dbb42680fc5d9636` |
| `lab/tests/smoke/test_observation_integrity_server.py` | `f63726f4673b225000559a24d9405a801160dc80` | `b5a92fd6ddc584e06ece77cd4eb30e48e628459c` |
| `lab/tests/smoke/test_observatory_source_adapter.py` | `282c44eea894faedb57763c3545a1401cf032a86` | `7f98846cd80daaca0bf922164b2d7e46e391f730` |
| `lab/tests/smoke/test_runtime_stream_adapter.py` | `55fafbb1488e64bd96d4f886078ea76743cf88db` | `e91bd77e18fab1a6f445657095481111b662e229` |
| `lab/tests/smoke/test_semantic_observation_server.py` | `ee1e68efc339433fe06455f891b672ebfc99bbf1` | `23b4c8b2eeee4cbe8881a3b11d4e7626f04a4f3f` |
| `lab/tests/smoke/test_unified_server.py` | `80e6435c92c1d61f14ad25f87fefaec210b4db15` | `2398ecb52def71693a4b956fbff81d25659c9358` |
| `lab/tests/experimental_integrity/test_physics3d_observation_independence.py` | `792d2dbd3e507d1d41300456cf826d8efe19fddb` | `7e3973f0084f3130a56774d58fbf243cd890d166` |
| `lab/tests/unit/lab/physics3d/test_observer_semantics.py` | `282c44eea894faedb57763c3545a1401cf032a86` | `7367a9f606780e0c33f4201ec1da3c8e5e3402d7` |
| `lab/tests/unit/lab/physics3d/test_session_observation_identity.py` | `053f6176b271a6b21c27f9c9d79b213217784003` | `fe723446e661491be28786cba6342c9173428026` |
| `lab/tests/unit/lab/physics3d/test_session.py` | `792d2dbd3e507d1d41300456cf826d8efe19fddb` | `2cc4a90bacd78122b6e7785eee17cd76fddb02f9` |
| `lab/tests/unit/lab/server/test_api.py` | `7f156e73f1824a908e46a0a7534221c38b09c6d7` | `a14bc0381d866ed2a2a72a6a3eff2bddef59b294` |
| `lab/tests/unit/lab/server/test_sse_transport.py` | `adee598bfa46b11c5734a2d0c84b9d6e97563544` | `cffec88663823bb24f97361f9b8ffcc20a1db04d` |
| `lab/tests/unit/lab/test_provenance_queries.py` | `282c44eea894faedb57763c3545a1401cf032a86` | `855c8277047a7f7e5d122e8b73b2a53e7ed2d121` |
| `lab/tests/unit/test_causal_provenance.py` | `282c44eea894faedb57763c3545a1401cf032a86` | `5fd2eb435848c589b0818f8a4603837f81890f35` |
| `lab/tests/unit/workbench/test_body_observation_boundary.py` | `c208afafc96114324a0f62589a860e825970ef08` | `650460fb3ea13d27ec5f62a5d4f05b17d1094d36` |
| `lab/tests/unit/workbench/test_observability_state.py` | `53c25147f85d8058311b53f91e62df87e06d6302` | `d37ea89da1c475dc18898e57af22e476388a72d0` |

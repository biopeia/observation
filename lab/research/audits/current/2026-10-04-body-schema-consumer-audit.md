# BodySchema consumer audit

**Scope:** SYM-04 consumer semantics on the current checkout, with emphasis on
whether a prior Body's BodySchema can be read as current-Body authority after
canonical re-embodiment. This is a source-and-test audit, not evidence that
BodySchema improves adaptation or transfers usefully between Bodies.

## Findings

`OrganismRuntime._body_schema` owns the active `BodySchemaEngine` and the
`body_schema` checkpoint field. `prepare_fresh_embodiment_checkpoint()` first
archives the closed episode with its full BodySchema, then calls
`reset_for_new_embodiment()` on the active engine before writing the new
checkpoint. The reset clears learned parts, regions, dependencies, derived
sensorimotor views, and agency-boundary evidence while retaining the opaque
identity salt.

The reader/writer trace found these live consumers:

| Path | Use | Authority boundary |
| --- | --- | --- |
| `core/domains/embodiment.py` and `actuation/acquisition.py` | Add current sensory/self-model/cognitive and causal sensorimotor observations to the active engine; rebuild its derived sensorimotor view | Reads the current active engine only; no archive lookup |
| `core/orchestration/individual.py` and `core/embodiment/adaptation.py` | Feed current schema confidence and revision/disruption indicators into the current `EmbodimentEpisode` adaptation record | Episode is closed and archived on Body replacement; this path does not authorize actions |
| `core/embodiment/memory.py` | Derive descriptive final-state metrics while closing an episode | Consumes the closed episode's `body_schema_prior` to write a historical summary, not to initialize a new active engine |
| `lab/integration/physics3d/apparatus.py`, `lab/physics3d/runtime.py`, telemetry and Observatory projection | Produce bounded summaries or passive snapshots | Outward observation only; no feedback path into organism state was found |
| checkpoint and `EmbodimentArchive` serialization | Persist the active schema separately from archived episode/body priors | Restore constructs the active schema from `body_schema`; the traced current-body action restoration independently validates bindings against the current actuator surface |

No active consumer of archived `body_schema_prior` was found outside historical
episode/body-memory serialization and episode-summary construction. In
particular, contract-memory lookup may recover historical motor candidates and
candidate model IDs, but the prior BodySchema is not installed into the active
`BodySchemaEngine` or used to validate current execution bindings.

## Test evidence

- `lab/tests/integration/test_reembodiment_continuity.py::test_knowledge_survives_as_knowledge_without_authority`
  checks the active schema is empty after re-embodiment, the old schema remains
  in closed history, the restored action domain has no valid old binding, and
  knowledge in other domains remains separately available.
- `lab/tests/integration/test_reembodiment_continuity.py::test_the_whole_lifecycle_holds_per_register_entry`
  checks restore/save/re-embodiment/restore/save against the continuity
  register, including invalidated and replaced fields.
- `lab/tests/unit/lab/physics3d/test_reembodiment.py` checks prior-schema
  archival and active-schema reset for legacy-transform fixtures.
- The focused integration file passed **9 tests** on 2026-10-04; the focused
  Physics3D re-embodiment unit file passed **18 tests** on 2026-10-04.

## Resolution and limits

The specific authority-leak hypothesis is **not reproduced in the audited
canonical path**: old BodySchema content is archived and the active schema is
reset before the new Body runtime is restored. The earlier demand for per-item
provenance is not justified as a prerequisite for this current path, because
prior entries are not mixed into the active representation or read by current
consumers. A future feature that retrieves archived BodySchema priors into
active inference would require explicit prior-vs-fact semantics and new
consumer tests before implementation.

This does not establish transfer utility, causal benefit, or correctness of
every BodySchema inference. The conclusion is bounded to the inspected source
paths, current canonical re-embodiment implementation, and named tests; it is
not a general guarantee for arbitrary external consumers of exported
checkpoints or observer snapshots.

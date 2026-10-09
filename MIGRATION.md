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

Validation: target package suite and wheel/sdist build are recorded with the migration PR. The extraction has not yet been integrated or reviewed.

### Review adjustments for the approved conceptual model (2026-10-09)

- Authority vocabulary now names `ORGANISM`, `EMBODIMENT`, `ENVIRONMENT`, and
  `WORLD`; `LAB` is available for Lab-derived claims only. `MODALITY` is not a
  primary authority.
- Current materialization identity includes semantic contract revision, so an
  incompatible revision cannot replace the prior revision's current value.
- `open_stream()` declares global publish-order sequencing, family-filtered
  sequence gaps, and explicit rebase signals for replay/live/bootstrap overflow;
  current-state bootstrap is never silently truncated. The
  compatibility `subscribe()` API is explicitly a lossy latest-value
  projection without gap signaling.
- `SubjectScope.key` is only a local scope descriptor, not a stable identity by
  itself; semantic-family contracts define required typed identity linkage.
- These clarifications do not select a wire format, API, transport, or storage
  mechanism. Stream ordering and bounded loss are in-process plane behavior.

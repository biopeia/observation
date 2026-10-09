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

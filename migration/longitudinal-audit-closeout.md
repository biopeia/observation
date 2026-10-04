# Longitudinal Integrity Audit Closeout

Date: 2026-10-04  
Branch: `migration/five-domain-architecture`

This closeout records the implementation state for SYM-01 through SYM-18 and
the debt intentionally left open. It supersedes stale schema-version numbers
in earlier audit notes for the current checkpoint loader; it does not replace
historical evidence or authorize scientific experiments.

## Closed engineering findings

| Issue | Closeout state | Evidence and scope |
|---|---|---|
| SYM-01 | Implemented | The current checkpoint carries a distinct continuation-condition hash; missing or changed contemporary controls fail validation. The hash provides integrity, not authentication. |
| SYM-02 | Resolved in this repository | Required restore is distinct from explicit first-boot creation; a missing required checkpoint does not create a new organism. External deployments are outside the audited scope. |
| SYM-03 | Resolved for the runtime and canonical profile v1 | Process telemetry does not charge organism metabolism. The canonical-profile instrumentation-invariance regression is recorded in `migration/open-issues.md`; non-canonical historical trajectories were not re-audited. |
| SYM-04 | Resolved for canonical re-embodiment | Active `BodySchema` is reset and the closed body's schema remains archival. No transfer-utility claim follows. |
| SYM-05 | Implemented | `symbiont/src/symbiont/host/checkpoint.py` accepts only checkpoint schema **14**. Historical schemas are not live-restorable. |
| SYM-06 | Cognitive-bridge boundary closed; register-wide audit remains debt | Commit `7bd9a29d5` inventories nested cognitive-bridge state and adds a restore/tick regression: historical readouts survive as knowledge but cannot become executable without current-body bindings. `uv run pytest -q lab/tests/integration/test_reembodiment_continuity.py lab/tests/unit/host/test_continuity_register.py`: 39 passed. |
| SYM-09 | Contract clarified | Budding is clonal; it is not represented as recombination or Genome v2 reproduction. |
| SYM-14 | Intentional behavior documented | Restart guarantees semantic continuity, not exact future-trajectory equivalence. |
| SYM-15 | No current executable v4 compatibility path found | Production re-embodiment requires a current lifecycle and episode. Commits `9bf5c5378` and `b7201c68d` remove stale v4 fixtures and correct v2/v5 source descriptions. Focused tests passed; `rg anthropomorphic-v4 --glob '*.py'` returned no matches at closeout. |
| SYM-16 | Current loader policy is strict; documentation debt remains | Runtime loader accepts schema 14 only; no schema 1–13 migration is retained. Older migration material is historical, not a live restore path. |
| SYM-17 | Composite engineering coverage present | `lab/tests/integration/test_reembodiment_continuity.py` covers acquired longitudinal state across checkpoint, restore, re-embodiment, and subsequent ticks. Unsupported somatic epigenetic priors are outside that coverage. |

## Explicit remaining debt

| Issue | Debt / boundary |
|---|---|
| SYM-06 | The cognitive bridge case is covered, but no claim is made that every nested field in the whole Continuity Register has independently verified semantics and consumers. Continue field-by-field audit before declaring the full register semantically closed. |
| SYM-07 | Complete the owner-approved epistemic ownership record for each live candidate system: assertion semantics, evidence, revision/invalidation, persistence, consumer, authority, and falsifying evaluation. Do not merge systems merely because their representations look similar. The current design at `docs/design/core/epistemic-ownership-and-claim-levels-v1.md` remains proposed. |
| SYM-08 | `OrganismRuntime` remains a broad composition root/orchestrator. Defer extraction until stable ownership boundaries justify it; this is architectural debt, not a request for a cosmetic rewrite. |
| SYM-10 | Genome v2 has a tested mechanical capture → parent restore → resident budding → child-expression path. Somatic `EpigeneticPrior` is separate and unsupported. Adaptive benefit, phenotype utility, and causal transgenerational claims remain unproven; no experiment was run for this closeout. |
| SYM-11 | Social claims/evidence and cultural retention exist, but there is no canonical peer-claim → reconciliation → accepted-knowledge → organism-decision policy. Do not add a trust score without an approved contract. |
| SYM-12 | Ancestry mechanics/persistence do not show that ancestry improves learning or adaptation. Utility requires a separately approved controlled study; none was run. |
| SYM-13 | Generative mechanisms are present and selected consumption paths are tested. Decision benefit and causal contribution are not established; any study remains subject to the repository's scientific gates. |
| SYM-18 | Capability statements must remain at the demonstrated evidence level (present, durable, consumed, useful, causal). No E3/E4 benefit or causal claim is made by this closeout. |
| Schema documentation | Source of truth is `CHECKPOINT_SCHEMA_VERSION = 14` in `symbiont/src/symbiont/host/checkpoint.py`. `migration/open-issues.md` is already modified outside this closeout and still contains a schema-12 statement; it was deliberately left untouched. Reconcile that file with its owner before publication. |
| `experimental_clean` legacy mode | Removal was not completed: its tick/population paths are interleaved with runtime, transaction, persistence, viewer, and callers. The failed partial refactor was discarded. Plan a manual, tested clean-only refactor; do not claim this mode is removed. |

## Validation and change boundaries

- SYM-06 continuity suites: 39 passed.
- SYM-15 lifecycle fixture tests: each focused test passed; humanoid apparatus tests passed (6), and the Lab contract suite passed (59, run from `lab/`).
- No scientific evidence run was performed.
- Commits for this closeout work are `7bd9a29d5`, `9bf5c5378`, and `b7201c68d`.
- Existing unrelated worktree edits (`AGENTS.md`, `lab/experiments/world/genesis-v1/view_world.py`, and `migration/open-issues.md`) were not staged or changed by this closeout.

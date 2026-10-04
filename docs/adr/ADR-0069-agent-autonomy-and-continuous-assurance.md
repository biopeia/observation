# ADR-0069 — Agent autonomy, impact-routed CI and continuous assurance

- **Status:** Proposed
- **Date:** 2026-10-04
- **Decision owner:** project owner
- **Relates to:** ADR-0057, ADR-0058, `scripts/agentctl.py`, `scripts/governance/ci_plan.py`, `.github/workflows/ci.yml`
- **Scope:** engineering publication and validation routing only. It does not redefine scientific evidence, experiment authority, FROZEN immutability or constitutional ownership.

## Context

The repository already has a compact agent contract: one `agentctl context`, one
implementation pass, one `agentctl publish`, with GitHub Actions as the sole technical
publication gate. In practice the validation path accumulated three independent sources
of avoidable cost:

1. the same candidate SHA could run CI once on `push agentctl/**`, again when its PR was
   opened, and again after integration into `main`;
2. SCIENTIFIC and CONSTITUTIONAL classifications were also used as proxies for technical
   impact, automatically selecting unrelated compatibility, host and protocol lanes;
3. full-repository compatibility and portability checks ran on individual candidates
   even when their value is primarily detection of integration drift over time.

The result was safe but increasingly hostile to unattended evolution. The governance
class answers **who may authorize a change**; it is not, by itself, proof that every
technical surface is affected.

ADR-0058 already accepted impact-based test selection, fail-closed fallback and a
scheduled full-suite safety net. This ADR fixes the surrounding publication topology so
that ADR-0058 can operate without duplicate work.

## Decision

1. **Validate one candidate SHA once.** The primary CI runs on governed candidate
   branches. Opening the PR does not repeat the same CI, and moving an already validated
   SHA to `main` does not repeat it. A future merge queue uses `merge_group` to validate
   the composed integration tree, which is new evidence rather than duplicate evidence.

2. **Authority and impact are orthogonal.** `classify.py` continues to decide ORDINARY,
   SCIENTIFIC, CONSTITUTIONAL and FROZEN authority. `validation-matrix.toml` alone routes
   technical lanes. A SCIENTIFIC change therefore receives the lanes declared for its
   causal surface, not an automatic repository-wide matrix.

3. **The optimizer cannot narrow its own validation.** Changes to CI planning,
   governance execution, validation policy or workflows retain a broad explicit
   `ci_control` fallback including canonical, architecture, compatibility, host and
   protocol sentinels. Markdown-only governance changes remain documentation-only.

4. **Obsolete engineering CI is disposable.** A newer commit on the same engineering
   branch cancels older CI. Scientific executions remain separate and are never covered
   by this cancellation policy.

5. **Broad integration assurance moves out of presubmit.** `canonical-full`, Python-next,
   Windows/macOS, Alpine and performance run periodically from `main`. Failure creates or
   updates a repository issue. Candidate CI may still select these lanes explicitly when
   the changed surface itself affects the corresponding contract.

6. **ADR-0058 starts in observe-only mode.** The static impact planner records direct
   ownership, reverse-import impact, semantic guards and conservative fallback reasons.
   It does not yet skip tests. Targeted execution may be enabled only after observation
   demonstrates that hypothetical selection does not miss failures.

7. **Every CI plan receives a deterministic adversarial check.** An uncovered changed
   path, a non-document change with no behavioral lane, or a control-plane implementation
   change without its broad fallback fails planning. This is a challenge to the plan,
   not a duplicate test suite.

8. **Validation cost becomes visible.** Governance classes have engineering wall-time
   targets. A budget is a diagnostic target, never permission to omit required evidence.

## Consequences

- Ordinary agent work approaches the intended path: implement, publish once, wait for one
  affected CI, then promote automatically when allowed.
- Scientific and constitutional review boundaries remain unchanged; only unrelated
  technical validation is removed from their default path.
- The repository keeps a full-suite safety net, but pays for it once per assurance window
  instead of once per candidate.
- Failures found only by continuous assurance are evidence that the impact model is
  incomplete and require a new ownership/semantic-guard rule or a wider fallback.
- Merge queue activation remains a repository setting because it changes GitHub-side
  branch integration semantics. The workflow is made `merge_group`-ready before that
  setting is enabled.

## Alternatives considered

- **Keep every validation on every SCIENTIFIC change.** Rejected: governance authority is
  not a causal dependency graph and the cost scales poorly with autonomous agents.
- **Use an LLM to choose tests.** Rejected as the technical gate: selection must remain
  deterministic, versioned and reproducible. An LLM may review evidence but cannot be the
  sole permission boundary.
- **Delete broad compatibility suites.** Rejected: they remain valuable as continuous
  assurance and explicit fallback evidence.
- **Immediately enable targeted test skipping.** Rejected: ADR-0058 requires an
  observation phase before narrowing execution.

## Acceptance and rollout

This ADR is intentionally **Proposed** in the implementation branch. Merging the control
plane requires the project owner to review this decision and change its status to
`Accepted`. No code in this branch should infer acceptance merely from passing CI.

After acceptance, the recommended rollout is:

1. merge the code with impact planner still `observe-only`;
2. enable GitHub merge queue after the manual ruleset steps documented in the PR;
3. collect impact manifests and continuous-assurance results;
4. graduate only high-confidence ORDINARY surfaces to targeted execution in a separate,
   evidence-backed change.

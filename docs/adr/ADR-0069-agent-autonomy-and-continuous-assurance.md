# ADR-0069 — Agent autonomy, impact-routed CI and continuous assurance

- **Status:** Accepted
- **Date:** 2026-10-04
- **Decision owner:** project owner
- **Relates to:** ADR-0057, ADR-0058, `scripts/agentctl.py`, `scripts/governance/ci_plan.py`, `.github/workflows/ci.yml`, `.github/workflows/promote.yml`
- **Scope:** engineering publication and validation routing only. It does not redefine scientific evidence, experiment authority, FROZEN immutability or constitutional ownership.

## Context

The repository already has a compact agent contract: one `agentctl context`, one
implementation pass and one `agentctl publish`, with GitHub Actions as the sole technical
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

After the first implementation, repository configuration established an additional
constraint: this repository is owned by a personal GitHub account, where GitHub Merge
Queue is not available. The accepted autonomy objective therefore requires repository-
local serialization rather than a GitHub-hosted merge queue.

## Decision

1. **Validate one candidate SHA once.** The primary CI runs on governed candidate
   branches. Opening the PR does not repeat the same CI, and moving an already validated
   current SHA to `main` does not repeat it. If `main` advanced, the candidate is rebased;
   the rebased SHA is a new composition and must receive fresh CI before integration.

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

9. **ORDINARY promotion is serialized and self-healing.** All automatic promotion jobs
   share the `promote-main` concurrency group. If a candidate is no longer based directly
   on current `main`, the workflow rebases it onto `main` and pushes the replacement SHA
   with `force-with-lease`. That push obtains fresh candidate CI. Only a green candidate
   whose parent is current `main` may be merged, and it is merged through its PR rather
   than by bypassing branch protection.

10. **Repository rules are part of the race guard.** `main` must require a pull request,
    `governed-ci-gate`, and the branch to be up to date before merge. The workflow does
    not bypass those requirements. If `main` advances between the freshness check and the
    merge attempt, branch protection rejects the merge; the workflow rebases and lets the
    new SHA re-enter normal CI.

## Consequences

- Ordinary agent work approaches the intended path: implement, publish once, wait for
  affected CI, then promote automatically when allowed.
- Concurrent ORDINARY agents no longer require repeated manual republication merely
  because another ORDINARY candidate reached `main` first.
- A stale candidate pays only for the evidence that actually became stale: its rebased
  composition receives fresh governed CI.
- Scientific and constitutional review boundaries remain unchanged; only unrelated
  technical validation is removed from their default path.
- The repository keeps a full-suite safety net, but pays for it once per assurance window
  instead of once per candidate.
- Failures found only by continuous assurance are evidence that the impact model is
  incomplete and require a new ownership/semantic-guard rule or a wider fallback.

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
- **Depend on GitHub Merge Queue.** Rejected for the current repository because the
  feature is unavailable to this personal-account repository. A future move to an
  organization may revisit that option, but it is not part of the current control plane.
- **Permit stale green PRs to merge.** Rejected: a candidate validated against an older
  `main` does not prove the resulting composition. Rebase plus fresh CI is required.

## Acceptance and rollout

This ADR is **Accepted** by the project owner for the implementation described here.
Passing CI remains a separate technical condition and does not replace owner approval.

The rollout is:

1. keep ADR-0058 impact planning in `observe-only`;
2. use serialized ORDINARY promotion with automatic rebase/revalidation;
3. require PRs, `governed-ci-gate`, and up-to-date branches in the `main` ruleset;
4. collect impact manifests and continuous-assurance results;
5. graduate only high-confidence ORDINARY surfaces to targeted execution in a separate,
   evidence-backed change.

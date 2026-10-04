from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from governance import pr_summary


def test_render_explains_authority_and_impact(monkeypatch) -> None:
    monkeypatch.setattr(
        pr_summary,
        "build_plan",
        lambda _base, _head: SimpleNamespace(
            classification="SCIENTIFIC",
            selected_lanes=("architecture_integrity", "physics3d"),
            budget_seconds=240,
            reasons=("embodiment/src/embodiment/body.py: physics3d-causal-engine",),
            changed_paths=("embodiment/src/embodiment/body.py",),
        ),
    )

    rendered = pr_summary.render("base", "head")

    assert "**Authority class:** `SCIENTIFIC`" in rendered
    assert "External owner/scientific review required" in rendered
    assert "`architecture_integrity`, `physics3d`" in rendered
    assert "240s" in rendered
    assert "observe-only" in rendered


def test_merge_body_replaces_existing_summary_instead_of_appending() -> None:
    first = pr_summary.merge_body("Human context", "SUMMARY-ONE")
    marked = pr_summary.merge_body(
        "Human context\n\n" + pr_summary.BEGIN + "\nold\n" + pr_summary.END + "\n\nTail",
        pr_summary.BEGIN + "\nnew\n" + pr_summary.END,
    )

    assert first.endswith("SUMMARY-ONE\n")
    assert marked.count(pr_summary.BEGIN) == 1
    assert marked.count(pr_summary.END) == 1
    assert "old" not in marked
    assert "new" in marked
    assert "Human context" in marked
    assert "Tail" in marked


def test_pr_summary_workflow_uses_trusted_workflow_run_definition() -> None:
    workflow = (ROOT / ".github/workflows/pr-governance-summary.yml").read_text(encoding="utf-8")

    assert "workflow_run:" in workflow
    assert 'workflows: ["CI"]' in workflow
    assert "pull_request_target:" not in workflow
    assert "ref: main" in workflow
    assert "pull-requests: write" in workflow
    assert "github.event.workflow_run.head_repository.full_name == github.repository" in workflow
    assert "github.event.workflow_run.head_sha" in workflow
    assert "Candidate advanced" in workflow
    assert 'git fetch origin "$HEAD_SHA"' in workflow
    assert "python scripts/governance/pr_summary.py" in workflow


def test_candidate_ci_is_not_duplicated_by_pr_or_main_push() -> None:
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")

    assert "pull_request:" not in workflow
    assert "branches: [agentctl/**, governance/**, refactor/*]" in workflow
    assert "branches: [main" not in workflow
    assert "merge_group:" in workflow
    assert "cancel-in-progress: true" in workflow

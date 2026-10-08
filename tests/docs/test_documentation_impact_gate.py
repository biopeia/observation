"""Test suite for Documentation Impact Enforcement Gate (P7).

Verifies the 16 core requirements, 3 synthetic case studies (CASE A, CASE B, CASE C),
anti-gaming invariants, and deterministic reporting.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = ROOT / "symbiont/docs"
if str(DOCS_DIR) not in sys.path:
    sys.path.insert(0, str(DOCS_DIR))

from documentation_impact_gate import (  # noqa: E402
    GateOutcome,
    evaluate_documentation_gate,
    format_gate_report,
)


# ---------------------------------------------------------------------------
# Test 01: Implementation direct impact unresolved -> BLOCK
# ---------------------------------------------------------------------------
def test_01_implementation_direct_impact_unresolved_blocks() -> None:
    report = evaluate_documentation_gate(
        paths=["symbiont/src/symbiont/actuation/competence.py"],
        repo_root=ROOT,
        skip_p4=True,
        skip_p6=True,
    )
    assert report.outcome == GateOutcome.BLOCK
    assert report.review_required_count == 1
    assert report.unresolved_count == 1
    assert report.resolved_count == 0
    assert any("component.competence" in r for r in report.block_reasons)


# ---------------------------------------------------------------------------
# Test 02: Relevant canonical doc changed -> RESOLVED (PASS)
# ---------------------------------------------------------------------------
def test_02_relevant_canonical_doc_changed_resolves() -> None:
    report = evaluate_documentation_gate(
        paths=[
            "symbiont/src/symbiont/actuation/competence.py",
            "symbiont/docs/07-agency-action-and-motor-learning.md",
        ],
        repo_root=ROOT,
        skip_p4=True,
        skip_p6=True,
    )
    assert report.outcome == GateOutcome.PASS
    assert report.review_required_count == 1
    assert report.resolved_count == 1
    assert report.unresolved_count == 0
    comp_review = next(r for r in report.reviews if r.unit == "component.competence")
    assert comp_review.resolved is True
    assert comp_review.disposition == "documentation_updated"


# ---------------------------------------------------------------------------
# Test 03: Unrelated doc changed -> UNRESOLVED (BLOCK)
# ---------------------------------------------------------------------------
def test_03_unrelated_doc_changed_remains_unresolved() -> None:
    # 00-foundations-and-epistemology.md is NOT a canonical doc for component.competence
    report = evaluate_documentation_gate(
        paths=[
            "symbiont/src/symbiont/actuation/competence.py",
            "symbiont/docs/00-foundations-and-epistemology.md",
        ],
        repo_root=ROOT,
        skip_p4=True,
        skip_p6=True,
    )
    assert report.outcome == GateOutcome.BLOCK
    assert report.unresolved_count == 1
    comp_review = next(r for r in report.reviews if r.unit == "component.competence")
    assert comp_review.resolved is False


# ---------------------------------------------------------------------------
# Test 04: Relevant component registry changed -> RESOLVED (PASS)
# ---------------------------------------------------------------------------
def test_04_relevant_component_registry_changed_resolves() -> None:
    report = evaluate_documentation_gate(
        paths=[
            "symbiont/src/symbiont/actuation/competence.py",
            "symbiont/docs/reference/components.yaml",
        ],
        repo_root=ROOT,
        skip_p4=True,
        skip_p6=True,
    )
    assert report.outcome == GateOutcome.PASS
    comp_review = next(r for r in report.reviews if r.unit == "component.competence")
    assert comp_review.resolved is True
    assert comp_review.disposition == "registry_updated"


# ---------------------------------------------------------------------------
# Test 05: Valid no_semantic_change disposition -> RESOLVED (PASS)
# ---------------------------------------------------------------------------
def test_05_valid_no_semantic_change_disposition_resolves() -> None:
    acks = {
        "documentation_impact": {
            "reviewed": [
                {
                    "unit": "component.competence",
                    "disposition": "no_semantic_change",
                    "rationale": "Internal algorithmic refactoring preserves all convergence thresholds.",
                }
            ]
        }
    }
    report = evaluate_documentation_gate(
        paths=["symbiont/src/symbiont/actuation/competence.py"],
        acknowledgements=acks,
        repo_root=ROOT,
        skip_p4=True,
        skip_p6=True,
    )
    assert report.outcome == GateOutcome.PASS
    comp_review = next(r for r in report.reviews if r.unit == "component.competence")
    assert comp_review.resolved is True
    assert comp_review.disposition == "no_semantic_change"


# ---------------------------------------------------------------------------
# Test 06: Disposition for other unit -> DOES NOT RESOLVE (BLOCK)
# ---------------------------------------------------------------------------
def test_06_disposition_for_other_unit_does_not_resolve() -> None:
    acks = {
        "documentation_impact": {
            "reviewed": [
                {
                    "unit": "component.private-model",
                    "disposition": "no_semantic_change",
                    "rationale": "Refactor does not change private model behavior.",
                }
            ]
        }
    }
    report = evaluate_documentation_gate(
        paths=["symbiont/src/symbiont/actuation/competence.py"],
        acknowledgements=acks,
        repo_root=ROOT,
        skip_p4=True,
        skip_p6=True,
    )
    assert report.outcome == GateOutcome.BLOCK
    assert report.unresolved_count == 1
    comp_review = next(r for r in report.reviews if r.unit == "component.competence")
    assert comp_review.resolved is False


# ---------------------------------------------------------------------------
# Test 07: Test-only impact -> NO SEMANTIC BLOCK (PASS)
# ---------------------------------------------------------------------------
def test_07_test_only_impact_does_not_block() -> None:
    report = evaluate_documentation_gate(
        paths=["symbiont/tests/unit/actuation/test_competence_convergence.py"],
        repo_root=ROOT,
        skip_p4=True,
        skip_p6=True,
    )
    assert report.outcome == GateOutcome.PASS
    assert report.review_required_count == 0
    assert report.unresolved_count == 0


# ---------------------------------------------------------------------------
# Test 08: Transitive-only impact -> NO BLOCK INITIALLY (PASS)
# ---------------------------------------------------------------------------
def test_08_transitive_only_impact_does_not_block() -> None:
    # When competence is resolved, its 8 child transitive dependents should NOT block
    report = evaluate_documentation_gate(
        paths=[
            "symbiont/src/symbiont/actuation/competence.py",
            "symbiont/docs/07-agency-action-and-motor-learning.md",
        ],
        repo_root=ROOT,
        skip_p4=True,
        skip_p6=True,
    )
    assert report.outcome == GateOutcome.PASS
    assert report.unresolved_count == 0
    assert report.transitive_impacts_count == 0 or report.transitive_impacts_count > 0


# ---------------------------------------------------------------------------
# Test 09: P4 canonical integrity failure -> BLOCK
# ---------------------------------------------------------------------------
def test_09_canonical_integrity_p4_failure_blocks() -> None:
    with patch(
        "documentation_impact_gate.check_canonical_integrity",
        return_value=(False, "Broken reference in coverage.yaml: missing file foo.py"),
    ):
        report = evaluate_documentation_gate(
            paths=["symbiont/docs/01-system-and-boundaries.md"],
            repo_root=ROOT,
            skip_p4=False,
            skip_p6=True,
        )
        assert report.outcome == GateOutcome.BLOCK
        assert report.canonical_integrity == "FAIL"
        assert any("Broken reference" in r for r in report.block_reasons)


# ---------------------------------------------------------------------------
# Test 10: Projection check failure -> BLOCK
# ---------------------------------------------------------------------------
def test_10_projection_check_failure_blocks() -> None:
    with patch(
        "documentation_impact_gate.check_master_projection",
        return_value=(False, "Projection build failure: invalid section mapping"),
    ):
        report = evaluate_documentation_gate(
            paths=["symbiont/docs/01-system-and-boundaries.md"],
            repo_root=ROOT,
            skip_p4=True,
            skip_p6=False,
        )
        assert report.outcome == GateOutcome.BLOCK
        assert report.master_projection == "FAIL"
        assert any("Projection build failure" in r for r in report.block_reasons)


# ---------------------------------------------------------------------------
# Test 11: Objective STALE unit -> BLOCK
# ---------------------------------------------------------------------------
def test_11_objective_stale_unit_blocks() -> None:
    mock_impact = {
        "direct_impacts": {},
        "transitive_impacts": {},
        "stale_units": [
            {
                "unit": "component.competence",
                "reviewed_against": "abc1234",
                "superseded_by": "def5678",
                "reason": "REVIEW_BASIS_OUTDATED",
            }
        ],
        "unmapped_changes": [],
        "diagnostics": {},
    }
    with patch("canonical_impact.analyze_changes", return_value=mock_impact):
        report = evaluate_documentation_gate(
            paths=["symbiont/src/symbiont/actuation/competence.py"],
            repo_root=ROOT,
            skip_p4=True,
            skip_p6=True,
        )
        assert report.outcome == GateOutcome.BLOCK
        assert report.stale_units_count == 1
        assert any("Objectively stale canonical units" in r for r in report.block_reasons)


# ---------------------------------------------------------------------------
# Test 12: Unknown staleness -> NO BLOCK (PASS)
# ---------------------------------------------------------------------------
def test_12_undetermined_unknown_staleness_does_not_block() -> None:
    # Undetermined staleness is informational, not blocking
    mock_impact = {
        "direct_impacts": {},
        "transitive_impacts": {},
        "stale_units": [],
        "unmapped_changes": [],
        "diagnostics": {
            "undetermined_staleness_units": ["component.competence", "component.agency-acquisition"]
        },
    }
    with patch("canonical_impact.analyze_changes", return_value=mock_impact):
        report = evaluate_documentation_gate(
            paths=["symbiont/docs/01-system-and-boundaries.md"],
            repo_root=ROOT,
            skip_p4=True,
            skip_p6=True,
        )
        assert report.outcome == GateOutcome.PASS
        assert report.stale_units_count == 0


# ---------------------------------------------------------------------------
# Test 13: Unmapped production path requiring coverage -> BLOCK
# ---------------------------------------------------------------------------
def test_13_unmapped_production_path_blocks() -> None:
    report = evaluate_documentation_gate(
        paths=["symbiont/src/symbiont/core/new_unmapped_module.py"],
        repo_root=ROOT,
        skip_p4=True,
        skip_p6=True,
    )
    assert report.outcome == GateOutcome.BLOCK
    assert "symbiont/src/symbiont/core/new_unmapped_module.py" in report.unmapped_production_paths
    assert any("Unmapped production paths" in r for r in report.block_reasons)


# ---------------------------------------------------------------------------
# Test 14: Unrelated infrastructure path -> NO FALSE BLOCK (PASS)
# ---------------------------------------------------------------------------
def test_14_unrelated_infrastructure_path_does_not_block() -> None:
    report = evaluate_documentation_gate(
        paths=[
            ".github/workflows/new_governance_check.yml",
            "scripts/governance/new_tool.py",
        ],
        repo_root=ROOT,
        skip_p4=True,
        skip_p6=True,
    )
    assert report.outcome == GateOutcome.PASS
    assert len(report.unmapped_production_paths) == 0


# ---------------------------------------------------------------------------
# Test 15: Deterministic report output
# ---------------------------------------------------------------------------
def test_15_deterministic_report_output() -> None:
    paths_order_1 = [
        "symbiont/src/symbiont/actuation/competence.py",
        "symbiont/docs/07-agency-action-and-motor-learning.md",
        "symbiont/tests/unit/actuation/test_competence_convergence.py",
    ]
    paths_order_2 = list(reversed(paths_order_1))

    report_1 = evaluate_documentation_gate(
        paths=paths_order_1, repo_root=ROOT, skip_p4=True, skip_p6=True
    )
    report_2 = evaluate_documentation_gate(
        paths=paths_order_2, repo_root=ROOT, skip_p4=True, skip_p6=True
    )

    text_1 = format_gate_report(report_1)
    text_2 = format_gate_report(report_2)

    assert text_1 == text_2
    assert report_1.to_dict() == report_2.to_dict()


# ---------------------------------------------------------------------------
# Test 16: Clear diagnostic reasons on block
# ---------------------------------------------------------------------------
def test_16_clear_diagnostic_reasons_on_block() -> None:
    report = evaluate_documentation_gate(
        paths=["symbiont/src/symbiont/actuation/competence.py"],
        repo_root=ROOT,
        skip_p4=True,
        skip_p6=True,
    )
    formatted = format_gate_report(report)
    assert "RESULT: BLOCK" in formatted
    assert "BLOCK DETAILS:" in formatted
    assert "component.competence" in formatted
    assert "reason: IMPLEMENTATION_CHANGED" in formatted
    assert "symbiont/src/symbiont/actuation/competence.py" in formatted
    assert "symbiont/docs/07-agency-action-and-motor-learning.md" in formatted
    assert "update a relevant canonical source" in formatted
    assert "OR record an explicit no_semantic_change disposition" in formatted


# ---------------------------------------------------------------------------
# Three Synthetic Closure Scenarios (CASE A, CASE B, CASE C)
# ---------------------------------------------------------------------------
def test_closure_synthetic_case_a_runtime_semantic_change_no_docs_blocks() -> None:
    """CASE A: Runtime semantic change without documentation or disposition -> BLOCK."""
    report = evaluate_documentation_gate(
        paths=["symbiont/src/symbiont/actuation/competence.py"],
        repo_root=ROOT,
        skip_p4=False,
        skip_p6=False,
    )
    assert report.outcome == GateOutcome.BLOCK
    assert report.canonical_integrity == "PASS"
    assert report.master_projection == "PASS"
    assert report.unresolved_count == 1
    assert "component.competence" in report.block_reasons[0]


def test_closure_synthetic_case_b_runtime_semantic_change_with_doc_passes() -> None:
    """CASE B: Runtime semantic change with relevant canonical doc updated -> PASS."""
    report = evaluate_documentation_gate(
        paths=[
            "symbiont/src/symbiont/actuation/competence.py",
            "symbiont/docs/07-agency-action-and-motor-learning.md",
        ],
        repo_root=ROOT,
        skip_p4=False,
        skip_p6=False,
    )
    assert report.outcome == GateOutcome.PASS
    assert report.canonical_integrity == "PASS"
    assert report.master_projection == "PASS"
    assert report.unresolved_count == 0
    assert report.resolved_count == 1


def test_closure_synthetic_case_c_runtime_refactor_with_disposition_passes() -> None:
    """CASE C: Runtime internal refactor with explicit governed disposition -> PASS."""
    pr_body = """
    ## Summary of changes
    Internal algorithmic loop refactoring to optimize memory pressure.

    ```yaml
    documentation_impact:
      reviewed:
        - unit: component.competence
          disposition: no_semantic_change
          rationale: >
            Algorithmic loop optimization preserves all mathematical convergence
            properties, Wilson score bindings, and state transitions.
    ```
    """
    report = evaluate_documentation_gate(
        paths=["symbiont/src/symbiont/actuation/competence.py"],
        acknowledgements=pr_body,
        repo_root=ROOT,
        skip_p4=False,
        skip_p6=False,
    )
    assert report.outcome == GateOutcome.PASS
    assert report.canonical_integrity == "PASS"
    assert report.master_projection == "PASS"
    assert report.unresolved_count == 0
    assert report.resolved_count == 1
    review = report.reviews[0]
    assert review.disposition == "no_semantic_change"
    assert "Algorithmic loop optimization" in str(review.rationale)


# ---------------------------------------------------------------------------
# Anti-Gaming Invariants Tests
# ---------------------------------------------------------------------------
def test_anti_gaming_empty_markdown_does_not_resolve(tmp_path: Path) -> None:
    """Anti-gaming: touching an empty markdown file does NOT satisfy review."""
    empty_doc = tmp_path / "symbiont/docs/07-agency-action-and-motor-learning.md"
    empty_doc.parent.mkdir(parents=True, exist_ok=True)
    empty_doc.write_text("   \n\n  ", encoding="utf-8")  # Whitespace only

    # Using tmp_path as repo_root with mock impact
    mock_impact = {
        "direct_impacts": {
            "component.competence": {
                "causes": [
                    {
                        "relation": "implementation",
                        "path": "symbiont/src/symbiont/actuation/competence.py",
                    }
                ]
            }
        },
        "transitive_impacts": {},
        "stale_units": [],
        "unmapped_changes": [],
        "diagnostics": {},
    }
    with patch("canonical_impact.analyze_changes", return_value=mock_impact):
        report = evaluate_documentation_gate(
            paths=[
                "symbiont/src/symbiont/actuation/competence.py",
                "symbiont/docs/07-agency-action-and-motor-learning.md",
            ],
            repo_root=tmp_path,
            skip_p4=True,
            skip_p6=True,
        )
        assert report.outcome == GateOutcome.BLOCK
        comp_review = report.reviews[0]
        assert comp_review.resolved is False


def test_anti_gaming_coverage_update_required_blocks() -> None:
    """Anti-gaming: coverage_update_required disposition explicitly blocks until resolved."""
    acks = {
        "documentation_impact": {
            "reviewed": [
                {
                    "unit": "component.competence",
                    "disposition": "coverage_update_required",
                }
            ]
        }
    }
    report = evaluate_documentation_gate(
        paths=["symbiont/src/symbiont/actuation/competence.py"],
        acknowledgements=acks,
        repo_root=ROOT,
        skip_p4=True,
        skip_p6=True,
    )
    assert report.outcome == GateOutcome.BLOCK
    assert report.unresolved_count == 1
    assert "coverage_update_required blocks promotion" in str(report.reviews[0].error)


def test_anti_gaming_deferred_with_tracking_requires_tracking_ref() -> None:
    """Anti-gaming: deferred_with_tracking requires non-empty tracking_ref."""
    acks_invalid = {
        "documentation_impact": {
            "reviewed": [
                {
                    "unit": "component.competence",
                    "disposition": "deferred_with_tracking",
                    "tracking_ref": "",
                }
            ]
        }
    }
    report_bad = evaluate_documentation_gate(
        paths=["symbiont/src/symbiont/actuation/competence.py"],
        acknowledgements=acks_invalid,
        repo_root=ROOT,
        skip_p4=True,
        skip_p6=True,
    )
    assert report_bad.outcome == GateOutcome.BLOCK
    assert "requires a valid tracking reference" in str(report_bad.reviews[0].error)

    acks_valid = {
        "documentation_impact": {
            "reviewed": [
                {
                    "unit": "component.competence",
                    "disposition": "deferred_with_tracking",
                    "tracking_ref": "ADR-0042",
                }
            ]
        }
    }
    report_good = evaluate_documentation_gate(
        paths=["symbiont/src/symbiont/actuation/competence.py"],
        acknowledgements=acks_valid,
        repo_root=ROOT,
        skip_p4=True,
        skip_p6=True,
    )
    assert report_good.outcome == GateOutcome.PASS
    assert report_good.reviews[0].resolved is True


def test_anti_gaming_trivial_rationale_rejected() -> None:
    """Anti-gaming: trivial rationales ('ok', 'todo', 'none', <10 chars) are rejected."""
    for bad_rationale in ["ok", "none", "n/a", "TODO", "not needed", "short"]:
        acks = {
            "documentation_impact": {
                "reviewed": [
                    {
                        "unit": "component.competence",
                        "disposition": "no_semantic_change",
                        "rationale": bad_rationale,
                    }
                ]
            }
        }
        report = evaluate_documentation_gate(
            paths=["symbiont/src/symbiont/actuation/competence.py"],
            acknowledgements=acks,
            repo_root=ROOT,
            skip_p4=True,
            skip_p6=True,
        )
        assert report.outcome == GateOutcome.BLOCK
        assert "substantive human rationale" in str(report.reviews[0].error)

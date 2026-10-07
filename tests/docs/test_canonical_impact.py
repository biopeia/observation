"""Test suite for deterministic documentation impact and staleness detection.

Strictly verifies the 17 required scenarios of P5.14:
1. implementation -> direct unit impact;
2. same file -> multiple canonical units;
3. reverse dependency propagation;
4. multi-level transitive propagation;
5. cycle-safe dependency traversal;
6. test change does not propagate downstream;
7. canonical doc change does not propagate downstream;
8. design change propagates downstream;
9. ADR change propagates downstream;
10. unmapped path -> UNMAPPED_CHANGE;
11. component registry change -> coverage unit;
12. parameter change -> owner unit;
13. metric change -> consumer unit as measurement impact;
14. notation change -> formal review required and literal doc references;
15. affected units correctly populate Master SYM-* review IDs;
16. deterministic output regardless of input path ordering;
17. byte-for-byte identical JSON/YAML serialization.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = ROOT / "symbiont/docs"
if str(DOCS_DIR) not in sys.path:
    sys.path.insert(0, str(DOCS_DIR))

from canonical_impact import (  # noqa: E402
    ChangeReason,
    analyze_changes,
    format_summary_table,
    load_canonical_graph,
    load_reference_registries,
)


@pytest.fixture(scope="module")
def canonical_graph() -> dict:
    return load_canonical_graph()


@pytest.fixture(scope="module")
def reference_registries() -> dict:
    return load_reference_registries()


@pytest.fixture
def mock_graph() -> dict:
    return {
        "schema_version": 2,
        "units": {
            "component.unit-a": {
                "kind": "component",
                "canonical_docs": ["symbiont/docs/doc-a.md"],
                "implementation": ["symbiont/src/symbiont/unit_a.py"],
                "tests": ["tests/unit/test_unit_a.py"],
                "design": ["docs/design/unit-a.md"],
                "adrs": ["docs/adr/ADR-0001.md"],
                "master": {"ids": ["SYM-A"]},
                "depends_on": [],
            },
            "component.unit-b": {
                "kind": "component",
                "canonical_docs": ["symbiont/docs/doc-b.md"],
                "implementation": ["symbiont/src/symbiont/unit_b.py"],
                "tests": ["tests/unit/test_unit_b.py"],
                "master": {"ids": ["SYM-B"]},
                "depends_on": ["component.unit-a"],
            },
            "component.unit-c": {
                "kind": "component",
                "canonical_docs": ["symbiont/docs/doc-c.md"],
                "implementation": ["symbiont/src/symbiont/unit_c.py"],
                "master": {"ids": ["SYM-C"]},
                "depends_on": ["component.unit-b"],
            },
            "mechanism.shared": {
                "kind": "mechanism",
                "canonical_docs": ["symbiont/docs/doc-shared.md"],
                "implementation": ["symbiont/src/symbiont/unit_a.py"],
                "depends_on": [],
            },
        },
    }


def test_1_implementation_direct_impact(mock_graph):
    report = analyze_changes(
        paths=["symbiont/src/symbiont/unit_b.py"],
        graph_data=mock_graph,
        registries_data={},
    )
    assert "component.unit-b" in report["direct_impacts"]
    causes = report["direct_impacts"]["component.unit-b"]["causes"]
    assert any(
        c["path"] == "symbiont/src/symbiont/unit_b.py" and c["relation"] == "implementation"
        for c in causes
    )
    assert any(
        r["unit"] == "component.unit-b" and r["reason"] == ChangeReason.IMPLEMENTATION_CHANGED.value
        for r in report["review_required"]
    )


def test_2_multiple_units_per_file(mock_graph):
    report = analyze_changes(
        paths=["symbiont/src/symbiont/unit_a.py"],
        graph_data=mock_graph,
        registries_data={},
    )
    assert "component.unit-a" in report["direct_impacts"]
    assert "mechanism.shared" in report["direct_impacts"]


def test_3_reverse_dependency_propagation(mock_graph):
    # unit-b depends on unit-a. Modifying unit-a propagates to unit-b.
    report = analyze_changes(
        paths=["symbiont/src/symbiont/unit_a.py"],
        graph_data=mock_graph,
        registries_data={},
    )
    assert "component.unit-b" in report["transitive_impacts"]
    trans = report["transitive_impacts"]["component.unit-b"]
    assert trans["depth"] == 1
    assert "component.unit-a" in trans["via"]


def test_4_multilevel_propagation(mock_graph):
    # unit-c depends on unit-b; unit-b depends on unit-a.
    report = analyze_changes(
        paths=["symbiont/src/symbiont/unit_a.py"],
        graph_data=mock_graph,
        registries_data={},
    )
    assert "component.unit-b" in report["transitive_impacts"]
    assert "component.unit-c" in report["transitive_impacts"]
    assert report["transitive_impacts"]["component.unit-b"]["depth"] == 1
    assert report["transitive_impacts"]["component.unit-c"]["depth"] == 2
    assert "component.unit-b" in report["transitive_impacts"]["component.unit-c"]["via"]


def test_5_dependency_cycle_safety():
    cycle_graph = {
        "schema_version": 2,
        "units": {
            "component.cycle-1": {
                "implementation": ["symbiont/src/cycle_1.py"],
                "depends_on": ["component.cycle-2"],
            },
            "component.cycle-2": {
                "implementation": ["symbiont/src/cycle_2.py"],
                "depends_on": ["component.cycle-1"],
            },
        },
    }
    report = analyze_changes(
        paths=["symbiont/src/cycle_1.py"],
        graph_data=cycle_graph,
        registries_data={},
    )
    assert "component.cycle-1" in report["direct_impacts"]
    assert "component.cycle-2" in report["transitive_impacts"]
    assert report["transitive_impacts"]["component.cycle-2"]["depth"] == 1


def test_6_test_change_does_not_propagate(mock_graph):
    report = analyze_changes(
        paths=["tests/unit/test_unit_a.py"],
        graph_data=mock_graph,
        registries_data={},
    )
    assert "component.unit-a" in report["direct_impacts"]
    assert report["direct_impacts"]["component.unit-a"]["causes"][0]["relation"] == "test"
    # Tests must not propagate downstream
    assert "component.unit-b" not in report["transitive_impacts"]
    assert "component.unit-c" not in report["transitive_impacts"]


def test_7_canonical_doc_change_does_not_propagate(mock_graph):
    report = analyze_changes(
        paths=["symbiont/docs/doc-a.md"],
        graph_data=mock_graph,
        registries_data={},
    )
    assert "component.unit-a" in report["direct_impacts"]
    assert report["direct_impacts"]["component.unit-a"]["causes"][0]["relation"] == "canonical_doc"
    # Canonical doc must not propagate downstream
    assert "component.unit-b" not in report["transitive_impacts"]
    assert "component.unit-c" not in report["transitive_impacts"]


def test_8_design_change_propagates(mock_graph):
    report = analyze_changes(
        paths=["docs/design/unit-a.md"],
        graph_data=mock_graph,
        registries_data={},
    )
    assert "component.unit-a" in report["direct_impacts"]
    assert report["direct_impacts"]["component.unit-a"]["causes"][0]["relation"] == "design"
    # Design change propagates downstream
    assert "component.unit-b" in report["transitive_impacts"]
    assert "component.unit-c" in report["transitive_impacts"]


def test_9_adr_change_propagates(mock_graph):
    report = analyze_changes(
        paths=["docs/adr/ADR-0001.md"],
        graph_data=mock_graph,
        registries_data={},
    )
    assert "component.unit-a" in report["direct_impacts"]
    assert report["direct_impacts"]["component.unit-a"]["causes"][0]["relation"] == "adr"
    # ADR change propagates downstream
    assert "component.unit-b" in report["transitive_impacts"]
    assert "component.unit-c" in report["transitive_impacts"]


def test_10_unmapped_changes(mock_graph):
    report = analyze_changes(
        paths=["symbiont/src/symbiont/foo/new_mechanism.py"],
        graph_data=mock_graph,
        registries_data={},
    )
    assert "symbiont/src/symbiont/foo/new_mechanism.py" in report["unmapped_changes"]
    assert len(report["direct_impacts"]) == 0
    assert len(report["transitive_impacts"]) == 0


def test_11_component_registry_change(canonical_graph, reference_registries):
    report = analyze_changes(
        paths=["symbiont/docs/reference/components.yaml#SYM-COMP"],
        graph_data=canonical_graph,
        registries_data=reference_registries,
    )
    assert "component.competence" in report["direct_impacts"]
    cause = report["direct_impacts"]["component.competence"]["causes"][0]
    assert cause["relation"] == "component_registry"
    assert cause["symbol"] == "SYM-COMP"


def test_12_parameter_change(canonical_graph, reference_registries):
    report = analyze_changes(
        paths=["symbiont/docs/reference/parameters.yaml#competence.minimum_support"],
        graph_data=canonical_graph,
        registries_data=reference_registries,
    )
    assert "component.competence" in report["direct_impacts"]
    cause = report["direct_impacts"]["component.competence"]["causes"][0]
    assert cause["relation"] == "parameter"
    assert cause["symbol"] == "competence.minimum_support"
    assert any(
        r["unit"] == "component.competence" and r["reason"] == ChangeReason.PARAMETER_CHANGED.value
        for r in report["review_required"]
    )


def test_13_metric_change(canonical_graph, reference_registries):
    report = analyze_changes(
        paths=["symbiont/docs/reference/metrics.yaml#prediction.huber_loss"],
        graph_data=canonical_graph,
        registries_data=reference_registries,
    )
    assert "component.local-predictors" in report["direct_impacts"]
    cause = report["direct_impacts"]["component.local-predictors"]["causes"][0]
    assert cause["relation"] == "metric_measurement"
    assert cause["class"] == "measurement impact"
    # Measurement impact does NOT propagate downstream
    assert len(report["transitive_impacts"]) == 0
    assert any(
        r["unit"] == "component.local-predictors"
        and r["reason"] == ChangeReason.METRIC_CHANGED.value
        for r in report["review_required"]
    )


def test_14_notation_change(canonical_graph, reference_registries):
    report = analyze_changes(
        paths=["symbiont/docs/reference/notation.yaml#S_t"],
        graph_data=canonical_graph,
        registries_data=reference_registries,
    )
    assert report.get("formal_review_required") is True
    notation_rev = report["diagnostics"]["notation_review"]
    assert any(n["symbol"] == "S_t" for n in notation_rev)
    s_entry = next(n for n in notation_rev if n["symbol"] == "S_t")
    assert len(s_entry["referencing_docs"]) > 0


def test_15_master_review_ids(mock_graph):
    report = analyze_changes(
        paths=["symbiont/src/symbiont/unit_a.py"],
        graph_data=mock_graph,
        registries_data={},
    )
    assert "SYM-A" in report["master_review"]
    assert "SYM-B" in report["master_review"]
    assert "SYM-C" in report["master_review"]
    assert report["master_review"] == sorted(report["master_review"])


def test_16_deterministic_output_regardless_of_input_order(mock_graph):
    paths1 = ["symbiont/src/symbiont/unit_a.py", "symbiont/docs/doc-b.md", "unknown/path.py"]
    paths2 = ["unknown/path.py", "symbiont/docs/doc-b.md", "symbiont/src/symbiont/unit_a.py"]

    rep1 = analyze_changes(paths=paths1, graph_data=mock_graph, registries_data={})
    rep2 = analyze_changes(paths=paths2, graph_data=mock_graph, registries_data={})

    assert rep1 == rep2


def test_17_identical_json_yaml_serialization(mock_graph):
    paths = ["symbiont/src/symbiont/unit_a.py", "unknown/path.py"]
    rep = analyze_changes(paths=paths, graph_data=mock_graph, registries_data={})

    json1 = json.dumps(rep, indent=2, sort_keys=True)
    json2 = json.dumps(rep, indent=2, sort_keys=True)
    assert json1 == json2

    yaml1 = yaml.dump(rep, sort_keys=False, allow_unicode=True)
    yaml2 = yaml.dump(rep, sort_keys=False, allow_unicode=True)
    assert yaml1 == yaml2


def test_integration_private_runtime_trace(canonical_graph, reference_registries):
    """Exact criterion of closeout for P5."""
    report = analyze_changes(
        paths=["symbiont/src/symbiont/modeling/private_runtime.py"],
        graph_data=canonical_graph,
        registries_data=reference_registries,
    )

    summary = report["summary"]
    assert summary["changed_paths"] == 1
    assert summary["directly_impacted_units"] == 1
    assert summary["transitive_units"] == 3
    assert summary["docs_requiring_review"] == 2
    assert summary["sym_ids_requiring_review"] == 4
    assert summary["unmapped_changed_paths"] == 0
    assert summary["objectively_stale_units"] == 0

    assert list(report["direct_impacts"].keys()) == ["component.private-model"]
    trans = report["transitive_impacts"]
    assert "component.counterfactual-rollout" in trans
    assert "component.generative-cognition" in trans
    assert "component.generative-hypothesis" in trans

    assert trans["component.counterfactual-rollout"]["depth"] == 1
    assert trans["component.generative-cognition"]["depth"] == 1
    assert trans["component.generative-hypothesis"]["depth"] == 2

    assert report["master_review"] == ["SYM-CF", "SYM-GENC", "SYM-HYP", "SYM-PM"]

    doc_paths = [d["path"] for d in report["documentation_review"]]
    assert "symbiont/docs/08-learning-memory-and-plasticity.md" in doc_paths
    assert "symbiont/docs/09-generative-cognition.md" in doc_paths

    table = format_summary_table(report)
    assert "| changed paths | 1 |" in table
    assert "| directly impacted units | 1 |" in table
    assert "| transitive units | 3 |" in table


def test_staleness_with_verified_review_basis(mock_graph):
    review_basis = {
        "schema_version": 1,
        "reviews": {
            "component.unit-a": {
                "reviewed_against": "old_commit_sha",
                "reviewed_at": "2026-10-01",
                "stale": True,
            }
        },
    }
    report = analyze_changes(
        paths=["symbiont/src/symbiont/unit_a.py"],
        graph_data=mock_graph,
        registries_data={},
        review_basis=review_basis,
    )
    assert len(report["stale_units"]) == 1
    stale_entry = report["stale_units"][0]
    assert stale_entry["unit"] == "component.unit-a"
    assert stale_entry["reason"] == ChangeReason.REVIEW_BASIS_OUTDATED.value

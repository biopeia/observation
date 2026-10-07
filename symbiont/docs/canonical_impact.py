#!/usr/bin/env python3
"""Deterministic documentation impact and staleness detection engine.

Sensor engine that computes:
  changed paths
       ↓
  directly impacted canonical units (with precise relations and causes)
       ↓
  transitive downstream units (via cycle-safe dependency graph traversal)
       ↓
  canonical documentation and Master SYM-* IDs requiring review
       ↓
  staleness detection against verified review basis

Operating Principles (P5):
- Sensor only: does NOT modify documentation, code, or coverage.
- Pure determinism: byte-for-byte reproducible JSON/YAML output regardless of input order.
- Closed reason vocabulary:
    IMPLEMENTATION_CHANGED, TEST_CHANGED, DESIGN_CHANGED, ADR_CHANGED,
    CANONICAL_DOC_CHANGED, PARAMETER_CHANGED, METRIC_CHANGED,
    NOTATION_CHANGED, DEPENDENCY_IMPACT, UNMAPPED_CHANGE, REVIEW_BASIS_OUTDATED.
- Propagation policy:
    implementation -> direct: True, propagate: True
    design         -> direct: True, propagate: True
    adr            -> direct: True, propagate: True
    test           -> direct: True, propagate: False
    canonical_doc  -> direct: True, propagate: False
    component_reg  -> direct: True, propagate: True
    parameter      -> direct: True, propagate: False
    metric_meas    -> direct: True, propagate: False
- Staleness: STALE is asserted ONLY when a verified review basis commit SHA is superseded.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import deque
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_COVERAGE_PATH = ROOT / "symbiont/docs/coverage.yaml"
DEFAULT_REFERENCE_DIR = ROOT / "symbiont/docs/reference"
DEFAULT_REVIEW_BASIS_PATH = ROOT / "symbiont/docs/reference/review-basis.yaml"


class ChangeReason(str, Enum):
    IMPLEMENTATION_CHANGED = "IMPLEMENTATION_CHANGED"
    TEST_CHANGED = "TEST_CHANGED"
    DESIGN_CHANGED = "DESIGN_CHANGED"
    ADR_CHANGED = "ADR_CHANGED"
    CANONICAL_DOC_CHANGED = "CANONICAL_DOC_CHANGED"
    PARAMETER_CHANGED = "PARAMETER_CHANGED"
    METRIC_CHANGED = "METRIC_CHANGED"
    NOTATION_CHANGED = "NOTATION_CHANGED"
    DEPENDENCY_IMPACT = "DEPENDENCY_IMPACT"
    UNMAPPED_CHANGE = "UNMAPPED_CHANGE"
    REVIEW_BASIS_OUTDATED = "REVIEW_BASIS_OUTDATED"


# (is_direct_impact, propagates_downstream)
PROPAGATION_POLICY: dict[str, tuple[bool, bool]] = {
    "implementation": (True, True),
    "design": (True, True),
    "adr": (True, True),
    "test": (True, False),
    "canonical_doc": (True, False),
    "component_registry": (True, True),
    "parameter": (True, False),
    "metric_measurement": (True, False),
}

RELATION_TO_REASON: dict[str, ChangeReason] = {
    "implementation": ChangeReason.IMPLEMENTATION_CHANGED,
    "design": ChangeReason.DESIGN_CHANGED,
    "adr": ChangeReason.ADR_CHANGED,
    "test": ChangeReason.TEST_CHANGED,
    "canonical_doc": ChangeReason.CANONICAL_DOC_CHANGED,
    "component_registry": ChangeReason.CANONICAL_DOC_CHANGED,
    "parameter": ChangeReason.PARAMETER_CHANGED,
    "metric_measurement": ChangeReason.METRIC_CHANGED,
}


class UniqueKeySafeLoader(yaml.SafeLoader):
    """YAML Loader that strictly rejects duplicate keys."""

    pass


def _construct_mapping(loader: yaml.Loader, node: yaml.MappingNode, deep: bool = False) -> dict:
    loader.flatten_mapping(node)
    mapping: dict = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise ValueError(
                f"Duplicate YAML key found: {key!r} at line {key_node.start_mark.line + 1}"
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeySafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping
)


def load_strict_yaml(path: Path) -> dict[str, Any]:
    """Load YAML file strictly rejecting duplicate keys."""
    if not path.is_file():
        return {}
    with path.open("r", encoding="utf-8") as fp:
        return yaml.load(fp, Loader=UniqueKeySafeLoader) or {}


def load_canonical_graph(coverage_path: Path | None = None) -> dict[str, Any]:
    """Load canonical coverage graph."""
    target = coverage_path or DEFAULT_COVERAGE_PATH
    return load_strict_yaml(target)


def load_reference_registries(reference_dir: Path | None = None) -> dict[str, dict[str, Any]]:
    """Load all 4 reference registries."""
    ref_dir = reference_dir or DEFAULT_REFERENCE_DIR
    return {
        "components": load_strict_yaml(ref_dir / "components.yaml"),
        "parameters": load_strict_yaml(ref_dir / "parameters.yaml"),
        "metrics": load_strict_yaml(ref_dir / "metrics.yaml"),
        "notation": load_strict_yaml(ref_dir / "notation.yaml"),
    }


def load_review_basis(review_basis_path: Path | None = None) -> dict[str, Any]:
    """Load verified review basis if present."""
    target = review_basis_path or DEFAULT_REVIEW_BASIS_PATH
    if target.is_file():
        return load_strict_yaml(target)
    return {}


def build_reverse_index(graph_data: dict[str, Any]) -> dict[str, list[dict[str, str]]]:
    """Build reverse index mapping file path -> list of {unit, relation}."""
    index: dict[str, list[dict[str, str]]] = {}
    units = graph_data.get("units", {})

    relation_fields = [
        ("implementation", "implementation"),
        ("design", "design"),
        ("adrs", "adr"),
        ("tests", "test"),
        ("canonical_docs", "canonical_doc"),
    ]

    for unit_id, unit_info in units.items():
        if not isinstance(unit_info, dict):
            continue
        for field_name, relation in relation_fields:
            paths = unit_info.get(field_name, [])
            if isinstance(paths, str):
                paths = [paths]
            for raw_path in paths:
                p = raw_path.strip()
                if not p:
                    continue
                index.setdefault(p, []).append({"unit": unit_id, "relation": relation})

    for path, entries in index.items():
        entries.sort(key=lambda x: (x["unit"], x["relation"]))
    return index


def build_dependents_graph(graph_data: dict[str, Any]) -> dict[str, list[str]]:
    """Build reverse dependency graph mapping dependency -> list of dependent units."""
    dependents: dict[str, list[str]] = {}
    units = graph_data.get("units", {})
    for unit_id, unit_info in units.items():
        if not isinstance(unit_info, dict):
            continue
        deps = unit_info.get("depends_on", [])
        if isinstance(deps, str):
            deps = [deps]
        for dep in deps:
            dep_id = dep.strip()
            if dep_id:
                dependents.setdefault(dep_id, []).append(unit_id)

    for dep_id, deps_list in dependents.items():
        deps_list.sort()
    return dependents


def changed_paths_between(base: str, head: str, repo_root: Path | None = None) -> list[str]:
    """Obtain changed file paths between two git commits."""
    root = repo_root or ROOT
    result = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=ACMRD", base, head],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return sorted(set(filter(None, result.stdout.splitlines())))


def _parse_changed_keys_from_yaml_diff(diff_text: str) -> list[str]:
    """Extract top-level and second-level changed YAML keys from unified diff."""
    keys: set[str] = set()
    key_pattern = re.compile(r"^\+\s{2,4}([A-Za-z0-9_.-]+):")
    for line in diff_text.splitlines():
        match = key_pattern.match(line)
        if match:
            keys.add(match.group(1))
    return sorted(keys)


def _find_symbol_in_docs(symbol: str, doc_paths: list[str], repo_root: Path) -> list[str]:
    """Deterministically find markdown docs literally containing a notation symbol."""
    found: list[str] = []
    pattern = re.compile(r"\b" + re.escape(symbol) + r"\b")
    for doc_rel in sorted(doc_paths):
        full_path = repo_root / doc_rel
        if full_path.is_file():
            try:
                content = full_path.read_text(encoding="utf-8", errors="replace")
                if pattern.search(content):
                    found.append(doc_rel)
            except OSError:
                continue
    return sorted(set(found))


def analyze_changes(
    paths: list[str],
    graph_data: dict[str, Any] | None = None,
    registries_data: dict[str, dict[str, Any]] | None = None,
    review_basis: dict[str, Any] | None = None,
    *,
    registry_changes: dict[str, list[str]] | None = None,
    diff_content: str | dict[str, str] | None = None,
    base: str | None = None,
    head: str | None = None,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Deterministic documentation impact and staleness analyzer.

    Args:
        paths: List of changed file paths.
        graph_data: Canonical graph dict (default: loaded from coverage.yaml).
        registries_data: Dict of registries (components, parameters, metrics, notation).
        review_basis: Verified review basis dict (default: loaded from review-basis.yaml).
        registry_changes: Optional explicit map of registry name -> changed keys.
        diff_content: Optional git diff string or path -> diff map.
        base: Optional base commit SHA.
        head: Optional head commit SHA.
        repo_root: Optional repository root Path.

    Returns:
        Deterministic ImpactReport dictionary conforming to P5.12.
    """
    root = repo_root or ROOT
    graph = graph_data if graph_data is not None else load_canonical_graph()
    registries = registries_data if registries_data is not None else load_reference_registries()
    basis = review_basis if review_basis is not None else load_review_basis()

    units_data: dict[str, Any] = graph.get("units", {})
    reverse_index = build_reverse_index(graph)
    dependents_graph = build_dependents_graph(graph)

    components_reg = registries.get("components", {}).get("components", {})
    parameters_reg = registries.get("parameters", {}).get("parameters", {})
    metrics_reg = registries.get("metrics", {}).get("metrics", {})
    notation_reg = registries.get("notation", {}).get("symbols", {})

    cleaned_paths = sorted(set(p.strip() for p in paths if p and p.strip()))

    direct_impacts: dict[str, dict[str, Any]] = {}
    unmapped_changes: list[str] = []
    notation_symbols_changed: set[str] = set()

    all_canonical_docs: set[str] = set()
    for u_info in units_data.values():
        if isinstance(u_info, dict):
            for d in u_info.get("canonical_docs", []):
                all_canonical_docs.add(d.strip())

    for raw_p in cleaned_paths:
        p_clean = raw_p
        selector: str | None = None
        if "#" in raw_p:
            p_clean, selector = raw_p.split("#", 1)
        elif ":" in raw_p and not raw_p.endswith(".py"):
            parts = raw_p.split(":", 1)
            p_clean, selector = parts[0], parts[1]

        matched = False

        if p_clean in reverse_index:
            matched = True
            for entry in reverse_index[p_clean]:
                u = entry["unit"]
                rel = entry["relation"]
                direct_impacts.setdefault(u, {"causes": []})
                cause = {"path": p_clean, "relation": rel}
                if cause not in direct_impacts[u]["causes"]:
                    direct_impacts[u]["causes"].append(cause)

        is_components_path = p_clean.endswith("components.yaml")
        is_parameters_path = p_clean.endswith("parameters.yaml")
        is_metrics_path = p_clean.endswith("metrics.yaml")
        is_notation_path = p_clean.endswith("notation.yaml")

        if is_components_path:
            matched = True
            changed_syms: list[str] = []
            if selector:
                changed_syms = [selector]
            elif registry_changes and "components" in registry_changes:
                changed_syms = registry_changes["components"]
            elif isinstance(diff_content, str):
                changed_syms = _parse_changed_keys_from_yaml_diff(diff_content)
            elif isinstance(diff_content, dict) and p_clean in diff_content:
                changed_syms = _parse_changed_keys_from_yaml_diff(diff_content[p_clean])
            else:
                changed_syms = list(components_reg.keys())

            for sym in sorted(changed_syms):
                comp_info = components_reg.get(sym, {})
                cov_unit = comp_info.get("coverage_unit")
                if cov_unit:
                    direct_impacts.setdefault(cov_unit, {"causes": []})
                    cause = {"path": p_clean, "relation": "component_registry", "symbol": sym}
                    if cause not in direct_impacts[cov_unit]["causes"]:
                        direct_impacts[cov_unit]["causes"].append(cause)

        if is_parameters_path:
            matched = True
            changed_params: list[str] = []
            if selector:
                changed_params = [selector]
            elif registry_changes and "parameters" in registry_changes:
                changed_params = registry_changes["parameters"]
            elif isinstance(diff_content, str):
                changed_params = _parse_changed_keys_from_yaml_diff(diff_content)
            elif isinstance(diff_content, dict) and p_clean in diff_content:
                changed_params = _parse_changed_keys_from_yaml_diff(diff_content[p_clean])
            else:
                changed_params = list(parameters_reg.keys())

            for param_id in sorted(changed_params):
                param_info = parameters_reg.get(param_id, {})
                owner_unit = param_info.get("owner")
                if owner_unit:
                    direct_impacts.setdefault(owner_unit, {"causes": []})
                    cause = {"path": p_clean, "relation": "parameter", "symbol": param_id}
                    if cause not in direct_impacts[owner_unit]["causes"]:
                        direct_impacts[owner_unit]["causes"].append(cause)

        if is_metrics_path:
            matched = True
            changed_metrics: list[str] = []
            if selector:
                changed_metrics = [selector]
            elif registry_changes and "metrics" in registry_changes:
                changed_metrics = registry_changes["metrics"]
            elif isinstance(diff_content, str):
                changed_metrics = _parse_changed_keys_from_yaml_diff(diff_content)
            elif isinstance(diff_content, dict) and p_clean in diff_content:
                changed_metrics = _parse_changed_keys_from_yaml_diff(diff_content[p_clean])
            else:
                changed_metrics = list(metrics_reg.keys())

            for m_id in sorted(changed_metrics):
                m_info = metrics_reg.get(m_id, {})
                consumer_unit = m_info.get("consumer")
                if consumer_unit:
                    direct_impacts.setdefault(consumer_unit, {"causes": []})
                    cause = {
                        "path": p_clean,
                        "relation": "metric_measurement",
                        "symbol": m_id,
                        "class": "measurement impact",
                    }
                    if cause not in direct_impacts[consumer_unit]["causes"]:
                        direct_impacts[consumer_unit]["causes"].append(cause)

        if is_notation_path:
            matched = True
            changed_symbols: list[str] = []
            if selector:
                changed_symbols = [selector]
            elif registry_changes and "notation" in registry_changes:
                changed_symbols = registry_changes["notation"]
            elif isinstance(diff_content, str):
                changed_symbols = _parse_changed_keys_from_yaml_diff(diff_content)
            elif isinstance(diff_content, dict) and p_clean in diff_content:
                changed_symbols = _parse_changed_keys_from_yaml_diff(diff_content[p_clean])
            else:
                changed_symbols = list(notation_reg.keys())

            notation_symbols_changed.update(changed_symbols)

        if not matched:
            unmapped_changes.append(raw_p)

    for u in direct_impacts:
        direct_impacts[u]["causes"].sort(
            key=lambda c: (c.get("path", ""), c.get("relation", ""), c.get("symbol", ""))
        )

    propagating_seeds: set[str] = set()
    for u, data in direct_impacts.items():
        for c in data["causes"]:
            rel = c.get("relation")
            if rel and PROPAGATION_POLICY.get(rel, (False, False))[1]:
                propagating_seeds.add(u)
                break

    transitive_impacts: dict[str, dict[str, Any]] = {}
    direct_unit_set = set(direct_impacts.keys())

    queue: deque[tuple[str, int]] = deque((u, 1) for u in sorted(propagating_seeds))
    visited_units: set[str] = set(direct_unit_set)

    while queue:
        curr, depth = queue.popleft()
        for child in dependents_graph.get(curr, []):
            if child in direct_unit_set:
                continue
            if child not in transitive_impacts:
                transitive_impacts[child] = {
                    "depth": depth,
                    "via": [curr],
                }
                visited_units.add(child)
                queue.append((child, depth + 1))
            else:
                if transitive_impacts[child]["depth"] == depth:
                    if curr not in transitive_impacts[child]["via"]:
                        transitive_impacts[child]["via"].append(curr)
                        transitive_impacts[child]["via"].sort()

    review_required: list[dict[str, str]] = []
    changed_path_set = set(cleaned_paths)

    for u in sorted(direct_impacts.keys()):
        u_info = units_data.get(u, {})
        u_docs = set(u_info.get("canonical_docs", []))
        u_design = set(u_info.get("design", []))
        u_adrs = set(u_info.get("adrs", []))

        causes = direct_impacts[u]["causes"]
        has_impl_change = any(c.get("relation") == "implementation" for c in causes)
        has_design_change = any(c.get("relation") == "design" for c in causes)
        has_adr_change = any(c.get("relation") == "adr" for c in causes)
        has_param_change = any(c.get("relation") == "parameter" for c in causes)
        has_metric_change = any(c.get("relation") == "metric_measurement" for c in causes)
        has_comp_change = any(c.get("relation") == "component_registry" for c in causes)

        if has_impl_change:
            doc_or_design_changed = bool((u_docs | u_design | u_adrs) & changed_path_set)
            if not doc_or_design_changed:
                review_required.append(
                    {"unit": u, "reason": ChangeReason.IMPLEMENTATION_CHANGED.value}
                )
        elif has_design_change:
            if not (u_docs & changed_path_set):
                review_required.append({"unit": u, "reason": ChangeReason.DESIGN_CHANGED.value})
        elif has_adr_change:
            if not (u_docs & changed_path_set):
                review_required.append({"unit": u, "reason": ChangeReason.ADR_CHANGED.value})
        elif has_comp_change:
            review_required.append({"unit": u, "reason": ChangeReason.CANONICAL_DOC_CHANGED.value})
        elif has_param_change:
            review_required.append({"unit": u, "reason": ChangeReason.PARAMETER_CHANGED.value})
        elif has_metric_change:
            review_required.append({"unit": u, "reason": ChangeReason.METRIC_CHANGED.value})

    all_affected_units = sorted(set(direct_impacts.keys()) | set(transitive_impacts.keys()))

    docs_to_units: dict[str, set[str]] = {}
    master_ids: set[str] = set()

    for u in all_affected_units:
        u_info = units_data.get(u, {})
        for doc in u_info.get("canonical_docs", []):
            d_clean = doc.strip()
            if d_clean:
                docs_to_units.setdefault(d_clean, set()).add(u)
        m_ids = u_info.get("master", {}).get("ids", [])
        if isinstance(m_ids, str):
            m_ids = [m_ids]
        for mid in m_ids:
            if mid.strip():
                master_ids.add(mid.strip())

    documentation_review = [
        {"path": doc, "units": sorted(docs_to_units[doc])} for doc in sorted(docs_to_units.keys())
    ]
    master_review = sorted(master_ids)

    notation_review: list[dict[str, Any]] = []
    if notation_symbols_changed:
        for sym in sorted(notation_symbols_changed):
            matching_docs = _find_symbol_in_docs(sym, sorted(all_canonical_docs), root)
            notation_review.append({"symbol": sym, "referencing_docs": matching_docs})

    stale_units: list[dict[str, Any]] = []
    reviews_basis_data = basis.get("reviews", {})
    if reviews_basis_data and base and head:
        for u in all_affected_units:
            if u in reviews_basis_data:
                review_entry = reviews_basis_data[u]
                reviewed_sha = review_entry.get("reviewed_against")
                u_info = units_data.get(u, {})
                impl_files = u_info.get("implementation", [])
                if reviewed_sha and impl_files:
                    try:
                        res = subprocess.run(
                            ["git", "rev-list", f"{reviewed_sha}..{head}", "--", *impl_files],
                            cwd=root,
                            check=False,
                            capture_output=True,
                            text=True,
                        )
                        if res.returncode == 0 and res.stdout.strip():
                            stale_units.append(
                                {
                                    "unit": u,
                                    "reviewed_against": reviewed_sha,
                                    "superseded_by": head,
                                    "reason": ChangeReason.REVIEW_BASIS_OUTDATED.value,
                                }
                            )
                    except OSError:
                        pass
    elif reviews_basis_data:
        for u, entry in sorted(reviews_basis_data.items()):
            if entry.get("status") == "STALE" or entry.get("stale"):
                stale_units.append(
                    {
                        "unit": u,
                        "reviewed_against": entry.get("reviewed_against", "unknown"),
                        "reason": ChangeReason.REVIEW_BASIS_OUTDATED.value,
                    }
                )

    false_positive_risks: list[dict[str, Any]] = []
    for u, trans in sorted(transitive_impacts.items()):
        if trans["depth"] >= 3:
            false_positive_risks.append(
                {"unit": u, "depth": trans["depth"], "risk": "deep transitive distance"}
            )

    high_fanout_units: list[dict[str, Any]] = []
    for u in all_affected_units:
        fanout = len(dependents_graph.get(u, []))
        if fanout >= 3:
            high_fanout_units.append({"unit": u, "fanout": fanout})

    units_without_canonical_docs: list[str] = [
        u for u in all_affected_units if not units_data.get(u, {}).get("canonical_docs")
    ]
    undetermined_staleness_units: list[str] = [
        u for u in all_affected_units if u not in reviews_basis_data
    ]

    direct_impacts_sorted = {u: direct_impacts[u] for u in sorted(direct_impacts.keys())}
    transitive_impacts_sorted = {
        u: transitive_impacts[u] for u in sorted(transitive_impacts.keys())
    }

    report: dict[str, Any] = {
        "schema_version": 1,
        "diff": {"base": base, "head": head} if (base or head) else None,
        "changed_paths": [{"path": p, "status": "modified"} for p in cleaned_paths],
        "direct_impacts": direct_impacts_sorted,
        "transitive_impacts": transitive_impacts_sorted,
        "review_required": sorted(review_required, key=lambda x: (x["unit"], x["reason"])),
        "documentation_review": documentation_review,
        "master_review": master_review,
        "unmapped_changes": sorted(unmapped_changes),
        "stale_units": sorted(stale_units, key=lambda x: x["unit"]),
        "diagnostics": {
            "false_positive_risks": sorted(false_positive_risks, key=lambda x: x["unit"]),
            "high_fanout_units": sorted(high_fanout_units, key=lambda x: x["unit"]),
            "notation_review": notation_review,
            "undetermined_staleness_units": sorted(undetermined_staleness_units),
            "units_without_canonical_docs": sorted(units_without_canonical_docs),
        },
        "summary": {
            "changed_paths": len(cleaned_paths),
            "directly_impacted_units": len(direct_impacts_sorted),
            "transitive_units": len(transitive_impacts_sorted),
            "docs_requiring_review": len(documentation_review),
            "sym_ids_requiring_review": len(master_review),
            "unmapped_changed_paths": len(unmapped_changes),
            "objectively_stale_units": len(stale_units),
        },
    }

    if notation_symbols_changed:
        report["formal_review_required"] = True

    return report


def format_summary_table(report: dict[str, Any]) -> str:
    """Format standard markdown deliverable summary table."""
    s = report.get("summary", {})
    lines = [
        "| Surface | Count |",
        "|---|---:|",
        f"| changed paths | {s.get('changed_paths', 0)} |",
        f"| directly impacted units | {s.get('directly_impacted_units', 0)} |",
        f"| transitive units | {s.get('transitive_units', 0)} |",
        f"| docs requiring review | {s.get('docs_requiring_review', 0)} |",
        f"| SYM IDs requiring review | {s.get('sym_ids_requiring_review', 0)} |",
        f"| unmapped changed paths | {s.get('unmapped_changed_paths', 0)} |",
        f"| objectively stale units | {s.get('objectively_stale_units', 0)} |",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Deterministic Documentation Impact & Staleness Analyzer"
    )
    parser.add_argument(
        "--paths",
        nargs="+",
        help="List of changed file paths to evaluate.",
    )
    parser.add_argument("--base", help="Git base commit SHA.")
    parser.add_argument("--head", help="Git head commit SHA.")
    parser.add_argument(
        "--range",
        dest="commit_range",
        help="Git commit range, e.g. <base>..<head>.",
    )
    parser.add_argument(
        "--format",
        choices=["yaml", "json", "summary"],
        default="yaml",
        help="Output format (default: yaml).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path to write report output.",
    )

    args = parser.parse_args(argv)

    paths: list[str] = []
    base_sha: str | None = args.base
    head_sha: str | None = args.head

    if args.commit_range:
        if ".." in args.commit_range:
            parts = args.commit_range.split("..", 1)
            base_sha, head_sha = parts[0], parts[1]
        else:
            parser.error("--range must be in <sha1>..<sha2> format")

    if base_sha and head_sha:
        paths = changed_paths_between(base_sha, head_sha)
    elif args.paths:
        paths = args.paths
    else:
        # Fallback to unstaged and staged changes in repository
        try:
            res = subprocess.run(
                ["git", "diff", "--name-only", "HEAD"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            paths = list(filter(None, res.stdout.splitlines()))
        except OSError:
            parser.error("No paths or git commit range provided.")

    report = analyze_changes(
        paths=paths,
        base=base_sha,
        head=head_sha,
    )

    if args.format == "json":
        output = json.dumps(report, indent=2, sort_keys=True)
    elif args.format == "summary":
        output = format_summary_table(report)
    else:
        output = yaml.dump(report, sort_keys=False, allow_unicode=True)

    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())

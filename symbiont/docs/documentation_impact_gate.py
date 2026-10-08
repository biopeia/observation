#!/usr/bin/env python3
"""Deterministic documentation impact enforcement gate (P7).

Converts P4 (canonical integrity), P5 (impact & staleness sensor), and
P6 (Master projection capability) facts into an automated CI enforcement
gate with closed vocabulary, fail-closed validation, and anti-gaming rules.

Gate Outcomes:
  PASS
  REVIEW_REQUIRED
  BLOCK

Closed Dispositions:
  documentation_updated
  registry_updated
  no_semantic_change
  coverage_update_required
  deferred_with_tracking
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
import tomllib
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = ROOT / "symbiont/docs"
if str(DOCS_DIR) not in sys.path:
    sys.path.insert(0, str(DOCS_DIR))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import canonical_impact  # noqa: E402
from master_projection import build_master_projection  # noqa: E402


class GateOutcome(str, Enum):
    PASS = "PASS"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCK = "BLOCK"


class Disposition(str, Enum):
    DOCUMENTATION_UPDATED = "documentation_updated"
    REGISTRY_UPDATED = "registry_updated"
    NO_SEMANTIC_CHANGE = "no_semantic_change"
    COVERAGE_UPDATE_REQUIRED = "coverage_update_required"
    DEFERRED_WITH_TRACKING = "deferred_with_tracking"


ALLOWED_DISPOSITIONS = frozenset(d.value for d in Disposition)


class PathSurfaceClassification(str, Enum):
    PRODUCTION = "PRODUCTION"
    TEST = "TEST"
    DOCS = "DOCS"
    INFRASTRUCTURE = "INFRASTRUCTURE"


# Surfaces in docs/governance/change-surfaces.toml that represent production runtime
# that MUST be registered in the canonical coverage graph.
PRODUCTION_SURFACE_IDS = frozenset(
    {
        "organism-causal-runtime",
        "physics3d-causal-engine",
        "private-model-lifecycle",
        "reembodiment",
    }
)

TEST_SURFACE_IDS = frozenset(
    {
        "domain-test-suites",
        "scientific-evidence-tests",
        "governance-tests",
    }
)

DOCS_SURFACE_IDS = frozenset(
    {
        "domain-docs",
        "architectural-decisions",
        "scientific-direction",
        "project-roadmap",
        "scientific-protocol",
    }
)


@dataclass
class ReviewStatus:
    unit: str
    reason: str
    causes: list[dict[str, Any]] = field(default_factory=list)
    canonical_docs: list[str] = field(default_factory=list)
    resolved: bool = False
    disposition: str | None = None
    rationale: str | None = None
    tracking_ref: str | None = None
    resolution_details: str | None = None
    error: str | None = None


@dataclass
class GateReport:
    outcome: GateOutcome
    direct_impacts_count: int
    transitive_impacts_count: int
    review_required_count: int
    resolved_count: int
    unresolved_count: int
    stale_units_count: int
    canonical_integrity: str
    master_projection: str
    unmapped_production_paths: list[str] = field(default_factory=list)
    unmapped_other_paths: list[str] = field(default_factory=list)
    reviews: list[ReviewStatus] = field(default_factory=list)
    transitive_units: list[dict[str, Any]] = field(default_factory=list)
    stale_units: list[dict[str, Any]] = field(default_factory=list)
    diagnostics: dict[str, Any] = field(default_factory=dict)
    block_reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["outcome"] = self.outcome.value
        return data


def classify_unmapped_path(path: str, repo_root: Path = ROOT) -> PathSurfaceClassification:
    """Classify an unmapped path against governance change surfaces."""
    surfaces_file = repo_root / "docs/governance/change-surfaces.toml"
    surfaces_data: dict[str, Any] = {}
    if surfaces_file.is_file():
        try:
            surfaces_data = tomllib.loads(surfaces_file.read_text(encoding="utf-8"))
        except Exception:
            surfaces_data = {}

    surfaces = surfaces_data.get("surface", [])

    matched_surface_ids: list[str] = []
    for s in surfaces:
        s_id = s.get("id", "")
        for pattern in s.get("paths", []):
            if fnmatch.fnmatchcase(path, pattern):
                matched_surface_ids.append(s_id)
                break

    # 1. Check production surfaces
    for s_id in matched_surface_ids:
        if s_id in PRODUCTION_SURFACE_IDS:
            return PathSurfaceClassification.PRODUCTION

    # Secondary check: paths under production source packages
    if any(
        path.startswith(f"{prefix}/src/")
        for prefix in ("symbiont", "embodiment", "modality", "environment", "lab")
    ):
        # Exclude known presentation/tooling subpackages
        if not path.startswith("lab/src/lab/observatory/") and not path.startswith(
            "lab/src/lab/workbench/"
        ):
            return PathSurfaceClassification.PRODUCTION

    # 2. Check test surfaces
    for s_id in matched_surface_ids:
        if s_id in TEST_SURFACE_IDS:
            return PathSurfaceClassification.TEST
    if "/tests/" in path or path.startswith("tests/") or path.endswith("_test.py"):
        return PathSurfaceClassification.TEST

    # 3. Check docs surfaces
    for s_id in matched_surface_ids:
        if s_id in DOCS_SURFACE_IDS:
            return PathSurfaceClassification.DOCS
    if path.endswith(".md"):
        return PathSurfaceClassification.DOCS

    # 4. Otherwise infrastructure/governance/tooling
    return PathSurfaceClassification.INFRASTRUCTURE


def parse_acknowledgements(raw_input: Any) -> list[dict[str, Any]]:
    """Parse structured PR acknowledgment metadata.

    Accepts:
      - dict with 'documentation_impact' or 'reviewed'
      - YAML string
      - PR Markdown body containing a ```yaml block with documentation_impact
      - Path to YAML/JSON file
    """
    if raw_input is None:
        return []

    if isinstance(raw_input, dict):
        if "documentation_impact" in raw_input and isinstance(
            raw_input["documentation_impact"], dict
        ):
            return list(raw_input["documentation_impact"].get("reviewed", []))
        return list(raw_input.get("reviewed", []))

    if isinstance(raw_input, Path):
        if not raw_input.is_file():
            return []
        content = raw_input.read_text(encoding="utf-8")
        return parse_acknowledgements(content)

    if isinstance(raw_input, str):
        content = raw_input.strip()
        if not content:
            return []

        # Check for ```yaml block
        match = re.search(r"```(?:ya?ml)?\s*(documentation_impact:[\s\S]*?)```", content)
        if match:
            content = match.group(1).strip()
        elif "documentation_impact:" in content:
            start_idx = content.find("documentation_impact:")
            content = content[start_idx:].strip()

        try:
            data = yaml.safe_load(content)
            if isinstance(data, dict):
                return parse_acknowledgements(data)
        except Exception:
            pass

    return []


def check_canonical_integrity(repo_root: Path = ROOT) -> tuple[bool, str]:
    """Execute P4 canonical integrity verification."""
    try:
        from tests.docs.test_canonical_references import (
            load_strict_yaml,
            test_components_canonical_alignment,
            test_coverage_dependencies_resolve,
            test_coverage_file_references_resolve,
            test_coverage_master_ids_unique_and_complete,
            test_coverage_schema_and_domain_topology,
            test_metrics_schema_and_epistemic_invariants,
            test_notation_symbols_and_invariants,
            test_parameters_ast_resolution_and_schema,
            test_strict_yaml_loading_no_duplicate_keys,
        )

        cov = load_strict_yaml(repo_root / "symbiont/docs/coverage.yaml")
        comp = load_strict_yaml(repo_root / "symbiont/docs/reference/components.yaml")
        param = load_strict_yaml(repo_root / "symbiont/docs/reference/parameters.yaml")
        met = load_strict_yaml(repo_root / "symbiont/docs/reference/metrics.yaml")
        notat = load_strict_yaml(repo_root / "symbiont/docs/reference/notation.yaml")

        test_strict_yaml_loading_no_duplicate_keys()
        test_coverage_schema_and_domain_topology(cov)
        test_coverage_file_references_resolve(cov)
        test_coverage_dependencies_resolve(cov)
        test_coverage_master_ids_unique_and_complete(cov)
        test_components_canonical_alignment(cov, comp)
        test_parameters_ast_resolution_and_schema(cov, param)
        test_metrics_schema_and_epistemic_invariants(cov, met)
        test_notation_symbols_and_invariants(notat)
        return True, "Canonical integrity verified"
    except Exception as exc:
        return False, f"P4 canonical integrity failure: {exc}"


def check_master_projection(repo_root: Path = ROOT) -> tuple[bool, str]:
    """Execute P6 master projection check."""
    try:
        build_master_projection(repo_root=repo_root)
        return True, "Master projection verified"
    except Exception as exc:
        return False, f"P6 master projection failure: {exc}"


def evaluate_documentation_gate(
    paths: list[str] | None = None,
    base: str | None = None,
    head: str | None = None,
    acknowledgements: Any = None,
    repo_root: Path = ROOT,
    enforce_direct: bool = True,
    skip_p4: bool = False,
    skip_p6: bool = False,
) -> GateReport:
    """Evaluate documentation impact enforcement gate deterministically."""
    clean_paths = sorted(set(paths or []))

    # 1. P4 Canonical Integrity Check
    p4_pass = True
    p4_err = ""
    if not skip_p4:
        p4_pass, p4_err = check_canonical_integrity(repo_root)

    # 2. P6 Master Projection Check
    p6_pass = True
    p6_err = ""
    if not skip_p6:
        p6_pass, p6_err = check_master_projection(repo_root)

    # 3. P5 Impact Sensor
    try:
        impact_report = canonical_impact.analyze_changes(
            paths=clean_paths,
            base=base,
            head=head,
            repo_root=repo_root,
        )
    except Exception as exc:
        return GateReport(
            outcome=GateOutcome.BLOCK,
            direct_impacts_count=0,
            transitive_impacts_count=0,
            review_required_count=0,
            resolved_count=0,
            unresolved_count=0,
            stale_units_count=0,
            canonical_integrity="PASS" if p4_pass else "FAIL",
            master_projection="PASS" if p6_pass else "FAIL",
            block_reasons=[f"P5 canonical impact analyzer internal failure: {exc}"],
        )

    direct_impacts = impact_report.get("direct_impacts", {})
    transitive_impacts = impact_report.get("transitive_impacts", {})
    stale_units = impact_report.get("stale_units", [])
    raw_unmapped = impact_report.get("unmapped_changes", [])
    diagnostics = impact_report.get("diagnostics", {})

    # Load canonical coverage to resolve units metadata
    cov_path = repo_root / "symbiont/docs/coverage.yaml"
    units_data: dict[str, Any] = {}
    if cov_path.is_file():
        try:
            cov_raw = yaml.safe_load(cov_path.read_text(encoding="utf-8")) or {}
            units_data = cov_raw.get("units", {})
        except Exception:
            pass

    # Load reference components, parameters, metrics to assist registry mapping
    ref_dir = repo_root / "symbiont/docs/reference"
    components_reg: dict[str, Any] = {}
    parameters_reg: dict[str, Any] = {}
    metrics_reg: dict[str, Any] = {}
    if ref_dir.is_dir():
        c_p = ref_dir / "components.yaml"
        if c_p.is_file():
            try:
                components_reg = yaml.safe_load(c_p.read_text(encoding="utf-8")) or {}
            except Exception:
                pass
        p_p = ref_dir / "parameters.yaml"
        if p_p.is_file():
            try:
                parameters_reg = yaml.safe_load(p_p.read_text(encoding="utf-8")) or {}
            except Exception:
                pass
        m_p = ref_dir / "metrics.yaml"
        if m_p.is_file():
            try:
                metrics_reg = yaml.safe_load(m_p.read_text(encoding="utf-8")) or {}
            except Exception:
                pass

    # 4. Classify unmapped paths
    unmapped_production: list[str] = []
    unmapped_other: list[str] = []
    for up in raw_unmapped:
        cat = classify_unmapped_path(up, repo_root)
        if cat == PathSurfaceClassification.PRODUCTION:
            unmapped_production.append(up)
        else:
            unmapped_other.append(up)
    unmapped_production.sort()
    unmapped_other.sort()

    # 5. Parse PR Acknowledgements
    parsed_acks = parse_acknowledgements(acknowledgements)
    acks_by_unit: dict[str, dict[str, Any]] = {}
    for entry in parsed_acks:
        u = entry.get("unit")
        if u and isinstance(u, str):
            acks_by_unit[u.strip()] = entry

    # 6. Evaluate Direct Impacts & Review Status
    reviews: list[ReviewStatus] = []
    changed_path_set = set(clean_paths)

    for unit in sorted(direct_impacts.keys()):
        u_info = units_data.get(unit, {})
        u_docs = sorted(u_info.get("canonical_docs", []))
        causes = direct_impacts[unit].get("causes", [])

        # Direct semantic changes that require documentation review are implementation, design, or ADR
        has_semantic_source_change = any(
            c.get("relation") in ("implementation", "design", "adr") for c in causes
        )
        if not has_semantic_source_change:
            continue

        # Primary reason from semantic source
        primary_cause = next(
            c for c in causes if c.get("relation") in ("implementation", "design", "adr")
        )
        primary_reason = primary_cause.get("relation", "IMPLEMENTATION").upper() + "_CHANGED"

        status = ReviewStatus(
            unit=unit,
            reason=primary_reason,
            causes=causes,
            canonical_docs=u_docs,
        )

        # Mechanism C: Structured Explicit Acknowledgement
        if unit in acks_by_unit:
            ack_entry = acks_by_unit[unit]
            disp = ack_entry.get("disposition")
            rationale = str(ack_entry.get("rationale", "")).strip()
            tracking_ref = str(ack_entry.get("tracking_ref", "")).strip()

            if disp not in ALLOWED_DISPOSITIONS:
                status.resolved = False
                status.disposition = disp
                status.error = (
                    f"Invalid disposition '{disp}'. Must be one of: {sorted(ALLOWED_DISPOSITIONS)}"
                )
            elif disp == Disposition.NO_SEMANTIC_CHANGE.value:
                if len(rationale) < 10 or rationale.lower() in (
                    "none",
                    "n/a",
                    "ok",
                    "todo",
                    "not needed",
                    "no change",
                ):
                    status.resolved = False
                    status.disposition = disp
                    status.error = (
                        "no_semantic_change requires a substantive human rationale "
                        "(minimum 10 characters)"
                    )
                else:
                    status.resolved = True
                    status.disposition = disp
                    status.rationale = rationale
                    status.resolution_details = f"Acknowledged no_semantic_change: {rationale}"
            elif disp == Disposition.DEFERRED_WITH_TRACKING.value:
                if not tracking_ref:
                    status.resolved = False
                    status.disposition = disp
                    status.error = "deferred_with_tracking requires a valid tracking reference"
                else:
                    status.resolved = True
                    status.disposition = disp
                    status.tracking_ref = tracking_ref
                    status.resolution_details = f"Deferred with tracking: {tracking_ref}"
            elif disp == Disposition.COVERAGE_UPDATE_REQUIRED.value:
                status.resolved = False
                status.disposition = disp
                status.error = "coverage_update_required blocks promotion until coverage is updated"
            elif disp == Disposition.DOCUMENTATION_UPDATED.value:
                # Explicit claim that doc was updated; verify
                matching_docs = [
                    d for d in u_docs if d in changed_path_set and not _is_empty_file(repo_root / d)
                ]
                if matching_docs:
                    status.resolved = True
                    status.disposition = disp
                    status.resolution_details = f"Verified doc update: {', '.join(matching_docs)}"
                else:
                    status.resolved = False
                    status.disposition = disp
                    status.error = (
                        "documentation_updated claimed, but no non-empty canonical doc for "
                        f"{unit} was modified"
                    )
            elif disp == Disposition.REGISTRY_UPDATED.value:
                # Explicit claim that registry was updated; verify
                matching_regs = _find_matching_registries(
                    unit, changed_path_set, components_reg, parameters_reg, metrics_reg
                )
                if matching_regs:
                    status.resolved = True
                    status.disposition = disp
                    status.resolution_details = (
                        f"Verified registry update: {', '.join(matching_regs)}"
                    )
                else:
                    status.resolved = False
                    status.disposition = disp
                    status.error = f"registry_updated claimed, but no relevant registry for {unit} was modified"

        # If not resolved by explicit acknowledgement, check mechanical satisfaction
        if not status.resolved and not status.error:
            # Mechanism A: Canonical documentation changed (anti-gaming: must not be empty)
            matching_docs = [
                d for d in u_docs if d in changed_path_set and not _is_empty_file(repo_root / d)
            ]
            if matching_docs:
                status.resolved = True
                status.disposition = Disposition.DOCUMENTATION_UPDATED.value
                status.resolution_details = (
                    f"Canonical documentation updated: {', '.join(matching_docs)}"
                )
            else:
                # Mechanism B: Relevant registry changed
                matching_regs = _find_matching_registries(
                    unit, changed_path_set, components_reg, parameters_reg, metrics_reg
                )
                if matching_regs:
                    status.resolved = True
                    status.disposition = Disposition.REGISTRY_UPDATED.value
                    status.resolution_details = (
                        f"Relevant registry updated: {', '.join(matching_regs)}"
                    )

        reviews.append(status)

    resolved_count = sum(1 for r in reviews if r.resolved)
    unresolved_count = sum(1 for r in reviews if not r.resolved)

    # 7. Collect Blocking Reasons
    block_reasons: list[str] = []

    if not p4_pass:
        block_reasons.append(p4_err)

    if not p6_pass:
        block_reasons.append(p6_err)

    if stale_units:
        stale_desc = ", ".join(s.get("unit", "") for s in stale_units)
        block_reasons.append(f"Objectively stale canonical units verified: {stale_desc}")

    if unmapped_production:
        block_reasons.append(
            f"Unmapped production paths requiring canonical coverage: {', '.join(unmapped_production)}"
        )

    if unresolved_count > 0:
        for r in reviews:
            if not r.resolved:
                cause_paths = [c.get("path", "") for c in r.causes if c.get("path")]
                paths_str = "\n    ".join(cause_paths) if cause_paths else "unknown"
                docs_str = "\n    ".join(r.canonical_docs) if r.canonical_docs else "none declared"
                reason_detail = (
                    f"{r.unit}\n"
                    f"  reason: {r.reason}\n"
                    f"  changed path:\n    {paths_str}\n"
                    f"  affected canonical docs:\n    {docs_str}\n"
                    f"  required:\n"
                    f"    update a relevant canonical source\n"
                    f"    OR record an explicit no_semantic_change disposition"
                )
                if r.error:
                    reason_detail += f"\n  disposition error: {r.error}"
                block_reasons.append(reason_detail)

    # 8. Determine Overall Outcome
    if not p4_pass or not p6_pass or stale_units or unmapped_production:
        outcome = GateOutcome.BLOCK
    elif unresolved_count > 0:
        outcome = GateOutcome.BLOCK if enforce_direct else GateOutcome.REVIEW_REQUIRED
    else:
        outcome = GateOutcome.PASS

    # Transitive units list
    transitive_list = [
        {"unit": u, "depth": data.get("depth", 1), "via": data.get("via", [])}
        for u, data in sorted(transitive_impacts.items())
    ]

    return GateReport(
        outcome=outcome,
        direct_impacts_count=len(direct_impacts),
        transitive_impacts_count=len(transitive_impacts),
        review_required_count=len(reviews),
        resolved_count=resolved_count,
        unresolved_count=unresolved_count,
        stale_units_count=len(stale_units),
        canonical_integrity="PASS" if p4_pass else "FAIL",
        master_projection="PASS" if p6_pass else "FAIL",
        unmapped_production_paths=unmapped_production,
        unmapped_other_paths=unmapped_other,
        reviews=reviews,
        transitive_units=transitive_list,
        stale_units=stale_units,
        diagnostics=diagnostics,
        block_reasons=block_reasons,
    )


def _is_empty_file(path: Path) -> bool:
    """Anti-gaming: check if file is non-existent, 0 bytes, or whitespace only."""
    if not path.is_file():
        return False
    try:
        content = path.read_text(encoding="utf-8", errors="replace").strip()
        return len(content) == 0
    except Exception:
        return False


def _find_matching_registries(
    unit: str,
    changed_paths: set[str],
    components_reg: dict[str, Any],
    parameters_reg: dict[str, Any],
    metrics_reg: dict[str, Any],
) -> list[str]:
    """Anti-gaming: only count registries where the unit is explicitly represented."""
    matches: list[str] = []

    # coverage.yaml
    if "symbiont/docs/coverage.yaml" in changed_paths:
        matches.append("symbiont/docs/coverage.yaml")

    # components.yaml: unit must be defined in components via coverage_unit
    if "symbiont/docs/reference/components.yaml" in changed_paths:
        comps = components_reg.get("components", {})
        for cid, cdata in comps.items():
            if cdata.get("coverage_unit") == unit or cid == unit:
                matches.append("symbiont/docs/reference/components.yaml")
                break

    # parameters.yaml: unit must own a parameter
    if "symbiont/docs/reference/parameters.yaml" in changed_paths:
        params = parameters_reg.get("parameters", {})
        for p_name, p_data in params.items():
            if p_data.get("owner") == unit:
                matches.append("symbiont/docs/reference/parameters.yaml")
                break

    # metrics.yaml: unit must own or consume a metric
    if "symbiont/docs/reference/metrics.yaml" in changed_paths:
        metrics = metrics_reg.get("metrics", {})
        for m_name, m_data in metrics.items():
            consumer = m_data.get("consumer")
            if consumer == unit:
                matches.append("symbiont/docs/reference/metrics.yaml")
                break

    return matches


def format_gate_report(report: GateReport) -> str:
    """Format standard human-readable and CI-compatible report."""
    lines = [
        "Documentation Impact Gate",
        "",
        f"Direct semantic impacts:       {report.direct_impacts_count}",
        f"Transitive impacts:            {report.transitive_impacts_count}",
        f"Review dispositions required:  {report.review_required_count}",
        f"Resolved:                      {report.resolved_count}",
        f"Unresolved:                    {report.unresolved_count}",
        f"Objective stale units:         {report.stale_units_count}",
        f"Canonical integrity:           {report.canonical_integrity}",
        f"Master projection:             {report.master_projection}",
        "",
        f"RESULT: {report.outcome.value}",
    ]

    if report.outcome == GateOutcome.BLOCK and report.block_reasons:
        lines.append("")
        lines.append("BLOCK DETAILS:")
        lines.append("")
        for reason in report.block_reasons:
            lines.append(reason)
            lines.append("")

    return "\n".join(lines).strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Documentation Impact Enforcement Gate (P7)",
    )
    parser.add_argument("--paths", nargs="+", help="Changed file paths to evaluate.")
    parser.add_argument("--base", help="Git base commit SHA.")
    parser.add_argument("--head", help="Git head commit SHA.")
    parser.add_argument(
        "--range",
        dest="commit_range",
        help="Git commit range, e.g. <base>..<head>.",
    )
    parser.add_argument(
        "--acknowledgements",
        help="Structured PR acknowledgement metadata (YAML string or file path).",
    )
    parser.add_argument(
        "--pr-body-file",
        type=Path,
        help="File containing PR description markdown with metadata.",
    )
    parser.add_argument(
        "--mode",
        choices=["enforce", "advisory"],
        default="enforce",
        help="Enforcement phase: enforce (P7.B, blocks unresolved) or advisory (P7.A).",
    )
    parser.add_argument(
        "--format",
        choices=["summary", "json", "yaml"],
        default="summary",
        help="Output format.",
    )
    parser.add_argument(
        "--skip-p4",
        action="store_true",
        help="Skip P4 canonical integrity check.",
    )
    parser.add_argument(
        "--skip-p6",
        action="store_true",
        help="Skip P6 master projection check.",
    )

    args = parser.parse_args(argv)

    base = args.base
    head = args.head
    if args.commit_range and ".." in args.commit_range:
        base, head = args.commit_range.split("..", 1)

    paths = args.paths
    if not paths and (base or head or not paths):
        # Auto-detect changed paths from git if not provided
        try:
            cmd = ["git", "diff", "--name-only"]
            if base and head:
                cmd.extend([f"{base}..{head}"])
            elif base:
                cmd.extend([base])
            res = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)
            if res.returncode == 0 and res.stdout.strip():
                paths = [p.strip() for p in res.stdout.splitlines() if p.strip()]
        except Exception:
            paths = []

    # Acknowledgements source
    acks_input: Any = args.acknowledgements
    if args.pr_body_file and args.pr_body_file.is_file():
        acks_input = args.pr_body_file.read_text(encoding="utf-8")

    enforce_direct = args.mode == "enforce"

    report = evaluate_documentation_gate(
        paths=paths,
        base=base,
        head=head,
        acknowledgements=acks_input,
        repo_root=ROOT,
        enforce_direct=enforce_direct,
        skip_p4=args.skip_p4,
        skip_p6=args.skip_p6,
    )

    if args.format == "json":
        print(json.dumps(report.to_dict(), indent=2))
    elif args.format == "yaml":
        print(yaml.safe_dump(report.to_dict(), sort_keys=False))
    else:
        print(format_gate_report(report))

    return 0 if report.outcome == GateOutcome.PASS else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Build and adversarially verify the governed CI validation plan.

Authority and validation impact are intentionally separate:
- ``classify.assess`` decides the governance/owner boundary.
- ``validation-matrix.toml`` decides which technical lanes are causally relevant.

A SCIENTIFIC label therefore does not, by itself, expand CI into every platform or
protocol. Uncertainty in the impact mapping widens validation instead of narrowing it.
"""

from __future__ import annotations

import argparse
import fnmatch
import importlib
import json
import subprocess
import sys
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

classify = importlib.import_module("governance.classify")
ChangeClass = classify.ChangeClass
assess = classify.assess

KNOWN_LANES = frozenset(
    {
        "docs",
        "governance",
        "software_core",
        "world",
        "observatory",
        "architecture_integrity",
        "runtime_contracts",
        "experiment_mechanics",
        "canonical_full",
        "physics3d",
        "modeling",
        "python_compat",
        "host_portability",
        "alpine",
        "protocol_mechanics",
        "performance",
    }
)
BEHAVIORAL_LANES = KNOWN_LANES - {"docs", "governance", "performance"}
DEFAULT_BUDGET_SECONDS = {
    ChangeClass.ORDINARY: 120,
    ChangeClass.SCIENTIFIC: 240,
    ChangeClass.CONSTITUTIONAL: 600,
    ChangeClass.FROZEN: 0,
}


@dataclass(frozen=True)
class CIPlan:
    classification: str
    code_quality: bool
    docs: bool
    governance: bool
    software_core: bool
    world: bool
    observatory: bool
    architecture_integrity: bool
    runtime_contracts: bool
    experiment_mechanics: bool
    canonical_full: bool
    physics3d: bool
    modeling: bool
    python_compat: bool
    host_portability: bool
    alpine: bool
    protocol_mechanics: bool
    performance: bool
    budget_seconds: int
    changed_paths: tuple[str, ...]
    matrix_sections: tuple[str, ...]
    selected_lanes: tuple[str, ...]
    reasons: tuple[str, ...]


def _git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def _load_matrix_at(base: str) -> dict:
    raw = _git("show", f"{base}:docs/governance/validation-matrix.toml")
    return tomllib.loads(raw)


def _matches(path: str, pattern: str) -> bool:
    return fnmatch.fnmatchcase(path, pattern)


def _sections_for_path(matrix: dict, path: str) -> list[str]:
    matched = [
        name
        for name, section in matrix.items()
        if name not in {"schema_version", "validation_budget"}
        and isinstance(section, dict)
        and any(_matches(path, pattern) for pattern in section.get("paths", []))
    ]
    # [tests] is deliberately broad. Prefer explicit ownership when present.
    if len(matched) > 1 and "tests" in matched:
        matched.remove("tests")
    return matched


def _selected_matrix_sections(base: str, paths: tuple[str, ...]) -> tuple[str, ...]:
    matrix = _load_matrix_at(base)
    selected: list[str] = []
    for path in paths:
        for name in _sections_for_path(matrix, path):
            if name not in selected:
                selected.append(name)
    return tuple(selected)


def _lanes_for_sections(base: str, sections: tuple[str, ...]) -> set[str]:
    matrix = _load_matrix_at(base)
    lanes: set[str] = set()
    for name in sections:
        section = matrix.get(name, {})
        lanes.update(str(item) for item in section.get("ci_lanes", []))
    unknown = lanes - KNOWN_LANES
    if unknown:
        raise RuntimeError(f"validation matrix declares unknown CI lanes: {sorted(unknown)}")
    return lanes


def _budget_for(base: str, classification: ChangeClass) -> int:
    matrix = _load_matrix_at(base)
    configured = matrix.get("validation_budget", {})
    raw = configured.get(str(classification)) if isinstance(configured, dict) else None
    if raw is None:
        return DEFAULT_BUDGET_SECONDS[classification]
    return int(raw)


def _is_markdown(path: str) -> bool:
    return path.endswith((".md", ".markdown"))


def _audit_plan(base: str, plan: CIPlan) -> tuple[str, ...]:
    """Adversarially look for unsafe omissions in the generated plan.

    This reviewer is deterministic on purpose. It does not add a second test suite;
    it challenges the planner's coverage and fails closed when a changed path is not
    represented by governed policy.
    """

    matrix = _load_matrix_at(base)
    findings: list[str] = []

    uncovered = [path for path in plan.changed_paths if not _sections_for_path(matrix, path)]
    if uncovered:
        findings.append("uncovered changed paths: " + ", ".join(uncovered))

    non_markdown = [path for path in plan.changed_paths if not _is_markdown(path)]
    if non_markdown and not (set(plan.selected_lanes) & BEHAVIORAL_LANES):
        findings.append(
            "non-document change has no behavioral validation lane; impact policy must widen"
        )

    control_plane = any(
        path == "scripts/agentctl.py"
        or path.startswith("scripts/governance/")
        or path.startswith(".github/workflows/")
        or path == "docs/governance/validation-matrix.toml"
        for path in plan.changed_paths
    )
    if control_plane and non_markdown and not plan.canonical_full:
        findings.append("control-plane implementation changed without canonical_full fallback")

    if plan.classification == str(ChangeClass.FROZEN):
        findings.append("FROZEN evidence reached CI planning; publication should have blocked it")

    return tuple(findings)


def build_plan(base: str, head: str) -> CIPlan:
    paths = tuple(
        line
        for line in _git("diff", "--name-only", "--diff-filter=ACMRD", base, head).splitlines()
        if line
    )
    diff_text = _git("diff", base, head)
    assessment = assess(ROOT, base, list(paths), diff_text)
    classification = assessment.classification
    sections = _selected_matrix_sections(base, paths)
    lanes = _lanes_for_sections(base, sections)

    markdown_only = bool(paths) and all(_is_markdown(path) for path in paths)
    if markdown_only:
        # Authority still comes from classification, but Markdown cannot cause a
        # behavioral lane merely because the document is scientific/constitutional.
        lanes.intersection_update({"docs", "governance"})
        lanes.add("docs")

    selected = tuple(sorted(lanes))
    plan = CIPlan(
        classification=str(classification),
        code_quality=bool(paths) and not markdown_only,
        docs="docs" in lanes,
        governance="governance" in lanes,
        software_core="software_core" in lanes,
        world="world" in lanes,
        observatory="observatory" in lanes,
        architecture_integrity="architecture_integrity" in lanes,
        runtime_contracts="runtime_contracts" in lanes,
        experiment_mechanics="experiment_mechanics" in lanes,
        canonical_full="canonical_full" in lanes,
        physics3d="physics3d" in lanes,
        modeling="modeling" in lanes,
        python_compat="python_compat" in lanes,
        host_portability="host_portability" in lanes,
        alpine="alpine" in lanes,
        protocol_mechanics="protocol_mechanics" in lanes,
        performance="performance" in lanes,
        budget_seconds=_budget_for(base, classification),
        changed_paths=paths,
        matrix_sections=sections,
        selected_lanes=selected,
        reasons=assessment.reasons,
    )

    findings = _audit_plan(base, plan)
    if findings:
        raise RuntimeError("adversarial validation-plan review failed: " + "; ".join(findings))
    return plan


def _bool(value: bool) -> str:
    return "true" if value else "false"


def emit_github_output(plan: CIPlan, output_path: Path) -> None:
    payload = asdict(plan)
    with output_path.open("a", encoding="utf-8") as handle:
        for key, value in payload.items():
            if isinstance(value, bool):
                handle.write(f"{key}={_bool(value)}\n")
            elif isinstance(value, (str, int)):
                handle.write(f"{key}={value}\n")
        handle.write("selected_lanes_json=" + json.dumps(plan.selected_lanes) + "\n")
        handle.write("changed_paths_json=" + json.dumps(plan.changed_paths) + "\n")
        handle.write("reasons_json=" + json.dumps(plan.reasons) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args()

    plan = build_plan(args.base, args.head)
    print(json.dumps(asdict(plan), indent=2, sort_keys=True))
    if args.github_output is not None:
        emit_github_output(plan, args.github_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Deterministic, conservative impact planner for ADR-0058.

Phase 0 is observe-only: this script never decides whether a CI lane passes and
never skips tests by itself. It emits the test set it would choose, together with
fallback reasons. The existing lane remains authoritative until the selector has
accumulated enough evidence to graduate.
"""

from __future__ import annotations

import argparse
import ast
import fnmatch
import json
import subprocess
import tomllib
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT / "docs" / "governance" / "test-impact-policy.toml"
SOURCE_ROOTS = (
    ROOT / "symbiont" / "src",
    ROOT / "embodiment" / "src",
    ROOT / "modality" / "src",
    ROOT / "environment" / "src",
    ROOT / "lab" / "src",
)
TEST_ROOTS = (
    ROOT / "symbiont" / "tests",
    ROOT / "embodiment" / "tests",
    ROOT / "modality" / "tests",
    ROOT / "environment" / "tests",
    ROOT / "lab" / "tests",
    ROOT / "tests",
)


@dataclass(frozen=True)
class ImpactManifest:
    schema_version: int
    mode: str
    base: str
    head: str
    changed_paths: tuple[str, ...]
    changed_modules: tuple[str, ...]
    impacted_modules: tuple[str, ...]
    selected_tests: tuple[str, ...]
    sentinels: tuple[str, ...]
    reasons: tuple[str, ...]
    fallbacks: tuple[str, ...]
    confidence: str


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


def _load_policy() -> dict:
    with POLICY_PATH.open("rb") as handle:
        return tomllib.load(handle)


def _matches(path: str, pattern: str) -> bool:
    return fnmatch.fnmatchcase(path, pattern)


def _expand_globs(patterns: list[str] | tuple[str, ...]) -> set[str]:
    matches: set[str] = set()
    for pattern in patterns:
        for path in ROOT.glob(pattern):
            if path.is_file() and path.suffix == ".py":
                matches.add(path.relative_to(ROOT).as_posix())
    return matches


def _module_for_path(path: Path) -> str | None:
    resolved = path.resolve()
    for root in SOURCE_ROOTS:
        try:
            relative = resolved.relative_to(root.resolve())
        except ValueError:
            continue
        if relative.suffix != ".py":
            return None
        parts = list(relative.with_suffix("").parts)
        if parts[-1:] == ["__init__"]:
            parts = parts[:-1]
        return ".".join(parts)
    return None


def _imports(path: Path) -> set[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError, UnicodeDecodeError):
        raise RuntimeError(f"cannot statically parse imports: {path.relative_to(ROOT)}")

    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


def _python_inventory() -> tuple[dict[str, Path], dict[str, set[str]], dict[str, set[str]]]:
    modules: dict[str, Path] = {}
    for root in SOURCE_ROOTS:
        if not root.is_dir():
            continue
        for path in root.rglob("*.py"):
            module = _module_for_path(path)
            if module:
                modules[module] = path

    reverse: dict[str, set[str]] = defaultdict(set)
    test_imports: dict[str, set[str]] = {}

    for module, path in modules.items():
        for imported in _imports(path):
            for candidate in modules:
                if imported == candidate or imported.startswith(candidate + "."):
                    reverse[candidate].add(module)

    for root in TEST_ROOTS:
        if not root.is_dir():
            continue
        for path in root.rglob("*.py"):
            rel = path.relative_to(ROOT).as_posix()
            test_imports[rel] = _imports(path)

    return modules, reverse, test_imports


def _transitive_importers(
    changed: set[str], reverse: dict[str, set[str]], max_modules: int
) -> tuple[set[str], bool]:
    impacted = set(changed)
    queue: deque[str] = deque(sorted(changed))
    exceeded = False
    while queue:
        module = queue.popleft()
        for importer in sorted(reverse.get(module, ())):
            if importer in impacted:
                continue
            impacted.add(importer)
            if len(impacted) > max_modules:
                exceeded = True
                return impacted, exceeded
            queue.append(importer)
    return impacted, exceeded


def _test_hits_modules(imports: set[str], modules: set[str]) -> bool:
    for imported in imports:
        for module in modules:
            if imported == module or imported.startswith(module + ".") or module.startswith(
                imported + "."
            ):
                return True
    return False


def _fallback_path_hit(path: str, patterns: list[str]) -> bool:
    return any(_matches(path, pattern) for pattern in patterns)


def build_manifest(base: str, head: str) -> ImpactManifest:
    policy = _load_policy()
    paths = tuple(
        line
        for line in _git("diff", "--name-only", "--diff-filter=ACMRD", base, head).splitlines()
        if line
    )
    status_lines = _git("diff", "--name-status", "--diff-filter=ACMRD", base, head).splitlines()
    max_modules = int(policy.get("max_impacted_modules", 80))

    selected: set[str] = set()
    sentinels: set[str] = set()
    reasons: list[str] = []
    fallbacks: list[str] = []

    fallback_cfg = policy.get("fallback", {})
    fallback_patterns = [str(item) for item in fallback_cfg.get("paths", [])]
    dynamic_tokens = [str(item) for item in fallback_cfg.get("dynamic_import_tokens", [])]

    for path in paths:
        if _fallback_path_hit(path, fallback_patterns):
            fallbacks.append(f"governed fallback surface changed: {path}")

    if any(line.startswith(("D\t", "R")) for line in status_lines):
        fallbacks.append("test/source deletion or rename requires conservative fallback")

    for mapping in policy.get("ownership", []):
        source = str(mapping.get("source", ""))
        if source and any(_matches(path, source) for path in paths):
            owned = _expand_globs([str(item) for item in mapping.get("tests", [])])
            selected.update(owned)
            reasons.append(f"direct ownership: {source}")

    for guard in policy.get("semantic_guard", []):
        guard_paths = [str(item) for item in guard.get("paths", [])]
        if any(any(_matches(path, pattern) for pattern in guard_paths) for path in paths):
            guard_tests = _expand_globs([str(item) for item in guard.get("tests", [])])
            selected.update(guard_tests)
            sentinels.update(guard_tests)
            reasons.append(f"semantic guard: {guard.get('id', 'unnamed')}")

    modules, reverse, test_imports = _python_inventory()
    changed_modules: set[str] = set()
    for raw in paths:
        path = ROOT / raw
        if raw.endswith(".py") and path.is_file():
            module = _module_for_path(path)
            if module:
                changed_modules.add(module)
                text = path.read_text(encoding="utf-8", errors="replace")
                if any(token in text for token in dynamic_tokens):
                    fallbacks.append(f"dynamic import/registration in changed source: {raw}")
            elif any(
                raw.startswith(root.relative_to(ROOT).as_posix() + "/") for root in SOURCE_ROOTS
            ):
                fallbacks.append(f"changed source cannot be mapped to module: {raw}")

    impacted, exceeded = _transitive_importers(changed_modules, reverse, max_modules)
    if exceeded:
        fallbacks.append(f"import impact exceeded max_impacted_modules={max_modules}")

    if impacted and not exceeded:
        for test_path, imports in test_imports.items():
            if _test_hits_modules(imports, impacted):
                selected.add(test_path)
        reasons.append("static reverse-import impact")

    changed_tests = {path for path in paths if path.endswith(".py") and "/tests/" in f"/{path}"}
    selected.update(path for path in changed_tests if (ROOT / path).is_file())
    if changed_tests:
        reasons.append("changed tests always select themselves")

    behavioral_python_change = any(
        raw.endswith(".py")
        and any(raw.startswith(root.relative_to(ROOT).as_posix() + "/") for root in SOURCE_ROOTS)
        for raw in paths
    )
    if behavioral_python_change and not selected:
        fallbacks.append("behavioral source change produced an empty selected test set")

    confidence = "LOW" if fallbacks else ("HIGH" if changed_modules else "MEDIUM")
    return ImpactManifest(
        schema_version=int(policy.get("schema_version", 1)),
        mode=str(policy.get("planner_mode", "observe-only")),
        base=base,
        head=head,
        changed_paths=paths,
        changed_modules=tuple(sorted(changed_modules)),
        impacted_modules=tuple(sorted(impacted)),
        selected_tests=tuple(sorted(selected)),
        sentinels=tuple(sorted(sentinels)),
        reasons=tuple(dict.fromkeys(reasons)),
        fallbacks=tuple(dict.fromkeys(fallbacks)),
        confidence=confidence,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    manifest = build_manifest(args.base, args.head)
    payload = json.dumps(asdict(manifest), indent=2, sort_keys=True) + "\n"
    print(payload, end="")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

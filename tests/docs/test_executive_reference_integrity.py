# tests/docs/test_executive_reference_integrity.py
"""Mechanical integrity checks for the executive synthesis layer.

The executive documents are navigation/synthesis only. They may not mint new
SYM-* identifiers or invent component-to-component relationships absent from
the canonical component registry.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
EXECUTIVE_DIR = ROOT / "symbiont/docs/executive"
COMPONENTS_PATH = ROOT / "symbiont/docs/reference/components.yaml"

SYM_RE = re.compile(r"\bSYM-[A-Z0-9]+(?:-[A-Z0-9]+)*\b")
MERMAID_BLOCK_RE = re.compile(r"```mermaid\n(.*?)\n```", re.DOTALL)
NODE_RE = re.compile(r'\b([A-Za-z][A-Za-z0-9_]*)\["(SYM-[A-Z0-9-]+):[^"]*"\]')
EDGE_RE = re.compile(r"^\s*([A-Za-z][A-Za-z0-9_]*)[^-\n]*-->\s*([A-Za-z][A-Za-z0-9_]*)", re.MULTILINE)


def _components() -> dict[str, dict]:
    with COMPONENTS_PATH.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)["components"]


def test_executive_sym_ids_resolve_to_canonical_components() -> None:
    """Every concrete SYM-* token in executive Markdown must exist canonically."""
    components = _components()
    valid_ids = set(components)
    errors: list[str] = []

    for path in sorted(EXECUTIVE_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        for match in SYM_RE.finditer(text):
            sym_id = match.group(0)
            if sym_id not in valid_ids:
                line = text.count("\n", 0, match.start()) + 1
                errors.append(f"{path.relative_to(ROOT)}:{line}: unknown canonical ID {sym_id}")

    assert not errors, "\n".join(errors)


def test_executive_mermaid_edges_are_registry_declared_consumer_relations() -> None:
    """Component edges in executive Mermaid views must be direct registry relations."""
    components = _components()
    sym_to_unit = {sym_id: entry["coverage_unit"] for sym_id, entry in components.items()}

    overview = (EXECUTIVE_DIR / "overview.md").read_text(encoding="utf-8")
    blocks = MERMAID_BLOCK_RE.findall(overview)
    assert blocks, "Executive overview must contain a traceable Mermaid relationship view"

    errors: list[str] = []
    for block in blocks:
        aliases = {alias: sym_id for alias, sym_id in NODE_RE.findall(block)}
        for src_alias, dst_alias in EDGE_RE.findall(block):
            # Only validate edges between canonical component nodes. External visual
            # nodes, if introduced later, are deliberately outside this rule.
            if src_alias not in aliases or dst_alias not in aliases:
                continue
            src_sym = aliases[src_alias]
            dst_sym = aliases[dst_alias]
            src_entry = components[src_sym]
            dst_unit = sym_to_unit[dst_sym]
            if dst_unit not in src_entry.get("consumers", []):
                errors.append(
                    f"{src_sym} -> {dst_sym} is not declared by "
                    f"{src_sym}.consumers (expected {dst_unit})"
                )

    assert not errors, "\n".join(errors)

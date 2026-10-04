from __future__ import annotations

import ast
from pathlib import Path


def test_runtime_and_core_cognition_use_canonical_genome_type() -> None:
    root = Path(__file__).resolve().parents[2]
    paths = (
        root / "symbiont" / "src" / "symbiont" / "core" / "orchestration" / "runtime.py",
        root / "symbiont" / "src" / "symbiont" / "core" / "cognition" / "bridge.py",
        root / "symbiont" / "src" / "symbiont" / "core" / "orchestration" / "individual.py",
    )
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports = [node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
        assert not any(module.endswith("cognition.genome") for module in imports)
        assert "SymbiontGenome" not in path.read_text(encoding="utf-8")

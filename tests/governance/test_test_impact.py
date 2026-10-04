from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from governance import test_impact


def test_transitive_importers_walk_reverse_graph() -> None:
    reverse = {
        "a": {"b", "c"},
        "b": {"d"},
        "c": set(),
        "d": set(),
    }
    impacted, exceeded = test_impact._transitive_importers({"a"}, reverse, 10)
    assert impacted == {"a", "b", "c", "d"}
    assert not exceeded


def test_transitive_importers_fall_back_when_breadth_exceeded() -> None:
    reverse = {"a": {"b", "c"}, "b": {"d"}, "c": set(), "d": set()}
    impacted, exceeded = test_impact._transitive_importers({"a"}, reverse, 2)
    assert exceeded
    assert len(impacted) > 2


def test_test_hits_impacted_module_prefixes() -> None:
    assert test_impact._test_hits_modules(
        {"symbiont.core.runtime", "pytest"}, {"symbiont.core"}
    )
    assert not test_impact._test_hits_modules({"pytest"}, {"symbiont.core"})


def test_module_for_path_under_domain_source_root() -> None:
    path = ROOT / "symbiont" / "src" / "symbiont" / "core" / "__init__.py"
    assert test_impact._module_for_path(path) == "symbiont.core"


def test_fallback_path_hit_is_fail_closed() -> None:
    patterns = ["scripts/governance/test_impact.py", "**/conftest.py"]
    assert test_impact._fallback_path_hit("scripts/governance/test_impact.py", patterns)
    assert test_impact._fallback_path_hit("lab/tests/conftest.py", patterns)
    assert not test_impact._fallback_path_hit("symbiont/src/symbiont/core/runtime.py", patterns)

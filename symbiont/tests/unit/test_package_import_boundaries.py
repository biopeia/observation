"""Leaf imports must not depend on eager initialization of the core facade."""

from __future__ import annotations

import subprocess
import sys

import pytest


@pytest.mark.parametrize(
    "module",
    ("symbiont.cognition.checkpoint", "symbiont.host.acclimation"),
)
def test_leaf_module_import_does_not_initialize_core_facade(module: str) -> None:
    source = (
        "import importlib, sys; "
        f"importlib.import_module({module!r}); "
        "assert 'symbiont.core' not in sys.modules"
    )
    result = subprocess.run(
        [sys.executable, "-c", source],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr


def test_core_facade_remains_available_on_demand() -> None:
    source = "from symbiont import core; from symbiont.core import OrganismRuntime; assert core.OrganismRuntime is OrganismRuntime"
    result = subprocess.run(
        [sys.executable, "-c", source],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr


def test_removed_compatibility_surfaces_are_not_importable() -> None:
    source = """
import importlib.util
import symbiont.core as core
import symbiont.core.regulation as regulation
for module in (
    'symbiont.core.foundation.limits',
    'symbiont.core.foundation.epistemic',
    'symbiont.core.lineage.germline',
):
    assert importlib.util.find_spec(module) is None, module
for name in ('SymbiontGenome', 'LocusSpec', 'LocusType'):
    assert not hasattr(core, name), name
assert not hasattr(regulation, 'PhenotypicRegulationState')
from symbiont.genetics import Genome, create_standard_genome
assert isinstance(create_standard_genome('canonical'), Genome)
"""
    result = subprocess.run(
        [sys.executable, "-c", source],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr

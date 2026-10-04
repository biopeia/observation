"""Every registered experiment id is unique and resolvable in the study index."""

from __future__ import annotations

import tomllib
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / "lab" / "research" / "STUDY-INDEX.md"


def _experiments() -> list[tuple[Path, dict]]:
    found = []
    for path in sorted((ROOT / "lab" / "experiments").rglob("experiment.toml")):
        experiment = tomllib.loads(path.read_text(encoding="utf-8")).get("experiment", {})
        if "id" in experiment:
            found.append((path.relative_to(ROOT), experiment))
    return found


def test_experiment_ids_are_unique() -> None:
    counts = Counter(experiment["id"] for _, experiment in _experiments())
    assert counts, "no experiment.toml with an [experiment] id was found"
    assert not {key: n for key, n in counts.items() if n > 1}


def test_every_experiment_id_is_in_the_study_index() -> None:
    index = INDEX.read_text(encoding="utf-8")
    missing = [
        str(path)
        for path, experiment in _experiments()
        if f"`{experiment['id']}`" not in index and f"`{experiment.get('protocol')}`" not in index
    ]
    assert not missing, f"add these studies to {INDEX.relative_to(ROOT)}: {missing}"

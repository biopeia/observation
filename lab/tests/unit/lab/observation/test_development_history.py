from __future__ import annotations

import json
from pathlib import Path

from lab.observation.development_history import build_development_history
from lab.physics3d.telemetry.v41 import TelemetryV41Writer


def _state(tick: int, organism_id: str, *, concepts: int) -> dict:
    nodes = [
        {"node_id": "sense.a", "kind": "sense", "bias": 0.0, "tau": 1.0},
        {"node_id": "predictor.a", "kind": "predictor", "bias": 0.0, "tau": 1.0},
    ]
    nodes.extend(
        {"node_id": f"concept.{index}", "kind": "concept", "bias": 0.0, "tau": 1.0}
        for index in range(concepts)
    )
    return {
        "schema_version": 3,
        "tick": tick,
        "organism_id": organism_id,
        "runtime": {"percepts": [], "narrative": []},
        "cognition": {
            "activations": {},
            "readouts": {},
            "prediction_errors": [],
            "topology_revision": concepts,
        },
        "cognitive_topology": {
            "nodes": nodes,
            "edges": [
                {
                    "source_id": "sense.a",
                    "target_id": "predictor.a",
                    "kind": "excitatory",
                    "weight": 0.1,
                    "plasticity": 0.0,
                    "delay_ticks": 0,
                    "support": tick,
                    "age_ticks": tick,
                    "stable_ticks": tick,
                    "last_use_tick": tick,
                }
            ],
        },
        "body_schema": {
            "parts": [{"part_id": "region.a", "kind": "cognitive_region"}],
            "dependencies": [{"source": "region.a", "target": "sense.a"}],
        },
    }


def _write_run(root: Path, run_id: str, organism_id: str, ticks: list[tuple[int, int]]) -> None:
    run_dir = root / run_id
    run_dir.mkdir(parents=True)
    (run_dir / "manifest.json").write_text(
        json.dumps({"run_id": run_id, "started_at": f"2026-10-05T00:00:{len(list(root.iterdir())):02d}+00:00"}),
        encoding="utf-8",
    )
    writer = TelemetryV41Writer(
        run_dir / "telemetry",
        organism_id=organism_id,
        start_tick=max(0, ticks[0][0] - 1),
        seed=42,
        physics_hz=240,
        cognition_hz=24,
        observation_hz=24,
        render_hz=60,
        embodiment_mode="new",
    )
    for tick, concepts in ticks:
        writer.append(
            {
                "tick": tick,
                "alive": True,
                "cognitive_motor_output_edges": 1,
                "schema_confidence": 0.5,
                "prediction_error": 0.25,
                "action_source": "exploration",
                "metabolic_reserve_ratio": 0.8,
                "resource_progress": 0.1,
                "sensorimotor_patterns": 2,
                "motor_competences": 1,
                "motor_competence_count": 1,
                "motor_repertoire_size": 1,
            },
            rich_state=_state(tick, organism_id, concepts=concepts),
        )
    writer.close()


def test_history_is_rebuilt_from_verified_managed_run_telemetry(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    runs.mkdir()
    _write_run(runs, "run-a", "symbiont:one", [(10, 1), (11, 2)])
    _write_run(runs, "run-b", "symbiont:one", [(20, 3)])
    _write_run(runs, "run-other", "symbiont:other", [(30, 9)])

    payload = build_development_history(runs, organism_id="symbiont:one", limit=16)

    assert payload["authority"] == "lab-physics3d-telemetry-v4.1"
    assert payload["available"] is True
    assert payload["complete"] is True
    assert [entry["run_id"] for entry in payload["coverage"]] == ["run-a", "run-b"]
    assert [(point["runId"], point["tick"]) for point in payload["points"]] == [
        ("run-a", 10),
        ("run-a", 11),
        ("run-b", 20),
    ]
    assert [point["concepts"] for point in payload["points"]] == [1, 2, 3]
    assert all(point["edges"] == 1 for point in payload["points"])
    assert payload["points"][0]["selfRegions"] == 1
    assert payload["points"][0]["selfDependencies"] == 1
    assert payload["snapshots"]
    assert all(item["runId"] in {"run-a", "run-b"} for item in payload["snapshots"])


def test_history_limit_is_longitudinal_and_browser_independent(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    runs.mkdir()
    _write_run(runs, "run-a", "symbiont:one", [(10, 1), (11, 2)])
    _write_run(runs, "run-b", "symbiont:one", [(20, 3), (21, 4)])

    first = build_development_history(runs, organism_id="symbiont:one", limit=2)
    second = build_development_history(runs, organism_id="symbiont:one", limit=2)

    assert first == second
    assert [(point["runId"], point["tick"]) for point in first["points"]] == [
        ("run-b", 20),
        ("run-b", 21),
    ]


def test_unknown_organism_does_not_inherit_another_run(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    runs.mkdir()
    _write_run(runs, "run-a", "symbiont:one", [(10, 1)])

    payload = build_development_history(runs, organism_id="symbiont:missing", limit=16)

    assert payload["available"] is False
    assert payload["points"] == []
    assert payload["snapshots"] == []

"""Executable regressions for epistemic absence and Development run boundaries."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[4]
WEB = ROOT / "lab/src/lab/workbench/web"


def _node(script: str) -> dict:
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js is required for executable Workbench regressions")
    result = subprocess.run(
        [node, "--input-type=module", "-e", script],
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_missing_alive_does_not_fabricate_active_physiology() -> None:
    derived = (WEB / "views/mind/derived.js").as_uri()
    state = (WEB / "views/mind/state.js").as_uri()
    out = _node(
        f"""
const {{currentPhysiologyState}} = await import({json.dumps(derived)});
const {{tel, snap, resetMindDataState}} = await import({json.dumps(state)});
resetMindDataState();
const absent = currentPhysiologyState();
tel.alive = true;
const alive = currentPhysiologyState();
tel.alive = false;
const dead = currentPhysiologyState();
snap.organismState = {{state:'dormant'}};
const explicit = currentPhysiologyState();
console.log(JSON.stringify({{absent, alive, dead, explicit}}));
"""
    )

    assert out == {
        "absent": "unknown",
        "alive": "active",
        "dead": "dead",
        "explicit": "dormant",
    }


def test_development_history_preserves_organism_continuity_but_segments_runs() -> None:
    history = (WEB / "views/mind/history.js").as_uri()
    state = (WEB / "views/mind/state.js").as_uri()
    out = _node(
        f"""
const store = new Map();
globalThis.window = {{localStorage: {{
  getItem: (key) => store.has(key) ? store.get(key) : null,
  setItem: (key, value) => store.set(key, String(value)),
}}}};
const {{
  activateMindDevelopmentHistory,
  recordMindHistory,
  nearestHistorySnapshot,
}} = await import({json.dumps(history)});
const {{
  mindHistory,
  milestones,
  developmentScope,
  tel,
  snap,
  streamState,
  resetMindDataState,
}} = await import({json.dumps(state)});
resetMindDataState();
activateMindDevelopmentHistory('org-1', 'run-a');
streamState.runId = 'run-a';
tel.tick = 10;
tel.cognitiveConcepts = 2;
tel.predictorCount = 3;
tel.alive = true;
snap.tick = 10;
snap.topology = {{nodes:[], edges:[]}};
recordMindHistory({{captureSnapshot:true, persist:false}});

activateMindDevelopmentHistory('org-1', 'run-b');
streamState.runId = 'run-b';
tel.tick = 11;
tel.cognitiveConcepts = 4;
tel.predictorCount = 5;
snap.tick = 11;
snap.topology = {{nodes:[], edges:[]}};
recordMindHistory({{captureSnapshot:true, persist:false}});

const a = nearestHistorySnapshot(10, 'run-a');
const b = nearestHistorySnapshot(11, 'run-b');
console.log(JSON.stringify({{
  scope: {{organismId:developmentScope.organismId, activeRunId:developmentScope.activeRunId}},
  points: mindHistory.map(x => [x.tick, x.runId]),
  milestones: milestones.map(x => [x.kind, x.runId]),
  a: a ? [a.tick, a.runId] : null,
  b: b ? [b.tick, b.runId] : null,
}}));
"""
    )

    assert out["scope"] == {"organismId": "org-1", "activeRunId": "run-b"}
    assert out["points"] == [[10, "run-a"], [11, "run-b"]]
    assert out["a"] == [10, "run-a"]
    assert out["b"] == [11, "run-b"]
    assert ["observer-attached", "run-a"] in out["milestones"]
    assert ["observer-attached", "run-b"] in out["milestones"]
    assert any(kind.startswith("run-boundary:") and run_id == "run-b" for kind, run_id in out["milestones"])

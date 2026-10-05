"""Executable regressions for Vision observation honesty and freshness."""

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


def test_observation_semantics_preserve_absence_zero_and_identity() -> None:
    semantics = (WEB / "views/shared/observation-semantics.js").as_uri()
    out = _node(
        f"""
const {{
  observedCollectionCount,
  observedFiniteNumber,
  observedTopologyCounts,
  refreshFrameCoherence,
  frameTimedOut,
}} = await import({json.dumps(semantics)});

const missingTopology = observedTopologyCounts(null, 'not_observed');
const emptyTopology = observedTopologyCounts({{nodes:[]}}, 'observed');
const topology = observedTopologyCounts({{nodes:[
  {{kind:'sense'}}, {{kind:'concept'}}, {{kind:'predictor'}}, {{kind:'readout'}},
]}}, 'observed');
const absentCollection = observedCollectionCount('not_observed', []);
const emptyCollection = observedCollectionCount('observed_empty', []);
const absentNumber = observedFiniteNumber(null);
const zeroNumber = observedFiniteNumber(0);

const state = {{
  status:'live', runId:null, organismId:'org-1', telemetryTick:20, snapshotTick:20,
  lastCoherentFrameAt:null, stale:true,
}};
const missingIdentityCoherent = refreshFrameCoherence(state, 1000);
state.runId = 'run-1';
const coherent = refreshFrameCoherence(state, 1000);
const freshAtBoundary = frameTimedOut(state, 6000, 5000);
const staleAfterBoundary = frameTimedOut(state, 6001, 5000);

console.log(JSON.stringify({{
  missingTopology, emptyTopology, topology,
  absentCollection, emptyCollection, absentNumber, zeroNumber,
  missingIdentityCoherent, coherent, lastCoherentFrameAt:state.lastCoherentFrameAt,
  freshAtBoundary, staleAfterBoundary,
}}));
"""
    )

    assert out["missingTopology"] == {
        "senses": None,
        "concepts": None,
        "predictors": None,
        "readouts": None,
    }
    assert out["emptyTopology"] == {
        "senses": 0,
        "concepts": 0,
        "predictors": 0,
        "readouts": 0,
    }
    assert out["topology"] == {
        "senses": 1,
        "concepts": 1,
        "predictors": 1,
        "readouts": 1,
    }
    assert out["absentCollection"] is None
    assert out["emptyCollection"] == 0
    assert out["absentNumber"] is None
    assert out["zeroNumber"] == 0
    assert out["missingIdentityCoherent"] is False
    assert out["coherent"] is True
    assert out["lastCoherentFrameAt"] == 1000
    assert out["freshAtBoundary"] is False
    assert out["staleAfterBoundary"] is True


def test_vision_wiring_rejects_historical_frames_and_resets_on_mount() -> None:
    source = (WEB / "views/vision.js").read_text(encoding="utf-8")

    assert "resetMindDataState();" in source
    assert source.count("if (meta.historical) return;") == 2
    assert "organismId: next.organismId ?? null" in source
    assert "bodyId: next.bodyId ?? null" in source
    assert "embodimentId: next.embodimentId ?? null" in source
    assert "Freshness" in source
    assert "observedFiniteNumber(tel.predictionError)" in source

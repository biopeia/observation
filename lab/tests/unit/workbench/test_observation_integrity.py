"""Executable regressions for Workbench observation identity and freshness.

These tests execute the ES modules with Node rather than inspecting source
strings. They cover the state transitions that previously allowed plausible but
stale values to survive run and transport boundaries.
"""

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


def test_complete_telemetry_does_not_carry_absent_or_null_values_forward() -> None:
    telemetry = (WEB / "views/mind/telemetry.js").as_uri()
    state = (WEB / "views/mind/state.js").as_uri()
    out = _node(
        f"""
const {{applyTelemetryEvent, telemetryAvailability}} = await import({json.dumps(telemetry)});
const {{tel, resetMindDataState}} = await import({json.dumps(state)});
resetMindDataState();
applyTelemetryEvent({{type:'cognition', tick:10, predictor_count:7,
  prospective_selected:true, slm_active:true, prediction_error:0.25}});
const before = {{...tel}};
applyTelemetryEvent({{type:'cognition', tick:11, predictor_count:0,
  prospective_selected:false, prediction_error:null}});
const after = {{...tel}};
const availability = {{...telemetryAvailability}};
console.log(JSON.stringify({{before, after, availability}}));
"""
    )

    assert out["before"]["predictorCount"] == 7
    assert out["before"]["prospective"] is True
    assert out["after"]["predictorCount"] == 0
    assert out["after"]["prospective"] is False
    assert out["after"]["predictionError"] is None
    # slm_active was not observed on tick 11; it is unknown now, not still true.
    assert out["after"]["slmActive"] is None
    assert out["availability"]["predictorCount"] == "observed"
    assert out["availability"]["prospective"] == "observed"
    assert out["availability"]["predictionError"] == "observed_null"
    assert out["availability"]["slmActive"] == "not_observed"


def test_snapshot_distinguishes_not_observed_null_empty_and_observed() -> None:
    snapshot = (WEB / "views/mind/snapshot.js").as_uri()
    state = (WEB / "views/mind/state.js").as_uri()
    out = _node(
        f"""
const {{applyMindSnapshot}} = await import({json.dumps(snapshot)});
const {{snap, resetMindDataState}} = await import({json.dumps(state)});
resetMindDataState();
applyMindSnapshot({{
  tick: 4,
  senses: [],
  beliefs: null,
  cognition: {{readouts: {{}}}},
  self_model: null,
}});
console.log(JSON.stringify({{
  senses: snap.senses,
  beliefs: snap.beliefs,
  availability: snap.availability,
}}));
"""
    )

    assert out["senses"] == []
    assert out["beliefs"] == []  # presentation remains type-stable
    availability = out["availability"]
    assert availability["senses"] == "observed_empty"
    assert availability["beliefs"] == "observed_null"
    assert availability["cognition"] == "observed"
    assert availability["selfModel"] == "observed_null"
    assert availability["bodySchema"] == "not_observed"
    assert availability["affordances"] == "not_observed"


def test_legacy_observer_classifications_are_adapted_once_and_removed_from_cognition() -> None:
    snapshot = (WEB / "views/mind/snapshot.js").as_uri()
    state = (WEB / "views/mind/state.js").as_uri()
    out = _node(
        f"""
const {{applyMindSnapshot}} = await import({json.dumps(snapshot)});
const {{snap, resetMindDataState}} = await import({json.dumps(state)});
resetMindDataState();
applyMindSnapshot({{
  tick: 8,
  cognition: {{
    readouts: {{motor: 0.4}},
    activationClasses: {{'concept.1': 12}},
    predictionErrors: {{'predictor.1': 'high'}},
  }},
}});
console.log(JSON.stringify({{
  cognition: snap.cognition,
  observerAnalysis: snap.observerAnalysis,
  availability: snap.availability,
}}));
"""
    )

    assert out["cognition"]["readouts"] == {"motor": 0.4}
    assert "activationClasses" not in out["cognition"]
    assert "predictionErrors" not in out["cognition"]
    assert out["observerAnalysis"]["activationClasses"] == {"concept.1": 12}
    assert out["observerAnalysis"]["predictionErrors"] == {"predictor.1": "high"}
    assert out["observerAnalysis"]["provenance"] == {
        "owner": "observer",
        "source": "legacy-cognition-adapter",
        "feedsBack": False,
    }
    assert out["availability"]["observerAnalysis"] == "observed"


def test_delta_gap_becomes_visible_and_rebase_recovers_channel() -> None:
    module = (WEB / "stream-delta.js").as_uri()
    out = _node(
        f"""
const {{LiveObservationDecoder}} = await import({json.dumps(module)});
const d = new LiveObservationDecoder();
const base = d.decode({{
  type:'observation_delta', contract:'observer-live-delta-v1', channel:'vitals',
  kind:'anchor', revision:1, state:{{type:'vitals', run_id:'r1', tick:1, alive:true}}
}});
const gap = d.decode({{
  type:'observation_delta', contract:'observer-live-delta-v1', channel:'vitals',
  kind:'delta', revision:3, base_revision:2, patch:[{{op:'set',path:'/tick',value:3}}]
}});
const gapIssue = d.takeIssue();
const recovered = d.decode({{
  type:'observation_delta', contract:'observer-live-delta-v1', channel:'vitals',
  kind:'anchor', revision:4, transport:{{rebase:'history_rotated'}},
  state:{{type:'vitals', run_id:'r1', tick:4, alive:true}}
}});
const rebaseIssue = d.takeIssue();
console.log(JSON.stringify({{base, gap, gapIssue, recovered, rebaseIssue}}));
"""
    )

    assert out["base"]["tick"] == 1
    assert out["gap"] is None
    assert out["gapIssue"]["kind"] == "gap"
    assert out["gapIssue"]["channel"] == "vitals"
    assert out["recovered"]["tick"] == 4
    assert out["rebaseIssue"]["kind"] == "rebase"
    assert out["rebaseIssue"]["reason"] == "history_rotated"


def test_mind_source_identity_changes_on_run_and_organism_but_not_body_only() -> None:
    module = (WEB / "views/mind/streams.js").as_uri()
    out = _node(
        f"""
const {{MindStreams}} = await import({json.dumps(module)});
const seen = [];
const s = new MindStreams({{onSourceState: (x) => seen.push(x)}});
s.emitSourceState('live', {{source:'physics3d', runId:'r1', organismId:'o1', bodyId:'b1', embodimentId:'e1'}});
s.emitSourceState('live', {{source:'physics3d', runId:'r2', organismId:'o1', bodyId:'b2', embodimentId:'e2'}});
s.emitSourceState('live', {{source:'physics3d', runId:'r3', organismId:'o2', bodyId:'b3', embodimentId:'e3'}});
s.emitSourceState('live', {{source:'physics3d', runId:'r3', organismId:'o2', bodyId:'b4', embodimentId:'e4'}});
console.log(JSON.stringify(seen));
"""
    )

    assert out[0]["identityChanged"] is True
    assert out[1]["identityChanged"] is True  # run changed, organism persisted
    assert out[2]["identityChanged"] is True  # organism changed
    assert out[3]["identityChanged"] is False
    assert out[3]["embodimentChanged"] is True


def test_multiple_observatory_instances_are_not_selected_by_array_order() -> None:
    module = (WEB / "views/mind/streams.js").as_uri()
    out = _node(
        f"""
const {{MindStreams}} = await import({json.dumps(module)});
const sourceStates = [];
const waiting = [];
class FakeEventSource {{
  constructor(url) {{ this.url=url; globalThis.created.push(this); }}
  close() {{ this.closed=true; }}
}}
globalThis.created = [];
globalThis.EventSource = FakeEventSource;
globalThis.fetch = async () => ({{ok:true, json:async()=>({{sources:{{observatory:{{available:true}}}}}})}});
const s = new MindStreams({{
  onSourceState: (x) => sourceStates.push(x),
  onWaiting: (visible, message) => waiting.push({{visible, message}}),
}});
s.closed = false;
await s.connectFleet();
const fleet = globalThis.created.find(x => x.url === '/fleet');
fleet.onmessage({{data:JSON.stringify({{instances:[
  {{instance_id:'i1', run_id:'r1', organism_id:'o1', liveness:'alive'}},
  {{instance_id:'i2', run_id:'r2', organism_id:'o2', liveness:'alive'}},
]}})}});
console.log(JSON.stringify({{sourceStates, waiting, created:globalThis.created.map(x=>x.url)}}));
"""
    )

    assert "/instances/i1" not in out["created"]
    assert "/instances/i2" not in out["created"]
    assert out["sourceStates"][-1]["reason"] == "multiple-live-instances"
    assert "no instance was selected automatically" in out["waiting"][-1]["message"]

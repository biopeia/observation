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


def test_mind_stream_boundary_clears_live_identity_until_new_coherent_frame() -> None:
    module = (WEB / "views/mind/streams.js").as_uri()
    out = _node(
        f"""
const {{MindStreams}} = await import({json.dumps(module)});
class FakeEventSource {{
  constructor() {{ globalThis.source = this; }}
  addEventListener(_name, callback) {{ this.onmessage = callback; }}
  close() {{ this.closed = true; }}
}}
globalThis.EventSource = FakeEventSource;
const states = [];
const waiting = [];
const stream = new MindStreams({{
  hydrateDevelopment: false,
  onSourceState: (state) => states.push({{
    status: state.status,
    source: state.source,
    runId: state.runId,
    organismId: state.organismId,
    reason: state.reason,
    identityChanged: state.identityChanged,
  }}),
  onWaiting: (visible, message) => waiting.push({{visible, message}}),
}});
stream.connectOrganism();
const send = (payload) => globalThis.source.onmessage({{data: JSON.stringify(payload)}});
send({{
  type:'observed_frame', source:'physics3d', run_id:'run-a', organism_id:'org-a', tick:10,
  body:null, cognition:null, vitals:null, mind:{{tick:10}},
}});
send({{type:'observation_boundary', phase:'begin', run_id:'run-b'}});
send({{
  type:'observed_frame', source:'physics3d', run_id:'run-b', organism_id:'org-b', tick:1,
  body:null, cognition:null, vitals:null, mind:{{tick:1}},
}});
send({{type:'observation_boundary', phase:'end', run_id:'run-b'}});
console.log(JSON.stringify({{states, waiting, localMindActive: stream.localMindActive}}));
"""
    )

    assert out["states"] == [
        {
            "status": "live",
            "source": "physics3d",
            "runId": "run-a",
            "organismId": "org-a",
            "reason": None,
            "identityChanged": True,
        },
        {
            "status": "waiting",
            "source": "physics3d",
            "runId": "run-b",
            "organismId": None,
            "reason": "run-starting",
            "identityChanged": True,
        },
        {
            "status": "live",
            "source": "physics3d",
            "runId": "run-b",
            "organismId": "org-b",
            "reason": None,
            "identityChanged": True,
        },
        {
            "status": "waiting",
            "source": None,
            "runId": None,
            "organismId": None,
            "reason": "run-ended",
            "identityChanged": True,
        },
    ]
    assert out["localMindActive"] is False
    assert "waiting for its first coherent frame" in out["waiting"][0]["message"]
    assert out["waiting"][-1] == {"visible": True, "message": "Physics3D run ended."}


def test_physical_boundary_rejects_first_sse_event_from_previous_run() -> None:
    module = (WEB / "views/body/observability.js").as_uri()
    out = _node(
        f"""
const {{PhysicalObservationBoundary}} = await import({json.dumps(module)});
let remounts = 0;
const decoder = {{decode: (payload) => payload, takeIssue: () => null}};
const viewer = {{
  decoder,
  liveDecoder: decoder,
  statusEl: {{dataset: {{}}, style: {{}}, textContent: ''}},
}};
const boundary = new PhysicalObservationBoundary({{onIdentityChange: () => remounts += 1}});
boundary.mount({{sources:{{physics3d:{{run_id:'run-b', body_ref:'body-b', body_kind:'crawler-v1'}}}}}});
boundary.attach(viewer);
const stale = decoder.decode({{
  type:'body_pose', run_id:'run-a', body_id:'apparatus-a', body_kind:'crawler-v1', tick:10,
}});
const fresh = decoder.decode({{
  type:'body_pose', run_id:'run-b', body_id:'apparatus-b', body_kind:'crawler-v1', tick:1,
}});
await Promise.resolve();
console.log(JSON.stringify({{
  stale,
  freshTick:fresh?.tick ?? null,
  remounts,
  freshness:viewer.statusEl.dataset.observationFreshness,
}}));
"""
    )

    assert out["stale"] is None
    assert out["freshTick"] == 1
    assert out["remounts"] == 1
    assert out["freshness"] == "stale"


def test_physical_boundary_event_never_reaches_viewer_as_observation() -> None:
    module = (WEB / "views/body/observability.js").as_uri()
    out = _node(
        f"""
const {{PhysicalObservationBoundary}} = await import({json.dumps(module)});
let remounts = 0;
const decoder = {{decode: (payload) => payload, takeIssue: () => null}};
const viewer = {{
  decoder,
  liveDecoder: decoder,
  statusEl: {{dataset: {{}}, style: {{}}, textContent: ''}},
}};
const boundary = new PhysicalObservationBoundary({{onIdentityChange: () => remounts += 1}});
boundary.mount({{sources:{{physics3d:{{run_id:'run-a', body_ref:'body-a', body_kind:'crawler-v1'}}}}}});
boundary.attach(viewer);
const result = decoder.decode({{type:'observation_boundary', phase:'begin', run_id:'run-b'}});
await Promise.resolve();
console.log(JSON.stringify({{
  result,
  remounts,
  status:viewer.statusEl.textContent,
  freshness:viewer.statusEl.dataset.observationFreshness,
}}));
"""
    )

    assert out["result"] is None
    assert out["remounts"] == 1
    assert "New run" in out["status"]
    assert out["freshness"] == "stale"

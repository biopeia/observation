"""Executable boundary regressions for Body/World observer presentation."""

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


def test_physical_stream_identity_change_is_dropped_before_old_viewer_consumes_it() -> None:
    module = (WEB / "views/body/observability.js").as_uri()
    out = _node(
        f"""
const {{PhysicalObservationBoundary}} = await import({json.dumps(module)});
let remounts = 0;
const boundary = new PhysicalObservationBoundary({{onIdentityChange: () => remounts += 1}});
const decoder = {{
  decode: (payload) => payload,
  takeIssue: () => null,
}};
const viewer = {{decoder, liveDecoder: decoder, statusEl: {{dataset: {{}}, style: {{}}, textContent: ''}}}};
boundary.mount({{sources:{{physics3d:{{run_id:'r1', body_ref:'b1', body_kind:'k'}}}}}});
boundary.attach(viewer);
const first = decoder.decode({{type:'body', run_id:'r1', body_id:'b1', tick:1}});
const crossed = decoder.decode({{type:'body', run_id:'r2', body_id:'b2', tick:2}});
await Promise.resolve();
const stateCatchup = boundary.update(viewer, {{sources:{{physics3d:{{run_id:'r2', body_ref:'b2', body_kind:'k'}}}}}});
const laterBoundary = boundary.update(viewer, {{sources:{{physics3d:{{run_id:'r3', body_ref:'b3', body_kind:'k'}}}}}});
console.log(JSON.stringify({{
  firstTick:first?.tick ?? null,
  crossed,
  remounts,
  stateCatchup,
  laterBoundary,
  status:viewer.statusEl.textContent,
  freshness:viewer.statusEl.dataset.observationFreshness,
}}));
"""
    )

    assert out["firstTick"] == 1
    assert out["crossed"] is None
    assert out["remounts"] == 1
    # The first /api/state poll after an earlier stream boundary establishes a
    # baseline instead of scheduling a redundant second remount.
    assert out["stateCatchup"] is False
    assert out["laterBoundary"] is True
    assert out["freshness"] == "stale"
    assert "resetting presentation" in out["status"]


def test_replayed_run_boundary_does_not_remount_again_after_viewer_recreation() -> None:
    module = (WEB / "views/body/observability.js").as_uri()
    out = _node(
        f"""
const {{PhysicalObservationBoundary}} = await import({json.dumps(module)});
let remounts = 0;
const boundary = new PhysicalObservationBoundary({{onIdentityChange: () => remounts += 1}});
const makeViewer = () => {{
  const decoder = {{decode: (payload) => payload, takeIssue: () => null}};
  return {{decoder, liveDecoder: decoder, statusEl: {{dataset: {{}}, style: {{}}, textContent: ''}}}};
}};
const first = makeViewer();
boundary.mount({{sources:{{physics3d:{{run_id:'run-1', body_ref:'body-1', body_kind:'crawler-v1'}}}}}});
boundary.attach(first);
const original = first.decoder.decode({{type:'observation_boundary', phase:'begin', run_id:'run-1'}});
await Promise.resolve();
const afterRemount = makeViewer();
boundary.attach(afterRemount);
const replay = afterRemount.decoder.decode({{type:'observation_boundary', phase:'begin', run_id:'run-1'}});
await Promise.resolve();
console.log(JSON.stringify({{original, replay, remounts}}));
""",
    )

    assert out == {"original": None, "replay": None, "remounts": 1}


def test_partial_tick_identity_does_not_reset_observer_viewer() -> None:
    module = (WEB / "views/body/observability.js").as_uri()
    out = _node(
        f"""
const {{PhysicalObservationBoundary}} = await import({json.dumps(module)});
let remounts = 0;
const boundary = new PhysicalObservationBoundary({{onIdentityChange: () => remounts += 1}});
const decoder = {{decode: (payload) => payload, takeIssue: () => null}};
const viewer = {{decoder, liveDecoder: decoder, statusEl: {{dataset: {{}}, style: {{}}, textContent: ''}}}};
boundary.mount(null);
boundary.attach(viewer);
const first = decoder.decode({{type:'body_pose', run_id:'r1', body_id:'apparatus-body-ref', body_kind:'crawler-v1', tick:1}});
const partial = decoder.decode({{type:'body_pose', run_id:'r1', tick:2}});
const enriched = decoder.decode({{type:'body', run_id:'r1', body_id:'runtime-body-id', body_kind:'crawler-v1', tick:3}});
const distinctProjection = decoder.decode({{type:'cognition', run_id:'r1', body_id:'runtime-body-id', tick:4}});
const repeatedPose = decoder.decode({{type:'body_pose', run_id:'r1', body_id:'apparatus-body-ref', body_kind:'crawler-v1', tick:5}});
await Promise.resolve();
console.log(JSON.stringify({{first:first?.tick, partial:partial?.tick, enriched:enriched?.tick, distinctProjection:distinctProjection?.tick, repeatedPose:repeatedPose?.tick, remounts}}));
""",
    )

    assert out == {
        "first": 1,
        "partial": 2,
        "enriched": 3,
        "distinctProjection": 4,
        "repeatedPose": 5,
        "remounts": 0,
    }


def test_identity_change_within_same_projection_family_resets_viewer() -> None:
    module = (WEB / "views/body/observability.js").as_uri()
    out = _node(
        f"""
const {{PhysicalObservationBoundary}} = await import({json.dumps(module)});
let remounts = 0;
const boundary = new PhysicalObservationBoundary({{onIdentityChange: () => remounts += 1}});
const decoder = {{decode: (payload) => payload, takeIssue: () => null}};
const viewer = {{decoder, liveDecoder: decoder, statusEl: {{dataset: {{}}, style: {{}}, textContent: ''}}}};
boundary.mount(null);
boundary.attach(viewer);
decoder.decode({{type:'body', run_id:'r1', body_id:'b1', tick:1}});
const changed = decoder.decode({{type:'body', run_id:'r1', body_id:'b2', tick:2}});
await Promise.resolve();
console.log(JSON.stringify({{changed, remounts}}));
""",
    )

    assert out == {"changed": None, "remounts": 1}


def test_dense_body_pose_marks_body_status_live() -> None:
    source = (WEB / "views/body/viewer.js").read_text()
    pose_handler = source.split("  handleBodyPoseEvent(data) {", 1)[1].split(
        "  handleBodyEvent(data) {", 1
    )[0]
    assert "this.markBodyLive();" in pose_handler


def test_body_view_consumes_complete_observed_frames() -> None:
    source = (WEB / "views/body/viewer.js").read_text()
    assert "case 'observed_frame': this.handleObservedFrame(data);" in source
    frame_handler = source.split("  handleObservedFrame(frame) {", 1)[1].split(
        "  markBodyLive() {", 1
    )[0]
    assert "this.handleBodyEvent(frame.body)" in frame_handler
    assert "this.handleCognitionEvent(frame.cognition)" in frame_handler
    assert "this.handleVitalsEvent(frame.vitals)" in frame_handler


def test_body_view_does_not_present_fallback_morphology_as_requested_body() -> None:
    source = (WEB / "views/body/viewer.js").read_text()
    model_handler = source.split("  ensureBodyModel(bodyKind) {", 1)[1].split(
        "  buildDOM() {", 1
    )[0]
    assert "this.skeletonRoot.visible = false" in model_handler
    assert "Observer model unavailable: ${requested}" in model_handler
    assert "this.skeletonRoot.visible = true" in model_handler
    assert "this.scheduleBodyModelRetry();" in source

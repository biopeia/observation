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

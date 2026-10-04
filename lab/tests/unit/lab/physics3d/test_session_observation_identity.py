from __future__ import annotations

import time
from pathlib import Path

from lab.app.physics3d.runs import Physics3DLaunchSpec
from lab.app.physics3d.session import Physics3DSession, Physics3DSessionState
from lab.experience import RunKind
from lab.observation.bus import ObservationBus


def _wait_terminal(session: Physics3DSession) -> None:
    deadline = time.monotonic() + 2.0
    while time.monotonic() < deadline:
        if session.snapshot().state in {Physics3DSessionState.STOPPED, Physics3DSessionState.FAILED}:
            return
        time.sleep(0.01)
    raise AssertionError("Physics3DSession did not reach a terminal state")


def test_unmanaged_physics3d_session_gets_ephemeral_run_identity() -> None:
    captured = {}

    def runner(**kwargs) -> int:
        captured["bridge"] = kwargs["viewer_bridge"]
        return 0

    session = Physics3DSession(ObservationBus(), runner=runner)
    assert session.start() is True
    _wait_terminal(session)

    snapshot = session.snapshot()
    assert snapshot.run_id is not None
    assert snapshot.run_id.startswith("local:")
    assert captured["bridge"].run_id == snapshot.run_id
    assert captured["bridge"].organism_id is None
    assert captured["bridge"].body_id is None


def test_managed_session_uses_durable_launch_identity(tmp_path: Path) -> None:
    captured = {}

    def runner(**kwargs) -> int:
        captured["bridge"] = kwargs["viewer_bridge"]
        return 0

    launch = Physics3DLaunchSpec(
        run_id="run-managed-1",
        organism_ref="org-1",
        body_ref="body-1",
        body_kind="anthropomorphic-v6",
        organism_mode="existing",
        body_mode="fresh",
        symbiont_file=tmp_path / "organism.symbiont",
        body_file=tmp_path / "body.json",
        telemetry_file=tmp_path / "telemetry.jsonl",
        run_kind=RunKind.WORLD_OPEN,
    )
    session = Physics3DSession(ObservationBus(), runner=runner)
    assert session.start(launch) is True
    _wait_terminal(session)

    snapshot = session.snapshot()
    assert snapshot.run_id == "run-managed-1"
    assert snapshot.organism_ref == "org-1"
    assert snapshot.body_ref == "body-1"
    assert captured["bridge"].run_id == "run-managed-1"
    assert captured["bridge"].organism_id == "org-1"
    assert captured["bridge"].body_id == "body-1"

"""Workbench contract for canonical semantic Body Pose consumption."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
VIEWER = ROOT / "lab/src/lab/workbench/web/views/body/viewer.js"


def test_body_viewer_connects_to_semantic_body_pose_stream() -> None:
    source = VIEWER.read_text(encoding="utf-8")
    assert "/api/observations/stream?family=${family}" in source
    assert "data?.family !== 'embodiment.body_pose'" in source
    assert "data?.wire_contract !== 'observation-semantic-wire-v1'" in source


def test_semantic_body_pose_becomes_canonical_over_legacy_dense_pose() -> None:
    source = VIEWER.read_text(encoding="utf-8")
    assert "this.hasSemanticPoseStream = true" in source
    assert "if (!this.hasSemanticPoseStream) this.handleBodyPoseEvent(data);" in source
    handler = source.split("  handleSemanticBodyPose(data) {", 1)[1].split(
        "  handleBodyPoseEvent(data) {", 1
    )[0]
    assert "value.position_m" in handler
    assert "value.orientation_xyzw" in handler
    assert "simulation_time_s" in handler
    assert "this.capturePoseFrame(receivedAt, sourceTimeMs);" in handler


def test_body_viewer_closes_semantic_stream_on_unmount() -> None:
    source = VIEWER.read_text(encoding="utf-8")
    unmount = source.split("  unmount() {", 1)[1]
    assert "this.semanticSse.close();" in unmount
    assert "this.semanticSse = null;" in unmount
"""Workbench contracts for canonical semantic observation consumption."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
VIEWER = ROOT / "lab/src/lab/workbench/web/views/body/viewer.js"


def test_body_viewer_uses_single_semantic_observation_stream() -> None:
    source = VIEWER.read_text(encoding="utf-8")
    assert "new EventSource('/api/observations/stream')" in source
    assert "'embodiment.body_pose'" in source
    assert "'embodiment.joint_kinematics'" in source
    assert "'embodiment.body_physiology'" in source
    assert "'symbiont.affordance'" in source


def test_canonical_pose_replaces_only_legacy_base_pose_capability() -> None:
    source = VIEWER.read_text(encoding="utf-8")
    assert "case 'body_pose':     this.handleBodyPoseEvent(data);" in source
    handler = source.split("  handleBodyPoseEvent(data) {", 1)[1].split(
        "  handleBodyEvent(data) {", 1
    )[0]
    assert "!this.hasSemanticPoseStream" in handler
    assert "data.base_position" in handler
    assert "data.base_orientation" in handler
    assert "Array.isArray(data.links)" in handler


def test_canonical_joint_kinematics_replaces_legacy_joint_capability() -> None:
    source = VIEWER.read_text(encoding="utf-8")
    semantic = source.split("  handleSemanticJointKinematics(data) {", 1)[1].split(
        "  handleSemanticBodyPhysiology(data) {", 1
    )[0]
    assert "joint_id" in semantic
    assert "position_rad" in semantic
    assert "this.bodyModel?.joints?.[index]?.name" in semantic
    assert "this.hasSemanticJointStream = true" in semantic
    assert "!this.hasSemanticJointStream && Array.isArray(data.joints)" in source


def test_canonical_physiology_replaces_legacy_vital_and_reserve_capability() -> None:
    source = VIEWER.read_text(encoding="utf-8")
    semantic = source.split("  handleSemanticBodyPhysiology(data) {", 1)[1].split(
        "  handleSemanticAffordance(data) {", 1
    )[0]
    assert "value.reserve_fraction" in semantic
    assert "value.vital_state" in semantic
    assert "value.age_ticks" in semantic
    assert "!this.hasSemanticPhysiologyStream && data.alive !== undefined" in source
    assert "!this.hasSemanticPhysiologyStream && data.metabolic_reserve !== undefined" in source


def test_canonical_affordance_replaces_only_mind_affordance_projection() -> None:
    source = VIEWER.read_text(encoding="utf-8")
    semantic = source.split("  handleSemanticAffordance(data) {", 1)[1].split(
        "  handleBodyPoseEvent(data) {", 1
    )[0]
    assert "this.semanticAffordances = value.affordances" in semantic
    assert "affordances: this.semanticAffordances" in source
    assert "this.lastMindSnapshot = snapshot" in source


def test_semantic_rebase_invalidates_capability_state_before_snapshot() -> None:
    source = VIEWER.read_text(encoding="utf-8")
    connect = source.split("  connectSemanticSSE() {", 1)[1].split(
        "  handleSemanticObservation(data) {", 1
    )[0]
    assert "data?.status === 'rebase_required'" in connect
    assert "this.hasSemanticPoseStream = false" in connect
    assert "this.hasSemanticJointStream = false" in connect
    assert "this.hasSemanticPhysiologyStream = false" in connect
    assert "this.hasSemanticAffordanceStream = false" in connect
    assert "for (const item of data.items ?? []) this.handleSemanticObservation(item);" in connect


def test_body_viewer_closes_semantic_stream_on_unmount() -> None:
    source = VIEWER.read_text(encoding="utf-8")
    unmount = source.split("  unmount() {", 1)[1]
    assert "this.semanticSse.close();" in unmount
    assert "this.semanticSse = null;" in unmount

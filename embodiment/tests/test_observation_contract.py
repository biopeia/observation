"""Embodiment Body Pose observation contract tests."""

from __future__ import annotations

import pytest

from embodiment.observation import BodyPoseSample
from embodiment.physics3d.observation_contract import body_pose_semantics


def test_physics3d_declares_canonical_body_pose_semantics() -> None:
    assert body_pose_semantics() == {
        "position_unit": "m",
        "handedness": "right",
        "up_axis": "+z",
        "orientation": "xyzw",
        "reference_frame": "physics3d.world",
        "body_frame": "body.root",
        "contract_revision": "v1",
    }


def test_body_pose_sample_requires_unit_quaternion() -> None:
    with pytest.raises(ValueError, match="unit quaternion"):
        BodyPoseSample(
            body_id="body.1",
            reference_frame="physics3d.world",
            body_frame="body.root",
            position_m=(0.0, 0.0, 0.0),
            orientation_xyzw=(0.0, 0.0, 0.0, 2.0),
            sample_kind="physics_step",
            sample_value=1,
        )


def test_body_pose_sample_rejects_non_finite_sample_time() -> None:
    with pytest.raises(ValueError, match="sample_time_s"):
        BodyPoseSample(
            body_id="body.1",
            reference_frame="physics3d.world",
            body_frame="body.root",
            position_m=(0.0, 0.0, 0.0),
            orientation_xyzw=(0.0, 0.0, 0.0, 1.0),
            sample_kind="physics_step",
            sample_value=1,
            sample_time_s=float("nan"),
        )
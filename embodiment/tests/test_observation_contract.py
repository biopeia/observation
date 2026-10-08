"""Embodiment Body Pose observation contract tests."""

from __future__ import annotations

import pytest

from embodiment.observation import (
    BodyPhysiologySample,
    BodyPoseSample,
    JointKinematicState,
    JointKinematicsSample,
)
from embodiment.physics3d.observation_contract import (
    body_pose_semantics,
    joint_kinematics_semantics,
)


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


def test_physics3d_declares_canonical_joint_kinematics_semantics() -> None:
    assert joint_kinematics_semantics() == {
        "joint_type": "revolute",
        "position_unit": "rad",
        "velocity_unit": "rad/s",
        "identity_scope": "body_local",
        "contract_revision": "v1",
    }


def test_joint_kinematics_reject_duplicate_body_local_ids() -> None:
    joint = JointKinematicState(
        joint_id="body.1:joint:2",
        position_rad=0.1,
        velocity_rad_s=0.2,
    )
    with pytest.raises(ValueError, match="unique"):
        JointKinematicsSample(
            body_id="body.1",
            joints=(joint, joint),
            sample_kind="physics_step",
            sample_value=3,
        )


def test_joint_kinematics_reject_non_finite_values() -> None:
    with pytest.raises(ValueError, match="finite"):
        JointKinematicState(
            joint_id="body.1:joint:2",
            position_rad=float("nan"),
            velocity_rad_s=0.0,
        )


def test_body_physiology_reserve_is_explicit_model_amount() -> None:
    with pytest.raises(ValueError, match="model_amount"):
        BodyPhysiologySample(
            body_id="body.1",
            reserve_amount=5.0,
            reserve_capacity=10.0,
            reserve_fraction=0.5,
            reserve_quantity_kind="joule",
            structural_integrity=0.9,
            temperature=0.5,
            fatigue=0.1,
            growth_progress=0.2,
            senescence=0.0,
            age_ticks=4,
            vital_state="alive",
        )


def test_body_physiology_rejects_inconsistent_reserve_fraction() -> None:
    with pytest.raises(ValueError, match="contradicts"):
        BodyPhysiologySample(
            body_id="body.1",
            reserve_amount=5.0,
            reserve_capacity=10.0,
            reserve_fraction=0.8,
            reserve_quantity_kind="model_amount",
            structural_integrity=0.9,
            temperature=0.5,
            fatigue=0.1,
            growth_progress=0.2,
            senescence=0.0,
            age_ticks=4,
            vital_state="alive",
        )

"""Adapters for Embodiment-owned semantic projections.

Observation maps approved owner projections to passive common records. It
does not calculate body state, establish World commit, or acquire authority.
"""

from __future__ import annotations

import math
import re
from typing import Protocol

from observation.semantic import (
    AcquisitionBasis,
    ActorRef,
    AuthorityDomain,
    DomainTimeRef,
    IdentityAssertion,
    IdentityRef,
    Lineage,
    LineageSourceRef,
    SemanticClaim,
    SemanticContractRef,
    SemanticFamily,
    SemanticObservation,
    SubjectScope,
    TransformationRef,
)


_FAMILY_ID = "embodiment.body_pose"
_FAMILY_REVISION = "v1"
_ASSERTER = "embodiment_owner_boundary"
_PRODUCER = "embodiment_owner_projection"
_DIGEST = re.compile(r"^[0-9a-f]{64}$")

_RESERVE_STATE_FAMILY_ID = "biopeia.embodiment.reserve_state_snapshot"
_RESERVE_STATE_REVISION = "1"


class _ReserveStateProjection(Protocol):
    semantic_family_id: str
    semantic_revision: str
    semantic_authority: str
    semantic_asserter: str
    semantic_producer: str
    body_id: str
    episode_id: str
    amount: float
    capacity: float
    fraction: float
    quantity_kind: str
    world_id: str
    causal_tick: int
    commit_id: str
    checkpoint_id: str
    checkpoint_schema: str
    checkpoint_version: int
    source_owner_checkpoint_sha256: str


def embodiment_reserve_state_observation(
    projection: _ReserveStateProjection,
) -> SemanticObservation[dict[str, object]]:
    """Adapt a committed Embodiment reserve snapshot without interpretation."""
    expected = {
        "semantic_family_id": _RESERVE_STATE_FAMILY_ID,
        "semantic_revision": _RESERVE_STATE_REVISION,
        "semantic_authority": "EMBODIMENT",
        "semantic_asserter": "embodiment.owner_checkpoint",
        "semantic_producer": "embodiment.checkpoint.project_committed_reserve_state",
        "quantity_kind": "model_amount",
    }
    for name, value in expected.items():
        if getattr(projection, name, None) != value:
            raise ValueError(f"Embodiment reserve projection has invalid {name}")
    body_id = _required_text(projection, "body_id")
    episode_id = _required_text(projection, "episode_id")
    world_id = _required_text(projection, "world_id")
    commit_id = _required_text(projection, "commit_id")
    checkpoint_id = _required_text(projection, "checkpoint_id")
    checkpoint_schema = _required_text(projection, "checkpoint_schema")
    tick = _required_tick(projection, "causal_tick")
    version = getattr(projection, "checkpoint_version", None)
    digest = _required_text(projection, "source_owner_checkpoint_sha256")
    if type(version) is not int or version < 1:
        raise ValueError("Embodiment checkpoint version must be a positive integer")
    if not _DIGEST.fullmatch(digest):
        raise ValueError("Embodiment owner checkpoint digest must be lowercase SHA-256")
    numbers: dict[str, float] = {}
    for name in ("amount", "capacity", "fraction"):
        value = getattr(projection, name, None)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f"Embodiment reserve {name} must be finite numeric data")
        numbers[name] = float(value)
    actor = ActorRef("embodiment", body_id)
    family = SemanticFamily(
        authority=AuthorityDomain.EMBODIMENT,
        path=("reserve_state_snapshot",),
        contract=SemanticContractRef(_RESERVE_STATE_FAMILY_ID, _RESERVE_STATE_REVISION),
    )
    subject = SubjectScope(
        kind="embodiment_reserve_state",
        identities=(
            IdentityAssertion(IdentityRef("body", body_id, actor, scope=episode_id), asserter=actor),
            IdentityAssertion(IdentityRef("embodiment_episode", episode_id, actor, scope=body_id), asserter=actor),
        ),
    )
    return SemanticObservation(
        claim=SemanticClaim(
            family=family,
            subject=subject,
            epistemic_kind="authoritative_state",
            value={
                "amount": {"value": numbers["amount"], "quantity_kind": "model_amount"},
                "capacity": {"value": numbers["capacity"], "quantity_kind": "model_amount"},
                "fraction": {"value": numbers["fraction"], "unit": "1"},
            },
        ),
        acquisition=AcquisitionBasis(method="embodiment_owner_checkpoint_projection"),
        asserter=ActorRef("embodiment_owner_boundary", "embodiment.owner_checkpoint"),
        producer=ActorRef("embodiment_projection", "embodiment.checkpoint.project_committed_reserve_state"),
        context_time=(DomainTimeRef(AuthorityDomain.WORLD, "world_causal_tick", tick),),
        lineage=Lineage(
            parents=(LineageSourceRef("embodiment_owner_checkpoint_sha256", digest),),
            transformation=TransformationRef(
                "embodiment.reserve_state_snapshot.project_committed_state",
                _RESERVE_STATE_REVISION,
                effective_configuration=(
                    ("world_id", world_id),
                    ("commit_id", commit_id),
                    ("checkpoint_id", checkpoint_id),
                    ("checkpoint_schema", checkpoint_schema),
                    ("checkpoint_version", str(version)),
                    ("body_id", body_id),
                    ("embodiment_episode_id", episode_id),
                ),
            ),
        ),
    )


class _BodyPoseSample(Protocol):
    body_id: str
    reference_frame: str
    body_frame: str
    position_m: tuple[float, float, float]
    orientation_xyzw: tuple[float, float, float, float]
    sample_kind: str
    sample_value: int | float | str
    contract_revision: str


class _PhysicalStepCorrelation(Protocol):
    world_id: str
    causal_tick: int
    physical_step_id: str
    body_id: str
    embodiment_episode_id: str
    morphology_revision: str
    environment_revision: str
    solver_config_revision: str


class _BodyPoseProjection(Protocol):
    world_id: str
    causal_tick: int
    body_id: str
    embodiment_episode_id: str
    morphology_revision: str
    source_state_sha256: str
    pose: _BodyPoseSample
    last_physical_step_id: str | None
    last_physical_step_source_tick: int | None
    environment_revision: str | None
    solver_config_revision: str | None
    physical_step_correlation: _PhysicalStepCorrelation | None


def embodiment_body_pose_observation(
    projection: _BodyPoseProjection,
) -> SemanticObservation[dict[str, object]]:
    """Map one approved Embodiment BodyPose v1 owner projection.

    This function intentionally uses the public structural contract rather
    than importing Embodiment's package. A mapped value remains only a passive
    projection: it is not evidence that World committed the represented cut.
    The World publication boundary must independently verify commit and
    correlation before delivery.
    """

    world_id = _required_text(projection, "world_id")
    body_id = _required_text(projection, "body_id")
    episode_id = _required_text(projection, "embodiment_episode_id")
    morphology_revision = _required_text(projection, "morphology_revision")
    source_digest = _required_text(projection, "source_state_sha256")
    if not _DIGEST.fullmatch(source_digest):
        raise ValueError("Embodiment source-state reference must be lowercase SHA-256")
    causal_tick = _required_tick(projection, "causal_tick")

    pose = getattr(projection, "pose", None)
    if pose is None:
        raise ValueError("Embodiment projection requires a pose")
    if _required_text(pose, "body_id") != body_id:
        raise ValueError("pose body identity differs from projection")
    if _required_text(pose, "contract_revision") != _FAMILY_REVISION:
        raise ValueError("BodyPose sample has an unsupported contract revision")
    reference_frame = _required_text(pose, "reference_frame")
    body_frame = _required_text(pose, "body_frame")
    sample_kind = _required_text(pose, "sample_kind")
    sample_value = getattr(pose, "sample_value", None)
    if isinstance(sample_value, bool) or not isinstance(sample_value, (int, float, str)):
        raise ValueError("BodyPose sample_value must be an int, float, or string")
    if isinstance(sample_value, float) and not math.isfinite(sample_value):
        raise ValueError("BodyPose sample_value must be finite")

    position = _finite_tuple(getattr(pose, "position_m", None), size=3, name="position_m")
    orientation = _finite_tuple(
        getattr(pose, "orientation_xyzw", None), size=4, name="orientation_xyzw"
    )
    if abs(sum(component * component for component in orientation) - 1.0) > 1e-5:
        raise ValueError("BodyPose orientation_xyzw must be a unit quaternion")

    step_id = getattr(projection, "last_physical_step_id", None)
    source_tick = getattr(projection, "last_physical_step_source_tick", None)
    environment_revision = getattr(projection, "environment_revision", None)
    solver_revision = getattr(projection, "solver_config_revision", None)
    correlation = getattr(projection, "physical_step_correlation", None)
    optional_step_values = (step_id, source_tick, environment_revision, solver_revision)
    if all(value is None for value in optional_step_values):
        if correlation is not None or sample_kind == "physics_step":
            raise ValueError("physics-step pose requires complete physical-step correlation")
        step_configuration: tuple[tuple[str, str], ...] = ()
    else:
        if any(value is None for value in optional_step_values):
            raise ValueError("physical-step projection correlation must be complete")
        step_id = _required_text(projection, "last_physical_step_id")
        environment_revision = _required_text(projection, "environment_revision")
        solver_revision = _required_text(projection, "solver_config_revision")
        source_tick = _required_tick(projection, "last_physical_step_source_tick")
        if source_tick + 1 != causal_tick:
            raise ValueError("physical-step source tick must immediately precede pose tick")
        if sample_kind != "physics_step" or sample_value != step_id:
            raise ValueError("pose sample does not identify the projected physical step")
        if correlation is None:
            raise ValueError("physical-step correlation record is required")
        expected_correlation = {
            "world_id": world_id,
            "causal_tick": source_tick,
            "physical_step_id": step_id,
            "body_id": body_id,
            "embodiment_episode_id": episode_id,
            "morphology_revision": morphology_revision,
            "environment_revision": environment_revision,
            "solver_config_revision": solver_revision,
        }
        for name, expected in expected_correlation.items():
            if getattr(correlation, name, None) != expected:
                raise ValueError(f"physical-step correlation has inconsistent {name}")
        step_configuration = (
            ("physical_step_id", step_id),
            ("physical_step_source_tick", str(source_tick)),
            ("environment_revision", environment_revision),
            ("solver_config_revision", solver_revision),
        )

    owner = ActorRef("embodiment", _ASSERTER)
    family = SemanticFamily(
        authority=AuthorityDomain.EMBODIMENT,
        path=("body_pose",),
        contract=SemanticContractRef(_FAMILY_ID, _FAMILY_REVISION),
    )
    body_identity = IdentityRef("body", body_id, owner, scope=episode_id)
    subject = SubjectScope(
        kind="embodiment_body",
        identities=(
            IdentityAssertion(body_identity, asserter=owner),
            IdentityAssertion(
                IdentityRef(
                    "embodiment_episode", episode_id, owner, scope=body_id
                ),
                asserter=owner,
            ),
            IdentityAssertion(
                IdentityRef(
                    "morphology_revision", morphology_revision, owner, scope=body_id
                ),
                asserter=owner,
            ),
        ),
    )
    return SemanticObservation(
        claim=SemanticClaim(
            family=family,
            subject=subject,
            epistemic_kind="authoritative_state",
            value={
                "position": {"value": position, "unit": "m"},
                "orientation": {
                    "value_xyzw": orientation,
                    "representation": "unit_quaternion_xyzw",
                    "convention": "right_handed_hamilton_q_v_q_conjugate",
                },
                "reference_frame": reference_frame,
                "body_frame": body_frame,
            },
        ),
        acquisition=AcquisitionBasis(method="embodiment_owner_state_projection"),
        asserter=ActorRef("embodiment_owner_boundary", _ASSERTER),
        producer=ActorRef("embodiment_owner_projection", _PRODUCER),
        # The BodyPose family declares no Embodiment-local domain time. World
        # causal time is preserved only as correlation context.
        context_time=(
            DomainTimeRef(AuthorityDomain.WORLD, "world_causal_tick", causal_tick),
        ),
        lineage=Lineage(
            parents=(LineageSourceRef("embodiment_state_sha256", source_digest),),
            transformation=TransformationRef(
                "embodiment.body_pose.project_observation",
                _FAMILY_REVISION,
                effective_configuration=(
                    ("world_id", world_id),
                    ("causal_tick", str(causal_tick)),
                    ("body_id", body_id),
                    ("embodiment_episode_id", episode_id),
                    ("morphology_revision", morphology_revision),
                    ("reference_frame", reference_frame),
                    ("body_frame", body_frame),
                    *step_configuration,
                ),
            ),
        ),
    )


def _required_text(source: object, name: str) -> str:
    value = getattr(source, name, None)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Embodiment projection {name} must be non-empty text")
    return value.strip()


def _required_tick(source: object, name: str) -> int:
    value = getattr(source, name, None)
    if type(value) is not int or value < 0:
        raise ValueError(f"Embodiment projection {name} must be a non-negative integer")
    return value


def _finite_tuple(value: object, *, size: int, name: str) -> tuple[float, ...]:
    if not isinstance(value, tuple) or len(value) != size:
        raise ValueError(f"Embodiment projection {name} must be a {size}-tuple")
    if any(
        isinstance(component, bool)
        or not isinstance(component, (int, float))
        or not math.isfinite(component)
        for component in value
    ):
        raise ValueError(f"Embodiment projection {name} must contain finite numbers")
    return tuple(float(component) for component in value)


__all__ = ["embodiment_body_pose_observation", "embodiment_reserve_state_observation"]

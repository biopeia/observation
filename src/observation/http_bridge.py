"""Local-only, read-only HTTP access to approved current observations.

This is a narrow developer bridge, not a network service or durable API. It
serves only the approved families from an existing
``ObservationPlane`` instance and never creates, joins, or interprets claims.
"""

from __future__ import annotations

import ipaddress
import hashlib
import json
import math
from dataclasses import fields, is_dataclass
from enum import Enum
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from typing import Any
from urllib.parse import urlsplit
import rfc8785

from .plane import ObservationPlane
from .spatial_contracts import (
    validate_environment_render_scene as _validate_environment_render_scene,
    validate_embodiment_render_morphology as _validate_embodiment_render_morphology,
)
from .semantic import (
    AcquisitionBasis,
    ActorRef,
    AuthorityDomain,
    ObservationCondition,
    DomainTimeRef,
    IdentityAssertion,
    IdentityLink,
    IdentityRef,
    Lineage,
    LineageSourceRef,
    SemanticClaim,
    SemanticContractRef,
    SemanticFamily,
    SemanticObservation,
    SubjectScope,
    TransformationRef,
    OrchestrationContext,
)

_APPROVED_FAMILY_CONTRACTS = {
    "embodiment.body_pose": (
        AuthorityDomain.EMBODIMENT,
        "embodiment.body_pose",
        "v1",
        "authoritative_state",
    ),
    "environment.finite_scalar_field": (
        AuthorityDomain.ENVIRONMENT,
        "biopeia.environment.finite-scalar-field",
        "1",
        "domain_derived",
    ),
    "environment.render_scene": (
        AuthorityDomain.ENVIRONMENT,
        "biopeia.environment.render-scene",
        "1",
        "authoritative_state",
    ),
    "embodiment.render_morphology": (
        AuthorityDomain.EMBODIMENT,
        "embodiment.render_morphology",
        "v1",
        "authoritative_state",
    ),
    "embodiment.render_link_pose": (
        AuthorityDomain.EMBODIMENT,
        "embodiment.render_link_pose",
        "v1",
        "authoritative_state",
    ),
}
APPROVED_FAMILIES = frozenset(_APPROVED_FAMILY_CONTRACTS)
DEFAULT_MAX_RESPONSE_BYTES = 1_000_000
_WIRE_TYPES = (
    AcquisitionBasis,
    ActorRef,
    DomainTimeRef,
    IdentityAssertion,
    IdentityLink,
    IdentityRef,
    Lineage,
    LineageSourceRef,
    ObservationCondition,
    OrchestrationContext,
    SemanticClaim,
    SemanticContractRef,
    SemanticFamily,
    SemanticObservation,
    SubjectScope,
    TransformationRef,
)


class LocalReadBridgeError(ValueError):
    """Raised when the bridge would violate its bounded local contract."""


class ResponseTooLargeError(LocalReadBridgeError):
    """Raised when a valid current view exceeds the configured response cap."""


def _wire_value(value: Any) -> Any:
    """Serialize only the explicit semantic model and built-in value trees."""
    if value is None or type(value) in (bool, int, float, str):
        return value
    if isinstance(value, Enum):
        return value.value
    if type(value) in (list, tuple):
        return [_wire_value(item) for item in value]
    if type(value) is dict:
        if any(type(key) is not str for key in value):
            raise LocalReadBridgeError("claim mapping keys must be strings")
        return {key: _wire_value(item) for key, item in value.items()}
    if is_dataclass(value) and type(value) in _WIRE_TYPES:
        return {field.name: _wire_value(getattr(value, field.name)) for field in fields(value)}
    raise LocalReadBridgeError(f"unsupported semantic wire value: {type(value).__name__}")


def encode_current_messages(plane: ObservationPlane, *, max_response_bytes: int) -> bytes:
    """Encode the retained current subset without implying a source census."""
    if type(max_response_bytes) is not int or max_response_bytes < 1:
        raise ValueError("max_response_bytes must be a positive integer")
    messages = []
    for message in plane.current_messages():
        observation = message.observation
        family = observation.family.qualified_name
        if family not in APPROVED_FAMILIES:
            continue
        expected_authority, expected_contract_id, expected_revision, expected_epistemic_kind = (
            _APPROVED_FAMILY_CONTRACTS[family]
        )
        contract = observation.family.contract
        if (
            observation.family.authority is not expected_authority
            or contract.contract_id != expected_contract_id
            or contract.revision != expected_revision
        ):
            # Same display family with another contract is not an approved M1 claim.
            continue
        if observation.claim.epistemic_kind != expected_epistemic_kind:
            raise LocalReadBridgeError("approved family has unexpected epistemic kind")
        _validate_approved_observation(family, observation)
        messages.append(
            {
                "delivery_sequence": message.sequence,
                "observation": _wire_value(observation),
            }
        )
    payload = {
        "schema": "biopeia.observation.current.v1",
        "availability": "available" if messages else "current_view_empty",
        "absence_semantics": "not_evidence_of_source_absence",
        "scope": "bounded_in_memory_current_subset",
        "freshness": "not_established_by_snapshot",
        "coherence": "per_message_only_no_cross_owner_snapshot_guarantee",
        "messages": messages,
    }
    encoded = json.dumps(payload, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")
    if len(encoded) > max_response_bytes:
        raise ResponseTooLargeError("current observation response exceeds configured byte limit")
    return encoded


def _validate_approved_observation(family: str, observation: SemanticObservation[object]) -> None:
    """Reject malformed approved-family envelopes; never repair or infer fields."""
    claim = observation.claim
    subject = claim.subject
    identities = {
        assertion.identity.kind: assertion.identity for assertion in subject.identities
    }
    if len(identities) != len(subject.identities):
        raise LocalReadBridgeError("approved family contains duplicate typed identities")
    if family == "embodiment.body_pose":
        if (
            observation.acquisition.method != "embodiment_owner_state_projection"
            or observation.asserter.kind != "embodiment_owner_boundary"
            or observation.asserter.identifier != "embodiment_owner_boundary"
            or observation.producer.kind != "embodiment_owner_projection"
            or observation.producer.identifier != "embodiment_owner_projection"
        ):
            raise LocalReadBridgeError("BodyPose authority provenance is invalid")
        value = claim.value
        if type(value) is not dict or set(value) != {
            "position",
            "orientation",
            "reference_frame",
            "body_frame",
        }:
            raise LocalReadBridgeError("BodyPose payload does not match its approved shape")
        position = value["position"]
        orientation = value["orientation"]
        if (
            type(position) is not dict
            or set(position) != {"value", "unit"}
            or position["unit"] != "m"
            or type(orientation) is not dict
            or set(orientation) != {"value_xyzw", "representation", "convention"}
            or orientation["representation"] != "unit_quaternion_xyzw"
            or orientation["convention"] != "right_handed_hamilton_q_v_q_conjugate"
        ):
            raise LocalReadBridgeError("BodyPose units or orientation contract are invalid")
        if (
            not _finite_vector(position["value"], length=3)
            or not _finite_vector(orientation["value_xyzw"], length=4)
            or abs(sum(component * component for component in orientation["value_xyzw"]) - 1.0)
            > 1e-5
            or not _nonempty_text(value["reference_frame"])
            or not _nonempty_text(value["body_frame"])
        ):
            raise LocalReadBridgeError("BodyPose geometry is malformed")
        if not all(kind in identities for kind in ("body", "embodiment_episode", "morphology_revision")):
            raise LocalReadBridgeError("BodyPose is missing a typed body identity")
        if not any(
            item.domain is AuthorityDomain.WORLD and item.kind == "world_causal_tick"
            and type(item.value) is int
            for item in observation.context_time
        ):
            raise LocalReadBridgeError("BodyPose is missing its World causal tick")
        if not any(
            parent.namespace == "embodiment_state_sha256"
            and _is_sha256(parent.reference)
            for parent in observation.lineage.parents
        ):
            raise LocalReadBridgeError("BodyPose is missing owner-state provenance")
        transformation = observation.lineage.transformation
        if (
            transformation is None
            or transformation.transformation_id != "embodiment.body_pose.project_observation"
            or not {
                "world_id",
                "causal_tick",
                "body_id",
                "embodiment_episode_id",
                "morphology_revision",
                "reference_frame",
                "body_frame",
            }.issubset(dict(transformation.effective_configuration))
        ):
            raise LocalReadBridgeError("BodyPose is missing its source transformation context")
        return

    if family == "environment.render_scene":
        value = observation.claim.value
        _validate_environment_render_scene(value)
        _validate_static_source_envelope(
            observation, subject_kind="environment", identities={
                "environment": value["environment_id"],
                "environment_revision": value["environment_revision"],
            }, digest=value["render_geometry_sha256"],
        )
        return
    if family == "embodiment.render_morphology":
        value = observation.claim.value
        _validate_embodiment_render_morphology(value)
        _validate_static_source_envelope(
            observation, subject_kind="embodiment_body", identities={
                "body": value["body_id"],
                "embodiment_episode": value["embodiment_episode_id"],
                "morphology_revision": value["morphology_revision"],
                "geometry_revision": value["geometry_revision"],
            }, digest=value["render_geometry_sha256"],
        )
        return
    if family == "embodiment.render_link_pose":
        value = observation.claim.value
        _validate_embodiment_render_link_pose(value)
        candidate = value["candidate"]
        cut = value["world_association"]["committed_cut"]
        checkpoint = value["world_association"]["owner_checkpoint_reference"]
        identities_expected = {
            "body": candidate["body_id"],
            "embodiment_episode": candidate["embodiment_episode_id"],
            "morphology_revision": candidate["morphology_revision"],
            "geometry_revision": candidate["geometry_revision"],
        }
        if observation.acquisition.method != "embodiment_owner_render_pose_candidate":
            raise LocalReadBridgeError("render_link_pose acquisition provenance is invalid")
        if (
            observation.asserter.kind != "embodiment_owner_boundary"
            or observation.asserter.identifier != "embodiment.owner_checkpoint"
            or observation.producer.kind != "embodiment_owner_projection"
            or observation.producer.identifier != "embodiment.render_link_pose_candidate"
        ):
            raise LocalReadBridgeError("render_link_pose owner provenance is invalid")
        if observation.claim.subject.kind != "embodiment_body" or {
            assertion.identity.kind: assertion.identity.value
            for assertion in observation.claim.subject.identities
        } != identities_expected:
            raise LocalReadBridgeError("render_link_pose subject identities differ from owner payload")
        if observation.context_time != (
            DomainTimeRef(AuthorityDomain.WORLD, "world_causal_tick", cut["causal_tick"]),
        ):
            raise LocalReadBridgeError("render_link_pose World time differs from associated cut")
        expected_parents = {
            ("embodiment_owner_checkpoint_sha256", checkpoint["sha256"]),
            ("embodiment_render_geometry_sha256", candidate["render_geometry_sha256"]),
        }
        if {(p.namespace, p.reference) for p in observation.lineage.parents} != expected_parents:
            raise LocalReadBridgeError("render_link_pose lineage differs from owner sources")
        transformation = observation.lineage.transformation
        expected_configuration = {
            "world_id": cut["world_id"], "causal_tick": str(cut["causal_tick"]),
            "commit_id": cut["commit_id"], "checkpoint_id": checkpoint["checkpoint_id"],
            "projection_sha256": value["world_association"]["projection_sha256"],
        }
        if (
            transformation is None
            or transformation.transformation_id != "world.transient_associate_embodiment_render_pose"
            or transformation.revision != "1"
            or dict(transformation.effective_configuration) != expected_configuration
        ):
            raise LocalReadBridgeError("render_link_pose World association lineage is invalid")
        return

    if (
        observation.acquisition.method != "environment_field_evaluation"
        or observation.asserter.kind != "environment_owner_boundary"
        or observation.asserter.identifier != "environment.identified_finite_scalar_field"
        or observation.producer.kind != "environment_projection"
        or observation.producer.identifier
        != "environment.identified_finite_scalar_field.project_observation"
    ):
        raise LocalReadBridgeError("finite_scalar_field authority provenance is invalid")
    value = claim.value
    if type(value) is not dict or set(value) != {
        "quantity_kind",
        "value",
        "unit",
        "valid_range",
        "reference_frame",
        "point_m",
    }:
        raise LocalReadBridgeError("finite_scalar_field payload does not match its approved shape")
    if (
        value["quantity_kind"] != "dimensionless_scalar_field"
        or value["unit"] != "1"
        or value["valid_range"] != (0.0, 1.0)
        or type(value["value"]) not in (float, int)
        or not 0.0 <= value["value"] <= 1.0
        or not _finite_vector(value["point_m"], length=3)
        or not _nonempty_text(value["reference_frame"])
    ):
        raise LocalReadBridgeError("finite_scalar_field value or units are invalid")
    if not all(kind in identities for kind in ("environment", "environment_resource")):
        raise LocalReadBridgeError("finite_scalar_field is missing typed resource identity")
    if not all(
        any(
            item.domain is AuthorityDomain.WORLD
            and item.kind == kind
            and type(item.value) is int
            for item in observation.context_time
        )
        for kind in ("world_source_causal_tick", "world_target_causal_tick")
    ):
        raise LocalReadBridgeError("finite_scalar_field is missing World causal context")
    if not any(
        parent.namespace == "owner_checkpoint_sha256" and _is_sha256(parent.reference)
        for parent in observation.lineage.parents
    ):
        raise LocalReadBridgeError("finite_scalar_field is missing owner-checkpoint provenance")
    transformation = observation.lineage.transformation
    if (
        transformation is None
        or transformation.transformation_id
        != "environment.finite_scalar_field.project_observation"
        or not {
            "world_id",
            "physical_step_id",
            "field_revision",
            "environment_revision",
            "frame_id",
        }.issubset(dict(transformation.effective_configuration))
    ):
        raise LocalReadBridgeError("finite_scalar_field is missing its source transformation")


def _finite_vector(value: object, *, length: int) -> bool:
    return (
        type(value) in (tuple, list)
        and len(value) == length
        and all(_finite_number(component) for component in value)
    )


def _validate_static_source_envelope(observation, *, subject_kind: str, identities: dict[str, str], digest: str) -> None:
    """Bind the carrier envelope to source values without asserting cross-domain meaning."""
    if observation.claim.subject.kind != subject_kind:
        raise LocalReadBridgeError("static projection subject does not match source identity")
    actual = {
        assertion.identity.kind: assertion.identity.value
        for assertion in observation.claim.subject.identities
    }
    if len(actual) != len(observation.claim.subject.identities) or actual != identities:
        raise LocalReadBridgeError("static projection subject identities do not match payload")
    parents = observation.lineage.parents
    if (
        len(parents) != 1
        or parents[0].namespace != "render_geometry_sha256"
        or parents[0].reference != digest
    ):
        raise LocalReadBridgeError("static projection lineage does not bind payload digest")
    transformation = observation.lineage.transformation
    if transformation is None:
        raise LocalReadBridgeError("static projection is missing transformation lineage")
    config_pairs = transformation.effective_configuration
    config = dict(config_pairs)
    if len(config_pairs) != len(identities) or config != identities:
        raise LocalReadBridgeError("static projection transformation identity does not match payload")
    # Transformation id/revision and acquisition/actor details are not emitted
    # by either owner descriptor. They are preserved but not mapped here.


def _finite_number(value: object) -> bool:
    if type(value) not in (int, float):
        return False
    try:
        return math.isfinite(float(value))
    except (OverflowError, ValueError):
        return False


def _bounded_text(value: object, *, limit: int = 128) -> bool:
    if not isinstance(value, str) or not value:
        return False
    try:
        encoded = value.encode("utf-8", errors="strict")
    except UnicodeEncodeError:
        return False
    return len(encoded) <= limit and not any(
        ord(char) <= 0x1F or 0x7F <= ord(char) <= 0x9F for char in value
    )


def _validate_embodiment_render_link_pose(value: object) -> None:
    """Validate the closed passive carrier, not the truth of World association."""
    if type(value) is not dict or set(value) != {"candidate", "world_association"}:
        raise LocalReadBridgeError("render_link_pose carrier does not match its closed shape")
    if len(json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")) > 384 * 1024:
        raise LocalReadBridgeError("render_link_pose carrier exceeds its approved bound")
    candidate, association = value["candidate"], value["world_association"]
    candidate_fields = {
        "contract_revision", "body_id", "embodiment_episode_id", "morphology_revision",
        "geometry_revision", "render_geometry_sha256", "source_world_id", "physical_step_id",
        "environment_revision", "solver_config_revision", "source_causal_tick", "target_causal_tick",
        "reference_frame", "coordinate_system", "length_unit", "completeness", "poses",
    }
    if type(candidate) is not dict or set(candidate) != candidate_fields:
        raise LocalReadBridgeError("render_link_pose candidate does not match its approved shape")
    if (
        candidate["contract_revision"] != "embodiment.render_link_pose_candidate/v1"
        or candidate["reference_frame"] != "physics3d.world"
        or candidate["coordinate_system"] != "right_handed_z_up"
        or candidate["length_unit"] != "m"
        or candidate["completeness"] != "complete"
        or any(not _source_identifier(candidate[field]) for field in (
            "body_id", "embodiment_episode_id", "morphology_revision", "geometry_revision",
            "source_world_id", "physical_step_id", "environment_revision", "solver_config_revision",
        ))
        or not _is_sha256(candidate["render_geometry_sha256"])
        or type(candidate["source_causal_tick"]) is not int
        or type(candidate["target_causal_tick"]) is not int
        or candidate["source_causal_tick"] < 0
        or candidate["target_causal_tick"] != candidate["source_causal_tick"] + 1
    ):
        raise LocalReadBridgeError("render_link_pose candidate identity or contract is invalid")
    poses = candidate["poses"]
    if type(poses) is not list or len(poses) > 128:
        raise LocalReadBridgeError("render_link_pose items exceed the approved bound")
    segment_ids: list[str] = []
    for pose in poses:
        if type(pose) is not dict or set(pose) != {"segment_id", "translation_m", "orientation_xyzw"}:
            raise LocalReadBridgeError("render_link_pose item shape is invalid")
        translation, orientation = pose["translation_m"], pose["orientation_xyzw"]
        if (
            not _source_identifier(pose["segment_id"])
            or not _finite_vector(translation, length=3)
            or not _finite_vector(orientation, length=4)
            # Match Embodiment RenderLinkPose's norm tolerance (1e-6), not a
            # stricter squared-norm check that rejects valid owner payloads.
            or not math.isclose(math.sqrt(sum(c*c for c in orientation)), 1.0, rel_tol=0.0, abs_tol=1e-6)
        ):
            raise LocalReadBridgeError("render_link_pose item values are invalid")
        segment_ids.append(pose["segment_id"])
    if segment_ids != sorted(set(segment_ids), key=lambda item: item.encode("utf-8")):
        raise LocalReadBridgeError("render_link_pose segment identities must be unique and sorted")
    if type(association) is not dict or set(association) != {
        "association_kind", "projection_sha256", "committed_cut", "owner_checkpoint_reference"
    } or association["association_kind"] != "transient_current_committed_cut":
        raise LocalReadBridgeError("render_link_pose World association does not match its closed shape")
    cut, checkpoint = association["committed_cut"], association["owner_checkpoint_reference"]
    if type(cut) is not dict or set(cut) != {
        "world_id", "causal_tick", "commit_id", "participant_ids", "presence_owner_links", "owner_checkpoint_references"
    }:
        raise LocalReadBridgeError("render_link_pose committed-cut metadata is malformed")
    if (
        not _source_identifier(cut["world_id"]) or not _source_identifier(cut["commit_id"])
        or type(cut["causal_tick"]) is not int or cut["causal_tick"] < 1
        or cut["world_id"] != candidate["source_world_id"]
        or cut["causal_tick"] != candidate["target_causal_tick"]
    ):
        raise LocalReadBridgeError("render_link_pose candidate differs from associated World cut")
    if type(checkpoint) is not dict or set(checkpoint) != {
        "owner", "owner_identity", "checkpoint_id", "schema_version", "locator", "sha256"
    }:
        raise LocalReadBridgeError("render_link_pose checkpoint reference is malformed")
    if (
        checkpoint["owner"] != "embodiment"
        or checkpoint["owner_identity"] != candidate["body_id"]
        or any(not _source_identifier(checkpoint[field]) for field in ("checkpoint_id", "schema_version"))
        or not _checkpoint_locator(checkpoint["locator"])
        or not _is_sha256(checkpoint["sha256"])
        or not _is_sha256(association["projection_sha256"])
    ):
        raise LocalReadBridgeError("render_link_pose checkpoint identity or digest is invalid")
    references = cut["owner_checkpoint_references"]
    checkpoint_fields = {"owner", "owner_identity", "checkpoint_id", "schema_version", "locator", "sha256"}
    if type(references) is not list or not all(
        type(item) is dict and set(item) == checkpoint_fields
        and all(_source_identifier(item[field]) for field in checkpoint_fields - {"sha256", "locator"})
        and _checkpoint_locator(item["locator"])
        and _is_sha256(item["sha256"])
        for item in references
    ):
        raise LocalReadBridgeError("render_link_pose cut checkpoint references are malformed")
    if references.count(checkpoint) != 1:
        raise LocalReadBridgeError("render_link_pose checkpoint is not exactly one cut member")
    if type(cut["participant_ids"]) is not list or type(cut["presence_owner_links"]) is not list:
        raise LocalReadBridgeError("render_link_pose committed-cut members are malformed")
    if (
        any(type(item) is not list or len(item) != 2 or any(not _source_identifier(v) for v in item)
            for item in cut["participant_ids"])
        or any(type(item) is not list or len(item) != 3 or any(not _source_identifier(v) for v in item)
               for item in cut["presence_owner_links"])
    ):
        raise LocalReadBridgeError("render_link_pose committed-cut member identities are malformed")
    canonical = rfc8785.dumps(candidate)
    if hashlib.sha256(canonical).hexdigest() != association["projection_sha256"]:
        raise LocalReadBridgeError("render_link_pose candidate digest differs from World association")
    if candidate["body_id"] != checkpoint["owner_identity"]:
        raise LocalReadBridgeError("render_link_pose body differs from associated checkpoint")


def _nonempty_text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _source_identifier(value: object) -> bool:
    return _bounded_text(value) and value == value.strip()


def _checkpoint_locator(value: object) -> bool:
    """Accept bounded checkpoint references without treating paths as identifiers."""
    # Paths are opaque source strings, not identifiers: preserve ordinary leading
    # and trailing spaces (valid in POSIX filenames) rather than normalizing them.
    if not isinstance(value, str) or not value:
        return False
    try:
        encoded = value.encode("utf-8", errors="strict")
    except UnicodeEncodeError:
        return False
    return len(encoded) <= 4096 and not any(
        ord(char) <= 0x1F or 0x7F <= ord(char) <= 0x9F for char in value
    )


def _is_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        character in "0123456789abcdef" for character in value
    )


class LocalObservationHTTPServer(ThreadingHTTPServer):
    """HTTP server restricted to loopback and one exact browser Origin."""

    daemon_threads = True
    allow_reuse_address = False

    def __init__(
        self,
        plane: ObservationPlane,
        *,
        host: str = "127.0.0.1",
        port: int = 4174,
        allowed_origin: str = "http://127.0.0.1:4173",
        max_response_bytes: int = DEFAULT_MAX_RESPONSE_BYTES,
    ) -> None:
        try:
            address = ipaddress.ip_address(host)
        except ValueError as exc:
            raise ValueError("bridge host must be a literal loopback IP address") from exc
        if not address.is_loopback:
            raise ValueError("bridge may bind only to a loopback address")
        parsed_origin = urlsplit(allowed_origin)
        if (
            parsed_origin.scheme != "http"
            or not parsed_origin.hostname
            or parsed_origin.path
            or parsed_origin.query
            or parsed_origin.fragment
            or parsed_origin.username
            or parsed_origin.password
        ):
            raise ValueError("allowed_origin must be one exact local HTTP origin")
        try:
            origin_address = ipaddress.ip_address(parsed_origin.hostname)
        except ValueError as exc:
            raise ValueError("allowed_origin host must be a literal loopback IP address") from exc
        if not origin_address.is_loopback:
            raise ValueError("allowed_origin must be a loopback origin")
        if type(max_response_bytes) is not int or max_response_bytes < 1:
            raise ValueError("max_response_bytes must be a positive integer")
        self.plane = plane
        self.allowed_origin = allowed_origin
        self.max_response_bytes = max_response_bytes
        host_header = f"[{host}]" if address.version == 6 else host
        self.expected_host = f"{host_header}:{port}" if port else None
        super().__init__((host, port), _make_handler())
        if port == 0:
            self.expected_host = f"{host_header}:{self.server_port}"


def _make_handler() -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"
        server_version = "BiopeiaObservationLocal/1"
        sys_version = ""

        def log_message(self, format: str, *args: object) -> None:
            # Avoid writing request paths and headers to shared logs.
            return

        def _reply(self, status: int, body: bytes, *, content_type: str = "application/json") -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(body)
            self.close_connection = True

        def _error(self, status: int, code: str) -> None:
            self._reply(status, json.dumps({"error": code}, separators=(",", ":")).encode())

        def _validate_request(self) -> bool:
            if self.headers.get("Host") != self.server.expected_host:  # type: ignore[attr-defined]
                self._error(400, "invalid_host")
                return False
            if self.headers.get("Origin") != self.server.allowed_origin:  # type: ignore[attr-defined]
                self._error(403, "origin_denied")
                return False
            if self.headers.get("Transfer-Encoding") is not None:
                self._error(400, "request_body_not_supported")
                return False
            content_length = self.headers.get("Content-Length")
            if content_length not in (None, "0"):
                self._error(400, "request_body_not_supported")
                return False
            return True

        def do_GET(self) -> None:
            if not self._validate_request():
                return
            if self.path != "/v1/current":
                self._error(404, "not_found")
                return
            try:
                body = encode_current_messages(
                    self.server.plane,  # type: ignore[attr-defined]
                    max_response_bytes=self.server.max_response_bytes,  # type: ignore[attr-defined]
                )
            except ResponseTooLargeError:
                self._error(413, "current_view_exceeds_response_limit")
                return
            except (LocalReadBridgeError, TypeError, ValueError):
                self._error(503, "current_view_unavailable")
                return
            self._reply(200, body)

        def do_HEAD(self) -> None:
            self._error(405, "method_not_allowed")

        def do_POST(self) -> None:
            self._error(405, "method_not_allowed")

        def do_PUT(self) -> None:
            self._error(405, "method_not_allowed")

        def do_PATCH(self) -> None:
            self._error(405, "method_not_allowed")

        def do_DELETE(self) -> None:
            self._error(405, "method_not_allowed")

        def do_OPTIONS(self) -> None:
            self._error(405, "method_not_allowed")

    return Handler


class LocalObservationReadBridge:
    """Manage the HTTP thread for one existing ObservationPlane."""

    def __init__(self, server: LocalObservationHTTPServer) -> None:
        self.server = server
        self._thread: Thread | None = None

    @classmethod
    def create(
        cls,
        plane: ObservationPlane,
        *,
        host: str = "127.0.0.1",
        port: int = 4174,
        allowed_origin: str = "http://127.0.0.1:4173",
        max_response_bytes: int = DEFAULT_MAX_RESPONSE_BYTES,
    ) -> LocalObservationReadBridge:
        return cls(LocalObservationHTTPServer(
            plane,
            host=host,
            port=port,
            allowed_origin=allowed_origin,
            max_response_bytes=max_response_bytes,
        ))

    @property
    def address(self) -> tuple[str, int]:
        return (str(self.server.server_address[0]), int(self.server.server_address[1]))

    def start(self) -> LocalObservationReadBridge:
        if self._thread is not None and self._thread.is_alive():
            raise RuntimeError("local observation bridge is already running")
        self._thread = Thread(target=self.server.serve_forever, name="observation-local-read", daemon=True)
        self._thread.start()
        return self

    def close(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            self.server.shutdown()
            self._thread.join(timeout=2)
        self.server.server_close()

    def __enter__(self) -> LocalObservationReadBridge:
        return self.start()

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()


__all__ = [
    "APPROVED_FAMILIES",
    "DEFAULT_MAX_RESPONSE_BYTES",
    "LocalObservationHTTPServer",
    "LocalObservationReadBridge",
    "LocalReadBridgeError",
    "encode_current_messages",
]

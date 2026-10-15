"""Closed validators for approved static spatial projection contracts.

These checks are shared by the in-process adapters and the local HTTP bridge so
invalid owner data cannot enter an ObservationPlane through a public adapter.
"""
from __future__ import annotations

import hashlib
import json
import math
import rfc8785


def _finite_number(value: object) -> bool:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(float(value))
    except (OverflowError, ValueError):
        return False


def _finite_vector(value: object, *, length: int) -> bool:
    return (type(value) in (list, tuple) and len(value) == length
            and all(_finite_number(component) for component in value))


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


def _source_identifier(value: object) -> bool:
    return _bounded_text(value) and value == value.strip()


def _is_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        character in "0123456789abcdef" for character in value
    )


def validate_environment_render_scene(value: object) -> None:
    """Check the closed Environment v1 static-scene projection without reinterpretation."""
    if type(value) is not dict or set(value) != {
        "schema_version", "environment_id", "environment_revision", "length_unit",
        "frame", "items", "render_geometry_sha256",
    }:
        raise ValueError("render_scene payload does not match its approved shape")
    if len(json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")) > 65_536:
        raise ValueError("render_scene descriptor exceeds the owner bound")
    if (
        type(value["schema_version"]) is not int or value["schema_version"] != 1
        or value["length_unit"] != "m"
        or not _bounded_text(value["environment_id"])
        or not _bounded_text(value["environment_revision"])
        or not _is_sha256(value["render_geometry_sha256"])
    ):
        raise ValueError("render_scene schema identity or digest is invalid")
    frame = value["frame"]
    if type(frame) is not dict or set(frame) != {
        "frame_id", "parent_frame_id", "origin_m", "x_axis_in_parent",
        "y_axis_in_parent", "z_axis_in_parent", "handedness", "up_axis",
    }:
        raise ValueError("render_scene frame does not match its approved shape")
    if (
        not _bounded_text(frame["frame_id"])
        or not _bounded_text(frame["parent_frame_id"])
        or any(not _finite_vector(frame[field], length=3) for field in (
            "origin_m", "x_axis_in_parent", "y_axis_in_parent", "z_axis_in_parent"
        ))
        or frame["handedness"] != "RIGHT_HANDED"
        or frame["up_axis"] not in ("X", "Y", "Z")
    ):
        raise ValueError("render_scene frame values are invalid")
    axes = [frame[name] for name in ("x_axis_in_parent", "y_axis_in_parent", "z_axis_in_parent")]
    if any(not math.isclose(sum(c*c for c in axis), 1.0, rel_tol=0.0, abs_tol=1e-9) for axis in axes):
        raise ValueError("render_scene frame axes must be unit vectors")
    if any(not math.isclose(sum(a*b for a, b in zip(axes[i], axes[j])), 0.0, rel_tol=0.0, abs_tol=1e-9)
           for i, j in ((0, 1), (0, 2), (1, 2))):
        raise ValueError("render_scene frame axes must be orthogonal")
    cross = (axes[0][1]*axes[1][2]-axes[0][2]*axes[1][1], axes[0][2]*axes[1][0]-axes[0][0]*axes[1][2], axes[0][0]*axes[1][1]-axes[0][1]*axes[1][0])
    if not all(math.isclose(c, z, rel_tol=0.0, abs_tol=1e-9) for c, z in zip(cross, axes[2])):
        raise ValueError("render_scene frame axes must be right-handed")
    items = value["items"]
    if type(items) is not list or len(items) > 128:
        raise ValueError("render_scene items exceed the approved bound")
    ids: list[str] = []
    for item in items:
        if type(item) is not dict or item.get("kind") not in ("ground_plane", "sphere"):
            raise ValueError("render_scene item kind is not approved")
        common = {"object_id", "kind", "frame_id"}
        expected = common | ({"normal", "offset_m"} if item["kind"] == "ground_plane" else {"center_m", "radius_m"})
        if set(item) != expected:
            raise ValueError("render_scene item does not match its approved shape")
        if not _bounded_text(item["object_id"]) or item["frame_id"] != frame["frame_id"]:
            raise ValueError("render_scene item identity or frame is invalid")
        ids.append(item["object_id"])
        if item["kind"] == "ground_plane":
            if (not _finite_vector(item["normal"], length=3) or not _finite_number(item["offset_m"])
                or not math.isclose(math.sqrt(sum(c*c for c in item["normal"])), 1.0, rel_tol=0.0, abs_tol=1e-9)):
                raise ValueError("render_scene plane values are invalid")
        elif (
            not _finite_vector(item["center_m"], length=3)
            or not _finite_number(item["radius_m"])
            or item["radius_m"] <= 0
        ):
            raise ValueError("render_scene sphere values are invalid")
    if ids != sorted(set(ids), key=lambda item: item.encode("utf-8")):
        raise ValueError("render_scene item identities must be unique and sorted")
    digest = hashlib.sha256(rfc8785.dumps({key: item for key, item in value.items() if key != "render_geometry_sha256"})).hexdigest()
    if digest != value["render_geometry_sha256"]:
        raise ValueError("render_scene digest does not match canonical payload")


def validate_embodiment_render_morphology(value: object) -> None:
    """Check the closed Embodiment v1 static morphology projection."""
    if type(value) is not dict or set(value) != {
        "contract_revision", "schema_version", "body_id", "embodiment_episode_id",
        "morphology_revision", "geometry_revision", "render_geometry_sha256",
        "coordinate_system", "length_unit", "segments", "joints",
    }:
        raise ValueError("render_morphology payload does not match its approved shape")
    if len(json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")) > 256 * 1024:
        raise ValueError("render_morphology descriptor exceeds the owner bound")
    if (
        value["contract_revision"] != "embodiment.render_morphology/v1"
        or type(value["schema_version"]) is not int or value["schema_version"] != 1
        or value["coordinate_system"] != "right_handed_z_up"
        or value["length_unit"] != "m"
        or any(not _source_identifier(value[field]) for field in (
            "body_id", "embodiment_episode_id", "morphology_revision", "geometry_revision"
        ))
        or not _is_sha256(value["render_geometry_sha256"])
    ):
        raise ValueError("render_morphology identity, schema, or digest is invalid")
    segments, joints = value["segments"], value["joints"]
    if type(segments) is not list or len(segments) > 128 or type(joints) is not list or len(joints) > 127:
        raise ValueError("render_morphology items exceed the approved bounds")
    segment_ids: list[str] = []
    for segment in segments:
        if type(segment) is not dict or set(segment) != {
            "segment_id", "shape", "dimensions_m", "visual_origin_in_link_m"
        }:
            raise ValueError("render_morphology segment shape is invalid")
        dims = segment["dimensions_m"]
        if (
            not _bounded_text(segment["segment_id"]) or segment["shape"] != "box"
            or not _finite_vector(dims, length=3) or any(component <= 0 for component in dims)
            or not _finite_vector(segment["visual_origin_in_link_m"], length=3)
        ):
            raise ValueError("render_morphology segment values are invalid")
        segment_ids.append(segment["segment_id"])
    joint_ids: list[str] = []
    for joint in joints:
        if type(joint) is not dict or set(joint) != {
            "joint_id", "parent_link_id", "child_link_id", "joint_type",
            "joint_origin_in_parent_m", "axis_in_joint_frame",
        }:
            raise ValueError("render_morphology joint shape is invalid")
        axis = joint["axis_in_joint_frame"]
        if (
            any(not _bounded_text(joint[field]) for field in ("joint_id", "parent_link_id", "child_link_id"))
            or joint["parent_link_id"] == joint["child_link_id"]
            or joint["joint_type"] != "revolute"
            or not _finite_vector(joint["joint_origin_in_parent_m"], length=3)
            or not _finite_vector(axis, length=3)
            or not math.isclose(math.sqrt(sum(component * component for component in axis)), 1.0, rel_tol=0.0, abs_tol=1e-9)
        ):
            raise ValueError("render_morphology joint values are invalid")
        joint_ids.append(joint["joint_id"])
    links = set(segment_ids)
    for joint in joints:
        links.update((joint["parent_link_id"], joint["child_link_id"]))
    if (
        segment_ids != sorted(set(segment_ids)) or joint_ids != sorted(set(joint_ids))
        or len(links) > 128
    ):
        raise ValueError("render_morphology identities exceed approved limits")
    digest_fields = {key: value[key] for key in ("contract_revision", "schema_version", "coordinate_system", "length_unit", "segments", "joints")}
    digest = hashlib.sha256(b"biopeia:embodiment.render_morphology/v1\n" + rfc8785.dumps(digest_fields)).hexdigest()
    if digest != value["render_geometry_sha256"]:
        raise ValueError("render_morphology digest does not match canonical payload")



"""Receptor-array vision channel (ADR-0011).

A square array of receptors rigidly mounted on a body link: physics world →
receptor array → bounded luminance per opaque receptor. The channel reads only
simulation state, handed to it as plain data, through its own deterministic CPU
ray caster over primitive geometry (ADR-0066); it imports no engine. It never reads
observer geometry, world_scene entities, the presentation camera or wall-clock
time, and it never emits depth, segmentation, entity identity or colour-channel
names. Which link carries the array, where on it, and under which receptor ids
is supplied by whoever mounts it; this module knows no body.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

VISUAL_ARRAY_SIDE = 12
VISUAL_RECEPTOR_COUNT = VISUAL_ARRAY_SIDE * VISUAL_ARRAY_SIDE


@dataclass(frozen=True, slots=True)
class PerceptualTopology:
    """Physical receptor adjacency as neighbour lists over opaque ids only."""

    neighbours: Mapping[str, tuple[str, ...]]

    @classmethod
    def grid(cls, ids_by_position: tuple[str, ...], side: int) -> PerceptualTopology:
        neighbours: dict[str, tuple[str, ...]] = {}
        for index, receptor_id in enumerate(ids_by_position):
            row, col = divmod(index, side)
            adjacent = [
                ids_by_position[r * side + c]
                for r, c in ((row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1))
                if 0 <= r < side and 0 <= c < side
            ]
            neighbours[receptor_id] = tuple(sorted(adjacent))
        return cls(neighbours=dict(sorted(neighbours.items())))

    def as_dict(self) -> dict[str, list[str]]:
        return {key: list(value) for key, value in self.neighbours.items()}


# One primitive of the scene: (kind, world position, world rotation as nine
# row-major values, size, luminance in [0, 1]).  Sizes follow the usual
# conventions: sphere (radius,), capsule and cylinder (radius, half-length
# along local z), box (three half-extents), plane (unused; local z = 0).
Primitive = tuple[str, Sequence[float], Sequence[float], Sequence[float], float]

# Luminance model.  Provisional: ADR-0066 leaves it to a calibration study.
BACKGROUND_LUMINANCE = 0.8
AMBIENT_FRACTION = 0.4
LIGHT_DIRECTION = (0.3, 0.2, 1.0)  # towards the light, world frame


def _sphere(np, o, d, radius):
    a = (d * d).sum(1)
    b = (o * d).sum(1)
    disc = b * b - a * ((o * o).sum(1) - radius * radius)
    t = np.where(disc >= 0.0, (-b - np.sqrt(np.maximum(disc, 0.0))) / a, np.inf)
    return t, (o + t[:, None] * d) / radius


def _tube(np, o, d, radius, half):
    """Side surface of a z-aligned cylinder, without its end faces."""
    a = np.maximum((d[:, :2] ** 2).sum(1), 1e-18)
    b = (o[:, :2] * d[:, :2]).sum(1)
    disc = b * b - a * ((o[:, :2] ** 2).sum(1) - radius * radius)
    t = np.where(disc >= 0.0, (-b - np.sqrt(np.maximum(disc, 0.0))) / a, np.inf)
    point = o + t[:, None] * d
    t = np.where(np.abs(point[:, 2]) <= half, t, np.inf)
    normal = point / radius
    normal[:, 2] = 0.0
    return t, normal


def _nearest(np, hits):
    t, normal = hits[0]
    for other_t, other_normal in hits[1:]:
        closer = other_t < t
        t = np.where(closer, other_t, t)
        normal = np.where(closer[:, None], other_normal, normal)
    return t, normal


def _intersect(np, kind, size, o, d):
    """First hit of each ray with one primitive in its own frame: (t, normal).

    ``t`` is in units of ``d`` and is infinite where the ray misses, starts
    inside the primitive or meets it behind the origin.
    """
    with np.errstate(divide="ignore", invalid="ignore"):
        if kind == "plane":
            t = np.where((d[:, 2] < 0.0) & (o[:, 2] > 0.0), -o[:, 2] / d[:, 2], np.inf)
            normal = np.zeros_like(d)
            normal[:, 2] = 1.0
        elif kind == "sphere":
            t, normal = _sphere(np, o, d, size[0])
        elif kind == "box":
            half = np.asarray(size[:3], dtype=float)
            safe = np.where(np.abs(d) < 1e-12, 1e-12, d)
            near = np.minimum((-half - o) / safe, (half - o) / safe)
            far = np.maximum((-half - o) / safe, (half - o) / safe)
            t = near.max(1)
            axis = near.argmax(1)
            t = np.where(far.min(1) >= t, t, np.inf)
            normal = np.zeros_like(d)
            rows = np.arange(len(d))
            normal[rows, axis] = -np.sign(safe[rows, axis])
        elif kind == "cylinder":
            radius, half = size[0], size[1]
            hits = [_tube(np, o, d, radius, half)]
            for sign in (1.0, -1.0):
                t = (sign * half - o[:, 2]) / d[:, 2]
                point = o + t[:, None] * d
                inside = (point[:, :2] ** 2).sum(1) <= radius * radius
                t = np.where(inside & (d[:, 2] * sign < 0.0), t, np.inf)
                normal = np.zeros_like(d)
                normal[:, 2] = sign
                hits.append((t, normal))
            t, normal = _nearest(np, hits)
        elif kind == "capsule":
            radius, half = size[0], size[1]
            hits = [_tube(np, o, d, radius, half)]
            for sign in (1.0, -1.0):
                centre = np.array([0.0, 0.0, sign * half])
                hits.append(_sphere(np, o - centre, d, radius))
            t, normal = _nearest(np, hits)
        else:
            raise ValueError(f"vision cannot sample geometry of kind {kind!r}")
    return np.where(np.isfinite(t) & (t > 0.0), t, np.inf), normal


class VisualApparatus:
    """One receptor array rigidly mounted on a body link.

    ``geometry()`` returns the scene's primitives and ``mount_pose()`` the
    carrying link's world position and rotation (nine row-major values), both
    as plain data for the current simulation state.
    """

    FIELD_OF_VIEW_DEG = 70.0
    NEAR = 0.02
    FAR = 8.0

    def __init__(
        self,
        *,
        geometry: Callable[[], Iterable[Primitive]],
        mount_pose: Callable[[], tuple[Sequence[float], Sequence[float]]],
        receptor_ids: tuple[str, ...],
        mount_offset: tuple[float, float, float],
        gaze_offset: tuple[float, float, float],
        side: int = VISUAL_ARRAY_SIDE,
    ) -> None:
        if len(receptor_ids) != side * side:
            raise ValueError("visual receptor ids must cover the complete array")
        import numpy

        self.np: Any = numpy
        self.geometry = geometry
        self.mount_pose = mount_pose
        self.side = side
        # Mount point and gaze target in the carrying link's frame (metres).
        self.mount_offset = mount_offset
        self.gaze_offset = gaze_offset
        self.receptor_ids = receptor_ids
        self.topology = PerceptualTopology.grid(receptor_ids, side)
        # Receptor centres on the image plane at unit depth, rows top to bottom.
        extent = math.tan(math.radians(self.FIELD_OF_VIEW_DEG) / 2.0)
        centres = (numpy.arange(side) + 0.5) / side * 2.0 - 1.0
        self._across = numpy.tile(centres * extent, side)
        self._upward = numpy.repeat(-centres * extent, side)
        light = numpy.asarray(LIGHT_DIRECTION, dtype=float)
        self._light = light / numpy.linalg.norm(light)
        # Observer correlation key (gap §25); never an organism signal.
        self.sample_index = 0

    def _rays(self):
        """Eye position and one direction per receptor, with unit forward depth."""
        np = self.np
        position, rotation = self.mount_pose()
        position = np.asarray(position, dtype=float)
        rotation = np.asarray(rotation, dtype=float).reshape(3, 3)
        eye = position + rotation @ np.asarray(self.mount_offset, dtype=float)
        forward = position + rotation @ np.asarray(self.gaze_offset, dtype=float) - eye
        forward /= np.linalg.norm(forward)
        right = np.cross(forward, rotation[:, 2])
        right /= np.linalg.norm(right)
        up = np.cross(right, forward)
        return eye, forward + self._across[:, None] * right + self._upward[:, None] * up

    def sample(self) -> dict[str, float]:
        np = self.np
        eye, directions = self._rays()
        depth = np.full(len(directions), self.FAR)
        luminance = np.full(len(directions), BACKGROUND_LUMINANCE)
        for kind, position, rotation, size, albedo in self.geometry():
            frame = np.asarray(rotation, dtype=float).reshape(3, 3)
            origin = np.broadcast_to(
                (eye - np.asarray(position, dtype=float)) @ frame, directions.shape
            )
            t, normal = _intersect(np, kind, size, origin, directions @ frame)
            closer = (t >= self.NEAR) & (t < depth)
            if not closer.any():
                continue
            normal = np.where(closer[:, None], normal, 0.0)  # misses carry no normal
            lit = np.maximum(0.0, (normal @ frame.T) @ self._light)
            shade = AMBIENT_FRACTION + (1.0 - AMBIENT_FRACTION) * lit
            depth = np.where(closer, t, depth)
            luminance = np.where(closer, float(albedo) * shade, luminance)
        values = np.clip(luminance, 0.0, 1.0).tolist()
        self.sample_index += 1
        return dict(zip(self.receptor_ids, values))


__all__ = [
    "AMBIENT_FRACTION",
    "BACKGROUND_LUMINANCE",
    "LIGHT_DIRECTION",
    "Primitive",
    "VISUAL_ARRAY_SIDE",
    "VISUAL_RECEPTOR_COUNT",
    "PerceptualTopology",
    "VisualApparatus",
]

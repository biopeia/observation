"""The receptor array samples primitive geometry with no physics engine (ADR-0066)."""

from __future__ import annotations

import pytest

from modality.vision import AMBIENT_FRACTION, BACKGROUND_LUMINANCE, VisualApparatus

IDENTITY = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)
SIDE = 4


def _sample(*primitives) -> list[list[float]]:
    """Rows top to bottom, looking along +x from the origin with +z up."""
    pytest.importorskip("numpy")
    ids = tuple(f"rec.{index}" for index in range(SIDE * SIDE))
    apparatus = VisualApparatus(
        geometry=lambda: primitives,
        mount_pose=lambda: ((0.0, 0.0, 0.0), IDENTITY),
        receptor_ids=ids,
        mount_offset=(0.0, 0.0, 0.0),
        gaze_offset=(1.0, 0.0, 0.0),
        side=SIDE,
    )
    values = apparatus.sample()
    assert tuple(values) == ids
    assert all(0.0 <= value <= 1.0 for value in values.values())
    return [[values[ids[row * SIDE + col]] for col in range(SIDE)] for row in range(SIDE)]


def test_empty_scene_is_uniform_background() -> None:
    assert _sample() == [[BACKGROUND_LUMINANCE] * SIDE] * SIDE


def test_ground_fills_the_lower_half_only() -> None:
    rows = _sample(("plane", (0.0, 0.0, -1.0), IDENTITY, (0.0, 0.0, 1.0), 0.5))
    assert rows[0] == [BACKGROUND_LUMINANCE] * SIDE
    # The nearest ground row is in range; its upward normal is mostly lit.
    assert all(AMBIENT_FRACTION * 0.5 < value < 0.5 for value in rows[-1])


@pytest.mark.parametrize(
    ("kind", "size"),
    [
        ("sphere", (0.8, 0.0, 0.0)),
        ("box", (0.8, 0.8, 0.8)),
        ("cylinder", (0.8, 0.8, 0.0)),
        ("capsule", (0.8, 0.4, 0.0)),
    ],
)
def test_a_dark_object_ahead_covers_the_centre_and_not_the_corners(kind, size) -> None:
    rows = _sample((kind, (3.0, 0.0, 0.0), IDENTITY, size, 0.1))
    centre = [rows[row][col] for row in (1, 2) for col in (1, 2)]
    assert all(value <= 0.1 for value in centre)
    assert rows[0][0] == rows[0][-1] == rows[-1][0] == rows[-1][-1] == BACKGROUND_LUMINANCE


def test_nearer_geometry_occludes_and_out_of_range_geometry_is_not_seen() -> None:
    near = ("box", (2.0, 0.0, 0.0), IDENTITY, (0.1, 5.0, 5.0), 0.0)
    behind = ("box", (4.0, 0.0, 0.0), IDENTITY, (0.1, 5.0, 5.0), 1.0)
    beyond = ("box", (20.0, 0.0, 0.0), IDENTITY, (0.1, 50.0, 50.0), 0.0)
    assert _sample(behind, near) == [[0.0] * SIDE] * SIDE
    assert _sample(beyond) == [[BACKGROUND_LUMINANCE] * SIDE] * SIDE


def test_a_rotated_primitive_is_sampled_in_its_own_frame() -> None:
    # A long thin box lying along world y after a quarter turn about z.
    quarter_turn = (0.0, -1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0)
    rows = _sample(("box", (3.0, 0.0, 0.0), quarter_turn, (5.0, 0.1, 0.8), 0.0))
    assert rows[1] == rows[2] == [0.0] * SIDE
    assert rows[0] == rows[3] == [BACKGROUND_LUMINANCE] * SIDE

"""Non-semantic physical resource for Physics3D locomotion experiments."""

from __future__ import annotations

import math
from collections.abc import Collection, Mapping
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class ContactMaterial:
    """How a world object behaves on contact, in the environment's own terms."""

    lateral_friction: float
    spinning_friction: float
    rolling_friction: float
    restitution: float
    linear_damping: float
    angular_damping: float


RESOURCE_MATERIAL = ContactMaterial(
    lateral_friction=0.72,
    spinning_friction=0.02,
    rolling_friction=0.003,
    restitution=0.01,
    linear_damping=0.0,
    angular_damping=0.0,
)


@dataclass(slots=True)
class PhysicalResource:
    """Finite static material source with a local scalar field.

    The object owns world truth. The organism may receive only field magnitude
    through an opaque receptor and scalar absorbed material after physical
    contact.
    """

    scene: Any = field(repr=False, compare=False)
    position: tuple[float, float, float] = (3.0, 0.0, 0.18)
    radius: float = 0.18
    field_radius: float = 6.0
    remaining: float = 200.0
    transfer_per_tick: float = 2.0

    BODY_NAME = "resource"

    def __post_init__(self) -> None:
        if self.radius <= 0.0 or self.field_radius <= self.radius:
            raise ValueError("invalid physical resource geometry")
        if self.remaining < 0.0 or self.transfer_per_tick <= 0.0:
            raise ValueError("invalid physical resource capacity")
        scene = self.scene
        body = scene.spec.worldbody.add_body(name=self.BODY_NAME, pos=list(self.position))
        body.add_geom(
            type=scene.mj.mjtGeom.mjGEOM_SPHERE,
            size=[self.radius, 0.0, 0.0],
            rgba=[0.52, 0.78, 0.36, 1.0],
            friction=[
                RESOURCE_MATERIAL.lateral_friction,
                RESOURCE_MATERIAL.spinning_friction,
                RESOURCE_MATERIAL.rolling_friction,
            ],
        )
        scene.recompile()

    @property
    def body_id(self) -> int:
        """Engine id of the resource; it may change when the scene is rebuilt."""
        return self.scene.name_to_id("body", self.BODY_NAME)

    def distance_to(self, point: tuple[float, float, float]) -> float:
        return math.sqrt(sum((float(a) - float(b)) ** 2 for a, b in zip(point, self.position)))

    def field_at(self, point: tuple[float, float, float]) -> float:
        """Local isotropic field; scalar only, with no direction or identity."""
        if self.remaining <= 0.0:
            return 0.0
        distance = self.distance_to(point)
        if distance >= self.field_radius:
            return 0.0
        normalized = max(0.0, 1.0 - distance / self.field_radius)
        return normalized * normalized

    def touching(self, body_ids: Collection[int]) -> bool:
        """Whether any of the given engine bodies is in contact with the resource."""
        if self.remaining <= 0.0:
            return False
        model, data = self.scene.model, self.scene.data
        own = self.body_id
        for index in range(int(data.ncon)):
            contact = data.contact[index]
            pair = (int(model.geom_bodyid[contact.geom1]), int(model.geom_bodyid[contact.geom2]))
            if (pair[0] == own and pair[1] in body_ids) or (pair[1] == own and pair[0] in body_ids):
                return True
        return False

    def offered_material(self) -> float:
        """Return the bounded amount physically available this cognitive tick."""
        if self.remaining <= 0.0:
            return 0.0
        return min(self.transfer_per_tick, self.remaining)

    def consume_absorbed(self, amount: float) -> float:
        """Remove only material actually accepted across the organism boundary."""
        if (
            isinstance(amount, bool)
            or not isinstance(amount, (int, float))
            or not math.isfinite(float(amount))
            or amount < 0.0
        ):
            raise ValueError("absorbed resource amount must be finite and non-negative")
        consumed = min(float(amount), self.remaining, self.transfer_per_tick)
        self.remaining -= consumed
        return consumed

    def take_contact_material(self, body_ids: Collection[int]) -> float:
        if not self.touching(body_ids):
            return 0.0
        amount = self.offered_material()
        self.consume_absorbed(amount)
        return amount

    def checkpoint(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "position": [float(value) for value in self.position],
            "radius": float(self.radius),
            "field_radius": float(self.field_radius),
            "remaining": float(self.remaining),
            "transfer_per_tick": float(self.transfer_per_tick),
        }

    @classmethod
    def from_state(cls, scene: Any, payload: Mapping[str, Any] | None) -> "PhysicalResource":
        if payload is None:
            return cls(scene)
        if int(payload.get("schema_version", -1)) != 1:
            raise ValueError("unsupported Physics3D resource state")
        position = tuple(float(value) for value in payload["position"])
        if len(position) != 3:
            raise ValueError("resource position must have three coordinates")
        return cls(
            scene,
            position=position,
            radius=float(payload["radius"]),
            field_radius=float(payload["field_radius"]),
            remaining=float(payload["remaining"]),
            transfer_per_tick=float(payload["transfer_per_tick"]),
        )


__all__ = ["ContactMaterial", "PhysicalResource", "RESOURCE_MATERIAL"]

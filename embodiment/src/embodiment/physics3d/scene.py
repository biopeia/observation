"""One MuJoCo world that Physics3D parts are added to (ADR-0066).

A MuJoCo model is compiled from one description, so a body and the objects
around it cannot each create themselves in a shared client the way they did.
A scene holds that description and its compiled state: a part adds itself to
``spec`` and asks for a recompile, which preserves the physical state already
there.  Element ids may move when the model is recompiled; parts resolve
theirs by name whenever ``revision`` changes.

The scene is plain apparatus.  Other domains use it by its attributes and do
not need to import this module.
"""

from __future__ import annotations

from collections.abc import Sequence

from embodiment.physics3d.mechanics import GROUND_MATERIAL, SurfaceMaterial

DEFAULT_GRAVITY = (0.0, 0.0, -9.81)


class PhysicsScene:
    def __init__(self, *, timestep: float, gravity: Sequence[float] = DEFAULT_GRAVITY) -> None:
        import mujoco

        if not timestep > 0.0:
            raise ValueError("timestep must be positive")
        self.mj = mujoco
        self.spec = mujoco.MjSpec()
        self.spec.option.timestep = float(timestep)
        self.spec.option.gravity = [float(value) for value in gravity]
        self.model = self.spec.compile()
        self.data = mujoco.MjData(self.model)
        self.revision = 0

    def add_ground(self, material: SurfaceMaterial = GROUND_MATERIAL) -> None:
        """Add the infinite ground plane, a geom of the world body (id 0)."""
        self.spec.worldbody.add_geom(
            name="ground",
            type=self.mj.mjtGeom.mjGEOM_PLANE,
            size=[0.0, 0.0, 1.0],
            friction=[
                material.lateral_friction,
                material.spinning_friction,
                material.rolling_friction,
            ],
        )
        self.recompile()

    def recompile(self) -> None:
        """Rebuild the model after ``spec`` changed, keeping the physical state."""
        self.model, self.data = self.spec.recompile(self.model, self.data)
        self.revision += 1
        self.forward()

    def forward(self) -> None:
        """Recompute positions, contacts and forces for the current state."""
        self.mj.mj_forward(self.model, self.data)

    def step(self) -> None:
        self.mj.mj_step(self.model, self.data)

    def primitives(self) -> list[tuple[str, list[float], list[float], list[float], float]]:
        """Every geom as plain data: kind, position, rotation, size, luminance.

        This is what a sensing channel that must not import the engine reads.
        """
        model, data = self.model, self.data
        primitives = []
        for geom in range(int(model.ngeom)):
            red, green, blue = (float(value) for value in model.geom_rgba[geom][:3])
            primitives.append(
                (
                    self.mj.mjtGeom(int(model.geom_type[geom]))
                    .name.removeprefix("mjGEOM_")
                    .lower(),
                    data.geom_xpos[geom].tolist(),
                    data.geom_xmat[geom].tolist(),
                    model.geom_size[geom].tolist(),
                    0.2126 * red + 0.7152 * green + 0.0722 * blue,
                )
            )
        return primitives

    def name_to_id(self, kind: str, name: str) -> int:
        """Id of a named ``body``, ``joint`` or ``geom``; raises if absent."""
        object_type = {
            "body": self.mj.mjtObj.mjOBJ_BODY,
            "joint": self.mj.mjtObj.mjOBJ_JOINT,
            "geom": self.mj.mjtObj.mjOBJ_GEOM,
        }[kind]
        identifier = int(self.mj.mj_name2id(self.model, object_type, name))
        if identifier < 0:
            raise KeyError(f"scene has no {kind} named {name!r}")
        return identifier


__all__ = ["DEFAULT_GRAVITY", "PhysicsScene"]

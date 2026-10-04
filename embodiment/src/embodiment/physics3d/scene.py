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

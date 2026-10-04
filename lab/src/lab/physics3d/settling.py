from __future__ import annotations

import math
from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class SettlingResult:
    converged: bool
    steps: int
    stable_samples_required: int
    stable_samples_observed: int
    residual_linear_speed_m_s: float
    residual_angular_speed_rad_s: float
    residual_joint_speed_rad_s: float
    residual_joint_reported_speed_rad_s: float = 0.0
    peak_joint_index: int | None = None
    peak_joint_name: str | None = None
    peak_joint_position_rad: float | None = None
    peak_joint_reported_velocity_rad_s: float | None = None
    peak_joint_applied_torque_nm: float | None = None
    peak_joint_contact_count: int = 0
    peak_joint_contacts: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


# Ten simulated seconds at 240 Hz.  Under MuJoCo the unactuated humanoid folds
# to the ground and comes to rest after about 1600 steps; the six-second
# budget calibrated on the previous engine was too short for it.
SETTLING_MAX_STEPS = 2400


def settle_passive_body(
    scene,
    body,
    *,
    max_steps: int = SETTLING_MAX_STEPS,
    stable_samples: int = 48,
    linear_threshold: float = 0.025,
    angular_threshold: float = 0.05,
    joint_threshold: float = 0.08,
) -> SettlingResult:
    """Measure passive mechanical convergence without inventing controller input."""
    if max_steps < 1 or stable_samples < 1:
        raise ValueError("settling bounds must be positive")
    for value, name in (
        (linear_threshold, "linear_threshold"),
        (angular_threshold, "angular_threshold"),
        (joint_threshold, "joint_threshold"),
    ):
        if not math.isfinite(float(value)) or float(value) < 0.0:
            raise ValueError(f"{name} must be finite and non-negative")

    time_step = float(scene.model.opt.timestep)
    body.apply_effectors({})
    stable = 0
    last_linear = last_angular = last_joint = 0.0
    states = body.joint_states()

    def result(*, converged: bool, steps: int) -> SettlingResult:
        speeds = [abs(velocity) for _position, velocity in states]
        peak = max(range(len(speeds)), key=speeds.__getitem__) if speeds else None
        contacts = (
            ()
            if peak is None
            else tuple(
                sorted(
                    f"body={item['other_body_id']},link={item['other_link_name'] or -1}"
                    for item in body.contact_details()
                    if item["link_index"] == peak
                )
            )
        )
        return SettlingResult(
            converged=converged,
            steps=steps,
            stable_samples_required=stable_samples,
            stable_samples_observed=stable,
            residual_linear_speed_m_s=last_linear,
            residual_angular_speed_rad_s=last_angular,
            residual_joint_speed_rad_s=last_joint,
            residual_joint_reported_speed_rad_s=max(speeds, default=0.0),
            peak_joint_index=peak,
            peak_joint_name=None if peak is None else body.observer_joint_specs[peak].name,
            peak_joint_position_rad=None if peak is None else states[peak][0],
            peak_joint_reported_velocity_rad_s=None if peak is None else states[peak][1],
            peak_joint_applied_torque_nm=None if peak is None else body.joint_torques()[peak],
            peak_joint_contact_count=len(contacts),
            peak_joint_contacts=contacts,
        )

    for step in range(1, max_steps + 1):
        previous = states
        body.prepare_physics_substep()
        scene.step()
        linear_velocity, angular_velocity = body.base_velocity()
        last_linear = math.sqrt(sum(value**2 for value in linear_velocity))
        last_angular = math.sqrt(sum(value**2 for value in angular_velocity))
        states = body.joint_states()
        # Displacement over the step, not the engine's reported velocity.
        last_joint = max(
            (abs(now[0] - before[0]) / time_step for now, before in zip(states, previous)),
            default=0.0,
        )
        if (
            last_linear <= linear_threshold
            and last_angular <= angular_threshold
            and last_joint <= joint_threshold
        ):
            stable += 1
            if stable >= stable_samples:
                return result(converged=True, steps=step)
        else:
            stable = 0

    return result(converged=False, steps=max_steps)


__all__ = ["SETTLING_MAX_STEPS", "SettlingResult", "settle_passive_body"]

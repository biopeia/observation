"""Pure observer-side projections from runtime telemetry into view contracts.

This module contains inherited migration-stage projections. They are
transitional bridges, not stable Biopeia semantic-family contracts.
"""

from __future__ import annotations

from typing import Any, Mapping


def _identity(tick: Mapping[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    if tick.get("source") is not None:
        result["source"] = str(tick["source"])
    if tick.get("instance_id") is not None:
        result["instance_id"] = str(tick["instance_id"])
    if tick.get("run_id") is not None:
        result["run_id"] = str(tick["run_id"])
    if tick.get("sequence") is not None:
        try:
            result["sequence"] = int(tick["sequence"])
        except (TypeError, ValueError):
            pass
    return result


def _copy_number(
    target: dict[str, Any],
    source: Mapping[str, Any],
    source_key: str,
    *,
    target_key: str | None = None,
    cast: type[int] | type[float] = float,
) -> None:
    value = source.get(source_key)
    if value is None:
        return
    try:
        target[target_key or source_key] = cast(value)
    except (TypeError, ValueError):
        return


def _copy_bool(
    target: dict[str, Any],
    source: Mapping[str, Any],
    source_key: str,
    *,
    target_key: str | None = None,
) -> None:
    value = source.get(source_key)
    if isinstance(value, bool):
        target[target_key or source_key] = value


def runtime_tick_events(tick: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    """Project legacy runtime telemetry into transitional presentation events.

    This is a migration bridge, not a stable Biopeia observation contract.
    It does not establish semantic authority, units, or provenance for fields.
    The source-specific ``symbiont_tick`` key is deliberately ignored and is
    never emitted or treated as an alias for ``tick``.
    A cognition event is emitted only when the input contains at least one
    cognition projection field; identity and tick context alone are not a
    cognition observation.
    """
    if not isinstance(tick, Mapping):
        raise TypeError("tick must be a mapping")

    identity = _identity(tick)

    body: dict[str, Any] = {**identity, "type": "body"}
    _copy_number(body, tick, "tick", cast=int)
    if tick.get("body_kind") is not None:
        body["body_kind"] = str(tick["body_kind"])
    if isinstance(tick.get("base_position"), (list, tuple)):
        try:
            body["base_position"] = [float(v) for v in tick["base_position"]]
        except (TypeError, ValueError):
            pass
    if isinstance(tick.get("base_orientation"), (list, tuple)):
        try:
            body["base_orientation"] = [float(v) for v in tick["base_orientation"]]
        except (TypeError, ValueError):
            pass
    if isinstance(tick.get("resource_position"), (list, tuple)):
        try:
            position = [float(v) for v in tick["resource_position"]]
            if len(position) == 3:
                body["resource_position"] = position
        except (TypeError, ValueError):
            pass
    if isinstance(tick.get("joints"), (list, tuple)):
        joints: list[dict[str, Any]] = []
        for item in tick["joints"]:
            if not isinstance(item, Mapping):
                continue
            joint: dict[str, Any] = {}
            if item.get("name") is not None:
                joint["name"] = str(item["name"])
            if item.get("position") is not None:
                try:
                    joint["position"] = float(item["position"])
                except (TypeError, ValueError):
                    pass
            if joint:
                joints.append(joint)
        body["joints"] = joints
    if isinstance(tick.get("links"), (list, tuple)):
        links: list[dict[str, Any]] = []
        for item in tick["links"]:
            if not isinstance(item, Mapping) or item.get("name") is None:
                continue
            raw_position = item.get("position")
            raw_orientation = item.get("orientation")
            if (
                not isinstance(raw_position, (list, tuple))
                or len(raw_position) != 3
                or not isinstance(raw_orientation, (list, tuple))
                or len(raw_orientation) != 4
            ):
                continue
            try:
                links.append(
                    {
                        "name": str(item["name"]),
                        "position": [float(v) for v in raw_position],
                        "orientation": [float(v) for v in raw_orientation],
                    }
                )
            except (TypeError, ValueError):
                continue
        if links:
            body["links"] = links
    _copy_number(body, tick, "contact_count", cast=int)
    _copy_number(body, tick, "ground_contact_count", cast=int)
    _copy_number(body, tick, "self_contact_count", cast=int)
    _copy_number(body, tick, "resource_contact_count", cast=int)
    # These source telemetry keys have distinct, unresolved meanings. Do not
    # collapse them into one ambiguous view field.
    # A target semantic-family contract may add a projection later.

    cognition: dict[str, Any] = {**identity, "type": "cognition"}
    _copy_number(cognition, tick, "tick", cast=int)
    _copy_number(cognition, tick, "schema_confidence")
    _copy_number(cognition, tick, "schema_parts", cast=int)
    _copy_number(cognition, tick, "schema_sensory_parts", cast=int)
    _copy_number(cognition, tick, "schema_cognitive_regions", cast=int)
    _copy_number(cognition, tick, "embodiment_epoch", cast=int)
    _copy_number(cognition, tick, "body_age_ticks", cast=int)
    _copy_number(cognition, tick, "body_senescence")
    _copy_number(cognition, tick, "reacclimation_remaining", cast=int)
    _copy_bool(cognition, tick, "reacclimating")
    if tick.get("motor_origin") is not None:
        cognition["motor_origin"] = str(tick["motor_origin"])
    if tick.get("motor_origin_detail") is not None:
        cognition["motor_origin_detail"] = str(tick["motor_origin_detail"])
    _copy_number(cognition, tick, "predictor_count", cast=int)
    _copy_number(cognition, tick, "sensorimotor_patterns", cast=int)
    _copy_number(cognition, tick, "motor_primitives", cast=int)
    _copy_number(cognition, tick, "cognitive_motor_primitives", cast=int)
    _copy_number(cognition, tick, "motor_repertoire_size", cast=int)
    _copy_number(cognition, tick, "recurrent_primitive_candidates", cast=int)
    _copy_number(cognition, tick, "max_primitive_samples", cast=int)
    _copy_number(cognition, tick, "full_competence_gate_candidates", cast=int)
    _copy_number(cognition, tick, "motor_readout_nodes", cast=int)
    _copy_number(cognition, tick, "primitive_readout_nodes", cast=int)
    _copy_number(cognition, tick, "cognitive_motor_output_edges", cast=int)
    _copy_number(cognition, tick, "cognitive_concepts", cast=int)
    _copy_number(cognition, tick, "cognitive_readouts", cast=int)
    if tick.get("prediction_error") is not None:
        cognition["prediction_error"] = tick["prediction_error"]
    _copy_bool(cognition, tick, "slm_active")
    if tick.get("slm_models") is not None:
        cognition["slm_models"] = tick["slm_models"]
    _copy_bool(cognition, tick, "prospective_selected")
    if tick.get("prospective_expected_value") is not None:
        cognition["prospective_expected_value"] = tick["prospective_expected_value"]

    vitals: dict[str, Any] = {**identity, "type": "vitals"}
    _copy_number(vitals, tick, "tick", cast=int)
    _copy_number(vitals, tick, "body_age_ticks", cast=int)
    _copy_number(vitals, tick, "body_senescence")
    _copy_bool(vitals, tick, "alive")
    _copy_number(vitals, tick, "joint_motion")
    _copy_number(vitals, tick, "active_effectors", cast=int)
    _copy_number(vitals, tick, "resource_distance")
    _copy_number(vitals, tick, "resource_progress")
    _copy_number(vitals, tick, "resource_remaining")
    _copy_number(vitals, tick, "displacement_from_origin")
    _copy_number(vitals, tick, "mechanical_work_joules")
    _copy_number(vitals, tick, "positive_actuator_work_joules")
    _copy_number(vitals, tick, "negative_actuator_work_joules")
    _copy_number(vitals, tick, "absolute_actuator_work_joules")
    _copy_number(vitals, tick, "net_actuator_work_joules")
    _copy_number(vitals, tick, "metabolic_work_cost")

    events = [body]
    if set(cognition).difference(identity, {"type", "tick"}):
        events.append(cognition)
    events.append(vitals)
    return tuple(events)

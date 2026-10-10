from copy import deepcopy

import pytest

from observation import ObservedFrame, runtime_tick_events


def test_observed_frame_emits_explicit_passive_projection_provenance() -> None:
    frame = ObservedFrame(
        tick=4,
        source="synthetic-fixture",
        run_id="run-1",
        organism_id="org-1",
        body={"position": [1, 2, 3]},
        cognition=None,
        vitals={"alive": True},
        mind={"signals": []},
        body_id="body-1",
    )
    event = frame.as_event()
    assert event["type"] == "observed_frame"
    assert event["tick"] == 4
    assert event["body_id"] == "body-1"
    assert event["provenance"]["owner"] == "observer"
    assert event["provenance"]["feeds_back"] is False
    assert event["body"] == {"position": [1, 2, 3]}


def test_runtime_tick_projection_is_mapping_only_and_does_not_mutate_source() -> None:
    tick = {
        "tick": "12",
        "run_id": "r-1",
        "base_position": [0.1, 2, 3],
        "alive": True,
        "schema_confidence": "0.8",
        "joints": [{"name": "elbow", "position": "0.5"}],
    }
    before = deepcopy(tick)
    body, cognition, vitals = runtime_tick_events(tick)
    assert tick == before
    assert body["base_position"] == [0.1, 2.0, 3.0]
    assert body["joints"] == [{"name": "elbow", "position": 0.5}]
    assert cognition["schema_confidence"] == 0.8
    assert vitals["alive"] is True


def test_projection_does_not_invent_observations_and_rejects_non_mapping() -> None:
    events = runtime_tick_events({"tick": 3})
    body, vitals = events
    assert body == {"type": "body", "tick": 3}
    assert vitals == {"type": "vitals", "tick": 3}
    assert all(event["type"] != "cognition" for event in events)
    with pytest.raises(TypeError, match="tick must be a mapping"):
        runtime_tick_events([])  # type: ignore[arg-type]


def test_projection_emits_cognition_only_when_cognition_data_is_present() -> None:
    events = runtime_tick_events({"source": "fixture", "tick": 3, "cognitive_readouts": 1})

    cognition = [event for event in events if event["type"] == "cognition"]
    assert cognition == [
        {"source": "fixture", "type": "cognition", "tick": 3, "cognitive_readouts": 1}
    ]


def test_projection_does_not_emit_or_alias_symbiont_tick() -> None:
    legacy_only = runtime_tick_events({"symbiont_tick": 37})
    assert legacy_only == ({"type": "body"}, {"type": "vitals"})

    with_distinct_tick = runtime_tick_events(
        {"tick": 12, "symbiont_tick": 37, "cognitive_readouts": 1}
    )
    body, cognition, vitals = with_distinct_tick
    assert body["tick"] == 12
    assert cognition["tick"] == 12
    assert vitals["tick"] == 12
    assert all("symbiont_tick" not in event for event in with_distinct_tick)


@pytest.mark.parametrize(
    "tick",
    [
        {"tick": 3, "prediction_error": None},
        {"tick": 3, "slm_models": None},
        {"tick": 3, "prospective_expected_value": None},
    ],
)
def test_projection_omits_cognition_when_recognized_values_are_only_none(
    tick: dict[str, object],
) -> None:
    events = runtime_tick_events(tick)

    assert all(event["type"] != "cognition" for event in events)


@pytest.mark.parametrize(
    "tick",
    [
        {"metabolic_reserve_ratio": 0.25},
        {"metabolic_reserve": 42.0},
        {"metabolic_reserve_ratio": 0.25, "metabolic_reserve": 42.0},
    ],
)
def test_projection_omits_unratified_metabolic_reserve_semantics(tick: dict[str, float]) -> None:
    events = runtime_tick_events(tick)

    assert all("metabolic_reserve" not in event for event in events)
    assert all("metabolic_reserve_ratio" not in event for event in events)

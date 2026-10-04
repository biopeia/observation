from __future__ import annotations

from types import SimpleNamespace

from symbiont.core.cognition.bridge import CognitiveBridgeResult
from symbiont.core.cognition.host_self_model import SelfModel
from symbiont.core.domains.action import ActionCognitionProjection
from symbiont.core.domains.cognition import CognitionDomain, CognitionServices
from symbiont.core.domains.context import TickContext
from symbiont.host.readings import (
    ReadingPrivacyClass,
    ReadingQuality,
    SensorReading,
    Unit,
)
from symbiont.sensory import SensorySystem


class _PredictorBridge:
    def __init__(self, *, cognitive_name: str, gain: float) -> None:
        self.shadow_predictions = (SimpleNamespace(source_id=cognitive_name, predictive_gain=gain),)
        self.graph = None

    def tick(self, *args: object, **kwargs: object) -> CognitiveBridgeResult:
        return CognitiveBridgeResult(
            tick=1,
            activations={},
            readouts={},
            prediction_errors=(),
            structural_mutations_applied=0,
            frozen=False,
            topology_revision=0,
        )


def _utility_after_cognition_step(predictive_gain: float) -> float:
    sensory = SensorySystem()
    reading = SensorReading(
        capability_id="signal.temperature",
        source="test-provider",
        value=0.5,
        unit=Unit.RATIO,
        monotonic_timestamp_ns=1,
        quality=ReadingQuality.NOMINAL,
        privacy_class=ReadingPrivacyClass.AGGREGATE,
    )
    sensory.transduce(
        [reading],
        percept_names={"signal.temperature": "temperature"},
        tick=1,
    )
    sensor = sensory.sensors[0]
    bridge = _PredictorBridge(cognitive_name=sensor.cognitive_name, gain=predictive_gain)
    services = CognitionServices(
        cognitive_bridge=bridge,  # type: ignore[arg-type]
        sensory_system=sensory,
        self_model=SelfModel(),
        charge_metabolism=lambda _domain, _cost: None,
    )
    perception = SimpleNamespace(
        percepts=(),
        cognitive_readings=(),
        cognitive_aliases={},
        perceptual_allocations=(),
        allocations=(),
        availability_by_capability={},
        percept_names={},
        developed_names={},
    )
    CognitionDomain().step(
        services=services,
        context=TickContext(symbiont_id="organism.test", symbiont_tick=1),
        perception=perception,  # type: ignore[arg-type]
        action_projection=ActionCognitionProjection(
            active_motor_actuator_ids=(),
            motor_effect_actuator_ids=(),
            active_competence_ids=(),
        ),
        plasticity_enabled=False,
        auto_promote_predictors=False,
        reacclimation_remaining=0,
        cognitive_self_namespace_key="a" * 64,
    )
    return sensor.utility


def test_predictor_credit_flows_through_cognition_domain_into_sensor_utility() -> None:
    without_predictive_evidence = _utility_after_cognition_step(0.0)
    with_predictive_evidence = _utility_after_cognition_step(0.8)

    assert with_predictive_evidence > without_predictive_evidence

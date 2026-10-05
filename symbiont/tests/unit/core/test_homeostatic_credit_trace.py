from __future__ import annotations

from dataclasses import dataclass

from symbiont.core.domains.regulation import RegulationDomain, RegulationServices


class _Bridge:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def observe_homeostatic_action_outcome(self, **kwargs) -> bool:
        self.calls.append(dict(kwargs))
        return True


class _Homeostasis:
    def __init__(self, value: float) -> None:
        self.value = value

    def deviation(self) -> float:
        return self.value


@dataclass
class _Living:
    alive: bool = True


def test_delayed_credit_preserves_action_context_and_execution_provenance() -> None:
    domain = RegulationDomain()
    bridge = _Bridge()

    domain.schedule_homeostatic_action_credit(
        cognitive_bridge=bridge,  # type: ignore[arg-type]
        family="primitive",
        action_id="competence.opaque",
        concept_ids=("concept.b", "concept.a", "concept.a"),
        baseline_error=0.8,
        tick=10,
        context_ref="context.v2.abc",
        commitment_ref="commitment.1",
        attempt_ref="attempt.1",
    )

    assert len(domain.pending_homeostatic_action_credit) == 4
    first = domain.pending_homeostatic_action_credit[0]
    assert first.due_tick == 14
    assert first.action_tick == 10
    assert first.concept_ids == ("concept.a", "concept.b")
    assert first.context_ref == "context.v2.abc"
    assert first.commitment_ref == "commitment.1"
    assert first.attempt_ref == "attempt.1"


def test_delayed_credit_keeps_existing_value_equation() -> None:
    domain = RegulationDomain()
    bridge = _Bridge()
    homeostasis = _Homeostasis(0.5)

    domain.schedule_homeostatic_action_credit(
        cognitive_bridge=bridge,  # type: ignore[arg-type]
        family="primitive",
        action_id="competence.opaque",
        concept_ids=("concept.a",),
        baseline_error=0.8,
        tick=10,
        context_ref="context.v2.abc",
        commitment_ref="commitment.1",
        attempt_ref="attempt.1",
    )
    domain.resolve_homeostatic_action_credit(
        services=RegulationServices(
            cognitive_bridge=bridge,  # type: ignore[arg-type]
            homeostasis=homeostasis,  # type: ignore[arg-type]
            living_body_state=_Living(),  # type: ignore[arg-type]
        ),
        tick=14,
    )

    assert len(bridge.calls) == 1
    call = bridge.calls[0]
    assert call["family"] == "primitive"
    assert call["action_id"] == "competence.opaque"
    assert call["concept_ids"] == ("concept.a",)
    assert call["value"] == 0.30000000000000004
    assert domain.last_resolved_homeostatic_action_credit is not None
    assert domain.last_resolved_homeostatic_action_credit.context_ref == "context.v2.abc"

"""Regulatory phenotype and delayed homeostatic credit."""

from __future__ import annotations

from dataclasses import dataclass

from ..cognition.bridge import CognitiveBridge
from ..embodiment.homeostasis import HomeostaticController
from ..embodiment.physiology import LivingBodyState


@dataclass(frozen=True, slots=True)
class RegulationServices:
    cognitive_bridge: CognitiveBridge | None
    homeostasis: HomeostaticController
    living_body_state: LivingBodyState


@dataclass(frozen=True, slots=True)
class HomeostaticCreditTrace:
    """One delayed intrinsic-credit claim with its causal provenance.

    The trace does not assert that the named action caused the later
    physiological change.  It preserves which actually executed action and
    cognitive context made the delayed eligibility trace possible, so later
    plasticity is auditable without turning correlation into causal evidence.
    """

    due_tick: int
    family: str
    action_id: str
    concept_ids: tuple[str, ...]
    baseline_error: float
    discount: float
    action_tick: int
    context_ref: str | None = None
    commitment_ref: str | None = None
    attempt_ref: str | None = None

    def __post_init__(self) -> None:
        if self.due_tick < self.action_tick or self.action_tick < 0:
            raise ValueError("invalid homeostatic credit ticks")
        if self.family not in {"motor", "primitive"}:
            raise ValueError("homeostatic credit family must be motor or primitive")
        if not self.action_id:
            raise ValueError("homeostatic credit action_id must not be empty")
        if not 0.0 <= self.discount <= 1.0:
            raise ValueError("homeostatic credit discount must be within [0, 1]")
        if self.context_ref is not None and not self.context_ref.startswith("context."):
            raise ValueError("homeostatic credit context_ref must be organism-owned")


class RegulationDomain:
    """Own phenotype regulation and delayed intrinsic action credit."""

    def __init__(self) -> None:
        self.pending_homeostatic_action_credit: list[HomeostaticCreditTrace] = []
        self.last_resolved_homeostatic_action_credit: HomeostaticCreditTrace | None = None

    def schedule_homeostatic_action_credit(
        self,
        *,
        cognitive_bridge: CognitiveBridge | None,
        family: str,
        action_id: str,
        concept_ids: tuple[str, ...],
        baseline_error: float,
        tick: int,
        context_ref: str | None = None,
        commitment_ref: str | None = None,
        attempt_ref: str | None = None,
    ) -> None:
        if cognitive_bridge is None or not concept_ids:
            return
        concepts = tuple(sorted(set(concept_ids)))
        for horizon, discount in (
            (4, 1.0),
            (16, 0.85),
            (64, 0.65),
            (256, 0.40),
        ):
            self.pending_homeostatic_action_credit.append(
                HomeostaticCreditTrace(
                    due_tick=int(tick) + horizon,
                    family=str(family),
                    action_id=str(action_id),
                    concept_ids=concepts,
                    baseline_error=float(baseline_error),
                    discount=float(discount),
                    action_tick=int(tick),
                    context_ref=context_ref,
                    commitment_ref=commitment_ref,
                    attempt_ref=attempt_ref,
                )
            )
        if len(self.pending_homeostatic_action_credit) > 4096:
            self.pending_homeostatic_action_credit.sort(key=lambda item: item.due_tick)
            self.pending_homeostatic_action_credit = self.pending_homeostatic_action_credit[:4096]

    def resolve_homeostatic_action_credit(
        self,
        *,
        services: RegulationServices,
        tick: int,
    ) -> None:
        pending = self.pending_homeostatic_action_credit
        if not pending:
            return
        if not services.living_body_state.alive:
            pending.clear()
            return
        current_error = services.homeostasis.deviation()
        remaining: list[HomeostaticCreditTrace] = []
        for trace in pending:
            if trace.due_tick > tick:
                remaining.append(trace)
                continue
            if services.cognitive_bridge is None:
                continue
            intrinsic_value = max(
                -1.0,
                min(
                    1.0,
                    (trace.baseline_error - current_error) * trace.discount,
                ),
            )
            services.cognitive_bridge.observe_homeostatic_action_outcome(
                family=trace.family,
                action_id=trace.action_id,
                concept_ids=trace.concept_ids,
                value=intrinsic_value,
                tick=tick,
            )
            self.last_resolved_homeostatic_action_credit = trace
        self.pending_homeostatic_action_credit = remaining


__all__ = ["HomeostaticCreditTrace", "RegulationDomain", "RegulationServices"]

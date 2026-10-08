"""Adapt Symbiont-owned affordances into the operational Observation Plane."""

from __future__ import annotations

from symbiont.agency.affordance import AffordanceObservation
from lab.observation.body_pose import LAB_PRODUCER, LAB_RUN_ISSUER
from lab.observation.semantic import (
    AcquisitionBasis,
    ActorRef,
    AuthorityDomain,
    DomainTimeRef,
    IdentityAssertion,
    IdentityRef,
    Lineage,
    LineageSourceRef,
    OrchestrationContext,
    SemanticClaim,
    SemanticContractRef,
    SemanticFamily,
    SemanticObservation,
    SubjectScope,
    TransformationRef,
)

SYMBIONT_RUNTIME = ActorRef("component", "symbiont.organism_runtime")
ACTION_DOMAIN_SOURCE = ActorRef("component", "symbiont.action_domain")


def _lineage(sample: AffordanceObservation) -> Lineage:
    refs: set[tuple[str, str]] = set()
    for item in sample.affordances:
        refs.add(("symbiont.competence", item.competence_id))
        refs.add(("symbiont.effect", item.anticipated_effect_id))
        if item.prediction_ref:
            refs.add(("symbiont.prediction", item.prediction_ref))
        refs.update(("symbiont.evidence", ref) for ref in item.evidence_refs)
        if item.context_ref:
            refs.add(("symbiont.context", item.context_ref))
        if item.embodiment_id:
            refs.add(("embodiment.episode", item.embodiment_id))
    parents = tuple(
        LineageSourceRef(namespace=namespace, reference=reference)
        for namespace, reference in sorted(refs)
    )
    if not parents:
        return Lineage()
    return Lineage(
        parents=parents,
        transformation=TransformationRef(
            transformation_id="symbiont.affordance_resolver",
            revision="v1",
        ),
    )


def affordance_observation(
    sample: AffordanceObservation,
    *,
    run_id: str | None = None,
) -> SemanticObservation[AffordanceObservation]:
    organism_identity = IdentityRef(
        kind="organism",
        value=sample.organism_id,
        issuer=SYMBIONT_RUNTIME,
        lifetime="organism",
    )
    subject = SubjectScope(
        kind="organism_affordance_set",
        identities=(
            IdentityAssertion(
                identity=organism_identity,
                asserter=SYMBIONT_RUNTIME,
            ),
        ),
    )
    family = SemanticFamily(
        authority=AuthorityDomain.SYMBIONT,
        path=("affordance",),
        contract=SemanticContractRef(
            contract_id="symbiont.affordance",
            revision=sample.contract_revision,
        ),
    )
    return SemanticObservation(
        claim=SemanticClaim(
            family=family,
            subject=subject,
            epistemic_kind="derived_action_opportunity",
            value=sample,
        ),
        acquisition=AcquisitionBasis(
            method="action_domain_affordance_resolution",
            measurement_source=ACTION_DOMAIN_SOURCE,
        ),
        asserter=ACTION_DOMAIN_SOURCE,
        producer=LAB_PRODUCER,
        orchestration=(
            OrchestrationContext(
                run_identity=IdentityAssertion(
                    identity=IdentityRef(
                        kind="run",
                        value=run_id,
                        issuer=LAB_RUN_ISSUER,
                        lifetime="lab_run",
                    ),
                    asserter=LAB_RUN_ISSUER,
                )
            )
            if run_id is not None
            else None
        ),
        domain_time=(
            DomainTimeRef(
                domain=AuthorityDomain.SYMBIONT,
                kind="organism_tick",
                value=sample.organism_tick,
            ),
        ),
        lineage=_lineage(sample),
    )


__all__ = ["affordance_observation"]

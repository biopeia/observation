"""Authority/time/lineage contracts for the remaining semantic families."""

from __future__ import annotations

from embodiment.observation import (
    BodyPhysiologySample,
    JointKinematicState,
    JointKinematicsSample,
)
from environment.observation import ResourcePoolItem, ResourcePoolObservation
from lab.observation.body_physiology import body_physiology_observation
from lab.observation.environment_resource import resource_state_observation
from lab.observation.joint_kinematics import joint_kinematics_observation
from lab.observation.symbiont_affordance import affordance_observation
from symbiont.agency.affordance import ActionAffordance, AffordanceObservation


def test_joint_kinematics_remains_embodiment_owned() -> None:
    observation = joint_kinematics_observation(
        JointKinematicsSample(
            body_id="body.1",
            joints=(
                JointKinematicState(
                    joint_id="body.1:joint:0",
                    position_rad=0.2,
                    velocity_rad_s=-0.1,
                ),
            ),
            sample_kind="physics_step",
            sample_value=12,
            sample_time_s=0.06,
        ),
        run_id="run.1",
    )

    assert observation.family.qualified_name == "embodiment.joint_kinematics"
    assert observation.authority.value == "embodiment"
    assert [item.kind for item in observation.domain_time] == [
        "physics_step",
        "simulation_time_s",
    ]
    assert observation.claim.value.joints[0].joint_id == "body.1:joint:0"


def test_body_physiology_uses_body_clock_and_organism_tick_only_as_context() -> None:
    observation = body_physiology_observation(
        BodyPhysiologySample(
            body_id="body.1",
            reserve_amount=8.0,
            reserve_capacity=10.0,
            reserve_fraction=0.8,
            reserve_quantity_kind="model_amount",
            structural_integrity=0.9,
            temperature=0.5,
            fatigue=0.1,
            growth_progress=0.2,
            senescence=0.0,
            age_ticks=27,
            vital_state="alive",
        ),
        organism_tick=103,
        run_id="run.1",
    )

    assert observation.family.qualified_name == "embodiment.body_physiology"
    assert observation.authority.value == "embodiment"
    assert [(item.domain.value, item.kind, item.value) for item in observation.domain_time] == [
        ("embodiment", "body_age_tick", 27)
    ]
    assert [(item.domain.value, item.kind, item.value) for item in observation.context_time] == [
        ("symbiont", "organism_tick", 103)
    ]


def test_environment_resource_state_is_logical_environment_state() -> None:
    observation = resource_state_observation(
        ResourcePoolObservation(
            q=2,
            r=3,
            resources=(
                ResourcePoolItem(
                    resource_id="resource.opaque",
                    amount=4.0,
                    capacity=10.0,
                ),
            ),
            world_tick=9,
        ),
        world_id="world.1",
    )

    assert observation.family.qualified_name == "environment.resource_state"
    assert observation.authority.value == "environment"
    assert observation.claim.subject.key == "hex:2,3"
    assert observation.domain_time[0].kind == "world_tick"
    assert observation.claim.value.resources[0].quantity_kind == "model_amount"


def test_affordance_is_symbiont_owned_and_preserves_derivation_lineage() -> None:
    item = ActionAffordance(
        affordance_id="affordance.1234567890abcdef12345678",
        competence_id="competence.walk",
        anticipated_effect_id="effect.forward",
        context_ref="context.7",
        embodiment_id="embodiment.3",
        prediction_confidence=0.7,
        controllability=0.8,
        executability_confidence=0.9,
        prediction_ref="prediction.11",
        evidence_refs=("evidence.1", "evidence.2"),
    )
    observation = affordance_observation(
        AffordanceObservation(
            organism_id="organism.1",
            organism_tick=44,
            affordances=(item,),
        ),
        run_id="run.1",
    )

    assert observation.family.qualified_name == "symbiont.affordance"
    assert observation.authority.value == "symbiont"
    assert observation.domain_time[0].kind == "organism_tick"
    assert observation.lineage.transformation is not None
    assert observation.lineage.transformation.transformation_id == "symbiont.affordance_resolver"
    parents = {
        (parent.namespace, parent.reference)
        for parent in observation.lineage.parents
    }
    assert ("symbiont.competence", "competence.walk") in parents
    assert ("symbiont.effect", "effect.forward") in parents
    assert ("embodiment.episode", "embodiment.3") in parents

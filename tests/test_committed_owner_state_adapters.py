from types import SimpleNamespace

import pytest

from observation import (
    embodiment_reserve_state_observation,
    environment_resource_state_observation,
)


def test_environment_adapter_preserves_owner_and_commit_provenance_without_units():
    projection = SimpleNamespace(
        semantic_family_id="biopeia.environment.resource_state_snapshot",
        semantic_revision="1",
        semantic_authority="ENVIRONMENT",
        semantic_asserter="environment.identified_finite_resource",
        semantic_producer="environment.identified_finite_resource.project_committed_state",
        resource_id="resource-1",
        remaining=2.0,
        world_id="world-1",
        causal_tick=4,
        commit_id="commit-4",
        checkpoint_id="environment-cut-4",
        checkpoint_type="biopeia.environment.identified-finite-resource",
        checkpoint_version=1,
        checkpoint_schema="environment-identified-resource-v2",
        source_owner_checkpoint_sha256="a" * 64,
    )
    observation = environment_resource_state_observation(projection)
    assert observation.claim.authority.value == "environment"
    assert observation.claim.value == {"remaining": 2.0}
    assert observation.context_time[0].value == 4
    configuration = dict(observation.lineage.transformation.effective_configuration)
    assert configuration["world_id"] == "world-1"
    assert configuration["commit_id"] == "commit-4"
    assert observation.lineage.parents[0].reference == "a" * 64
    assert "unit" not in observation.claim.value


def test_embodiment_adapter_preserves_model_amount_and_episode_identity():
    projection = SimpleNamespace(
        semantic_family_id="biopeia.embodiment.reserve_state_snapshot",
        semantic_revision="1",
        semantic_authority="EMBODIMENT",
        semantic_asserter="embodiment.owner_checkpoint",
        semantic_producer="embodiment.checkpoint.project_committed_reserve_state",
        body_id="body-1",
        episode_id="episode-2",
        amount=3.0,
        capacity=5.0,
        fraction=0.6,
        quantity_kind="model_amount",
        world_id="world-1",
        causal_tick=4,
        commit_id="commit-4",
        checkpoint_id="body-cut-4",
        checkpoint_schema="embodiment-checkpoint-v2",
        checkpoint_version=2,
        source_owner_checkpoint_sha256="b" * 64,
    )
    observation = embodiment_reserve_state_observation(projection)
    assert observation.claim.authority.value == "embodiment"
    assert observation.claim.value["amount"] == {"value": 3.0, "quantity_kind": "model_amount"}
    assert observation.claim.value["capacity"] == {"value": 5.0, "quantity_kind": "model_amount"}
    assert observation.claim.value["fraction"] == {"value": 0.6, "unit": "1"}
    assert observation.context_time[0].value == 4
    identities = [item.identity.value for item in observation.claim.subject.identities]
    assert identities == ["body-1", "episode-2"]
    configuration = dict(observation.lineage.transformation.effective_configuration)
    assert configuration["commit_id"] == "commit-4"
    assert configuration["checkpoint_schema"] == "embodiment-checkpoint-v2"


@pytest.mark.parametrize("field,value", [("commit_id", ""), ("semantic_authority", "LAB")])
def test_adapters_reject_missing_or_wrong_authority(field, value):
    projection = SimpleNamespace(
        semantic_family_id="biopeia.environment.resource_state_snapshot",
        semantic_revision="1",
        semantic_authority="ENVIRONMENT",
        semantic_asserter="environment.identified_finite_resource",
        semantic_producer="environment.identified_finite_resource.project_committed_state",
        resource_id="resource-1",
        remaining=2.0,
        world_id="world-1",
        causal_tick=4,
        commit_id="commit-4",
        checkpoint_id="environment-cut-4",
        checkpoint_type="biopeia.environment.identified-finite-resource",
        checkpoint_version=1,
        checkpoint_schema="environment-identified-resource-v2",
        source_owner_checkpoint_sha256="a" * 64,
    )
    setattr(projection, field, value)
    with pytest.raises(ValueError):
        environment_resource_state_observation(projection)

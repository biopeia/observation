from __future__ import annotations

import json
import hashlib
from copy import deepcopy
import socket
from types import SimpleNamespace
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest
import rfc8785

from observation.http_bridge import (
    LocalObservationReadBridge,
    LocalReadBridgeError,
    encode_current_messages,
)
from observation import (
    embodiment_body_pose_observation,
    embodiment_render_morphology_observation,
    embodiment_render_link_pose_observation,
    environment_finite_scalar_field_observation,
    environment_render_scene_observation,
)
from observation.plane import ObservationPlane
from observation.semantic import (
    AcquisitionBasis,
    ActorRef,
    AuthorityDomain,
    DomainTimeRef,
    IdentityAssertion,
    IdentityRef,
    Lineage,
    LineageSourceRef,
    SemanticClaim,
    SemanticContractRef,
    SemanticFamily,
    SemanticObservation,
    SubjectScope,
    TransformationRef,
)

FRONTEND_ORIGIN = "http://127.0.0.1:4173"


def body_pose_observation() -> SemanticObservation[object]:
    pose = SimpleNamespace(
        body_id="body-a",
        reference_frame="world",
        body_frame="root",
        position_m=(1.0, 2.0, 3.0),
        orientation_xyzw=(0.0, 0.0, 0.0, 1.0),
        sample_kind="initial_state",
        sample_value="genesis",
        contract_revision="v1",
    )
    projection = SimpleNamespace(
        world_id="world-a",
        causal_tick=4,
        body_id="body-a",
        embodiment_episode_id="episode-a",
        morphology_revision="morphology-r1",
        source_state_sha256="a" * 64,
        pose=pose,
        last_physical_step_id=None,
        last_physical_step_source_tick=None,
        environment_revision=None,
        solver_config_revision=None,
        physical_step_correlation=None,
    )
    return embodiment_body_pose_observation(projection)


def finite_scalar_observation() -> SemanticObservation[object]:
    projection = SimpleNamespace(
        semantic_family_id="biopeia.environment.finite-scalar-field",
        semantic_revision="1",
        semantic_authority="ENVIRONMENT",
        epistemic_basis="DOMAIN_DERIVED",
        acquisition_basis="environment_field_evaluation",
        semantic_asserter="environment.identified_finite_scalar_field",
        semantic_producer="environment.identified_finite_scalar_field.project_observation",
        quantity_kind="dimensionless_scalar_field",
        unit="1",
        valid_range=(0.0, 1.0),
        resource_id="resource-a",
        field_revision="field-r1",
        environment_id="environment-a",
        environment_revision="environment-r1",
        world_id="world-a",
        source_causal_tick=3,
        target_causal_tick=4,
        physical_step_id="step-3",
        frame_id="environment-local",
        point_m=(1.0, 2.0, 3.0),
        value=0.25,
        source_owner_checkpoint_sha256="b" * 64,
    )
    return environment_finite_scalar_field_observation(projection)


def unauthorized_observation() -> SemanticObservation[object]:
    actor = ActorRef("organism", "organism-1")
    return SemanticObservation(
        claim=SemanticClaim(
            family=SemanticFamily(
                AuthorityDomain.ORGANISM,
                ("private_state",),
                SemanticContractRef("organism.private_state", "1"),
            ),
            subject=SubjectScope("organism", key="organism-1"),
            epistemic_kind="authoritative_state",
            value={"private": True},
        ),
        acquisition=AcquisitionBasis("owner_projection"),
        asserter=actor,
        producer=actor,
    )


def environment_render_scene() -> SemanticObservation[object]:
    value = {
        "schema_version": 1,
        "environment_id": "environment-a",
        "environment_revision": "environment-r1",
        "length_unit": "m",
        "frame": {
            "frame_id": "environment-local",
            "parent_frame_id": "world",
            "origin_m": [0.0, 0.0, 0.0],
            "x_axis_in_parent": [1.0, 0.0, 0.0],
            "y_axis_in_parent": [0.0, 1.0, 0.0],
            "z_axis_in_parent": [0.0, 0.0, 1.0],
            "handedness": "RIGHT_HANDED",
            "up_axis": "Z",
        },
        "items": [{
            "object_id": "ground-a",
            "kind": "ground_plane",
            "frame_id": "environment-local",
            "normal": [0.0, 0.0, 1.0],
            "offset_m": 0.0,
        }],
        "render_geometry_sha256": "",
    }
    value["render_geometry_sha256"] = hashlib.sha256(rfc8785.dumps({k: v for k, v in value.items() if k != "render_geometry_sha256"})).hexdigest()
    return environment_render_scene_observation(value)


def embodiment_render_morphology() -> SemanticObservation[object]:
    value = {
        "contract_revision": "embodiment.render_morphology/v1",
        "schema_version": 1,
        "body_id": "body-a",
        "embodiment_episode_id": "episode-a",
        "morphology_revision": "morphology-r1",
        "geometry_revision": "geometry-r1",
        "render_geometry_sha256": "",
        "coordinate_system": "right_handed_z_up",
        "length_unit": "m",
        "segments": [{
            "segment_id": "link-a", "shape": "box", "dimensions_m": [1.0, 2.0, 3.0],
            "visual_origin_in_link_m": [0.0, 0.0, 0.0],
        }],
        "joints": [{
            "joint_id": "joint-a", "parent_link_id": "link-a", "child_link_id": "link-b",
            "joint_type": "revolute", "joint_origin_in_parent_m": [0.0, 0.0, 0.0],
            "axis_in_joint_frame": [0.0, 0.0, 1.0],
        }],
    }
    digest_fields = {key: value[key] for key in ("contract_revision", "schema_version", "coordinate_system", "length_unit", "segments", "joints")}
    value["render_geometry_sha256"] = hashlib.sha256(b"biopeia:embodiment.render_morphology/v1\n" + rfc8785.dumps(digest_fields)).hexdigest()
    return embodiment_render_morphology_observation(value)


@pytest.mark.parametrize(
    ("adapter", "projection"),
    [
        (environment_render_scene_observation, {"schema_version": 1}),
        (embodiment_render_morphology_observation, {"schema_version": 1}),
    ],
)
def test_static_spatial_adapters_reject_non_contract_shapes(adapter, projection) -> None:
    with pytest.raises(ValueError, match="invalid shape"):
        adapter(projection)


@pytest.mark.parametrize(
    ("adapter", "source", "mutate", "message"),
    [
        (environment_render_scene_observation, environment_render_scene,
         lambda value: value.update(frame=None, render_geometry_sha256="b" * 64), "frame"),
        (environment_render_scene_observation, environment_render_scene,
         lambda value: value.update(render_geometry_sha256="b" * 64), "digest"),
        (environment_render_scene_observation, environment_render_scene,
         lambda value: value.update(environment_revision="x" * 70_000), "owner bound"),
        (embodiment_render_morphology_observation, embodiment_render_morphology,
         lambda value: value.update(segments=[None]), "segment shape"),
        (embodiment_render_morphology_observation, embodiment_render_morphology,
         lambda value: value.update(render_geometry_sha256="b" * 64), "digest"),
        (embodiment_render_morphology_observation, embodiment_render_morphology,
         lambda value: value.update(body_id="x" * 300_000), "owner bound"),
    ],
)
def test_static_spatial_adapters_reject_invalid_owner_projection_before_observation(
    adapter, source, mutate, message
) -> None:
    projection = deepcopy(source().claim.value)
    mutate(projection)
    with pytest.raises(ValueError, match=message):
        adapter(projection)


def test_environment_static_adapter_detaches_owner_payload() -> None:
    source = environment_render_scene().claim.value
    adapted = environment_render_scene_observation(source)
    source["items"][0]["object_id"] = "mutated-after-adaptation"
    assert adapted.claim.value["items"][0]["object_id"] == "ground-a"


def dynamic_pose_source(*, wrong_cut: bool = False, wrong_checkpoint: bool = False):
    candidate_value = {
        "contract_revision": "embodiment.render_link_pose_candidate/v1",
        "body_id": "body-a", "embodiment_episode_id": "episode-a",
        "morphology_revision": "morphology-r1", "geometry_revision": "geometry-r1",
        "render_geometry_sha256": "a" * 64, "source_world_id": "world-a",
        "physical_step_id": "step-4", "environment_revision": "environment-r1",
        "solver_config_revision": "solver-r1", "source_causal_tick": 4,
        "target_causal_tick": 5, "reference_frame": "physics3d.world",
        "coordinate_system": "right_handed_z_up", "length_unit": "m",
        "completeness": "complete", "poses": [{
            "segment_id": "link-a", "translation_m": [1.0, 2.0, 3.0],
            "orientation_xyzw": [0.0, 0.0, 0.0, 1.0],
        }],
    }

    class Candidate:
        def __init__(self):
            self.value = candidate_value

        def to_payload(self):
            return self.value

        def canonical_bytes(self):
            return rfc8785.dumps(self.value)

        def __getattr__(self, name):
            return self.value[name]

    checkpoint = SimpleNamespace(
        owner="embodiment", owner_identity="other-body" if wrong_checkpoint else "body-a",
        checkpoint_id="checkpoint-5", schema_version="1", locator="local:checkpoint-5", sha256="b" * 64,
    )
    cut_checkpoint = SimpleNamespace(
        owner="embodiment", owner_identity="body-a", checkpoint_id="checkpoint-5",
        schema_version="1", locator="local:checkpoint-5", sha256="b" * 64,
    )
    cut = SimpleNamespace(
        world_id="world-a", causal_tick=6 if wrong_cut else 5, commit_id="world-a:commit:5",
        participant_ids=(("embodiment", "body-a"),),
        presence_owner_links=(("organism", "organism-a", "body-a"),),
        owner_checkpoint_references=(cut_checkpoint,),
    )
    return SimpleNamespace(
        committed_cut=cut, owner_checkpoint_reference=checkpoint,
        projection_sha256=hashlib.sha256(rfc8785.dumps(candidate_value)).hexdigest(), candidate=Candidate(),
    )


@pytest.mark.parametrize("observation", [environment_render_scene(), embodiment_render_morphology()])
def test_static_spatial_projections_are_carried_without_reinterpretation(observation) -> None:
    plane = ObservationPlane()
    plane.publish(observation)
    wire = json.loads(encode_current_messages(plane, max_response_bytes=1_000_000))
    assert wire["messages"][0]["observation"]["claim"]["value"] == observation.claim.value
    assert wire["messages"][0]["observation"]["acquisition"]["method"] == "owner_projection"
    assert wire["messages"][0]["observation"]["asserter"]["identifier"] == "owner_projection"


def test_dynamic_render_pose_is_passively_carried_with_transient_world_cut() -> None:
    observation = embodiment_render_link_pose_observation(dynamic_pose_source())
    plane = ObservationPlane()
    plane.publish(observation)
    wire = json.loads(encode_current_messages(plane, max_response_bytes=1_000_000))
    carried = wire["messages"][0]["observation"]["claim"]["value"]
    assert carried == observation.claim.value
    assert carried["world_association"]["association_kind"] == "transient_current_committed_cut"
    assert carried["world_association"]["committed_cut"]["commit_id"] == "world-a:commit:5"
    assert carried["candidate"]["poses"][0]["segment_id"] == "link-a"


@pytest.mark.parametrize("source", [
    dynamic_pose_source(wrong_cut=True),
    dynamic_pose_source(wrong_checkpoint=True),
])
def test_dynamic_render_pose_mapper_rejects_wrong_cut_or_checkpoint(source) -> None:
    with pytest.raises(ValueError, match="cut|checkpoint"):
        embodiment_render_link_pose_observation(source)


@pytest.mark.parametrize("mutation", [
    lambda value: value["world_association"]["committed_cut"].update(causal_tick=6),
    lambda value: value["world_association"]["committed_cut"]["owner_checkpoint_references"].append(
        value["world_association"]["owner_checkpoint_reference"]
    ),
    lambda value: value["candidate"].update(morphology_revision="other-morphology"),
    lambda value: value["candidate"]["poses"][0].update(orientation_xyzw=[0.0, 0.0, 0.0, 2.0]),
    lambda value: value["candidate"].update(extra_field="not-approved"),
])
def test_dynamic_render_pose_http_carrier_rejects_tampering(mutation) -> None:
    observation = embodiment_render_link_pose_observation(dynamic_pose_source())
    value = json.loads(json.dumps(observation.claim.value))
    mutation(value)
    altered = SemanticObservation(
        claim=SemanticClaim(observation.family, observation.claim.subject, observation.claim.epistemic_kind, value),
        acquisition=observation.acquisition, asserter=observation.asserter, producer=observation.producer,
        context_time=observation.context_time, lineage=observation.lineage,
    )
    plane = ObservationPlane()
    plane.publish(altered)
    with pytest.raises(ValueError, match="render_link_pose"):
        encode_current_messages(plane, max_response_bytes=1_000_000)


def test_dynamic_render_pose_accepts_embodiment_quaternion_norm_boundary() -> None:
    source = dynamic_pose_source()
    source.candidate.value["poses"][0]["orientation_xyzw"] = [0.0, 0.0, 0.0, 1.0000005]
    source.projection_sha256 = hashlib.sha256(source.candidate.canonical_bytes()).hexdigest()
    observation = embodiment_render_link_pose_observation(source)
    plane = ObservationPlane()
    plane.publish(observation)
    wire = json.loads(encode_current_messages(plane, max_response_bytes=1_000_000))
    assert wire["messages"][0]["observation"]["claim"]["value"]["candidate"]["poses"][0]["orientation_xyzw"][-1] == 1.0000005


@pytest.mark.parametrize(
    ("observation", "mutation"),
    [
        (environment_render_scene(), lambda value: value.update(extra_field=True)),
        (environment_render_scene(), lambda value: value["items"][0].update(kind="mesh")),
        (environment_render_scene(), lambda value: value["items"][0].update(offset_m=10**1000)),
        (environment_render_scene(), lambda value: value.update(render_geometry_sha256=17)),
        (embodiment_render_morphology(), lambda value: value["segments"][0].update(shape="sphere")),
        (embodiment_render_morphology(), lambda value: value["joints"][0].update(axis_in_joint_frame=[0.0, 0.0, 0.0])),
    ],
)
def test_static_spatial_projections_reject_unapproved_shapes(observation, mutation) -> None:
    value = json.loads(json.dumps(observation.claim.value))
    mutation(value)
    altered = SemanticObservation(
        claim=SemanticClaim(observation.family, observation.claim.subject, observation.claim.epistemic_kind, value),
        acquisition=observation.acquisition,
        asserter=observation.asserter,
        producer=observation.producer,
        domain_time=observation.domain_time,
        context_time=observation.context_time,
        lineage=observation.lineage,
        conditions=observation.conditions,
    )
    plane = ObservationPlane()
    plane.publish(altered)
    with pytest.raises(ValueError, match="render_"):
        encode_current_messages(plane, max_response_bytes=1_000_000)


@pytest.mark.parametrize("family", ["environment", "embodiment"])
def test_static_spatial_projection_rejects_subject_or_lineage_mismatch(family) -> None:
    observation = environment_render_scene() if family == "environment" else embodiment_render_morphology()
    wrong_subject = SemanticObservation(
        claim=SemanticClaim(observation.family, SubjectScope(observation.claim.subject.kind, key="wrong"), observation.claim.epistemic_kind, observation.claim.value),
        acquisition=observation.acquisition, asserter=observation.asserter, producer=observation.producer,
        lineage=observation.lineage,
    )
    wrong_digest = Lineage(parents=(LineageSourceRef("render_geometry_sha256", "0" * 64),), transformation=observation.lineage.transformation)
    wrong_lineage = SemanticObservation(
        claim=observation.claim, acquisition=observation.acquisition, asserter=observation.asserter,
        producer=observation.producer, lineage=wrong_digest,
    )
    for malformed in (wrong_subject, wrong_lineage):
        plane = ObservationPlane()
        plane.publish(malformed)
        with pytest.raises(ValueError):
            encode_current_messages(plane, max_response_bytes=1_000_000)

    extra_identity = IdentityAssertion(
        IdentityRef("world", "world-a", observation.asserter), observation.asserter
    )
    subject = observation.claim.subject
    duplicate_kind_identity = IdentityAssertion(
        IdentityRef(
            subject.identities[0].identity.kind,
            "conflicting-duplicate",
            observation.asserter,
        ),
        observation.asserter,
    )
    with_duplicate_kind = SemanticObservation(
        claim=SemanticClaim(
            observation.family,
            SubjectScope(
                subject.kind,
                key=subject.key,
                identities=(*subject.identities, duplicate_kind_identity),
            ),
            observation.claim.epistemic_kind,
            observation.claim.value,
        ),
        acquisition=observation.acquisition,
        asserter=observation.asserter,
        producer=observation.producer,
        lineage=observation.lineage,
    )
    plane = ObservationPlane()
    plane.publish(with_duplicate_kind)
    with pytest.raises(ValueError, match="duplicate typed identities|subject identities"):
        encode_current_messages(plane, max_response_bytes=1_000_000)

    with_extra_identity = SemanticObservation(
        claim=SemanticClaim(
            observation.family,
            SubjectScope(subject.kind, key=subject.key, identities=(*subject.identities, extra_identity)),
            observation.claim.epistemic_kind,
            observation.claim.value,
        ),
        acquisition=observation.acquisition, asserter=observation.asserter,
        producer=observation.producer, lineage=observation.lineage,
    )
    extra_config = Lineage(
        parents=observation.lineage.parents,
        transformation=TransformationRef(
            "owner.static_render_projection", "1",
            (*observation.lineage.transformation.effective_configuration, ("unexpected", "value")),
        ),
    )
    with_extra_config = SemanticObservation(
        claim=observation.claim, acquisition=observation.acquisition, asserter=observation.asserter,
        producer=observation.producer, lineage=extra_config,
    )
    unrelated_namespace = Lineage(
        parents=(LineageSourceRef("unrelated", observation.claim.value["render_geometry_sha256"]),),
        transformation=observation.lineage.transformation,
    )
    with_wrong_namespace = SemanticObservation(
        claim=observation.claim, acquisition=observation.acquisition, asserter=observation.asserter,
        producer=observation.producer, lineage=unrelated_namespace,
    )
    for malformed in (with_extra_identity, with_extra_config, with_wrong_namespace):
        plane = ObservationPlane(); plane.publish(malformed)
        with pytest.raises(ValueError):
            encode_current_messages(plane, max_response_bytes=1_000_000)


def test_environment_frame_and_plane_vectors_enforce_owner_invariants() -> None:
    cases = [
        lambda value: value["frame"]["x_axis_in_parent"].__setitem__(0, 2.0),
        lambda value: value["frame"]["z_axis_in_parent"].__setitem__(0, 1.0),
        lambda value: value["items"][0]["normal"].__setitem__(2, 2.0),
    ]
    original = environment_render_scene()
    for mutation in cases:
        value = json.loads(json.dumps(original.claim.value))
        mutation(value)
        altered = SemanticObservation(
            claim=SemanticClaim(original.family, original.claim.subject, original.claim.epistemic_kind, value),
            acquisition=original.acquisition, asserter=original.asserter, producer=original.producer,
            lineage=original.lineage,
        )
        plane = ObservationPlane(); plane.publish(altered)
        with pytest.raises(ValueError):
            encode_current_messages(plane, max_response_bytes=1_000_000)


def test_embodiment_source_ids_reject_whitespace_normalization() -> None:
    original = embodiment_render_morphology()
    value = json.loads(json.dumps(original.claim.value))
    value["body_id"] = " body-a "
    altered = SemanticObservation(
        claim=SemanticClaim(original.family, original.claim.subject, original.claim.epistemic_kind, value),
        acquisition=original.acquisition, asserter=original.asserter, producer=original.producer,
        lineage=original.lineage,
    )
    plane = ObservationPlane(); plane.publish(altered)
    with pytest.raises(ValueError):
        encode_current_messages(plane, max_response_bytes=1_000_000)


@pytest.mark.parametrize("family", ["environment", "embodiment"])
def test_static_spatial_projection_rejects_stale_content_digest(family) -> None:
    original = environment_render_scene() if family == "environment" else embodiment_render_morphology()
    value = json.loads(json.dumps(original.claim.value))
    if family == "environment":
        value["items"][0]["offset_m"] = 0.5
    else:
        value["segments"][0]["dimensions_m"][0] = 0.5
    altered = SemanticObservation(
        claim=SemanticClaim(original.family, original.claim.subject, original.claim.epistemic_kind, value),
        acquisition=original.acquisition, asserter=original.asserter, producer=original.producer,
        lineage=original.lineage,
    )
    plane = ObservationPlane(); plane.publish(altered)
    with pytest.raises(ValueError, match="digest"):
        encode_current_messages(plane, max_response_bytes=1_000_000)


def _get(url: str, *, host: str | None = None, origin: str | None = FRONTEND_ORIGIN):
    request = Request(url, method="GET", headers={})
    if host is not None:
        request.add_header("Host", host)
    if origin is not None:
        request.add_header("Origin", origin)
    return urlopen(request, timeout=2)


def test_wire_snapshot_preserves_semantic_and_delivery_provenance() -> None:
    plane = ObservationPlane()
    plane.publish(body_pose_observation())
    encoded = encode_current_messages(plane, max_response_bytes=100_000)
    payload = json.loads(encoded)

    assert payload["availability"] == "available"
    assert payload["scope"] == "bounded_in_memory_current_subset"
    assert payload["freshness"] == "not_established_by_snapshot"
    assert payload["coherence"] == "per_message_only_no_cross_owner_snapshot_guarantee"
    assert payload["messages"][0]["delivery_sequence"] == 1
    observation = payload["messages"][0]["observation"]
    assert observation["claim"]["family"]["authority"] == "embodiment"
    assert observation["claim"]["family"]["contract"]["revision"] == "v1"
    assert observation["claim"]["value"]["position"]["value"] == [1.0, 2.0, 3.0]
    assert observation["context_time"][0]["value"] == 4
    assert observation["lineage"]["parents"][0]["reference"] == "a" * 64


def test_empty_current_view_is_not_reported_as_source_absence() -> None:
    payload = json.loads(encode_current_messages(ObservationPlane(), max_response_bytes=100_000))
    assert payload["availability"] == "current_view_empty"
    assert payload["absence_semantics"] == "not_evidence_of_source_absence"
    assert payload["messages"] == []


def test_wire_snapshot_preserves_environment_units_identity_and_cut_context() -> None:
    plane = ObservationPlane()
    plane.publish(finite_scalar_observation())
    payload = json.loads(encode_current_messages(plane, max_response_bytes=100_000))
    message = payload["messages"][0]
    observation = message["observation"]
    assert observation["claim"]["family"]["authority"] == "environment"
    assert observation["claim"]["family"]["contract"] == {
        "contract_id": "biopeia.environment.finite-scalar-field",
        "revision": "1",
    }
    assert observation["claim"]["value"]["unit"] == "1"
    assert observation["claim"]["value"]["value"] == 0.25
    assert [item["kind"] for item in observation["context_time"]] == [
        "world_source_causal_tick",
        "world_target_causal_tick",
    ]
    assert observation["lineage"]["parents"][0]["namespace"] == "owner_checkpoint_sha256"


@pytest.mark.parametrize(
    ("contract_id", "revision"),
    [("embodiment.body_pose", "v2"), ("biopeia.environment.finite-scalar-field", "2")],
)
def test_wire_snapshot_excludes_unapproved_contract_revisions(contract_id, revision) -> None:
    observation = body_pose_observation() if contract_id.startswith("embodiment") else finite_scalar_observation()
    altered = SemanticObservation(
        claim=SemanticClaim(
            family=SemanticFamily(
                observation.family.authority,
                observation.family.path,
                SemanticContractRef(contract_id, revision),
            ),
            subject=observation.claim.subject,
            epistemic_kind=observation.claim.epistemic_kind,
            value=observation.claim.value,
        ),
        acquisition=observation.acquisition,
        asserter=observation.asserter,
        producer=observation.producer,
        domain_time=observation.domain_time,
        context_time=observation.context_time,
        lineage=observation.lineage,
        conditions=observation.conditions,
    )
    plane = ObservationPlane()
    plane.publish(altered)
    payload = json.loads(encode_current_messages(plane, max_response_bytes=100_000))
    assert payload["availability"] == "current_view_empty"
    assert payload["messages"] == []


def test_exact_approved_family_with_wrong_authority_provenance_fails_closed() -> None:
    observation = body_pose_observation()
    altered = SemanticObservation(
        claim=SemanticClaim(
            family=observation.family,
            subject=observation.claim.subject,
            epistemic_kind=observation.claim.epistemic_kind,
            value=observation.claim.value,
        ),
        acquisition=observation.acquisition,
        asserter=ActorRef("unexpected_owner", "not_embodiment"),
        producer=observation.producer,
        context_time=observation.context_time,
        lineage=observation.lineage,
    )
    plane = ObservationPlane()
    plane.publish(altered)
    with pytest.raises(ValueError, match="authority provenance"):
        encode_current_messages(plane, max_response_bytes=100_000)


def test_malformed_approved_family_payload_fails_closed() -> None:
    observation = body_pose_observation()
    value = dict(observation.claim.value)
    value.pop("position")
    malformed = SemanticObservation(
        claim=SemanticClaim(
            family=observation.family,
            subject=observation.claim.subject,
            epistemic_kind=observation.claim.epistemic_kind,
            value=value,
        ),
        acquisition=observation.acquisition,
        asserter=observation.asserter,
        producer=observation.producer,
        context_time=observation.context_time,
        lineage=observation.lineage,
    )
    plane = ObservationPlane()
    plane.publish(malformed)
    with pytest.raises(LocalReadBridgeError, match="approved shape"):
        encode_current_messages(plane, max_response_bytes=100_000)


def test_body_pose_rejects_wrong_quaternion_convention() -> None:
    observation = body_pose_observation()
    value = dict(observation.claim.value)
    value["orientation"] = dict(value["orientation"], convention="unspecified")
    malformed = SemanticObservation(
        claim=SemanticClaim(
            family=observation.family,
            subject=observation.claim.subject,
            epistemic_kind=observation.claim.epistemic_kind,
            value=value,
        ),
        acquisition=observation.acquisition,
        asserter=observation.asserter,
        producer=observation.producer,
        context_time=observation.context_time,
        lineage=observation.lineage,
    )
    plane = ObservationPlane()
    plane.publish(malformed)
    with pytest.raises(LocalReadBridgeError, match="orientation contract"):
        encode_current_messages(plane, max_response_bytes=100_000)


def test_malformed_approved_family_is_unavailable_not_oversize() -> None:
    observation = body_pose_observation()
    malformed_value = dict(observation.claim.value)
    malformed_value.pop("position")
    malformed = SemanticObservation(
        claim=SemanticClaim(
            family=observation.family,
            subject=observation.claim.subject,
            epistemic_kind=observation.claim.epistemic_kind,
            value=malformed_value,
        ),
        acquisition=observation.acquisition,
        asserter=observation.asserter,
        producer=observation.producer,
        context_time=observation.context_time,
        lineage=observation.lineage,
    )
    plane = ObservationPlane()
    plane.publish(malformed)
    bridge = LocalObservationReadBridge.create(plane, host="127.0.0.1", port=0)
    with bridge:
        host, port = bridge.address
        with pytest.raises(HTTPError) as exc:
            _get(f"http://{host}:{port}/v1/current", host=f"{host}:{port}")
        assert exc.value.code == 503
        assert json.loads(exc.value.read()) == {"error": "current_view_unavailable"}


def test_bridge_serves_only_allowlisted_current_observations() -> None:
    plane = ObservationPlane()
    plane.publish(body_pose_observation())
    plane.publish(unauthorized_observation())
    bridge = LocalObservationReadBridge.create(plane, host="127.0.0.1", port=0)
    with bridge:
        host, port = bridge.address
        with _get(f"http://{host}:{port}/v1/current", host=f"{host}:{port}") as response:
            body = json.loads(response.read())
            assert response.status == 200
            assert response.headers["Cache-Control"] == "no-store"
            assert len(body["messages"]) == 1
            assert body["messages"][0]["observation"]["claim"]["family"]["authority"] == "embodiment"
    assert plane.latest_sequence == 2


@pytest.mark.parametrize(
    ("host", "origin", "status", "error"),
    [
        ("attacker.example", FRONTEND_ORIGIN, 400, "invalid_host"),
        ("wrong-host:1", FRONTEND_ORIGIN, 400, "invalid_host"),
        ("<current>", None, 403, "origin_denied"),
        ("wrong-host:1", "http://evil.example", 400, "invalid_host"),
    ],
)
def test_bridge_rejects_invalid_host_or_origin(host, origin, status, error) -> None:
    bridge = LocalObservationReadBridge.create(ObservationPlane(), host="127.0.0.1", port=0)
    with bridge:
        address_host, port = bridge.address
        actual_host = f"{address_host}:{port}" if host == "<current>" else host
        with pytest.raises(HTTPError) as exc:
            _get(f"http://{address_host}:{port}/v1/current", host=actual_host, origin=origin)
        assert exc.value.code == status
        assert json.loads(exc.value.read())["error"] == error


def test_bridge_rejects_non_get_methods_and_unknown_routes() -> None:
    bridge = LocalObservationReadBridge.create(ObservationPlane(), host="127.0.0.1", port=0)
    with bridge:
        host, port = bridge.address
        url = f"http://{host}:{port}/v1/current"
        request = Request(url, method="POST", headers={"Host": f"{host}:{port}", "Origin": FRONTEND_ORIGIN})
        with pytest.raises(HTTPError) as exc:
            urlopen(request, timeout=2)
        assert exc.value.code == 405
        request = Request(url + "?family=organism.private_state", headers={"Host": f"{host}:{port}", "Origin": FRONTEND_ORIGIN})
        with pytest.raises(HTTPError) as exc:
            urlopen(request, timeout=2)
        assert exc.value.code == 404


def test_bridge_rejects_missing_host_header() -> None:
    bridge = LocalObservationReadBridge.create(ObservationPlane(), host="127.0.0.1", port=0)
    with bridge:
        host, port = bridge.address
        with socket.create_connection((host, port), timeout=2) as connection:
            connection.sendall(
                b"GET /v1/current HTTP/1.1\r\n"
                b"Origin: http://127.0.0.1:4173\r\n"
                b"Connection: close\r\n\r\n"
            )
            chunks = []
            while chunk := connection.recv(4096):
                chunks.append(chunk)
            response = b"".join(chunks)
        assert b"400 Bad Request" in response
        assert b"invalid_host" in response


def test_bridge_rejects_non_loopback_configuration_and_payload_overflow() -> None:
    with pytest.raises(ValueError, match="loopback"):
        LocalObservationReadBridge.create(ObservationPlane(), host="0.0.0.0", port=0)
    with pytest.raises(ValueError, match="loopback origin"):
        LocalObservationReadBridge.create(
            ObservationPlane(), allowed_origin="http://192.0.2.2:4173", port=0
        )
    plane = ObservationPlane()
    plane.publish(body_pose_observation())
    with pytest.raises(ValueError, match="byte limit"):
        encode_current_messages(plane, max_response_bytes=1)


def test_current_read_does_not_mutate_claim_or_advance_plane() -> None:
    plane = ObservationPlane()
    plane.publish(body_pose_observation())
    before = plane.current_messages()
    bridge = LocalObservationReadBridge.create(plane, host="127.0.0.1", port=0)
    with bridge:
        host, port = bridge.address
        for _ in range(2):
            with _get(f"http://{host}:{port}/v1/current", host=f"{host}:{port}") as response:
                json.loads(response.read())
    after = plane.current_messages()
    assert plane.latest_sequence == 1
    assert before == after

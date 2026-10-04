"""Longitudinal Integrity v1 LI-P0: no runtime state may remain unclassified."""

from __future__ import annotations

import inspect

import pytest

from lab.integration.organism import create_canonical_organism
from symbiont.core.orchestration.runtime import OrganismRuntime
from symbiont.host.continuity import (
    APPARATUS_FIELDS,
    CONDITIONAL_FIELDS,
    ENVELOPE_FIELDS,
    LAYERS,
    REGISTER,
    ContinuityClass,
    Reembodiment,
    entries_for,
)
from symbiont.modeling.private_runtime import PrivateModelOrganismRuntime
from symbiont.modeling.runtime import ModeledOrganismRuntime

RUNTIMES = dict(zip(LAYERS, (OrganismRuntime, ModeledOrganismRuntime, PrivateModelOrganismRuntime)))
# Audit findings whose contract the code does not meet yet. A new gap must be
# named here and in the register entry that carries it.
# Semantic classification findings not yet resolved. A gap is attached to the
# exact state entry whose contract still needs owner-level resolution.
OPEN_GAPS: set[str] = set()


def _runtime(layer: str, **kwargs: object) -> OrganismRuntime:
    runtime = create_canonical_organism(
        RUNTIMES[layer],
        bootstrap_semantic_senses=True,
        discover_senses=False,
        min_samples=1,
        **kwargs,
    )
    runtime.tick()
    return runtime


def test_register_has_one_entry_per_attribute() -> None:
    names = [entry.attribute for entry in REGISTER]
    assert sorted(names) == sorted(set(names))


@pytest.mark.parametrize("layer", LAYERS)
def test_every_runtime_attribute_is_classified(layer: str) -> None:
    registered = {entry.attribute for entry in entries_for(layer)}
    assert registered == set(vars(_runtime(layer)))


@pytest.mark.parametrize("layer", LAYERS)
@pytest.mark.parametrize("persist_replay_state", [False, True])
def test_every_checkpoint_field_is_owned(layer: str, persist_replay_state: bool) -> None:
    owned = {field for entry in entries_for(layer) for field in entry.checkpoint_fields}
    owned |= {field.checkpoint_field for field in ENVELOPE_FIELDS}
    runtime = _runtime(layer, persist_replay_state=persist_replay_state)
    written = set(runtime.checkpoint())
    assert written <= owned
    assert owned - written <= CONDITIONAL_FIELDS


def test_nested_checkpoint_envelope_fields_are_inventoried() -> None:
    runtime = _runtime(LAYERS[0])
    payload = runtime.checkpoint()

    def nested_paths(value: dict[str, object], prefix: str = "") -> set[str]:
        paths: set[str] = set()
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else key
            paths.add(path)
            if isinstance(child, dict):
                paths.update(nested_paths(child, path))
        return paths

    for envelope in ENVELOPE_FIELDS:
        if not envelope.nested_checkpoint_fields:
            continue
        nested = payload[envelope.checkpoint_field]
        assert isinstance(nested, dict), envelope.checkpoint_field
        assert nested_paths(nested) <= set(envelope.nested_checkpoint_fields), (
            envelope.checkpoint_field
        )


def test_continuation_controls_have_matching_register_owners() -> None:
    provenance = next(
        entry for entry in ENVELOPE_FIELDS if entry.checkpoint_field == "runtime_provenance"
    )
    controls = {
        path.split(".", maxsplit=2)[1]
        for path in provenance.nested_checkpoint_fields
        if path.startswith("session_controls.")
    }
    registered = {
        entry.attribute.removeprefix("_")
        for entry in REGISTER
        if entry.checkpoint_field == "runtime_provenance"
    }

    assert controls == registered
    assert all(
        entry.continuity is ContinuityClass.MUST_REAPPLY_CONFIG
        and not entry.in_state_identity
        for entry in REGISTER
        if entry.checkpoint_field == "runtime_provenance"
    )


def test_state_identity_flag_matches_the_hashed_payload() -> None:
    runtime = _runtime(LAYERS[-1])
    hashed = set(runtime._build_checkpoint_payload()) - {"runtime_provenance"}
    declared = {
        field for entry in REGISTER if entry.in_state_identity for field in entry.checkpoint_fields
    }
    declared |= {field.checkpoint_field for field in ENVELOPE_FIELDS if field.in_state_identity}
    assert declared - CONDITIONAL_FIELDS == hashed


def test_entries_are_internally_consistent() -> None:
    for entry in REGISTER:
        assert entry.owner and entry.restore_path and entry.migration, entry.attribute
        if entry.continuity is ContinuityClass.MUST_PRESERVE and entry.checkpoint_field is None:
            assert entry.known_gap is not None, entry.attribute
        if entry.continuity is ContinuityClass.MUST_RESET:
            assert entry.reembodiment is not Reembodiment.INVALIDATED, entry.attribute
        if entry.continuity is ContinuityClass.MUST_INVALIDATE_AUTHORITY:
            assert entry.reembodiment is Reembodiment.INVALIDATED, entry.attribute
        if entry.continuity is ContinuityClass.MUST_REAPPLY_CONFIG:
            assert entry.checkpoint_field is not None, entry.attribute
        nested_paths = [path for path, _ in entry.nested_reembodiment]
        assert len(nested_paths) == len(set(nested_paths)), entry.attribute
        if entry.nested_reembodiment:
            # Nested paths may document mixed behavior inside a field whose
            # aggregate contract is authority invalidation.
            assert entry.reembodiment in {
                Reembodiment.PRESERVED,
                Reembodiment.INVALIDATED,
                Reembodiment.MIXED,
            }, entry.attribute
            assert entry.nested_checkpoint_fields, entry.attribute
            assert set(entry.nested_checkpoint_fields) <= set(entry.checkpoint_fields), (
                entry.attribute
            )
        else:
            assert not entry.nested_checkpoint_fields, entry.attribute


def test_retired_heritable_genome_is_not_misclassified_as_reembodiment_state() -> None:
    entry = next(entry for entry in REGISTER if entry.attribute == "_heritable_genome")

    assert entry.continuity is ContinuityClass.MUST_RESET
    assert entry.reembodiment is Reembodiment.NOT_APPLICABLE
    assert "rejected" in entry.migration
    assert "write null" in entry.migration


def test_developmental_tracker_resets_only_body_bound_stress_edge() -> None:
    entry = next(entry for entry in REGISTER if entry.attribute == "_developmental_tracker")

    assert entry.reembodiment is Reembodiment.PRESERVED
    assert dict(entry.nested_reembodiment) == {
        "schema_version": Reembodiment.NOT_APPLICABLE,
        "tick": Reembodiment.PRESERVED,
        "stress_ticks": Reembodiment.PRESERVED,
        "recovery_events": Reembodiment.PRESERVED,
        "repair_events": Reembodiment.PRESERVED,
        "excretion_events": Reembodiment.PRESERVED,
        "maintenance_burden": Reembodiment.PRESERVED,
        "retention_burden": Reembodiment.PRESERVED,
        "previous_stressed": Reembodiment.REPLACED,
    }


def test_reembodiment_register_distinguishes_active_state_from_archived_priors() -> None:
    entries = {entry.attribute: entry for entry in REGISTER}

    assert entries["_sensory_system"].reembodiment is Reembodiment.REPLACED
    assert entries["_sensory_system"].archived_as_prior == (
        "embodiment_archive.body_memories[*].sensory_prior.sensory_system"
    )
    assert entries["_adaptive_senses"].reembodiment is Reembodiment.REPLACED
    assert entries["_adaptive_senses"].archived_as_prior == (
        "embodiment_archive.body_memories[*].sensory_prior.sensory_development"
    )
    assert entries["_body_schema"].reembodiment is Reembodiment.MIXED
    assert entries["_body_schema"].archived_as_prior == (
        "embodiment_archive.body_memories[*].body_schema_prior"
    )


def test_open_gaps_are_exactly_the_audit_findings() -> None:
    assert {entry.known_gap for entry in REGISTER} - {None} == OPEN_GAPS


def test_apparatus_fields_name_real_physics3d_state() -> None:
    pytest.importorskip("pybullet")
    from lab.physics3d.runtime import PyBulletEmbodimentRuntime
    from symbiont.core.embodiment import transition as reembodiment

    source = inspect.getsource(PyBulletEmbodimentRuntime) + inspect.getsource(reembodiment)
    for field in APPARATUS_FIELDS:
        assert f"self.{field.attribute}" in source, field.attribute
        assert f'"{field.checkpoint_field}"' in source, field.checkpoint_field

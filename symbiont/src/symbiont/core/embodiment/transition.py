"""How the organism transforms its own state when its embodiment changes.

A caller describes the new embodiment by an opaque contract (kind, receptor and
effector counts) and asks for the transition. What is kept, archived or cleared
is decided here, in terms of the organism's own state; no simulator, body
implementation or apparatus is known to this module.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Mapping

from symbiont.actuation.surface import ActuatorSurface
from symbiont.core.embodiment import (
    BodySpecificMemory,
    EmbodimentArchive,
    archive_episode_checkpoint,
)
from symbiont.core.embodiment.body_schema import BodySchemaEngine
from symbiont.core.embodiment.longitudinal import (
    CONTRACT_FINGERPRINT_SCHEMA_VERSION,
    append_epoch_summary,
    archive_contract_memory,
    build_epoch_summary,
    contract_fingerprint,
    historical_motor_candidates,
    inject_memory_candidates,
    memory_for_contract,
)
from symbiont.core.regulation.reactivity import InnateReactivity
from symbiont.host.checkpoint import (
    CHECKPOINT_SCHEMA_VERSION,
    stamp_checkpoint_identity,
    verify_checkpoint_identity,
)
from symbiont.host.continuity import LongitudinalContract

# Longitudinal contract of the subject this module builds (issue #273).
LONGITUDINAL_CONTRACT = LongitudinalContract.CANONICAL_REEMBODIMENT

_MAX_EMBODIMENT_HISTORY = 8
_SCHEMA_VERSION = 1
_CANONICAL_CONTRACT_FINGERPRINT_SCHEMA_VERSION = 3


@dataclass(frozen=True, slots=True)
class EmbodimentDescriptor:
    body_kind: str
    receptor_count: int
    effector_count: int

    def as_dict(self) -> dict[str, object]:
        return {
            "body_kind": self.body_kind,
            "receptor_count": self.receptor_count,
            "effector_count": self.effector_count,
        }


def _body_vital_state(payload: Mapping[str, Any]) -> str:
    living = payload.get("living_body")
    if isinstance(living, Mapping):
        value = living.get("vital_state")
        if isinstance(value, str) and value:
            return value
    return "unknown"


def _declares_current_checkpoint_schema(payload: Mapping[str, Any]) -> bool:
    """Recognize current-schema markers even if one envelope field was lost."""
    provenance = payload.get("runtime_provenance")
    lineage = payload.get("checkpoint_lineage")
    declared = (
        payload.get("schema_version"),
        provenance.get("checkpoint_schema_version") if isinstance(provenance, Mapping) else None,
        lineage.get("schema_version") if isinstance(lineage, Mapping) else None,
    )
    return any(
        isinstance(version, int)
        and not isinstance(version, bool)
        and version >= CHECKPOINT_SCHEMA_VERSION
        for version in declared
    )


def _legacy_contract(_payload: Mapping[str, Any]) -> EmbodimentDescriptor:
    """Apply ``LEGACY_COMPATIBILITY_ASSUMPTION`` for pre-epoch files.

    This is not a current-body discovery mechanism: historical portable
    Physics3D checkpoints without an epoch descriptor are interpreted as the
    one known legacy profile (anthropomorphic-v4, 107 receptors, 62 effectors).
    Do not reuse this fallback for new checkpoints. Remove it only after an
    artifact census proves no retained checkpoint needs this interpretation.
    """
    return EmbodimentDescriptor("anthropomorphic-v4", 107, 62)


def migrate_temporal_domains(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Repair the legacy global-tick -> Body-age contamination when unambiguous.

    This migration fixes clock coordinates only. It deliberately does not
    reverse senescence, wear, energy loss or any other historical physiology
    already produced under the contaminated clock.
    """
    result = deepcopy(dict(payload))
    lifecycle = result.get("embodiment_lifecycle")
    living = result.get("living_body")
    if not isinstance(lifecycle, Mapping) or not isinstance(living, dict):
        return result
    if lifecycle.get("schema_version") != _SCHEMA_VERSION:
        return result
    current = lifecycle.get("current")
    if not isinstance(current, Mapping):
        return result

    saved_tick = result.get("saved_at_tick")
    started_tick = current.get("started_tick")
    stored_age = living.get("age_ticks")
    if (
        isinstance(saved_tick, bool)
        or not isinstance(saved_tick, int)
        or isinstance(started_tick, bool)
        or not isinstance(started_tick, int)
        or isinstance(stored_age, bool)
        or not isinstance(stored_age, int)
    ):
        return result
    if started_tick <= 0 or saved_tick < started_tick:
        return result

    expected_age = saved_tick - started_tick
    if stored_age == expected_age:
        return result

    # Legacy Physics3D wrote Body age from the global runtime tick. Accept a
    # one-tick tolerance because checkpoints are taken after tick completion.
    if abs(stored_age - saved_tick) > 1:
        return result

    # This migration also re-identifies its output. Do not let an authorized
    # clock correction become a way to bless unrelated checkpoint tampering.
    verify_checkpoint_identity(dict(payload))
    old_age = stored_age
    living["age_ticks"] = expected_age
    raw_death = living.get("death_tick")
    if isinstance(raw_death, int) and not isinstance(raw_death, bool):
        if abs(raw_death - old_age) <= 1 or abs(raw_death - saved_tick) <= 1:
            living["death_tick"] = expected_age

    physiology = result.get("physiology")
    if isinstance(physiology, dict):
        raw_phys_death = physiology.get("death_tick")
        if isinstance(raw_phys_death, int) and not isinstance(raw_phys_death, bool):
            if abs(raw_phys_death - old_age) <= 1 or abs(raw_phys_death - saved_tick) <= 1:
                physiology["death_tick"] = expected_age

    result["temporal_migration"] = {
        "schema_version": 1,
        "kind": "global_tick_to_body_age",
        "source_age_ticks": old_age,
        "body_age_ticks": expected_age,
        "started_at_symbiont_tick": started_tick,
        "saved_at_symbiont_tick": saved_tick,
    }
    # The corrected clock is a different organism state than the one saved.
    return stamp_checkpoint_identity(result, transform="temporal-decontamination")


def lifecycle_summary(payload: Mapping[str, Any]) -> dict[str, object]:
    episode = payload.get("embodiment_episode")
    if isinstance(episode, Mapping) and int(episode.get("schema_version") or 0) in {2, 3}:
        contract = episode.get("contract")
        contract = contract if isinstance(contract, Mapping) else {}
        return {
            "state": str(episode.get("state") or "suspended"),
            "epoch": max(1, int(episode.get("epoch") or 1)),
            "current": {
                "embodiment_id": str(episode.get("embodiment_id") or ""),
                "body_id": str(episode.get("body_id") or ""),
                "started_tick": int(episode.get("start_symbiont_tick") or 0),
                "embodiment_tick": int(episode.get("embodiment_tick") or 0),
                "contract_fingerprint": str(contract.get("contract_fingerprint") or ""),
                "body_vital_state": _body_vital_state(payload),
            },
            "history_count": len(payload.get("embodiment_epoch_summaries", ()))
            if isinstance(payload.get("embodiment_epoch_summaries"), list)
            else 0,
        }
    raw = payload.get("embodiment_lifecycle")
    if isinstance(raw, Mapping) and raw.get("schema_version") == _SCHEMA_VERSION:
        current = raw.get("current")
        return {
            "state": str(raw.get("state") or "dormant"),
            "epoch": int(raw.get("epoch") or 1),
            "current": dict(current) if isinstance(current, Mapping) else {},
            "history_count": len(raw.get("history", ()))
            if isinstance(raw.get("history"), list)
            else 0,
        }
    # A current-schema checkpoint should always carry one of the recognized
    # lifecycle representations. Do not turn missing/corrupt current metadata
    # into an anthropomorphic-v4 legacy body assertion.
    if _declares_current_checkpoint_schema(payload):
        return {
            "state": "unavailable",
            "epoch": 0,
            "current": {},
            "history_count": 0,
        }
    contract = _legacy_contract(payload)
    return {
        "state": "dormant",
        "epoch": 1,
        "current": {
            **contract.as_dict(),
            "started_tick": 0,
            "body_vital_state": _body_vital_state(payload),
        },
        "history_count": 0,
    }


def _detach_body_specific_cognition(
    checkpoint: Mapping[str, Any],
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """Archive embodiment-sensitive cognition without deleting Symbiont memory.

    Re-embodiment changes current-body authority, not autobiographical
    knowledge. The CognitiveGraph is Symbiont-owned longitudinal state and must
    therefore survive *every* Body replacement intact, regardless of whether
    the new opaque contract is equal, known or novel.

    Body authority is withdrawn elsewhere: fresh sensory/body state, fresh
    actuator health, cleared execution bindings/commitments and the normal
    reacclimation gate. The archival projection returned here records which
    preserved nodes/edges were embodiment-sensitive without mutating the live
    cognitive bridge.
    """
    raw_bridge = checkpoint.get("cognitive_bridge")
    if not isinstance(raw_bridge, Mapping):
        return (
            deepcopy(raw_bridge) if isinstance(raw_bridge, dict) else None,
            None,
        )

    bridge = deepcopy(dict(raw_bridge))
    graph = bridge.get("graph")
    if not isinstance(graph, Mapping):
        return bridge, None

    nodes = graph.get("nodes")
    edges = graph.get("edges")
    if not isinstance(nodes, list) or not isinstance(edges, list):
        return bridge, None

    def body_bound_node(node: Mapping[str, Any]) -> bool:
        node_id = str(node.get("node_id") or "")
        kind = str(node.get("kind") or "")
        return (
            kind in {"sense", "predictor"}
            or node_id.startswith("readout_motor:")
            or node_id.startswith("readout_primitive:")
        )

    body_bound_ids = {
        str(node.get("node_id"))
        for node in nodes
        if isinstance(node, Mapping) and body_bound_node(node)
    }

    archived_nodes = [
        deepcopy(node)
        for node in nodes
        if isinstance(node, Mapping) and str(node.get("node_id")) in body_bound_ids
    ]
    archived_edges = [
        deepcopy(edge)
        for edge in edges
        if isinstance(edge, Mapping)
        and (
            str(edge.get("source_id")) in body_bound_ids
            or str(edge.get("target_id")) in body_bound_ids
        )
    ]

    # P0 longitudinal invariant: a Body replacement must never delete cognition
    # owned by the Symbiont. Archive is a provenance/view over the preserved
    # graph, not a transfer operation.
    return bridge, {
        "nodes": archived_nodes,
        "edges": archived_edges,
    }


def _active_private_model_id(checkpoint: Mapping[str, Any]) -> str | None:
    registry = checkpoint.get("private_model_registry")
    records = registry.get("records") if isinstance(registry, Mapping) else None
    if not isinstance(records, list):
        return None
    for record in records:
        if (
            isinstance(record, Mapping)
            and record.get("state") == "active"
            and isinstance(record.get("model_id"), str)
        ):
            return str(record["model_id"])
    return None


def _historical_sensory_prior(checkpoint: Mapping[str, Any]) -> dict[str, object] | None:
    """Capture learned sensory state without granting it active source bindings."""
    fields = ("sensory_system", "sensory_development")
    prior = {
        field: deepcopy(dict(checkpoint[field]))
        for field in fields
        if isinstance(checkpoint.get(field), Mapping)
    }
    return prior or None


def _carry_sensorimotor_v2_knowledge(
    previous: Mapping[str, Any],
    fresh_actuation: dict[str, Any],
) -> dict[str, Any]:
    """Attach a fresh execution surface without rewriting learned motor knowledge.

    Re-embodiment must preserve the Symbiont's learned causal/motor state.
    Only current-Body authority is replaced: the actuator constitution/evidence
    surface comes from the fresh Body, execution bindings are empty, and
    in-flight execution state is cleared. Competences, effects, causal evidence,
    exploration memory, composition and acquired dimensions are copied exactly
    from the prior Symbiont checkpoint.
    """
    previous_actuation = previous.get("actuation")
    if not isinstance(previous_actuation, Mapping):
        return deepcopy(fresh_actuation)

    result = deepcopy(fresh_actuation)
    prior_domain = previous_actuation.get("action_domain")
    prior_v2 = (
        prior_domain.get("sensorimotor_v2")
        if isinstance(prior_domain, Mapping)
        else previous_actuation.get("sensorimotor_v2")
    )
    fresh_domain = result.get("action_domain")
    fresh_v2 = (
        fresh_domain.get("sensorimotor_v2")
        if isinstance(fresh_domain, Mapping)
        else result.get("sensorimotor_v2")
    )

    if isinstance(prior_v2, Mapping) and isinstance(fresh_v2, Mapping):
        preserved_v2 = deepcopy(dict(prior_v2))
        prior_acquisition = prior_v2.get("agency_acquisition")
        preserved_v2["schema_version"] = 4
        if isinstance(prior_acquisition, Mapping):
            preserved_v2["agency_acquisition"] = deepcopy(dict(prior_acquisition))
        elif not isinstance(preserved_v2.get("agency_acquisition"), Mapping):
            preserved_v2["agency_acquisition"] = {
                "schema_version": 1,
                "attempt_count": 0,
                "intervention_signatures": None,
                "action_dimensions": None,
            }
        # The only rewritten v2 fields describe *current execution authority*.
        # Everything learned remains untouched.
        if "surface_binding" in fresh_v2:
            preserved_v2["surface_binding"] = deepcopy(fresh_v2["surface_binding"])
        preserved_v2["execution_bindings"] = {
            "schema_version": 1,
            "capacity": 512,
            "items": [],
        }
        preserved_v2["binding_invalidation"] = "reembodiment"

        if isinstance(fresh_domain, dict):
            fresh_domain["sensorimotor_v2"] = preserved_v2
            fresh_domain["active_commitment"] = None
            fresh_domain["last_executed_controller_seed_id"] = None
            fresh_domain["pending_motor_observation"] = []
            fresh_domain["pending_proprioception"] = {}
            result["action_domain"] = fresh_domain
        else:
            result["sensorimotor_v2"] = preserved_v2
            result["action_commitment"] = None
            result["last_executed_primitive_id"] = None
            result["pending_motor_observation"] = []
            result["pending_proprioception"] = {}

    return result


def migrate_legacy_memory_store(
    archive: EmbodimentArchive,
    store: Mapping[str, Any] | None,
) -> EmbodimentArchive:
    """One-way import of pre-v2 contract memory into the canonical archive."""
    if not isinstance(store, Mapping) or int(store.get("schema_version") or 0) != 1:
        return archive
    contracts = store.get("contracts")
    if not isinstance(contracts, list):
        return archive
    for index, entry in enumerate(contracts[-8:]):
        if not isinstance(entry, Mapping):
            continue
        fingerprint = str(entry.get("contract_fingerprint") or "")
        if not fingerprint:
            continue
        archive.remember_body(
            BodySpecificMemory(
                body_id=f"legacy-body.{fingerprint[:20]}.{index}",
                contract_fingerprint=fingerprint,
                last_embodiment_id=(f"legacy-embodiment.{int(entry.get('last_seen_epoch') or 0)}"),
                body_schema_prior=(
                    deepcopy(dict(entry["body_schema"]))
                    if isinstance(entry.get("body_schema"), Mapping)
                    else None
                ),
                historical_motor_candidates=tuple(
                    deepcopy(dict(item))
                    for item in entry.get("historical_primitives", [])
                    if isinstance(item, Mapping)
                ),
                motor_cognitive_surface=(
                    deepcopy(dict(entry["motor_cognitive_surface"]))
                    if isinstance(entry.get("motor_cognitive_surface"), Mapping)
                    else None
                ),
                private_model_ids=tuple(str(value) for value in entry.get("private_model_ids", [])),
            )
        )
    return archive


def _legacy_equivalent_contract_fingerprint(
    fresh: Mapping[str, Any],
    descriptor: EmbodimentDescriptor,
) -> str:
    """Reconstruct the pre-v3 contract identity for one equivalent interface."""
    legacy_surface = ActuatorSurface.from_count(
        descriptor.effector_count,
        fingerprint_material=(
            f"{descriptor.body_kind}:{descriptor.receptor_count}:{descriptor.effector_count}"
        ),
    )
    translated = deepcopy(dict(fresh))
    actuation = translated.get("actuation")
    if isinstance(actuation, dict):
        constitution = actuation.get("constitution")
        if isinstance(constitution, dict):
            constitution["contract_fingerprint"] = legacy_surface.contract_fingerprint
    return contract_fingerprint(
        translated,
        receptor_count=descriptor.receptor_count,
        effector_count=descriptor.effector_count,
    )


def prepare_fresh_embodiment_checkpoint(
    previous: Mapping[str, Any],
    fresh: Mapping[str, Any],
    *,
    contract: EmbodimentDescriptor,
    canonical_contract_fingerprint: str | None = None,
) -> dict[str, Any]:
    """Move one unchanged Symbiont into a fresh Body.

    Re-embodiment preserves longitudinal Symbiont knowledge and archives the
    closed episode. Body-relative boundary classification and execution
    authority are withdrawn; adaptation to the new embodiment must be acquired
    through ordinary experience.
    """
    raw_lifecycle = previous.get("embodiment_lifecycle")
    has_current_lifecycle = (
        isinstance(raw_lifecycle, Mapping)
        and raw_lifecycle.get("schema_version") == _SCHEMA_VERSION
        and isinstance(raw_lifecycle.get("current"), Mapping)
    )
    current_contract = raw_lifecycle.get("current") if has_current_lifecycle else None
    has_current_lifecycle = (
        has_current_lifecycle
        and isinstance(current_contract, Mapping)
        and (
            isinstance(current_contract.get("body_kind"), str)
            and bool(current_contract.get("body_kind"))
            and all(
                isinstance(current_contract.get(field), int)
                and not isinstance(current_contract.get(field), bool)
                and current_contract[field] >= 0
                for field in ("receptor_count", "effector_count", "started_tick")
            )
        )
    )
    if _declares_current_checkpoint_schema(previous) and not has_current_lifecycle:
        raise ValueError(
            "current-schema checkpoint lacks valid embodiment_lifecycle; "
            "refusing legacy body fallback"
        )
    # Re-embodiment stamps a new identity after transforming the payload. Verify
    # the source first, otherwise a caller could use this authorized transform
    # to bless tampered current-schema state with a fresh checkpoint identity.
    verify_checkpoint_identity(dict(previous))
    previous = migrate_temporal_domains(previous)
    result = deepcopy(dict(previous))
    # Percept deltas and physiological velocity are one-Body baselines. Keeping
    # them would compare Body B's first readings against Body A's final frame.
    reactivity = result.get("innate_reactivity")
    if isinstance(reactivity, Mapping):
        raw_detector = reactivity.get("reactivity")
        if isinstance(raw_detector, Mapping):
            detector = InnateReactivity.restore(dict(raw_detector))
            detector.reset_for_new_embodiment()
            result["innate_reactivity"] = {
                **dict(reactivity),
                "reactivity": detector.checkpoint(),
            }
    # Archive the canonical episode before removing its current authority.
    raw_episode = previous.get("embodiment_episode")
    if isinstance(raw_episode, Mapping) and int(raw_episode.get("schema_version") or 0) in {2, 3}:
        raw_archive = previous.get("embodiment_archive")
        archive = EmbodimentArchive.restore(
            raw_archive if isinstance(raw_archive, Mapping) else None
        )
        archive_episode_checkpoint(
            archive,
            raw_episode,
            body_schema_prior=(
                previous.get("body_schema")
                if isinstance(previous.get("body_schema"), Mapping)
                else None
            ),
            sensory_prior=_historical_sensory_prior(previous),
            living_body=(
                previous.get("living_body")
                if isinstance(previous.get("living_body"), Mapping)
                else None
            ),
            symbiont_tick=int(previous.get("saved_at_tick") or 0),
            end_reason=("body_death" if _body_vital_state(previous) == "dead" else "body_replaced"),
        )
        result["embodiment_archive"] = archive.checkpoint()
    # The prior full BodySchema is retained in the closed episode archive.
    # No learned entry is allowed to remain active as a fact about a different
    # Body. Start a clean active schema with the same opaque identity salt.
    raw_body_schema = result.get("body_schema")
    if isinstance(raw_body_schema, dict):
        body_schema = BodySchemaEngine.restore(
            raw_body_schema,
            current_tick=int(previous.get("saved_at_tick") or 0),
        )
        body_schema.reset_for_new_embodiment()
        result["body_schema"] = body_schema.export(
            current_tick=int(previous.get("saved_at_tick") or 0)
        )
    # Acquired sensory models bind opaque source/capability IDs. Preserve them
    # only as historical priors; fresh models prevent reused IDs from
    # reactivating old transducers or adaptive sense states.
    for sensory_field in ("sensory_system", "sensory_development"):
        fresh_sensory = fresh.get(sensory_field)
        if isinstance(fresh_sensory, Mapping):
            result[sensory_field] = deepcopy(dict(fresh_sensory))
        else:
            result.pop(sensory_field, None)
    # Rhythm and drift baselines are keyed by percept name, not stable Body
    # source identity. Reusing them could classify a new Body's first signal
    # against statistics from a different physical stream. Start those
    # body-bound estimators fresh; capability-keyed acclimation remains a
    # longitudinal prior and is preserved separately.
    for baseline_field in ("rhythms", "rhythms_replay", "drift", "drift_replay"):
        if baseline_field in fresh:
            result[baseline_field] = deepcopy(fresh[baseline_field])
        else:
            result.pop(baseline_field, None)
    # The new Body starts a new physiological episode. Carrying the previous
    # tick's stress bit would turn its first active observation into a false
    # recovery event for the closed Body.
    development = result.get("development")
    if isinstance(development, dict) and "previous_stressed" in development:
        development["previous_stressed"] = False
    # A new physical Body always starts a new canonical episode. Never carry
    # the previous body/episode identity through the compatibility transform.
    result.pop("embodiment_episode", None)
    prior_lifecycle = previous.get("embodiment_lifecycle")
    if (
        isinstance(prior_lifecycle, Mapping)
        and prior_lifecycle.get("schema_version") == _SCHEMA_VERSION
    ):
        epoch = max(1, int(prior_lifecycle.get("epoch") or 1))
        prior_current = prior_lifecycle.get("current")
        current = (
            dict(prior_current)
            if isinstance(prior_current, Mapping)
            else {**_legacy_contract(previous).as_dict(), "started_tick": 0}
        )
        history = (
            deepcopy(prior_lifecycle.get("history"))
            if isinstance(prior_lifecycle.get("history"), list)
            else []
        )
    else:
        epoch = 1
        current = {**_legacy_contract(previous).as_dict(), "started_tick": 0}
        history = []

    previous_contract = EmbodimentDescriptor(
        body_kind=str(current.get("body_kind") or "unknown"),
        receptor_count=int(current.get("receptor_count") or 0),
        effector_count=int(current.get("effector_count") or 0),
    )
    saved_tick = int(previous.get("saved_at_tick") or 0)
    started_tick = int(current.get("started_tick") or 0)
    current_fingerprint_version = int(current.get("contract_fingerprint_schema_version") or 0)
    episode_contract = raw_episode.get("contract") if isinstance(raw_episode, Mapping) else None
    episode_fingerprint = (
        str(episode_contract.get("contract_fingerprint"))
        if isinstance(episode_contract, Mapping)
        and isinstance(episode_contract.get("contract_fingerprint"), str)
        and episode_contract.get("contract_fingerprint")
        else None
    )
    if episode_fingerprint is not None:
        previous_fingerprint = episode_fingerprint
    elif (
        current_fingerprint_version == CONTRACT_FINGERPRINT_SCHEMA_VERSION
        and isinstance(current.get("contract_fingerprint"), str)
        and current.get("contract_fingerprint")
    ):
        previous_fingerprint = str(current["contract_fingerprint"])
    else:
        previous_fingerprint = contract_fingerprint(
            previous,
            receptor_count=previous_contract.receptor_count,
            effector_count=previous_contract.effector_count,
        )

    if canonical_contract_fingerprint is not None:
        if not canonical_contract_fingerprint:
            raise ValueError("canonical contract fingerprint must not be empty")
        new_fingerprint = str(canonical_contract_fingerprint)
        new_fingerprint_schema = _CANONICAL_CONTRACT_FINGERPRINT_SCHEMA_VERSION
    else:
        new_fingerprint = contract_fingerprint(
            fresh,
            receptor_count=contract.receptor_count,
            effector_count=contract.effector_count,
        )
        new_fingerprint_schema = CONTRACT_FINGERPRINT_SCHEMA_VERSION
    legacy_new_fingerprint = _legacy_equivalent_contract_fingerprint(
        fresh,
        contract,
    )
    historical_bridge, historical_motor_surface = _detach_body_specific_cognition(previous)
    active_model_id = _active_private_model_id(previous)
    metrics = current.get("metrics") if isinstance(current.get("metrics"), Mapping) else {}
    summary = build_epoch_summary(
        previous,
        epoch=epoch,
        started_tick=started_tick,
        contract_fingerprint_value=previous_fingerprint,
        body_kind=previous_contract.body_kind,
        metrics=metrics,
        reembodied_alive=_body_vital_state(previous) != "dead",
    )
    append_epoch_summary(result, summary)

    # EmbodimentArchive is the sole v2 longitudinal memory authority.
    raw_archive = result.get("embodiment_archive")
    archive = EmbodimentArchive.restore(raw_archive if isinstance(raw_archive, Mapping) else None)
    current_candidates = tuple(
        historical_motor_candidates(
            previous,
            contract_fingerprint_value=previous_fingerprint,
        )
    )
    if isinstance(raw_episode, Mapping) and int(raw_episode.get("schema_version") or 0) in {2, 3}:
        body_id = str(raw_episode.get("body_id") or "")
        existing = archive.for_body(body_id) if body_id else None
        if existing is not None:
            archive.remember_body(
                BodySpecificMemory(
                    body_id=existing.body_id,
                    contract_fingerprint=existing.contract_fingerprint,
                    last_embodiment_id=existing.last_embodiment_id,
                    body_schema_prior=existing.body_schema_prior,
                    sensory_prior=_historical_sensory_prior(previous) or existing.sensory_prior,
                    dynamics_prior=existing.dynamics_prior,
                    execution_binding_priors=existing.execution_binding_priors,
                    historical_causal_state=existing.historical_causal_state,
                    historical_motor_candidates=current_candidates,
                    motor_cognitive_surface=(
                        deepcopy(dict(historical_motor_surface))
                        if isinstance(historical_motor_surface, Mapping)
                        else None
                    ),
                    private_model_ids=(
                        (active_model_id,) if isinstance(active_model_id, str) else ()
                    ),
                )
            )
    else:
        # One-way migration for pre-v2 checkpoints. Their historical store had
        # no physical Body identity, so migrated entries are contract-level
        # priors only and can never be mistaken for same-Body memory.
        migrated_previous_contract = (
            new_fingerprint
            if (
                canonical_contract_fingerprint is not None
                and previous_fingerprint == legacy_new_fingerprint
            )
            else previous_fingerprint
        )
        archive.remember_body(
            BodySpecificMemory(
                body_id=f"legacy-body.{previous_fingerprint[:24]}",
                contract_fingerprint=migrated_previous_contract,
                last_embodiment_id=f"legacy-embodiment.{epoch}",
                body_schema_prior=(
                    deepcopy(dict(previous["body_schema"]))
                    if isinstance(previous.get("body_schema"), Mapping)
                    else None
                ),
                sensory_prior=_historical_sensory_prior(previous),
                historical_motor_candidates=current_candidates,
                motor_cognitive_surface=(
                    deepcopy(dict(historical_motor_surface))
                    if isinstance(historical_motor_surface, Mapping)
                    else None
                ),
                private_model_ids=((active_model_id,) if isinstance(active_model_id, str) else ()),
            )
        )
        legacy_known = memory_for_contract(
            previous.get("embodiment_memory")
            if isinstance(previous.get("embodiment_memory"), Mapping)
            else None,
            legacy_new_fingerprint,
        )
        if isinstance(legacy_known, Mapping):
            archive.remember_body(
                BodySpecificMemory(
                    body_id=f"legacy-body.{new_fingerprint[:24]}.historical",
                    contract_fingerprint=new_fingerprint,
                    last_embodiment_id="legacy-embodiment.historical",
                    body_schema_prior=(
                        deepcopy(dict(legacy_known["body_schema"]))
                        if isinstance(legacy_known.get("body_schema"), Mapping)
                        else None
                    ),
                    sensory_prior=None,
                    historical_motor_candidates=tuple(
                        deepcopy(dict(item))
                        for item in legacy_known.get("historical_primitives", [])
                        if isinstance(item, Mapping)
                    ),
                    motor_cognitive_surface=(
                        deepcopy(dict(legacy_known["motor_cognitive_surface"]))
                        if isinstance(legacy_known.get("motor_cognitive_surface"), Mapping)
                        else None
                    ),
                    private_model_ids=tuple(
                        str(value) for value in legacy_known.get("private_model_ids", [])
                    ),
                )
            )

    result["embodiment_archive"] = archive.checkpoint()
    # Remove the superseded writable store after its one-way migration.
    result.pop("embodiment_memory", None)
    matching_memories = archive.for_contract(new_fingerprint)
    known_prior = matching_memories[0] if matching_memories else None
    known_memory = (
        {
            "historical_primitives": [
                deepcopy(item) for item in known_prior.historical_motor_candidates
            ],
            "private_model_ids": list(known_prior.private_model_ids),
        }
        if known_prior is not None
        else None
    )

    history.append(
        {
            "epoch": epoch,
            "body_kind": previous_contract.body_kind,
            "receptor_count": previous_contract.receptor_count,
            "effector_count": previous_contract.effector_count,
            "contract_fingerprint": previous_fingerprint,
            "started_tick": started_tick,
            "ended_tick": saved_tick,
            "end_body_vital_state": _body_vital_state(previous),
            "body_schema": deepcopy(previous.get("body_schema")),
            "motor_cognitive_surface": historical_motor_surface,
            "active_private_model_id": active_model_id,
            "epoch_summary": deepcopy(summary),
        }
    )
    history = history[-_MAX_EMBODIMENT_HISTORY:]

    # A fresh Body owns fresh physiology regardless of Symbiont history.
    for key in ("living_body", "metabolism", "homeostasis", "physiology"):
        if key in fresh:
            result[key] = deepcopy(fresh[key])
    result["pending_embodied_work"] = 0.0
    result["resting_requested"] = False
    result["last_runtime_vital_state"] = "active"

    # Every fresh Body starts with fresh actuator health and learning surfaces.
    fresh_actuation = deepcopy(fresh.get("actuation"))
    if not isinstance(fresh_actuation, dict):
        fresh_actuation = {"enabled": False}
    fresh_actuation = inject_memory_candidates(fresh_actuation, known_memory)
    result["actuation"] = _carry_sensorimotor_v2_knowledge(
        previous,
        fresh_actuation,
    )
    # An in-flight executive intention is bound to the closed embodiment even
    # when its sensorimotor commitment has already been removed. Preserve the
    # terminal counts and outcome ledger, but withdraw active intent and its
    # body-specific reconciliation trace before stamping the new checkpoint.
    raw_intention = result.get("executive_intention")
    if isinstance(raw_intention, dict):
        raw_intention["active"] = None
        raw_intention["active_commitment_id"] = None
        raw_intention["progress_evidence"] = 0
        raw_intention["consecutive_mismatches"] = 0
        raw_intention["reconciliation_trace"] = None

    # The Symbiont itself is invariant across re-embodiment. Cognitive state,
    # private models and self-model are preserved. Sensory learning is archived
    # as a historical prior because its source bindings belong to the old Body.
    # The active BodySchema is fresh for the new Body; its prior complete schema
    # remains in the closed episode archive as historical evidence.
    if historical_bridge is not None:
        result["cognitive_bridge"] = historical_bridge

    # Genome v2 is body-independent. Re-embodiment changes physiology,
    # sensory/actuator surfaces and acquired embodiment state only; genotype
    # and genome hashes remain byte-for-byte unchanged.

    # prepare_fresh_embodiment_checkpoint always creates a new physical Body.
    # A matching interface is therefore a known-contract prior, never same-Body.
    relation = "known-contract" if known_prior is not None else "changed"
    result["embodiment_lifecycle"] = {
        "schema_version": _SCHEMA_VERSION,
        "state": "active",
        "epoch": epoch + 1,
        "current": {
            **contract.as_dict(),
            "contract_fingerprint": new_fingerprint,
            "contract_fingerprint_schema_version": new_fingerprint_schema,
            "started_tick": saved_tick,
            "body_vital_state": "active",
            "contract_relation": relation,
            "known_contract_memory": known_memory is not None,
            "candidate_private_model_ids": (
                list(known_prior.private_model_ids) if known_prior is not None else []
            ),
            "metrics": {
                "absorbed_material_total": 0.0,
                "mechanical_work_total": 0.0,
                "physiological_cost_total": 0.0,
                "reacclimation_ticks_consumed": 0,
                "reacclimation_completed": False,
                "vital_state_ticks": {},
            },
        },
        "history": history,
    }
    # Fresh Body physiology and withdrawn execution authority make this a new
    # organism state; its identity chains from the checkpoint it replaced.
    return stamp_checkpoint_identity(result, transform="re-embodiment")


def update_lifecycle_for_checkpoint(
    payload: dict[str, Any],
    *,
    contract: EmbodimentDescriptor,
    state: str,
    metrics: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Attach execution lifecycle metadata without changing organism cognition."""
    if state not in {"active", "dormant", "suspended"}:
        raise ValueError("invalid Symbiont lifecycle state")

    raw = payload.get("embodiment_lifecycle")
    if isinstance(raw, Mapping) and raw.get("schema_version") == _SCHEMA_VERSION:
        epoch = max(1, int(raw.get("epoch") or 1))
        history = deepcopy(raw.get("history")) if isinstance(raw.get("history"), list) else []
        current_raw = raw.get("current")
        current: dict[str, Any] = dict(current_raw) if isinstance(current_raw, Mapping) else {}
    else:
        epoch = 1
        history = []
        current = {"started_tick": 0}

    current.update(contract.as_dict())
    current["body_vital_state"] = _body_vital_state(payload)
    current.setdefault("started_tick", 0)
    episode = payload.get("embodiment_episode")
    episode_contract = (
        episode.get("contract")
        if isinstance(episode, Mapping) and int(episode.get("schema_version") or 0) in {2, 3}
        else None
    )
    canonical_fingerprint = (
        str(episode_contract.get("contract_fingerprint"))
        if isinstance(episode_contract, Mapping)
        and isinstance(episode_contract.get("contract_fingerprint"), str)
        and episode_contract.get("contract_fingerprint")
        else None
    )
    if canonical_fingerprint is not None:
        current["contract_fingerprint"] = canonical_fingerprint
        current["contract_fingerprint_schema_version"] = (
            _CANONICAL_CONTRACT_FINGERPRINT_SCHEMA_VERSION
        )
    else:
        if (
            int(current.get("contract_fingerprint_schema_version") or 0)
            != CONTRACT_FINGERPRINT_SCHEMA_VERSION
            or not isinstance(current.get("contract_fingerprint"), str)
            or not current.get("contract_fingerprint")
        ):
            current["contract_fingerprint"] = contract_fingerprint(
                payload,
                receptor_count=contract.receptor_count,
                effector_count=contract.effector_count,
            )
        current["contract_fingerprint_schema_version"] = CONTRACT_FINGERPRINT_SCHEMA_VERSION
    if metrics is not None:
        current["metrics"] = deepcopy(dict(metrics))

    payload["embodiment_lifecycle"] = {
        "schema_version": _SCHEMA_VERSION,
        "state": state,
        "epoch": epoch,
        "current": current,
        "history": history[-_MAX_EMBODIMENT_HISTORY:],
    }

    if current["body_vital_state"] == "dead":
        summary = build_epoch_summary(
            payload,
            epoch=epoch,
            started_tick=int(current.get("started_tick") or 0),
            contract_fingerprint_value=str(current["contract_fingerprint"]),
            body_kind=str(contract.body_kind),
            metrics=current.get("metrics") if isinstance(current.get("metrics"), Mapping) else {},
            reembodied_alive=False,
        )
        append_epoch_summary(payload, summary)
        current["closed"] = True
        current["epoch_summary"] = deepcopy(summary)
        if not (
            isinstance(payload.get("embodiment_episode"), Mapping)
            and int(payload["embodiment_episode"].get("schema_version") or 0) in {2, 3}
        ):
            # Pre-v2 compatibility only. Canonical Physics3D checkpoints have
            # already archived the closed episode in EmbodimentArchive.
            _bridge, motor_surface = _detach_body_specific_cognition(payload)
            payload["embodiment_memory"] = archive_contract_memory(
                payload,
                contract_fingerprint_value=str(current["contract_fingerprint"]),
                epoch=epoch,
                motor_cognitive_surface=motor_surface,
                active_private_model_id=_active_private_model_id(payload),
            )
        else:
            payload.pop("embodiment_memory", None)

    return payload


__all__ = [
    "EmbodimentDescriptor",
    "lifecycle_summary",
    "migrate_legacy_memory_store",
    "migrate_temporal_domains",
    "prepare_fresh_embodiment_checkpoint",
    "update_lifecycle_for_checkpoint",
]

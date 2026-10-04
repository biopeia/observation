from __future__ import annotations

import json
import stat
from hashlib import sha256
from pathlib import Path
from typing import Any

from ..foundation.limits import OrganismLimits
from .acclimation import CapabilityBaseline, HostAcclimation
from .consolidated_baseline import (
    ConsolidatedBaselineSeed,
    consolidate_baseline,
    seed_capability_baseline,
)
from .continuity import APPARATUS_FIELDS, required_checkpoint_fields
from .drift import DriftAwareBaseline
from .durable import durable_atomic_write
from .rhythms import CyclePhase, RhythmModel

CHECKPOINT_SCHEMA_VERSION = 14
# v10 -> v11 (Longitudinal Integrity v1 §4-§5) introduced organism-state
# identity. v12 adds an independent hash of continuation conditions because
# runtime controls affect future learning but are apparatus configuration, not
# organism state. v13 persists birth-expression baselines for metaplastic
# regulation. No migration is retained: prior schemas lack current contracts.
IDENTITY_SCOPE = "organism-state-v1"
# Save-event metadata and embodiment history written around the organism
# checkpoint by the embodiment apparatus are not organism state identity.
_IDENTITY_EXCLUDED_FIELDS = frozenset(
    {"checkpoint_lineage", "runtime_provenance"}
    | {field.checkpoint_field for field in APPARATUS_FIELDS}
)
MAX_HOST_CHECKPOINT_BYTES = OrganismLimits().max_host_checkpoint_bytes


class CheckpointError(ValueError):
    """Raised for a malformed checkpoint payload or an unsupported schema version."""


def _capability_fingerprint(capability_id: str) -> str:
    return sha256(f"symbiont-seen:{capability_id}".encode("utf-8")).hexdigest()


def _seed_payload(seed: ConsolidatedBaselineSeed) -> dict[str, int]:
    return {
        "center_class": seed.center_class,
        "scale_class": seed.scale_class,
        "maturity_class": seed.maturity_class,
    }


def _seed_from_payload(entry: dict[str, Any]) -> ConsolidatedBaselineSeed:
    return ConsolidatedBaselineSeed(
        center_class=int(entry["center_class"]),
        scale_class=int(entry["scale_class"]),
        maturity_class=int(entry["maturity_class"]),
    )


def _baseline_from_stats_entry(entry: dict[str, Any]) -> CapabilityBaseline:
    """Only the consolidated {center_class, scale_class, maturity_class} shape reaches here."""
    return seed_capability_baseline(_seed_from_payload(entry))


def export_checkpoint(
    *,
    acclimation: HostAcclimation | None = None,
    rhythm_model: RhythmModel | None = None,
    drift_baselines: dict[str, DriftAwareBaseline] | None = None,
    saved_at_tick: int | None = None,
    include_replay: bool = False,
) -> dict[str, Any]:
    """Serialize public descriptive projections and, on request, replay state.

    Public projections remain coarse and omit raw telemetry. Replay blocks
    (``include_replay``) are a separate causal contract for deterministic
    hosts only: they retain bounded accumulators and raw-derived buffers
    required to continue exactly after restore, so the real host never
    requests them and restarts from the coarse projection instead.

    ``saved_at_tick`` is an organism-relative tick counter, not a timestamp or
    calendar date. Exact replay state is intentionally explicit so callers can
    distinguish deterministic continuation from the privacy-reducing public
    snapshot.
    """
    payload: dict[str, Any] = {"schema_version": CHECKPOINT_SCHEMA_VERSION}

    if saved_at_tick is not None:
        payload["saved_at_tick"] = saved_at_tick

    if acclimation is not None:
        payload["acclimation"] = {
            capability_id: _seed_payload(consolidate_baseline(baseline))
            for capability_id in acclimation.acclimated_capabilities
            if (baseline := acclimation.baseline(capability_id)) is not None
        }
        if include_replay:
            payload["acclimation_replay"] = acclimation.replay_state()

    if rhythm_model is not None:
        payload["rhythms"] = [
            {
                "percept_name": percept_name,
                "phase": phase.value,
                **_seed_payload(consolidate_baseline(baseline)),
            }
            for percept_name, phase in rhythm_model.learned_contexts
            if (baseline := rhythm_model.baseline(percept_name, phase)) is not None
        ]
        if include_replay:
            payload["rhythms_replay"] = rhythm_model.replay_state()

    if drift_baselines is not None:
        payload["drift"] = {
            name: _seed_payload(consolidate_baseline(baseline))
            for name, baseline in drift_baselines.items()
            if baseline.is_established
        }
        # The public projection above is intentionally coarse.  Preserve the
        # bounded state that can affect the very next observation separately;
        # otherwise restoring during a pending drift streak changes novelty,
        # regulation, and therefore the future trajectory.
        if include_replay:
            payload["drift_replay"] = {
                name: baseline.replay_state() for name, baseline in drift_baselines.items()
            }

    return payload


def checkpoint_state_hash(payload: dict[str, Any]) -> str:
    """Content hash of organism state, key order independent.

    Excludes ``checkpoint_lineage`` (save events), ``runtime_provenance`` (what
    produced the save) and apparatus-owned embodiment history. Two checkpoints
    of the same organism state hash identically whenever they were taken.
    """
    state = {key: value for key, value in payload.items() if key not in _IDENTITY_EXCLUDED_FIELDS}
    encoded = json.dumps(state, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return sha256(encoded.encode("utf-8")).hexdigest()


def continuation_condition_hash(controls: dict[str, Any]) -> str:
    """Hash apparatus controls that govern how a saved organism continues."""
    encoded = json.dumps(controls, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return sha256(encoded.encode("utf-8")).hexdigest()


def lineage_history(payload: dict[str, Any]) -> dict[str, Any]:
    """Return authorized state transforms that later saves must carry."""
    lineage = payload.get("checkpoint_lineage")
    lineage = lineage if isinstance(lineage, dict) else {}
    history: dict[str, Any] = {}
    transforms = lineage.get("transforms")
    if isinstance(transforms, list) and transforms:
        history["transforms"] = [str(item) for item in transforms]
    return history


def stamp_checkpoint_identity(payload: dict[str, Any], *, transform: str) -> dict[str, Any]:
    """Re-identify a checkpoint that an authorized transform has changed.

    A transform such as re-embodiment produces a different organism state, so
    the stored identifier no longer describes it. The new identifier chains
    from the one it replaced and names the transform, so the change is recorded
    instead of being indistinguishable from corruption. Returns a new payload.
    """
    if not transform:
        raise ValueError("transform must name the authorized change")
    stamped = dict(payload)
    previous = stamped.get("checkpoint_lineage")
    previous = previous if isinstance(previous, dict) else {}
    history = lineage_history(stamped)
    lineage: dict[str, Any] = {
        "checkpoint_id": checkpoint_state_hash(stamped),
        "parent_checkpoint_hash": previous.get("checkpoint_id"),
        "identity_scope": IDENTITY_SCOPE,
        **history,
        "transforms": [*history.get("transforms", []), transform],
    }
    provenance = stamped.get("runtime_provenance")
    controls = provenance.get("session_controls") if isinstance(provenance, dict) else None
    previous_condition_hash = previous.get("continuation_condition_hash")
    if isinstance(controls, dict):
        lineage["continuation_condition_hash"] = continuation_condition_hash(controls)
    elif isinstance(previous_condition_hash, str):
        # A transform may intentionally remove a required field. Preserve the
        # prior condition identity so restore rejects the incomplete result.
        lineage["continuation_condition_hash"] = previous_condition_hash
    else:
        raise CheckpointError("current checkpoint is missing required session_controls")
    lineage["schema_version"] = CHECKPOINT_SCHEMA_VERSION
    stamped["checkpoint_lineage"] = lineage
    return stamped


def verify_checkpoint_identity(payload: dict[str, Any]) -> None:
    """Fail closed unless a checkpoint matches the identity it recorded.

    The current checkpoint contract always records a verifiable lineage and
    continuation-condition hash. Missing or obsolete identity metadata fails closed.
    """
    lineage = payload.get("checkpoint_lineage")
    if not isinstance(lineage, dict):
        raise CheckpointError("current checkpoint is missing required checkpoint_lineage")
    if lineage.get("identity_scope") != IDENTITY_SCOPE:
        raise CheckpointError("checkpoint_lineage has an unsupported identity_scope")
    try:
        recomputed = checkpoint_state_hash(payload)
    except (TypeError, ValueError) as exc:
        raise CheckpointError(f"checkpoint state is not canonical JSON: {exc}") from exc
    if lineage.get("checkpoint_id") != recomputed:
        raise CheckpointError(
            "checkpoint state does not match its recorded checkpoint_id; "
            "the checkpoint was modified after it was saved"
        )
    normalize_checkpoint(payload)
    provenance = payload.get("runtime_provenance")
    if not isinstance(provenance, dict):
        raise CheckpointError("current checkpoint is missing required field 'runtime_provenance'")
    controls = provenance.get("session_controls")
    if not isinstance(controls, dict):
        raise CheckpointError("current checkpoint is missing required field 'session_controls'")
    try:
        expected = continuation_condition_hash(controls)
    except (TypeError, ValueError) as exc:
        raise CheckpointError(
            f"checkpoint continuation conditions are not canonical JSON: {exc}"
        ) from exc
    if lineage.get("continuation_condition_hash") != expected:
        raise CheckpointError("checkpoint continuation conditions do not match their recorded hash")


def require_current_schema_fields(payload: dict[str, Any], *, layer: str) -> None:
    """Reject a current-schema checkpoint that lost acquired state.

    Absence is loss and must not become a healthy empty subsystem.
    """
    for field in sorted(required_checkpoint_fields(layer)):
        if field not in payload:
            raise CheckpointError(f"current-schema checkpoint is missing required field {field!r}")


def normalize_checkpoint(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate that a checkpoint is at the current schema and return a copy.

    Every restore consumer reads the object returned here, so they all see the
    same payload. Older schemas are rejected: no migration path is kept. The
    input object is never mutated.
    """
    if not isinstance(payload, dict):
        raise CheckpointError("checkpoint payload must be a JSON object")

    schema_version = payload.get("schema_version")
    if isinstance(schema_version, bool) or not isinstance(schema_version, int):
        if schema_version is None:
            raise CheckpointError("current checkpoint is missing required field 'schema_version'")
        raise CheckpointError("checkpoint schema_version must be an integer")
    if schema_version > CHECKPOINT_SCHEMA_VERSION:
        raise CheckpointError(
            f"checkpoint schema_version {schema_version!r} is newer than this code supports "
            f"({CHECKPOINT_SCHEMA_VERSION})"
        )

    if schema_version != CHECKPOINT_SCHEMA_VERSION:
        raise CheckpointError(
            f"unsupported checkpoint schema_version {schema_version!r}; this code loads only "
            f"schema {CHECKPOINT_SCHEMA_VERSION} and carries no migrations from older schemas"
        )
    return dict(payload)


def import_checkpoint(
    payload: dict[str, Any],
    *,
    acclimation: HostAcclimation | None = None,
    rhythm_model: RhythmModel | None = None,
) -> tuple[HostAcclimation, RhythmModel, dict[str, DriftAwareBaseline]]:
    """Reconstruct model instances from a checkpoint payload.

    Only the exact current checkpoint schema is accepted. Historical payloads
    remain archival evidence but require a separately governed conversion
    process before they can become live runtime state.

    Pass an existing ``acclimation``/``rhythm_model`` (matching the
    ``min_samples``/bound config the checkpoint was exported with) to
    restore into it rather than a freshly-defaulted one — a baseline
    exported once it passed a lower ``min_samples`` may otherwise not read
    back as "already learned" against a differently-configured instance.
    """
    payload = normalize_checkpoint(payload)

    try:
        acclimation = acclimation if acclimation is not None else HostAcclimation()
        for capability_id, stats in payload.get("acclimation", {}).items():
            acclimation.restore(capability_id, _baseline_from_stats_entry(stats))
        raw_acclimation_replay = payload.get("acclimation_replay")
        if raw_acclimation_replay is not None:
            if not isinstance(raw_acclimation_replay, dict):
                raise CheckpointError("acclimation_replay must be an object")
            acclimation.restore_replay_state(raw_acclimation_replay)

        rhythm_model = rhythm_model if rhythm_model is not None else RhythmModel()
        for entry in payload.get("rhythms", []):
            rhythm_model.restore(
                entry["percept_name"],
                CyclePhase(entry["phase"]),
                _baseline_from_stats_entry(entry),
            )
        raw_rhythms_replay = payload.get("rhythms_replay")
        if raw_rhythms_replay is not None:
            if not isinstance(raw_rhythms_replay, dict):
                raise CheckpointError("rhythms_replay must be an object")
            rhythm_model.restore_replay_state(raw_rhythms_replay)

        drift_baselines: dict[str, DriftAwareBaseline] = {}
        for name, stats in payload.get("drift", {}).items():
            seeded = _baseline_from_stats_entry(stats)
            baseline = DriftAwareBaseline()
            baseline.restore(count=seeded.count, mean=seeded.mean, variance=seeded.variance)
            drift_baselines[name] = baseline
        raw_replay = payload.get("drift_replay", {})
        if raw_replay is not None:
            if not isinstance(raw_replay, dict):
                raise CheckpointError("drift_replay must be an object")
            for name, replay_state in raw_replay.items():
                if not isinstance(name, str) or not isinstance(replay_state, dict):
                    raise CheckpointError("malformed drift replay state")
                baseline = drift_baselines.get(name)
                if baseline is None:
                    baseline = DriftAwareBaseline()
                    drift_baselines[name] = baseline
                baseline.restore_replay_state(replay_state)
    except (KeyError, TypeError, ValueError) as exc:
        raise CheckpointError(f"malformed checkpoint payload: {exc}") from exc

    return acclimation, rhythm_model, drift_baselines


def save_checkpoint_atomic(payload: dict[str, Any], path: str | Path) -> None:
    """Write a checkpoint to disk atomically and durably (roadmap v0.46).

    Writes to a temporary file in the same directory, flushes and fsyncs
    it, renames it into place with ``os.replace``, and fsyncs the parent
    directory so directory entries reach persistent storage on POSIX.
    """
    target = Path(path)
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode(
        "utf-8"
    )
    if len(encoded) > MAX_HOST_CHECKPOINT_BYTES:
        raise CheckpointError("checkpoint exceeds host size limit")
    durable_atomic_write(target, encoded, sync_dir=True)


def load_checkpoint_file(path: str | Path) -> dict[str, Any] | None:
    """Read a checkpoint previously written by :func:`save_checkpoint_atomic`
    (roadmap v0.46 — crash/restart recovery).

    Returns ``None`` if the file does not exist, so a caller can treat "no
    prior state" and "state that failed to parse" differently: the former
    is a normal first run, the latter (a malformed or truncated file, which
    the atomic write above should make unreachable in practice) raises
    :class:`CheckpointError` rather than silently starting fresh over
    corrupted data.
    """
    target = Path(path)
    try:
        file_stat = target.stat()
    except FileNotFoundError as exc:
        if target.is_symlink():
            raise CheckpointError(f"checkpoint path {target} is a dangling symlink") from exc
        return None
    except OSError as exc:
        raise CheckpointError(f"checkpoint path {target} cannot be inspected: {exc}") from exc
    if not stat.S_ISREG(file_stat.st_mode):
        raise CheckpointError(f"checkpoint path {target} is not a regular file")
    try:
        with target.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except OSError as exc:
        raise CheckpointError(f"checkpoint file {target} cannot be read: {exc}") from exc
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise CheckpointError(f"checkpoint file {target} is not valid UTF-8 JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise CheckpointError(f"checkpoint file {target} does not contain a JSON object")
    return payload

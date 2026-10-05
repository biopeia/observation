"""Passive instance registry and immutable run identity for resident Symbionts.

Heartbeat files describe current liveness.  Run records and archived topology
revisions are append-only observer evidence used to reconstruct historical
coverage without guessing identity from today's registry state.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from symbiont.host.durable import durable_atomic_write_json

_NAMESPACE = "symbiont-observatory-instance"
_RUN_RECORD_VERSION = 1


def derive_instance_id(resolved_state_file_path: str) -> str:
    digest = hashlib.sha256((_NAMESPACE + resolved_state_file_path).encode("utf-8")).hexdigest()
    return digest[:16]


def new_run_id() -> str:
    return str(uuid.uuid4())


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    durable_atomic_write_json(path, payload, sort_keys=False, ensure_ascii=False, sync_dir=True)


def _read_json_object(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _persist_run_identity(
    observatory_dir: Path,
    *,
    instance_id: str,
    run_id: str,
    display_id: str,
    started_at: str,
    organism_id: str | None,
) -> None:
    """Persist one immutable run→instance/organism binding.

    Older Observatory data did not record this binding durably, so historical
    readers must treat those runs as uncovered rather than infer ownership.
    """
    root = Path(observatory_dir)
    path = root / "runs" / f"{run_id}.json"
    expected = {
        "schema_version": _RUN_RECORD_VERSION,
        "run_id": run_id,
        "instance_id": instance_id,
        "organism_id": organism_id,
        "display_id": display_id,
        "started_at": started_at,
    }
    current = _read_json_object(path)
    if current is not None:
        comparable = {key: current.get(key) for key in expected}
        if comparable != expected:
            raise RuntimeError(f"immutable Observatory run identity conflict for {run_id}")
        return
    _atomic_write_json(path, expected)


def _archive_topology_revision(
    observatory_dir: Path,
    *,
    instance_id: str,
    topology_revision: int,
) -> None:
    """Archive the exact published topology revision if it is available.

    Journals carry ``topology_revision`` but the historical implementation kept
    only ``instances/<id>.topology.json``.  Archiving revisions makes future
    Development reconstruction lossless while leaving missing legacy revisions
    explicitly uncovered.
    """
    root = Path(observatory_dir)
    source = root / "instances" / f"{instance_id}.topology.json"
    payload = _read_json_object(source)
    if payload is None:
        return
    revision = payload.get("topology_revision")
    if isinstance(revision, bool) or not isinstance(revision, int):
        return
    if revision != topology_revision:
        return
    target = root / "topology" / f"{instance_id}-{topology_revision:010d}.json"
    if target.exists():
        return
    _atomic_write_json(target, payload)


def write_heartbeat(
    observatory_dir: Path,
    *,
    instance_id: str,
    run_id: str,
    pid: int,
    display_id: str,
    started_at: str,
    topology_revision: int,
    organism_id: str | None = None,
    key_fingerprint: str | None = None,
) -> None:
    record: dict[str, Any] = {
        "instance_id": instance_id,
        "run_id": run_id,
        "pid": pid,
        "display_id": display_id,
        "started_at": started_at,
        "last_heartbeat": datetime.now(timezone.utc).isoformat(),
        "topology_revision": topology_revision,
    }
    if organism_id is not None:
        record["organism_id"] = organism_id
    if key_fingerprint is not None:
        record["key_fingerprint"] = key_fingerprint

    root = Path(observatory_dir)
    _persist_run_identity(
        root,
        instance_id=instance_id,
        run_id=run_id,
        display_id=display_id,
        started_at=started_at,
        organism_id=organism_id,
    )
    _archive_topology_revision(
        root,
        instance_id=instance_id,
        topology_revision=topology_revision,
    )
    _atomic_write_json(root / "instances" / f"{instance_id}.json", record)


def _aware_datetime(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed


def _valid_registry_record(record: object) -> bool:
    if not isinstance(record, dict):
        return False
    instance_id = record.get("instance_id")
    run_id = record.get("run_id")
    pid = record.get("pid")
    display_id = record.get("display_id")
    revision = record.get("topology_revision")
    if (
        not isinstance(instance_id, str)
        or len(instance_id) != 16
        or any(char not in "0123456789abcdef" for char in instance_id)
    ):
        return False
    if not isinstance(run_id, str) or not run_id:
        return False
    if isinstance(pid, bool) or not isinstance(pid, int) or pid < 0:
        return False
    if not isinstance(display_id, str) or not display_id:
        return False
    if isinstance(revision, bool) or not isinstance(revision, int) or revision < 0:
        return False
    if _aware_datetime(record.get("started_at")) is None:
        return False
    if _aware_datetime(record.get("last_heartbeat")) is None:
        return False
    return True


def read_registry(observatory_dir: Path) -> list[dict[str, Any]]:
    instances_dir = Path(observatory_dir) / "instances"
    if not instances_dir.is_dir():
        return []
    records = []
    for path in sorted(instances_dir.glob("*.json")):
        if path.name.endswith(".topology.json"):
            continue
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if _valid_registry_record(record):
            records.append(record)
    return records


def classify_liveness(
    record: dict[str, Any],
    *,
    now: datetime,
    heartbeat_interval_seconds: float,
    ttl_seconds: float = 600.0,
) -> str:
    """Heartbeat timestamp is authoritative; malformed/future records expire."""
    last_heartbeat = _aware_datetime(record.get("last_heartbeat"))
    if last_heartbeat is None or now.tzinfo is None or now.utcoffset() is None:
        return "expired"
    try:
        age = (now - last_heartbeat).total_seconds()
    except TypeError:
        return "expired"
    if age < -2 * heartbeat_interval_seconds:
        return "expired"
    if age <= 2 * heartbeat_interval_seconds:
        return "alive"
    if age <= ttl_seconds:
        return "stale"
    return "expired"

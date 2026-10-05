"""Canonical observer-side Development history reconstructed from Observatory evidence.

The browser is not an authority.  This module joins immutable run identity
records, append-only journals and archived topology revisions.  Any legacy run
that lacks one of those links is reported as uncovered rather than inferred.
"""

from __future__ import annotations

import gzip
import json
from pathlib import Path
from typing import Any, Iterable

_HISTORY_SCHEMA_VERSION = 1
_MAX_POINTS = 2048
_MAX_SNAPSHOTS = 160


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _run_records(root: Path, organism_id: str) -> list[dict[str, Any]]:
    runs_dir = root / "runs"
    if not runs_dir.is_dir():
        return []
    records: list[dict[str, Any]] = []
    for path in sorted(runs_dir.glob("*.json")):
        record = _read_json(path)
        if not record or record.get("schema_version") != 1:
            continue
        if record.get("organism_id") != organism_id:
            continue
        run_id = record.get("run_id")
        instance_id = record.get("instance_id")
        if not isinstance(run_id, str) or not run_id:
            continue
        if not isinstance(instance_id, str) or len(instance_id) != 16:
            continue
        records.append(record)
    records.sort(key=lambda item: str(item.get("started_at") or ""))
    return records


def _journal_paths(root: Path, run_id: str) -> list[Path]:
    journal = root / "journal"
    if not journal.is_dir():
        return []
    return sorted([*journal.glob(f"{run_id}-*.ndjson"), *journal.glob(f"{run_id}-*.ndjson.gz")])


def _journal_run_ids(root: Path) -> set[str]:
    journal = root / "journal"
    if not journal.is_dir():
        return set()
    run_ids: set[str] = set()
    for path in [*journal.glob("*.ndjson"), *journal.glob("*.ndjson.gz")]:
        name = path.name.removesuffix(".gz").removesuffix(".ndjson")
        run_id, separator, suffix = name.rpartition("-")
        if separator and suffix.isdigit() and run_id:
            run_ids.add(run_id)
    return run_ids


def _journal_entries(paths: Iterable[Path], run_id: str) -> Iterable[dict[str, Any]]:
    for path in paths:
        opener = gzip.open if path.suffix == ".gz" else open
        try:
            with opener(path, "rt", encoding="utf-8") as handle:
                for line in handle:
                    if not line.strip():
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if not isinstance(entry, dict) or entry.get("run_id") != run_id:
                        continue
                    snapshot = entry.get("snapshot")
                    if isinstance(snapshot, dict):
                        yield entry
        except OSError:
            continue


def _topology(root: Path, instance_id: str, revision: int | None) -> dict[str, Any] | None:
    if revision is None:
        return None
    path = root / "topology" / f"{instance_id}-{revision:010d}.json"
    payload = _read_json(path)
    if payload is None or payload.get("topology_revision") != revision:
        return None
    return payload


def _topology_counts(topology: dict[str, Any] | None) -> dict[str, int | None]:
    if topology is None:
        return {
            "concepts": None,
            "predictors": None,
            "readouts": None,
            "edges": None,
        }
    nodes = topology.get("nodes")
    edges = topology.get("edges")
    if not isinstance(nodes, list) or not isinstance(edges, list):
        return {
            "concepts": None,
            "predictors": None,
            "readouts": None,
            "edges": None,
        }
    return {
        "concepts": sum(1 for node in nodes if isinstance(node, dict) and node.get("kind") == "concept"),
        "predictors": sum(
            1 for node in nodes if isinstance(node, dict) and node.get("kind") == "predictor"
        ),
        "readouts": sum(1 for node in nodes if isinstance(node, dict) and node.get("kind") == "readout"),
        "edges": len(edges),
    }


def _body_schema_counts(organism: dict[str, Any]) -> tuple[int | None, int | None]:
    body_schema = organism.get("body_schema")
    if not isinstance(body_schema, dict):
        return None, None
    parts = body_schema.get("parts")
    dependencies = body_schema.get("dependencies")
    self_regions = None
    self_dependencies = None
    if isinstance(parts, list):
        self_regions = sum(
            1 for part in parts if isinstance(part, dict) and part.get("kind") == "cognitive_region"
        )
    if isinstance(dependencies, list):
        self_dependencies = len(dependencies)
    return self_regions, self_dependencies


def _point(
    *,
    run_id: str,
    snapshot: dict[str, Any],
    topology: dict[str, Any] | None,
) -> dict[str, Any] | None:
    tick = snapshot.get("tick")
    if isinstance(tick, bool) or not isinstance(tick, int) or tick <= 0:
        return None
    organism = snapshot.get("organism")
    if not isinstance(organism, dict):
        return None
    cognition = organism.get("cognition") if isinstance(organism.get("cognition"), dict) else {}
    physiology = organism.get("physiology") if isinstance(organism.get("physiology"), dict) else {}
    development = organism.get("development") if isinstance(organism.get("development"), dict) else {}
    counts = _topology_counts(topology)
    self_regions, self_dependencies = _body_schema_counts(organism)
    return {
        "tick": tick,
        "runId": run_id,
        **counts,
        "motorEdges": None,
        "schemaConfidence": None,
        "predictionError": None,
        "motorOrigin": None,
        "energy": None,
        "physiology": physiology.get("state") if isinstance(physiology.get("state"), str) else None,
        "resourceProgress": None,
        "sensorimotorPatterns": None,
        "motorCompetences": None,
        "cognitiveCompetences": None,
        "repertoire": None,
        "selfRegions": self_regions,
        "selfDependencies": self_dependencies,
        "topologyRevision": cognition.get("topology_revision")
        if isinstance(cognition.get("topology_revision"), int)
        and not isinstance(cognition.get("topology_revision"), bool)
        else None,
        "developmentPhase": development.get("phase")
        if isinstance(development.get("phase"), str)
        else None,
    }


def build_development_history(
    observatory_dir: Path | str | None,
    *,
    organism_id: str,
    limit: int = _MAX_POINTS,
) -> dict[str, Any]:
    """Build reproducible browser-independent Development evidence.

    ``complete`` is deliberately strict: every returned journal observation must
    have its referenced topology revision archived.  Legacy journals without an
    immutable run identity are listed as unindexed and are never assigned to the
    requested organism by heuristic.
    """
    bounded_limit = max(1, min(int(limit), _MAX_POINTS))
    if observatory_dir is None:
        return {
            "schema_version": _HISTORY_SCHEMA_VERSION,
            "authority": "observatory-journal",
            "organism_id": organism_id,
            "available": False,
            "complete": False,
            "coverage": [],
            "points": [],
            "snapshots": [],
            "unindexed_run_count": 0,
        }

    root = Path(observatory_dir)
    records = _run_records(root, organism_id)
    indexed_run_ids = {str(record["run_id"]) for record in records}
    all_journal_run_ids = _journal_run_ids(root)

    points: list[dict[str, Any]] = []
    snapshots: list[dict[str, Any]] = []
    coverage: list[dict[str, Any]] = []
    all_complete = True

    for record in records:
        run_id = str(record["run_id"])
        instance_id = str(record["instance_id"])
        run_points: list[dict[str, Any]] = []
        run_ticks: list[int] = []
        missing_revisions: set[int] = set()
        topology_cache: dict[int, dict[str, Any] | None] = {}
        entries = 0

        for entry in _journal_entries(_journal_paths(root, run_id), run_id):
            entries += 1
            snapshot = entry["snapshot"]
            tick = snapshot.get("tick")
            if isinstance(tick, int) and not isinstance(tick, bool):
                run_ticks.append(tick)
            organism = snapshot.get("organism")
            cognition = organism.get("cognition") if isinstance(organism, dict) else None
            revision = cognition.get("topology_revision") if isinstance(cognition, dict) else None
            if isinstance(revision, bool) or not isinstance(revision, int):
                revision = None
            topology = None
            if revision is not None:
                if revision not in topology_cache:
                    topology_cache[revision] = _topology(root, instance_id, revision)
                topology = topology_cache[revision]
                if topology is None:
                    missing_revisions.add(revision)
            point = _point(run_id=run_id, snapshot=snapshot, topology=topology)
            if point is not None:
                run_points.append(point)
            if topology is not None and len(snapshots) < _MAX_SNAPSHOTS:
                snapshots.append(
                    {
                        "tick": point["tick"] if point else snapshot.get("tick"),
                        "runId": run_id,
                        "snapshot": {
                            "tick": snapshot.get("tick"),
                            "topology": topology,
                            "cognition": cognition,
                            "observerAnalysis": None,
                            "observerSemantics": None,
                            "sensorimotor": organism.get("sensorimotor")
                            if isinstance(organism, dict)
                            else None,
                            "outcome": organism.get("outcome") if isinstance(organism, dict) else None,
                            "provenance": snapshot.get("observer"),
                        },
                    }
                )

        run_complete = entries > 0 and not missing_revisions
        if not run_complete:
            all_complete = False
        coverage.append(
            {
                "run_id": run_id,
                "instance_id": instance_id,
                "started_at": record.get("started_at"),
                "entries": entries,
                "tick_min": min(run_ticks) if run_ticks else None,
                "tick_max": max(run_ticks) if run_ticks else None,
                "missing_topology_revisions": sorted(missing_revisions),
                "complete": run_complete,
            }
        )
        points.extend(run_points)

    points.sort(key=lambda item: (next(
        (index for index, record in enumerate(records) if record["run_id"] == item["runId"]),
        len(records),
    ), item["tick"]))
    points = points[-bounded_limit:]
    snapshots = snapshots[-_MAX_SNAPSHOTS:]

    unindexed = all_journal_run_ids - indexed_run_ids
    if unindexed:
        all_complete = False

    return {
        "schema_version": _HISTORY_SCHEMA_VERSION,
        "authority": "observatory-journal",
        "organism_id": organism_id,
        "available": bool(records),
        "complete": bool(records) and all_complete,
        "coverage": coverage,
        "points": points,
        "snapshots": snapshots,
        "unindexed_run_count": len(unindexed),
    }


__all__ = ["build_development_history"]

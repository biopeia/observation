"""Canonical Development history for managed Physics3D Workbench runs.

Physics3D telemetry v4.1 is already an append-only, integrity-verified, lossless
observer record of each rich state. Development is reconstructed from that
evidence instead of browser localStorage or a second journal.
"""

from __future__ import annotations

import json
from collections import deque
from pathlib import Path
from typing import Any, Mapping

from lab.observation.projection import mind_snapshot_from_rich_state
from lab.physics3d.telemetry.reader import open_telemetry

_HISTORY_SCHEMA_VERSION = 1
_AUTHORITY = "lab-physics3d-telemetry-v4.1"
_MAX_POINTS = 2048
_MAX_SNAPSHOTS = 160
_SNAPSHOT_MAX_GAP = 64


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _telemetry_manifest_candidates(telemetry_root: Path) -> list[dict[str, Any]]:
    """Return persisted telemetry manifests without assuming writer layout.

    TelemetryV41Writer creates a generated child run directory below the root
    supplied by Physics3D. Older/manual fixtures may place the manifest directly
    at the supplied root. This helper inspects only those two supported levels;
    it does not infer scientific identity from Lab catalog metadata.
    """
    paths = [telemetry_root / "manifest.json"]
    if telemetry_root.is_dir():
        try:
            children = sorted(telemetry_root.iterdir(), key=lambda item: item.name, reverse=True)
        except OSError:
            children = []
        paths.extend(child / "manifest.json" for child in children if child.is_dir())

    manifests: list[dict[str, Any]] = []
    for path in paths:
        if not path.is_file():
            continue
        manifest = _read_json(path)
        if manifest:
            manifests.append(manifest)
    return manifests


def _number(value: Any) -> int | float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return value


def _nodes(topology: Any) -> list[Mapping[str, Any]]:
    if not isinstance(topology, Mapping):
        return []
    raw = topology.get("nodes")
    if not isinstance(raw, list):
        return []
    return [item for item in raw if isinstance(item, Mapping)]


def _edges(topology: Any) -> list[Mapping[str, Any]]:
    if not isinstance(topology, Mapping):
        return []
    raw = topology.get("edges")
    if not isinstance(raw, list):
        return []
    return [item for item in raw if isinstance(item, Mapping)]


def _body_schema_counts(snapshot: Mapping[str, Any]) -> tuple[int | None, int | None]:
    body_schema = snapshot.get("body_schema")
    if not isinstance(body_schema, Mapping):
        return None, None
    parts = body_schema.get("parts")
    dependencies = body_schema.get("dependencies")
    regions = None
    dependency_count = None
    if isinstance(parts, list):
        regions = sum(
            1
            for item in parts
            if isinstance(item, Mapping) and item.get("kind") == "cognitive_region"
        )
    if isinstance(dependencies, list):
        dependency_count = len(dependencies)
    return regions, dependency_count


def _point(
    run_id: str,
    summary: Mapping[str, Any],
    snapshot: Mapping[str, Any],
) -> dict[str, Any] | None:
    tick = summary.get("tick", snapshot.get("tick"))
    if isinstance(tick, bool) or not isinstance(tick, int) or tick <= 0:
        return None
    topology = snapshot.get("topology")
    nodes = _nodes(topology)
    edges = _edges(topology)
    self_regions, self_dependencies = _body_schema_counts(snapshot)
    physiology = (
        "dead"
        if summary.get("alive") is False
        else "active"
        if summary.get("alive") is True
        else None
    )
    return {
        "tick": tick,
        "runId": run_id,
        "concepts": sum(1 for node in nodes if node.get("kind") == "concept"),
        "predictors": sum(1 for node in nodes if node.get("kind") == "predictor"),
        "readouts": sum(1 for node in nodes if node.get("kind") == "readout"),
        "motorEdges": _number(summary.get("cognitive_motor_output_edges")),
        "edges": len(edges) if isinstance(topology, Mapping) else None,
        "schemaConfidence": _number(summary.get("schema_confidence")),
        "predictionError": _number(summary.get("prediction_error")),
        "motorOrigin": (
            summary.get("action_source") if isinstance(summary.get("action_source"), str) else None
        ),
        "energy": _number(summary.get("metabolic_reserve_ratio")),
        "physiology": physiology,
        "resourceProgress": _number(summary.get("resource_progress")),
        "sensorimotorPatterns": _number(summary.get("sensorimotor_patterns")),
        "motorCompetences": _number(summary.get("motor_competences")),
        "cognitiveCompetences": _number(summary.get("motor_competence_count")),
        "repertoire": _number(summary.get("motor_repertoire_size")),
        "selfRegions": self_regions,
        "selfDependencies": self_dependencies,
    }


def _history_snapshot(tick: int, run_id: str, snapshot: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "tick": tick,
        "runId": run_id,
        "snapshot": {
            "tick": tick,
            "topology": snapshot.get("topology"),
            "cognition": snapshot.get("cognition"),
            "observerAnalysis": snapshot.get("observer_analysis"),
            "observerSemantics": snapshot.get("observer_semantics"),
            "sensorimotor": snapshot.get("sensorimotor"),
            "outcome": snapshot.get("outcome"),
            "provenance": snapshot.get("provenance"),
        },
    }


def _snapshot_fingerprint(snapshot: Mapping[str, Any]) -> str:
    topology = snapshot.get("topology")
    nodes = sorted(
        f"{item.get('id', item.get('node_id', ''))}:{item.get('kind', '')}"
        for item in _nodes(topology)
    )
    edges = sorted(
        f"{item.get('sourceId', item.get('source_id', ''))}>{item.get('targetId', item.get('target_id', ''))}:{item.get('kind', '')}"
        for item in _edges(topology)
    )
    cognition = snapshot.get("cognition")
    revision = cognition.get("topologyRevision") if isinstance(cognition, Mapping) else None
    if revision is None and isinstance(cognition, Mapping):
        revision = cognition.get("topology_revision")
    observer = snapshot.get("observer_analysis")
    prediction = observer.get("predictionErrors") if isinstance(observer, Mapping) else None
    return json.dumps([revision, nodes, edges, prediction], sort_keys=True, separators=(",", ":"))


def _managed_runs(runs_dir: Path, organism_id: str) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    if not runs_dir.is_dir():
        return matches
    for run_dir in runs_dir.iterdir():
        if not run_dir.is_dir():
            continue
        lab_manifest = _read_json(run_dir / "manifest.json")
        telemetry_root = run_dir / "telemetry"
        reader = None
        availability = "readable"
        telemetry_manifest: dict[str, Any]

        # Normal readable telemetry is authoritative about both its resolved
        # v4.1 root and scientific organism identity. Do not assume the writer's
        # manifest is stored directly under the Lab-provided telemetry root.
        try:
            reader = open_telemetry(telemetry_root)
        except (FileNotFoundError, ValueError, OSError):
            # If verification/opening fails, retain the run only when a persisted
            # telemetry manifest at a supported location independently identifies
            # the requested organism. Catalog refs and aliases are not sufficient.
            candidate_manifests = [
                manifest
                for manifest in _telemetry_manifest_candidates(telemetry_root)
                if manifest.get("organism_id") == organism_id
            ]
            if not candidate_manifests:
                continue
            telemetry_manifest = max(
                candidate_manifests,
                key=lambda manifest: str(manifest.get("started_at_utc") or ""),
            )
            availability = "unreadable"
        else:
            telemetry_manifest = _read_json(reader.root / "manifest.json")
            if telemetry_manifest.get("organism_id") != organism_id:
                continue

        matches.append(
            {
                "run_id": str(lab_manifest.get("run_id") or run_dir.name),
                "started_at": str(
                    lab_manifest.get("started_at") or telemetry_manifest.get("started_at_utc") or ""
                ),
                "reader": reader,
                "telemetry_manifest": telemetry_manifest,
                "availability": availability,
            }
        )
    matches.sort(key=lambda item: (item["started_at"], item["run_id"]))
    return matches


def build_development_history(
    runs_dir: Path | str,
    *,
    organism_id: str,
    limit: int = _MAX_POINTS,
) -> dict[str, Any]:
    """Reconstruct browser-independent Development evidence from telemetry.

    The v4.1 reader verifies the telemetry integrity chain. No run is assigned
    by alias, browser cache, current registry state, or another observer source.
    """
    bounded_limit = max(1, min(int(limit), _MAX_POINTS))
    runs = _managed_runs(Path(runs_dir), organism_id)
    if not runs:
        return {
            "schema_version": _HISTORY_SCHEMA_VERSION,
            "authority": _AUTHORITY,
            "organism_id": organism_id,
            "available": False,
            "complete": False,
            "coverage": [],
            "points": [],
            "snapshots": [],
        }

    selected_by_run: dict[str, list[dict[str, Any]]] = {}
    coverage: list[dict[str, Any]] = []
    for run in runs:
        reader = run["reader"]
        manifest = run["telemetry_manifest"]
        if reader is None:
            coverage.append(
                {
                    "run_id": run["run_id"],
                    "started_at": run["started_at"] or None,
                    "status": manifest.get("status"),
                    "entries": None,
                    "tick_min": None,
                    "tick_max": None,
                    "integrity": manifest.get("integrity"),
                    "availability": "unreadable",
                }
            )
            continue

        summaries = list(reader.iter_summaries())
        ticks = [
            int(item["tick"])
            for item in summaries
            if isinstance(item, Mapping)
            and isinstance(item.get("tick"), int)
            and not isinstance(item.get("tick"), bool)
        ]
        coverage.append(
            {
                "run_id": run["run_id"],
                "started_at": run["started_at"] or None,
                "status": manifest.get("status"),
                "entries": len(ticks),
                "tick_min": min(ticks) if ticks else None,
                "tick_max": max(ticks) if ticks else None,
                "integrity": manifest.get("integrity"),
                "availability": "readable",
            }
        )
        selected_by_run[run["run_id"]] = summaries

    remaining = bounded_limit
    selected_ticks: dict[str, set[int]] = {}
    for run in reversed(runs):
        if remaining <= 0:
            break
        usable = [
            item
            for item in selected_by_run.get(run["run_id"], [])
            if isinstance(item, Mapping)
            and isinstance(item.get("tick"), int)
            and not isinstance(item.get("tick"), bool)
        ]
        chosen = usable[-remaining:]
        selected_ticks[run["run_id"]] = {int(item["tick"]) for item in chosen}
        remaining -= len(chosen)

    points: list[dict[str, Any]] = []
    snapshots: deque[dict[str, Any]] = deque(maxlen=_MAX_SNAPSHOTS)
    previous_snapshot_tick: dict[str, int] = {}
    previous_fingerprint: dict[str, str] = {}

    for run in runs:
        run_id = run["run_id"]
        wanted = selected_ticks.get(run_id)
        reader = run["reader"]
        if not wanted or reader is None:
            continue
        summaries = {
            int(item["tick"]): item
            for item in selected_by_run[run_id]
            if isinstance(item, Mapping)
            and isinstance(item.get("tick"), int)
            and not isinstance(item.get("tick"), bool)
            and int(item["tick"]) in wanted
        }
        for rich_state in reader.iter_states(
            start_tick=min(wanted),
            end_tick=max(wanted),
        ):
            if not isinstance(rich_state, Mapping):
                continue
            tick = rich_state.get("tick")
            if isinstance(tick, bool) or not isinstance(tick, int) or tick not in wanted:
                continue
            summary = summaries.get(tick, {"tick": tick})
            snapshot = mind_snapshot_from_rich_state(rich_state)
            point = _point(run_id, summary, snapshot)
            if point is not None:
                points.append(point)

            fingerprint = _snapshot_fingerprint(snapshot)
            last_tick = previous_snapshot_tick.get(run_id)
            last_fingerprint = previous_fingerprint.get(run_id)
            if (
                last_tick is None
                or tick - last_tick >= _SNAPSHOT_MAX_GAP
                or fingerprint != last_fingerprint
            ):
                snapshots.append(_history_snapshot(tick, run_id, snapshot))
                previous_snapshot_tick[run_id] = tick
                previous_fingerprint[run_id] = fingerprint

    complete = bool(coverage) and all(
        str(item.get("status") or "") == "closed" and item.get("availability") == "readable"
        for item in coverage
    )
    return {
        "schema_version": _HISTORY_SCHEMA_VERSION,
        "authority": _AUTHORITY,
        "organism_id": organism_id,
        "available": True,
        "complete": complete,
        "coverage": coverage,
        "points": points[-bounded_limit:],
        "snapshots": list(snapshots),
    }


__all__ = ["build_development_history"]

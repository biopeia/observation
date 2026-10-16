"""Append-only local archive for already-authorized semantic observations.

This module is deliberately separate from :mod:`observation.plane`: creating an
archive does not change publication, delivery, World commit, or Lab evidence
semantics. Callers must hand it observations only after the owning publication
boundary has authorized them. Receipt sequence is local archive order, never
domain time or causal order.
"""

from __future__ import annotations

import base64
import hashlib
import json
import math
import os
import sqlite3
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from .semantic import (
    AcquisitionBasis,
    ActorRef,
    AuthorityDomain,
    ConditionDimension,
    ConditionOrigin,
    DomainTimeRef,
    IdentityAssertion,
    IdentityLink,
    IdentityLinkState,
    IdentityRef,
    Lineage,
    LineageSourceRef,
    ObservationCondition,
    OrchestrationContext,
    SemanticClaim,
    SemanticContractRef,
    SemanticFamily,
    SemanticObservation,
    SubjectScope,
    TransformationRef,
)

_SCHEMA = "biopeia.observation.archive-record.v1"
_MODEL_TYPES = (
    AcquisitionBasis, ActorRef, DomainTimeRef, IdentityAssertion, IdentityLink,
    IdentityRef, Lineage, LineageSourceRef, ObservationCondition,
    OrchestrationContext, SemanticClaim, SemanticContractRef, SemanticFamily,
    SemanticObservation, SubjectScope, TransformationRef,
)
_SNAPSHOT_ATOMS = (type(None), bool, int, float, str, bytes)
_SNAPSHOT_CONTAINERS = (list, tuple, set, frozenset, dict)


def _validate_snapshot_value(value: object, active: set[int] | None = None) -> None:
    """Validate the same plain value-tree boundary as the in-memory plane."""
    if type(value) in _SNAPSHOT_ATOMS:
        if type(value) is float and not math.isfinite(value):
            raise TypeError("archive values require finite floats")
        return
    if type(value) not in _SNAPSHOT_CONTAINERS:
        raise TypeError("claim value must be built-in scalar/container data")
    active = set() if active is None else active
    ident = id(value)
    if ident in active:
        raise TypeError("claim value must not contain recursive containers")
    active.add(ident)
    try:
        values = (item for pair in value.items() for item in pair) if type(value) is dict else iter(value)
        for item in values:
            _validate_snapshot_value(item, active)
    finally:
        active.remove(ident)


class ArchiveError(RuntimeError):
    """Base exception for local archive failures."""


class ArchiveCapacityReached(ArchiveError):
    """The configured payload budget is exhausted; no original was discarded."""


class ArchiveCorrupt(ArchiveError):
    """A stored record failed schema, decode, or digest verification."""


@dataclass(frozen=True, slots=True)
class ArchiveRecord:
    receipt_sequence: int
    observation: SemanticObservation[object]
    content_sha256: str
    payload_bytes: int
    # Local capture-stream identity only; never a domain or causal identifier.
    capture_id: str | None = None
    source_sequence: int | None = None


@dataclass(frozen=True, slots=True)
class SourceDeliveryGap:
    capture_id: str | None
    first_sequence: int
    last_sequence: int
    reason: str


@dataclass(frozen=True, slots=True)
class CaptureSession:
    """Durable lifecycle marker for one local capture worker.

    ``running`` means no terminal record was persisted; after process loss it
    is deliberately not upgraded to a claim of complete history. Sequence
    watermarks bound local delivery only; they are not causal positions or
    proof that every source publication was archived.
    """

    capture_id: str
    initial_source_sequence: int
    final_source_sequence: int | None
    status: str
    terminal_reason: str | None


@dataclass(frozen=True, slots=True)
class CaptureCoverage:
    """Evidence-based accounting for one capture's local delivery interval.

    ``closure_verified`` means every source sequence in the bounded interval
    is accounted for by persisted publications and/or durable gap markers. It
    does not mean every publication was retained. ``complete`` is stricter:
    every sequence must be persisted, with no gaps, and the session stopped
    normally. An open session has no verified end.
    """

    capture_id: str
    status: str
    persisted_sequences: tuple[int, ...]
    received_not_persisted: tuple[tuple[int, int, str], ...]
    known_source_gaps: tuple[tuple[int, int, str], ...]
    # ``None`` as the upper bound means the durable session has no verified
    # terminal watermark, so the tail is open-ended rather than complete.
    unverifiable_intervals: tuple[tuple[int, int | None], ...]
    # The bounded interval is accounted for by durable publication rows and/or
    # durable loss markers. This does not mean every publication was retained.
    closure_verified: bool
    complete: bool


@dataclass(frozen=True, slots=True)
class ArchiveStatus:
    record_count: int
    payload_bytes: int
    max_payload_bytes: int
    capture_gap_start: int | None
    capture_gap_end: int | None
    # Preserve the original v1 tuple shape for existing callers. The additive
    # records expose capture-instance scope without changing that API.
    source_gaps: tuple[tuple[int, int, str], ...] = ()
    source_gap_records: tuple[SourceDeliveryGap, ...] = ()


def _encode_value(value: Any, active: set[int] | None = None) -> Any:
    """Encode the supported built-in tree without collapsing tuple/set types."""
    if value is None or type(value) in (bool, int, str):
        return value
    if type(value) is float:
        if not math.isfinite(value):
            raise TypeError("archive values require finite floats")
        return value
    if type(value) is bytes:
        return {"$archive_type": "bytes", "base64": base64.b64encode(value).decode("ascii")}
    if active is None:
        active = set()
    if type(value) in (list, tuple, set, frozenset, dict):
        ident = id(value)
        if ident in active:
            raise TypeError("archive value must not contain recursive containers")
        active.add(ident)
        try:
            if type(value) is list:
                return {"$archive_type": "list", "items": [_encode_value(v, active) for v in value]}
            if type(value) is tuple:
                return {"$archive_type": "tuple", "items": [_encode_value(v, active) for v in value]}
            if type(value) in (set, frozenset):
                items = [_encode_value(v, active) for v in value]
                items.sort(key=lambda item: json.dumps(item, sort_keys=True, separators=(",", ":"), ensure_ascii=False))
                kind = "set" if type(value) is set else "frozenset"
                return {"$archive_type": kind, "items": items}
            pairs = [[_encode_value(k, active), _encode_value(v, active)] for k, v in value.items()]
            pairs.sort(key=lambda pair: json.dumps(pair[0], sort_keys=True, separators=(",", ":"), ensure_ascii=False))
            return {"$archive_type": "dict", "items": pairs}
        finally:
            active.remove(ident)
    raise TypeError(f"unsupported archive value type: {type(value).__name__}")


def _decode_value(value: Any) -> Any:
    if value is None or type(value) in (bool, int, float, str):
        return value
    if type(value) is not dict or type(value.get("$archive_type")) is not str:
        raise ArchiveCorrupt("invalid tagged archive value")
    kind = value["$archive_type"]
    if kind == "bytes" and set(value) == {"$archive_type", "base64"}:
        try:
            return base64.b64decode(value["base64"], validate=True)
        except (ValueError, TypeError) as exc:
            raise ArchiveCorrupt("invalid archived bytes") from exc
    if kind in {"list", "tuple", "set", "frozenset"} and set(value) == {"$archive_type", "items"}:
        items = [_decode_value(item) for item in value["items"]]
        if kind == "list":
            return items
        if kind == "tuple":
            return tuple(items)
        return set(items) if kind == "set" else frozenset(items)
    if kind == "dict" and set(value) == {"$archive_type", "items"}:
        try:
            return {_decode_value(pair[0]): _decode_value(pair[1]) for pair in value["items"]}
        except (TypeError, IndexError) as exc:
            raise ArchiveCorrupt("invalid archived mapping") from exc
    raise ArchiveCorrupt(f"unknown archived value encoding: {kind!r}")


def _model_value(value: Any) -> Any:
    if value is None or type(value) in (bool, int, float, str):
        if type(value) is float and not math.isfinite(value):
            raise TypeError("archive semantic fields require finite floats")
        return value
    if isinstance(value, Enum):
        return {"$model_enum": type(value).__name__, "value": value.value}
    if type(value) in (list, tuple):
        encoded = [_model_value(item) for item in value]
        return encoded if type(value) is list else {"$model_tuple": encoded}
    if type(value) is dict:
        if any(type(key) is not str for key in value):
            raise TypeError("semantic model mappings require string keys")
        return {key: _model_value(item) for key, item in value.items()}
    if type(value) is SemanticClaim:
        return {
            "$model_type": "SemanticClaim",
            "family": _model_value(value.family),
            "subject": _model_value(value.subject),
            "epistemic_kind": _model_value(value.epistemic_kind),
            # Claim values are family-owned data, not common-model fields.
            "value": None,
        }
    if type(value) in _MODEL_TYPES:
        return {
            "$model_type": type(value).__name__,
            **{name: _model_value(getattr(value, name)) for name in value.__dataclass_fields__},
        }
    raise TypeError(f"unsupported semantic model value: {type(value).__name__}")


def _restore_model(value: Any) -> Any:
    if value is None or type(value) in (bool, int, float, str):
        return value
    if type(value) is list:
        return [_restore_model(item) for item in value]
    if type(value) is tuple:
        return tuple(_restore_model(item) for item in value)
    if type(value) in (bytes, set, frozenset):
        return value
    if type(value) is not dict:
        raise ArchiveCorrupt("invalid semantic model value")
    if "$model_enum" in value:
        enums = {
            "AuthorityDomain": AuthorityDomain,
            "ConditionDimension": ConditionDimension,
            "ConditionOrigin": ConditionOrigin,
            "IdentityLinkState": IdentityLinkState,
        }
        enum_type = enums.get(value["$model_enum"])
        if enum_type is None or set(value) != {"$model_enum", "value"}:
            raise ArchiveCorrupt("unknown semantic enum")
        try:
            return enum_type(value["value"])
        except ValueError as exc:
            raise ArchiveCorrupt("invalid semantic enum value") from exc
    if "$model_tuple" in value:
        if set(value) != {"$model_tuple"} or type(value["$model_tuple"]) is not list:
            raise ArchiveCorrupt("invalid semantic tuple")
        return tuple(_restore_model(item) for item in value["$model_tuple"])
    if "$model_type" in value:
        cls = next((candidate for candidate in _MODEL_TYPES if candidate.__name__ == value["$model_type"]), None)
        if cls is None:
            raise ArchiveCorrupt("unknown semantic model type")
        fields = {name: _restore_model(item) for name, item in value.items() if name != "$model_type"}
        try:
            return cls(**fields)
        except (TypeError, ValueError) as exc:
            raise ArchiveCorrupt("invalid semantic model record") from exc
    return {key: _restore_model(item) for key, item in value.items()}


def _encode_observation(observation: SemanticObservation[object]) -> bytes:
    if type(observation) is not SemanticObservation:
        raise TypeError("archive accepts SemanticObservation instances only")
    _validate_snapshot_value(observation.claim.value)
    encoded = _model_value(observation)
    encoded["claim"]["value"] = _encode_value(observation.claim.value)
    return json.dumps(
        {"schema": _SCHEMA, "observation": encoded},
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _decode_observation(payload: bytes) -> SemanticObservation[object]:
    try:
        document = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ArchiveCorrupt("invalid archived JSON") from exc
    if type(document) is not dict or set(document) != {"schema", "observation"} or document["schema"] != _SCHEMA:
        raise ArchiveCorrupt("unsupported archive record schema")
    model = document["observation"]
    if type(model) is not dict or type(model.get("claim")) is not dict:
        raise ArchiveCorrupt("invalid archived observation envelope")
    try:
        model["claim"]["value"] = _decode_value(model["claim"]["value"])
        observation = _restore_model(model)
    except (KeyError, TypeError, ValueError) as exc:
        raise ArchiveCorrupt("invalid archived observation") from exc
    if type(observation) is not SemanticObservation:
        raise ArchiveCorrupt("archive record is not a semantic observation")
    return observation


class SQLiteObservationArchive:
    """Append-only local archive with a logical payload-byte ceiling.

    Each successful call is retained, including identical repeated claims;
    there is no source event ID in the common model and Observation does not
    infer one. `max_payload_bytes` bounds encoded record payloads, not SQLite
    index/page overhead. A capacity gap is persisted in metadata and originals
    are never expired or overwritten. This is not a disk-full guarantee.
    """

    def __init__(self, path: str | os.PathLike[str], *, max_payload_bytes: int) -> None:
        if type(max_payload_bytes) is not int or max_payload_bytes < 1:
            raise ValueError("max_payload_bytes must be a positive integer")
        self.path = Path(path)
        if self.path.is_symlink():
            raise ValueError("archive database path must not be a symlink")
        if not self.path.parent.is_dir():
            raise ValueError("archive parent directory must already exist")
        self.max_payload_bytes = max_payload_bytes
        self._db = sqlite3.connect(self.path, timeout=2.0)
        os.chmod(self.path, 0o600)
        self._db.execute("PRAGMA journal_mode=DELETE")
        self._db.execute("PRAGMA synchronous=FULL")
        self._db.execute("PRAGMA foreign_keys=ON")
        meta_exists = self._db.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='archive_meta'"
        ).fetchone()
        if meta_exists:
            version = self._db.execute(
                "SELECT value FROM archive_meta WHERE key='archive_schema_version'"
            ).fetchone()
            if version is not None and version[0] not in {"2", "3"}:
                self._db.close()
                raise ValueError(f"unsupported archive schema version: {version[0]}")
        self._db.executescript(
            """
            CREATE TABLE IF NOT EXISTS archive_meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS archive_records (
                receipt_sequence INTEGER PRIMARY KEY,
                family TEXT NOT NULL,
                authority TEXT NOT NULL,
                payload BLOB NOT NULL,
                content_sha256 TEXT NOT NULL,
                payload_bytes INTEGER NOT NULL,
                capture_id TEXT,
                source_sequence INTEGER
            );
            CREATE TABLE IF NOT EXISTS archive_source_gaps (
                gap_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_sequence INTEGER NOT NULL,
                last_sequence INTEGER NOT NULL,
                reason TEXT NOT NULL,
                capture_id TEXT
            );
            CREATE TABLE IF NOT EXISTS archive_capture_sessions (
                capture_id TEXT PRIMARY KEY,
                initial_source_sequence INTEGER NOT NULL,
                final_source_sequence INTEGER,
                status TEXT NOT NULL,
                terminal_reason TEXT
            );
            CREATE INDEX IF NOT EXISTS archive_family_sequence
                ON archive_records(family, receipt_sequence);
            """
        )
        # Additive, idempotent migration from the first local archive schema.
        # Old rows remain byte-identical with null capture metadata.
        record_columns = {row[1] for row in self._db.execute("PRAGMA table_info(archive_records)")}
        gap_columns = {row[1] for row in self._db.execute("PRAGMA table_info(archive_source_gaps)")}
        if "capture_id" not in record_columns:
            self._db.execute("ALTER TABLE archive_records ADD COLUMN capture_id TEXT")
        if "source_sequence" not in record_columns:
            self._db.execute("ALTER TABLE archive_records ADD COLUMN source_sequence INTEGER")
        if "capture_id" not in gap_columns:
            self._db.execute("ALTER TABLE archive_source_gaps ADD COLUMN capture_id TEXT")
        schema = self._db.execute("SELECT value FROM archive_meta WHERE key='archive_schema_version'").fetchone()
        if schema is not None and schema[0] not in {"2", "3"}:
            self._db.close()
            raise ValueError(f"unsupported archive schema version: {schema[0]}")
        self._db.execute("UPDATE archive_meta SET value='3' WHERE key='archive_schema_version' AND value='2'")
        self._db.execute("INSERT OR IGNORE INTO archive_meta(key,value) VALUES('archive_schema_version','3')")
        self._db.execute(
            "INSERT OR IGNORE INTO archive_meta(key,value) VALUES('max_payload_bytes',?)",
            (str(max_payload_bytes),),
        )
        configured = int(self._db.execute(
            "SELECT value FROM archive_meta WHERE key='max_payload_bytes'"
        ).fetchone()[0])
        if configured != max_payload_bytes:
            self._db.close()
            raise ValueError("archive capacity cannot change after creation")
        self._db.execute("INSERT OR IGNORE INTO archive_meta(key,value) VALUES('last_attempt', '0')")
        self._db.execute("INSERT OR IGNORE INTO archive_meta(key,value) VALUES('gap_start', '')")
        self._db.execute("INSERT OR IGNORE INTO archive_meta(key,value) VALUES('gap_end', '')")
        self._db.commit()

    def start_capture_session(self, capture_id: str, *, initial_source_sequence: int) -> None:
        """Persist opt-in capture start without asserting a causal position."""
        if type(capture_id) is not str or not capture_id.strip():
            raise ValueError("capture_id must be a non-empty string")
        if type(initial_source_sequence) is not int or initial_source_sequence < 0:
            raise ValueError("initial_source_sequence must be a non-negative integer")
        with self._db:
            try:
                self._db.execute(
                    "INSERT INTO archive_capture_sessions(capture_id,initial_source_sequence,status) VALUES(?,?,'running')",
                    (capture_id, initial_source_sequence),
                )
            except sqlite3.IntegrityError as exc:
                raise ValueError("capture_id already exists") from exc

    def finish_capture_session(
        self,
        capture_id: str,
        *,
        status: str = "stopped",
        reason: str | None = None,
        final_source_sequence: int,
    ) -> None:
        """Persist a terminal worker state; terminal states cannot be rewritten."""
        if type(status) is not str or status not in {"stopped", "failed"}:
            raise ValueError("capture session terminal status must be stopped or failed")
        if reason is not None and (type(reason) is not str or not reason.strip()):
            raise ValueError("reason must be a non-empty string when provided")
        if type(final_source_sequence) is not int or final_source_sequence < 0:
            raise ValueError("final_source_sequence must be a non-negative integer")
        with self._db:
            row = self._db.execute(
                "SELECT status,initial_source_sequence FROM archive_capture_sessions WHERE capture_id=?",
                (capture_id,),
            ).fetchone()
            if row is None:
                raise ValueError("capture session does not exist")
            if row[0] != "running":
                raise ValueError("capture session is already terminal")
            if final_source_sequence < row[1]:
                raise ValueError("final_source_sequence cannot precede initial_source_sequence")
            self._db.execute(
                "UPDATE archive_capture_sessions SET status=?,terminal_reason=?,final_source_sequence=? "
                "WHERE capture_id=?",
                (status, reason, final_source_sequence, capture_id),
            )

    def capture_sessions(self) -> tuple[CaptureSession, ...]:
        rows = self._db.execute(
            "SELECT capture_id,initial_source_sequence,final_source_sequence,status,terminal_reason "
            "FROM archive_capture_sessions ORDER BY rowid"
        ).fetchall()
        return tuple(
            CaptureSession(
                str(capture_id),
                int(initial_sequence),
                None if final_sequence is None else int(final_sequence),
                str(status),
                reason,
            )
            for capture_id, initial_sequence, final_sequence, status, reason in rows
        )

    def capture_coverage(self, capture_id: str) -> CaptureCoverage:
        """Compute coverage from durable rows and explicit durable gap markers."""
        # Keep the several reads below on one SQLite snapshot. A second archive
        # handle may be open concurrently, but must not make one report combine
        # metadata from before and after its commit.
        self._db.execute("BEGIN")
        try:
            return self._capture_coverage_snapshot(capture_id)
        finally:
            if self._db.in_transaction:
                self._db.rollback()

    def _capture_coverage_snapshot(self, capture_id: str) -> CaptureCoverage:
        integrity = self._db.execute("PRAGMA quick_check").fetchone()
        if integrity is None or integrity[0] != "ok":
            detail = "missing result" if integrity is None else str(integrity[0])
            raise ArchiveCorrupt(f"SQLite quick_check failed: {detail}")
        session = next((s for s in self.capture_sessions() if s.capture_id == capture_id), None)
        if session is None:
            raise ValueError("capture session does not exist")
        record_rows = self._db.execute(
            "SELECT source_sequence,payload,content_sha256,payload_bytes FROM archive_records "
            "WHERE capture_id=? AND source_sequence IS NOT NULL ORDER BY source_sequence", (capture_id,)
        ).fetchall()
        for sequence, payload, digest, size in record_rows:
            payload = bytes(payload)
            if len(payload) != int(size) or hashlib.sha256(payload).hexdigest() != digest:
                raise ArchiveCorrupt(f"capture record at source sequence {sequence} failed digest/size check")
            _decode_observation(payload)
        persisted = tuple(int(row[0]) for row in record_rows)
        gaps = tuple((int(first), int(last), str(reason)) for first, last, reason in self._db.execute(
            "SELECT first_sequence,last_sequence,reason FROM archive_source_gaps "
            "WHERE capture_id=? ORDER BY first_sequence,last_sequence", (capture_id,)
        ).fetchall())
        if session.final_source_sequence is None:
            received = tuple(g for g in gaps if g[2] in {"archive_capacity_reached", "archive_write_failed"})
            first = session.initial_source_sequence + 1
            accounted = sorted(
                [(seq, seq) for seq in persisted if seq >= first]
                + [(max(lo, first), hi) for lo, hi, _reason in gaps if hi >= first],
            )
            intervals: list[tuple[int, int | None]] = []
            cursor = first
            for lo, hi in accounted:
                if lo > cursor:
                    intervals.append((cursor, lo - 1))
                cursor = max(cursor, hi + 1)
            # The durable session has no final watermark. Even when every
            # observed row is intact, no upper bound can be asserted.
            intervals.append((cursor, None))
            return CaptureCoverage(
                capture_id, "open_unverified", persisted, received, gaps,
                tuple(intervals), False, False,
            )

        # Walk the closed bounded interval. Anything not represented by a
        # persisted row or a durable gap is unknown; overlapping/contradictory
        # markers are also treated as unverifiable rather than complete.
        first = session.initial_source_sequence + 1
        final = session.final_source_sequence
        accounted = sorted(
            [(seq, seq, "persisted") for seq in persisted if first <= seq <= final]
            + [(max(lo, first), min(hi, final), reason) for lo, hi, reason in gaps
               if max(lo, first) <= min(hi, final)],
            key=lambda item: (item[0], item[1]),
        )
        # Rows/markers outside the session's declared source interval are
        # evidence that its persisted boundary is inconsistent, not ignorable
        # extras that permit a completeness claim.
        contradictory = any(seq < first or seq > final for seq in persisted) or any(
            lo < first or hi > final for lo, hi, _reason in gaps
        )
        intervals: list[tuple[int, int]] = []
        cursor = first
        for lo, hi, _reason in accounted:
            if lo < cursor:
                contradictory = True
            if lo > cursor:
                intervals.append((cursor, lo - 1))
            cursor = max(cursor, hi + 1)
        if cursor <= final:
            intervals.append((cursor, final))
        received = tuple(g for g in gaps if g[2] in {"archive_capacity_reached", "archive_write_failed"})
        has_loss = bool(received)
        verified = not intervals and not contradictory
        complete = verified and not gaps and session.status == "stopped"
        status = "closed_verified" if verified else "closed_unverifiable"
        if verified and has_loss:
            status = "closed_verified_with_persisted_loss"
        elif verified and gaps:
            status = "closed_verified_with_gaps"
        return CaptureCoverage(capture_id, status, persisted, received, gaps, tuple(intervals), verified, complete)

    def append(
        self,
        observation: SemanticObservation[object],
        *,
        capture_id: str | None = None,
        source_sequence: int | None = None,
    ) -> int:
        if type(observation) is not SemanticObservation:
            raise TypeError("archive accepts SemanticObservation instances only")
        if observation.authority is AuthorityDomain.LAB:
            raise ValueError("Lab-authority observations are outside this operational archive")
        if (capture_id is None) != (source_sequence is None):
            raise ValueError("capture_id and source_sequence must be provided together")
        if capture_id is not None and (type(capture_id) is not str or not capture_id.strip()):
            raise ValueError("capture_id must be a non-empty string")
        if source_sequence is not None and (type(source_sequence) is not int or source_sequence < 1):
            raise ValueError("source_sequence must be a positive integer")
        payload = _encode_observation(observation)
        family = observation.family.qualified_name
        digest = hashlib.sha256(payload).hexdigest()
        capacity_reached = False
        with self._db:
            if capture_id is not None:
                session = self._db.execute(
                    "SELECT status FROM archive_capture_sessions WHERE capture_id=?",
                    (capture_id,),
                ).fetchone()
                if session is not None and session[0] != "running":
                    raise ValueError("cannot append to a terminal capture session")
            sequence = int(self._db.execute(
                "SELECT value FROM archive_meta WHERE key='last_attempt'"
            ).fetchone()[0]) + 1
            self._db.execute("UPDATE archive_meta SET value=? WHERE key='last_attempt'", (str(sequence),))
            gap_start = self._db.execute("SELECT value FROM archive_meta WHERE key='gap_start'").fetchone()[0]
            payload_used = int(self._db.execute(
                "SELECT COALESCE(SUM(payload_bytes),0) FROM archive_records"
            ).fetchone()[0])
            if gap_start or payload_used + len(payload) > self.max_payload_bytes:
                if not gap_start:
                    self._db.execute("UPDATE archive_meta SET value=? WHERE key='gap_start'", (str(sequence),))
                self._db.execute("UPDATE archive_meta SET value=? WHERE key='gap_end'", (str(sequence),))
                capacity_reached = True
            else:
                self._db.execute(
                    "INSERT INTO archive_records(receipt_sequence,family,authority,payload,content_sha256,payload_bytes,capture_id,source_sequence) VALUES(?,?,?,?,?,?,?,?)",
                    (sequence, family, observation.authority.value, payload, digest, len(payload), capture_id, source_sequence),
                )
        if capacity_reached:
            raise ArchiveCapacityReached("archive payload budget reached; observation not retained")
        return sequence

    def record_source_gap(
        self, first_sequence: int, last_sequence: int, reason: str, *, capture_id: str | None = None
    ) -> None:
        """Persist a known source-delivery gap without claiming source causality.

        These are ObservationPlane delivery sequence numbers, not World ticks.
        Each marker is append-only and never changes archived originals.
        """
        if type(first_sequence) is not int or first_sequence < 1:
            raise ValueError("first_sequence must be a positive integer")
        if type(last_sequence) is not int or last_sequence < first_sequence:
            raise ValueError("last_sequence must be >= first_sequence")
        if type(reason) is not str or not reason.strip():
            raise ValueError("reason must be a non-empty string")
        if capture_id is not None and (type(capture_id) is not str or not capture_id.strip()):
            raise ValueError("capture_id must be a non-empty string")
        with self._db:
            if capture_id is not None:
                session = self._db.execute(
                    "SELECT status FROM archive_capture_sessions WHERE capture_id=?",
                    (capture_id,),
                ).fetchone()
                if session is not None and session[0] != "running":
                    raise ValueError("cannot add a gap to a terminal capture session")
            self._db.execute(
                "INSERT INTO archive_source_gaps(first_sequence,last_sequence,reason,capture_id) VALUES(?,?,?,?)",
                (first_sequence, last_sequence, reason, capture_id),
            )

    def query(
        self,
        *,
        family: str | None = None,
        after_receipt_sequence: int = 0,
        limit: int = 100,
    ) -> tuple[ArchiveRecord, ...]:
        if type(after_receipt_sequence) is not int or after_receipt_sequence < 0:
            raise ValueError("after_receipt_sequence must be a non-negative integer")
        if type(limit) is not int or not 1 <= limit <= 1000:
            raise ValueError("limit must be between 1 and 1000")
        if family is None:
            rows = self._db.execute(
                "SELECT receipt_sequence,payload,content_sha256,payload_bytes,capture_id,source_sequence FROM archive_records "
                "WHERE receipt_sequence>? ORDER BY receipt_sequence LIMIT ?",
                (after_receipt_sequence, limit),
            )
        else:
            rows = self._db.execute(
                "SELECT receipt_sequence,payload,content_sha256,payload_bytes,capture_id,source_sequence FROM archive_records "
                "WHERE family=? AND receipt_sequence>? ORDER BY receipt_sequence LIMIT ?",
                (family, after_receipt_sequence, limit),
            )
        records = []
        for sequence, payload, digest, size, capture_id, source_sequence in rows.fetchall():
            payload = bytes(payload)
            if hashlib.sha256(payload).hexdigest() != digest or len(payload) != size:
                raise ArchiveCorrupt(f"record {sequence} failed content digest/size check")
            observation = _decode_observation(payload)
            records.append(ArchiveRecord(sequence, observation, digest, size, capture_id, source_sequence))
        return tuple(records)

    def status(self) -> ArchiveStatus:
        meta = dict(self._db.execute("SELECT key,value FROM archive_meta"))
        count, used = self._db.execute(
            "SELECT COUNT(*),COALESCE(SUM(payload_bytes),0) FROM archive_records"
        ).fetchone()
        return ArchiveStatus(
            record_count=int(count),
            payload_bytes=int(used),
            max_payload_bytes=self.max_payload_bytes,
            capture_gap_start=int(meta["gap_start"]) if meta["gap_start"] else None,
            capture_gap_end=int(meta["gap_end"]) if meta["gap_end"] else None,
            source_gaps=tuple(
                (int(first), int(last), str(reason))
                for first, last, reason in self._db.execute(
                    "SELECT first_sequence,last_sequence,reason FROM archive_source_gaps ORDER BY gap_id"
                ).fetchall()
            ),
            source_gap_records=tuple(
                SourceDeliveryGap(capture_id, int(first), int(last), str(reason))
                for first, last, reason, capture_id in self._db.execute(
                    "SELECT first_sequence,last_sequence,reason,capture_id FROM archive_source_gaps ORDER BY gap_id"
                ).fetchall()
            ),
        )

    def close(self) -> None:
        self._db.close()

    def __enter__(self) -> SQLiteObservationArchive:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


__all__ = [
    "ArchiveCapacityReached",
    "ArchiveCorrupt",
    "ArchiveError",
    "ArchiveRecord",
    "ArchiveStatus",
    "CaptureSession",
    "SourceDeliveryGap",
    "SQLiteObservationArchive",
]

from __future__ import annotations

import hashlib
import stat
import sqlite3

import pytest

from observation.archive import (
    ArchiveCapacityReached,
    ArchiveCorrupt,
    SQLiteObservationArchive,
    _encode_observation,
)
from observation.semantic import (
    AcquisitionBasis, ActorRef, AuthorityDomain, DomainTimeRef, SemanticClaim,
    SemanticContractRef, SemanticFamily, SemanticObservation, SubjectScope,
)


def sample(value: object = None, step: int = 1) -> SemanticObservation[object]:
    owner = ActorRef("component", "environment.runtime")
    return SemanticObservation(
        claim=SemanticClaim(
            family=SemanticFamily(
                AuthorityDomain.ENVIRONMENT,
                ("finite_scalar_field",),
                SemanticContractRef("environment.finite_scalar_field", "v1"),
            ),
            subject=SubjectScope("environment_location", key="cell:0"),
            epistemic_kind="domain_derived",
            value={"sample": (step, value)},
        ),
        acquisition=AcquisitionBasis("world_model_state"),
        asserter=owner,
        producer=owner,
        domain_time=(DomainTimeRef(AuthorityDomain.ENVIRONMENT, "world_revision", step),),
    )


def test_round_trip_preserves_semantic_models_and_builtin_value_types(tmp_path) -> None:
    observation = sample({"tuple": (1, b"raw", frozenset({"x", "y"})), "list": [True]})
    with SQLiteObservationArchive(tmp_path / "archive.sqlite", max_payload_bytes=100_000) as archive:
        assert archive.append(observation) == 1
        record = archive.query()[0]
    assert record.observation == observation
    assert type(record.observation.domain_time) is tuple
    assert type(record.observation.claim.value["sample"]) is tuple
    assert record.content_sha256 == hashlib.sha256(_encode_observation(observation)).hexdigest()


def test_archive_checks_effective_sqlite_durability_settings(tmp_path) -> None:
    with SQLiteObservationArchive(tmp_path / "archive.sqlite", max_payload_bytes=100_000) as archive:
        assert archive._db.execute("PRAGMA journal_mode").fetchone()[0].lower() == "delete"
        assert archive._db.execute("PRAGMA synchronous").fetchone()[0] == 3
        assert archive._db.execute("PRAGMA foreign_keys").fetchone()[0] == 1


def test_reopen_keeps_records_and_repeated_claims_as_distinct_receipts(tmp_path) -> None:
    path = tmp_path / "archive.sqlite"
    with SQLiteObservationArchive(path, max_payload_bytes=100_000) as archive:
        assert archive.append(sample()) == 1
        assert archive.append(sample()) == 2
    with SQLiteObservationArchive(path, max_payload_bytes=100_000) as archive:
        records = archive.query()
        assert [record.receipt_sequence for record in records] == [1, 2]
        assert records[0].observation == records[1].observation
        assert archive.status().record_count == 2
        with pytest.raises(ValueError, match="cannot change"):
            SQLiteObservationArchive(path, max_payload_bytes=100_001)


def test_capacity_stop_persists_capture_gap_without_discarding_prior_records(tmp_path) -> None:
    path = tmp_path / "archive.sqlite"
    first = sample()
    payload_size = len(_encode_observation(first))
    with SQLiteObservationArchive(path, max_payload_bytes=payload_size) as archive:
        archive.append(first)
        with pytest.raises(ArchiveCapacityReached):
            archive.append(sample(step=2))
        assert archive.status().record_count == 1
        assert archive.status().capture_gap_start == 2
        assert archive.status().capture_gap_end == 2
        with pytest.raises(ArchiveCapacityReached):
            archive.append(sample(step=3))
        assert archive.status().capture_gap_end == 3
    with SQLiteObservationArchive(path, max_payload_bytes=payload_size) as archive:
        assert [r.receipt_sequence for r in archive.query()] == [1]
        assert (archive.status().capture_gap_start, archive.status().capture_gap_end) == (2, 3)


def test_invalid_payload_is_rejected_before_receipt_or_gap_metadata_changes(tmp_path) -> None:
    with SQLiteObservationArchive(tmp_path / "archive.sqlite", max_payload_bytes=100_000) as archive:
        with pytest.raises(TypeError, match="finite floats"):
            archive.append(sample(float("nan")))
        assert archive.status().record_count == 0
        assert archive.status().capture_gap_start is None


def test_lab_authority_observation_is_rejected_without_archive_side_effects(tmp_path) -> None:
    lab_owner = ActorRef("component", "lab.evidence")
    lab_observation = SemanticObservation(
        claim=SemanticClaim(
            family=SemanticFamily(
                AuthorityDomain.LAB,
                ("evidence",),
                SemanticContractRef("lab.evidence", "v1"),
            ),
            subject=SubjectScope("evidence_record", key="record:1"),
            epistemic_kind="lab_derived",
            value={"result": "accepted"},
        ),
        acquisition=AcquisitionBasis("lab_analysis"),
        asserter=lab_owner,
        producer=lab_owner,
    )
    with SQLiteObservationArchive(tmp_path / "archive.sqlite", max_payload_bytes=100_000) as archive:
        with pytest.raises(ValueError, match="Lab-authority"):
            archive.append(lab_observation)
        assert archive.status().record_count == 0
        assert archive.status().capture_gap_start is None


def test_query_filters_and_paginates_by_local_receipt_sequence(tmp_path) -> None:
    with SQLiteObservationArchive(tmp_path / "archive.sqlite", max_payload_bytes=100_000) as archive:
        archive.append(sample(step=1))
        archive.append(sample(step=2))
        rows = archive.query(family="environment.finite_scalar_field", after_receipt_sequence=1, limit=1)
        assert len(rows) == 1
        assert rows[0].receipt_sequence == 2
        assert rows[0].observation.domain_time[0].value == 2


def test_capture_delivery_identity_is_scoped_and_not_embedded_in_claim(tmp_path) -> None:
    with SQLiteObservationArchive(tmp_path / "archive.sqlite", max_payload_bytes=100_000) as archive:
        archive.append(sample(step=7), capture_id="capture-a", source_sequence=12)
        archive.record_source_gap(13, 14, "consumer_overflow", capture_id="capture-a")
        record = archive.query()[0]
        status = archive.status()
    assert (record.capture_id, record.source_sequence) == ("capture-a", 12)
    assert record.observation == sample(step=7)
    assert status.source_gaps == ((13, 14, "consumer_overflow"),)
    assert status.source_gap_records[0].capture_id == "capture-a"
    assert (status.source_gap_records[0].first_sequence, status.source_gap_records[0].last_sequence) == (13, 14)


def test_capture_identity_fields_must_be_paired_and_valid(tmp_path) -> None:
    with SQLiteObservationArchive(tmp_path / "archive.sqlite", max_payload_bytes=100_000) as archive:
        with pytest.raises(ValueError, match="provided together"):
            archive.append(sample(), capture_id="capture-a")
        with pytest.raises(ValueError, match="positive integer"):
            archive.append(sample(), capture_id="capture-a", source_sequence=0)
        assert archive.status().record_count == 0


def test_v1_archive_is_additively_migrated_preserving_original_payload(tmp_path) -> None:
    path = tmp_path / "archive.sqlite"
    observation = sample(step=4)
    payload = _encode_observation(observation)
    digest = hashlib.sha256(payload).hexdigest()
    with sqlite3.connect(path) as db:
        db.executescript("""
            CREATE TABLE archive_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE archive_records (
                receipt_sequence INTEGER PRIMARY KEY, family TEXT NOT NULL, authority TEXT NOT NULL,
                payload BLOB NOT NULL, content_sha256 TEXT NOT NULL, payload_bytes INTEGER NOT NULL
            );
            CREATE TABLE archive_source_gaps (
                gap_id INTEGER PRIMARY KEY AUTOINCREMENT, first_sequence INTEGER NOT NULL,
                last_sequence INTEGER NOT NULL, reason TEXT NOT NULL
            );
        """)
        db.executemany("INSERT INTO archive_meta VALUES(?,?)", [
            ("max_payload_bytes", "100000"), ("last_attempt", "1"), ("gap_start", ""), ("gap_end", "")
        ])
        db.execute("INSERT INTO archive_records VALUES(1,?,?,?,?,?)", (
            "environment.finite_scalar_field", "environment", payload, digest, len(payload)
        ))
    with SQLiteObservationArchive(path, max_payload_bytes=100_000) as archive:
        row = archive.query()[0]
        assert row.observation == observation
        assert row.capture_id is row.source_sequence is None
        archive.append(sample(step=5), capture_id="capture-b", source_sequence=2)
    with sqlite3.connect(path) as db:
        assert db.execute("SELECT value FROM archive_meta WHERE key='archive_schema_version'").fetchone()[0] == "3"
        assert db.execute("SELECT content_sha256 FROM archive_records WHERE receipt_sequence=1").fetchone()[0] == digest


def test_unknown_future_archive_schema_is_rejected_before_mutation(tmp_path) -> None:
    path = tmp_path / "archive.sqlite"
    with SQLiteObservationArchive(path, max_payload_bytes=100_000):
        pass
    with sqlite3.connect(path) as db:
        db.execute("UPDATE archive_meta SET value='99' WHERE key='archive_schema_version'")
        columns_before = tuple(row[1] for row in db.execute("PRAGMA table_info(archive_records)"))
    with pytest.raises(ValueError, match="unsupported archive schema version"):
        SQLiteObservationArchive(path, max_payload_bytes=100_000)
    with sqlite3.connect(path) as db:
        assert tuple(row[1] for row in db.execute("PRAGMA table_info(archive_records)")) == columns_before
        assert db.execute("SELECT value FROM archive_meta WHERE key='archive_schema_version'").fetchone()[0] == "99"


def test_v2_archive_is_additively_migrated_to_capture_lifecycle_schema(tmp_path) -> None:
    path = tmp_path / "archive.sqlite"
    original = sample(step=6)
    with SQLiteObservationArchive(path, max_payload_bytes=100_000) as archive:
        archive.append(original, capture_id="capture-old", source_sequence=9)
    with sqlite3.connect(path) as db:
        db.execute("UPDATE archive_meta SET value='2' WHERE key='archive_schema_version'")

    with SQLiteObservationArchive(path, max_payload_bytes=100_000) as archive:
        rows = archive.query()
        assert rows[0].observation == original
        assert (rows[0].capture_id, rows[0].source_sequence) == ("capture-old", 9)
        assert archive.capture_sessions() == ()
    with sqlite3.connect(path) as db:
        assert db.execute(
            "SELECT value FROM archive_meta WHERE key='archive_schema_version'"
        ).fetchone()[0] == "3"




def test_tampered_record_is_reported_as_corrupt(tmp_path) -> None:
    path = tmp_path / "archive.sqlite"
    with SQLiteObservationArchive(path, max_payload_bytes=100_000) as archive:
        archive.append(sample())
    with sqlite3.connect(path) as db:
        db.execute("UPDATE archive_records SET content_sha256=?", ("0" * 64,))
    with SQLiteObservationArchive(path, max_payload_bytes=100_000) as archive:
        with pytest.raises(ArchiveCorrupt, match="digest"):
            archive.query()


def test_archive_file_is_owner_only_and_symlink_database_is_rejected(tmp_path) -> None:
    path = tmp_path / "archive.sqlite"
    with SQLiteObservationArchive(path, max_payload_bytes=10_000):
        assert stat.S_IMODE(path.stat().st_mode) == 0o600

    link = tmp_path / "archive-link.sqlite"
    link.symlink_to(path)
    with pytest.raises(ValueError, match="symlink"):
        SQLiteObservationArchive(link, max_payload_bytes=10_000)


def test_terminal_capture_cannot_be_mutated_after_closure(tmp_path) -> None:
    path = tmp_path / "archive.sqlite"
    with SQLiteObservationArchive(path, max_payload_bytes=100_000) as archive:
        archive.start_capture_session("closed", initial_source_sequence=0)
        archive.append(sample(step=1), capture_id="closed", source_sequence=1)
        archive.finish_capture_session("closed", final_source_sequence=1)
        with pytest.raises(ValueError, match="terminal capture session"):
            archive.append(sample(step=2), capture_id="closed", source_sequence=2)
        with pytest.raises(ValueError, match="terminal capture session"):
            archive.record_source_gap(2, 2, "late_gap", capture_id="closed")
        coverage = archive.capture_coverage("closed")
        assert coverage.closure_verified
        assert coverage.complete
        assert coverage.persisted_sequences == (1,)


def test_closed_capture_with_records_outside_its_watermark_is_not_verified(tmp_path) -> None:
    path = tmp_path / "archive.sqlite"
    late = sample(step=2)
    payload = _encode_observation(late)
    digest = hashlib.sha256(payload).hexdigest()
    with SQLiteObservationArchive(path, max_payload_bytes=100_000) as archive:
        archive.start_capture_session("bounded", initial_source_sequence=0)
        archive.append(sample(step=1), capture_id="bounded", source_sequence=1)
        archive.finish_capture_session("bounded", final_source_sequence=1)
    # Simulate a legacy/corrupt archive produced before terminal writes were
    # rejected. The valid payload is outside the durable closure watermark.
    with sqlite3.connect(path) as db:
        db.execute(
            "INSERT INTO archive_records(receipt_sequence,family,authority,payload,content_sha256,payload_bytes,capture_id,source_sequence) "
            "VALUES(99,?,?,?,?,?,?,?)",
            (late.family.qualified_name, late.authority.value, payload, digest, len(payload), "bounded", 2),
        )
    with SQLiteObservationArchive(path, max_payload_bytes=100_000) as archive:
        coverage = archive.capture_coverage("bounded")
        assert coverage.status == "closed_unverifiable"
        assert coverage.closure_verified is False
        assert coverage.complete is False

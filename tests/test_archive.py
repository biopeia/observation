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

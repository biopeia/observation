from __future__ import annotations

import hashlib
import sqlite3
import time

import pytest

from observation.archive import (
    ArchiveCorrupt,
    ArchiveError,
    ArchiveReader,
    SQLiteObservationArchive,
    _encode_observation,
)
from observation import LocalObservationArchiveCapture, ObservationPlane
from test_archive import sample


def test_reader_paginates_exact_family_subject_revision_and_domain_time_read_only(tmp_path) -> None:
    path = tmp_path / "archive.sqlite"
    first = sample(step=1)
    second = sample(step=1)
    with SQLiteObservationArchive(path, max_payload_bytes=100_000) as archive:
        archive.append(first)
        archive.append(second)
    before = path.read_bytes()

    with ArchiveReader(path) as reader:
        page = reader.query_page(
            filters={
                "owner": first.authority.value,
                "family": first.family.qualified_name,
                "subject": first.claim.subject,
                "revision": first.family.contract.revision,
                "domain_time": first.domain_time[0],
            },
            limit=1,
        )
        assert page.status == "results"
        assert [record.receipt_sequence for record in page.records] == [1]
        assert page.records[0].observation == first
        assert page.has_more is True
        assert page.next_after_receipt_sequence == 1
        assert page.identity_status == "not_applicable"

        page2 = reader.query_page(
            filters={"family": first.family.qualified_name},
            after_receipt_sequence=page.next_after_receipt_sequence,
            limit=1,
        )
        assert [record.receipt_sequence for record in page2.records] == [2]
        assert page2.has_more is False
        assert page2.records[0].original_payload == _encode_observation(second)
        assert page2.records[0].content_sha256 == hashlib.sha256(
            page2.records[0].original_payload
        ).hexdigest()
    assert path.read_bytes() == before
    assert not list(tmp_path.glob("archive.sqlite-*-journal"))
    assert not list(tmp_path.glob("archive.sqlite-*-wal"))


def test_reader_reports_unsupported_filters_and_unasserted_identity_without_claiming_source_absence(tmp_path) -> None:
    path = tmp_path / "archive.sqlite"
    observation = sample(step=1)
    with SQLiteObservationArchive(path, max_payload_bytes=100_000) as archive:
        archive.append(observation)

    with ArchiveReader(path) as reader:
        owner_page = reader.query_page(filters={"owner": observation.authority.value})
        assert owner_page.status == "results"
        assert owner_page.records[0].observation.authority == observation.authority
        unsupported = reader.query_page(filters={"world_tick": 1})
        assert unsupported.status == "unsupported_filter"
        assert unsupported.unsupported_filters == ("world_tick",)
        assert unsupported.records == ()

        missing_subject = type(observation.claim.subject)(
            "environment_location", key="not-in-this-archive"
        )
        missing = reader.query_page(filters={"subject": missing_subject})
        assert missing.status == "no_matching_publications"
        assert missing.identity_status == "not_asserted_in_page"


def test_reader_exposes_capture_catalog_and_unverifiable_open_coverage_without_recovery_mutation(tmp_path) -> None:
    path = tmp_path / "archive.sqlite"
    with SQLiteObservationArchive(path, max_payload_bytes=100_000) as archive:
        archive.start_capture_session("interrupted", initial_source_sequence=0)
        archive.append(sample(step=1), capture_id="interrupted", source_sequence=1)
    before = path.read_bytes()

    with ArchiveReader(path) as reader:
        catalog = reader.capture_catalog()
        assert catalog.status == "available"
        assert [session.capture_id for session in catalog.sessions] == ["interrupted"]
        coverage = reader.capture_coverage("interrupted")
        assert coverage.status == "available"
        assert coverage.coverage.status == "open_unverified"
        assert coverage.coverage.closure_verified is False
        assert coverage.coverage.complete is False
        assert coverage.coverage.unverifiable_intervals == ((2, None),)
        assert reader.integrity_check() == "ok"
    assert path.read_bytes() == before


def test_reader_reads_capture_output_as_closed_verified_local_archive(tmp_path) -> None:
    """Exercise the supported writer-to-reader path, not two isolated APIs."""
    path = tmp_path / "captured.sqlite"
    observation = sample(step=1)
    plane = ObservationPlane()
    capture = LocalObservationArchiveCapture(
        plane, path, max_payload_bytes=100_000
    )
    capture.start()
    try:
        plane.publish(observation)
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline:
            if capture.status().last_persisted_sequence == 1:
                break
            time.sleep(0.01)
        assert capture.status().last_persisted_sequence == 1
    finally:
        capture.stop()

    before = path.read_bytes()
    with ArchiveReader(path) as reader:
        page = reader.query_page(limit=10)
        assert page.status == "results"
        assert len(page.records) == 1
        record, = page.records
        assert record.observation == observation
        assert record.source_sequence == 1
        assert record.capture_id == capture.capture_id
        assert record.original_payload == _encode_observation(observation)

        catalog = reader.capture_catalog()
        assert catalog.status == "available"
        assert len(catalog.sessions) == 1
        session, = catalog.sessions
        assert session.capture_id == capture.capture_id
        assert session.status == "stopped"
        coverage = reader.capture_coverage(capture.capture_id)
        assert coverage.status == "available"
        assert coverage.coverage is not None
        assert coverage.coverage.status == "closed_verified"
        assert coverage.coverage.persisted_sequences == (1,)
        assert coverage.coverage.closure_verified is True
        assert coverage.coverage.complete is True
        assert reader.integrity_check() == "ok"
    assert path.read_bytes() == before


def test_reader_verifies_payload_digest_and_refuses_unknown_schema(tmp_path) -> None:
    path = tmp_path / "archive.sqlite"
    with SQLiteObservationArchive(path, max_payload_bytes=100_000) as archive:
        archive.append(sample())
    with sqlite3.connect(path) as db:
        db.execute("UPDATE archive_records SET content_sha256=?", ("0" * 64,))
    with ArchiveReader(path) as reader:
        with pytest.raises(ArchiveCorrupt, match="digest"):
            reader.query_page()

    unknown = tmp_path / "unknown.sqlite"
    with SQLiteObservationArchive(unknown, max_payload_bytes=100_000):
        pass
    with sqlite3.connect(unknown) as db:
        db.execute(
            "UPDATE archive_meta SET value='999' WHERE key='archive_schema_version'"
        )
    with pytest.raises(ArchiveCorrupt, match="unsupported archive schema"):
        ArchiveReader(unknown)


@pytest.mark.parametrize(
    ("column", "value", "filter_name", "filter_value"),
    [
        ("authority", "corrupt.owner", "owner", "corrupt.owner"),
        ("family", "corrupt.family", "family", "corrupt.family"),
    ],
)
def test_reader_rejects_indexed_filter_metadata_drift_even_for_queries_that_would_omit_the_record(
    tmp_path, column, value, filter_name, filter_value
) -> None:
    path = tmp_path / "archive.sqlite"
    observation = sample()
    with SQLiteObservationArchive(path, max_payload_bytes=100_000) as archive:
        archive.append(observation)
    with sqlite3.connect(path) as db:
        db.execute(f"UPDATE archive_records SET {column}=?", (value,))

    with ArchiveReader(path) as reader:
        with pytest.raises(ArchiveCorrupt, match="indexed family/authority"):
            reader.query_page(filters={filter_name: filter_value})


def test_reader_reports_unavailable_capture_catalog_when_lifecycle_metadata_is_absent(tmp_path) -> None:
    path = tmp_path / "archive.sqlite"
    with SQLiteObservationArchive(path, max_payload_bytes=100_000):
        pass
    with sqlite3.connect(path) as db:
        db.execute("DROP TABLE archive_capture_sessions")
        db.execute("DROP TABLE archive_source_gaps")

    with ArchiveReader(path) as reader:
        catalog = reader.capture_catalog()
        assert catalog.status == "unsupported_schema"
        assert catalog.sessions == ()
        with pytest.raises(ArchiveError, match="metadata is unavailable"):
            reader.capture_sessions()


def test_reader_returns_explicit_unverifiable_capture_and_rejects_missing_file(tmp_path) -> None:
    path = tmp_path / "archive.sqlite"
    with SQLiteObservationArchive(path, max_payload_bytes=100_000):
        pass
    before = path.read_bytes()
    with ArchiveReader(path) as reader:
        result = reader.capture_coverage("not-present")
        assert result.status == "capture_not_found"
        assert result.coverage is None
    assert path.read_bytes() == before
    with pytest.raises(FileNotFoundError):
        ArchiveReader(tmp_path / "does-not-exist.sqlite")


def test_reader_rejects_symlink_and_invalid_query_without_writing(tmp_path) -> None:
    path = tmp_path / "archive.sqlite"
    with SQLiteObservationArchive(path, max_payload_bytes=100_000) as archive:
        archive.append(sample())
    before = path.read_bytes()
    alias = tmp_path / "alias.sqlite"
    alias.symlink_to(path)
    with pytest.raises(ValueError, match="symlink"):
        ArchiveReader(alias)
    with ArchiveReader(path) as reader:
        with pytest.raises(ValueError, match="limit"):
            reader.query_page(limit=0)
        with pytest.raises(ValueError, match="after_receipt_sequence"):
            reader.query_page(after_receipt_sequence=-1)
    assert path.read_bytes() == before


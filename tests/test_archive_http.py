from __future__ import annotations

from observation.archive import SQLiteObservationArchive
from observation.archive_http import read_archive_query, MAX_PAGE
from test_archive import sample


def test_archive_http_receipt_pages_are_read_only(tmp_path):
    path = tmp_path / "archive.sqlite"
    with SQLiteObservationArchive(path, max_payload_bytes=100_000) as archive:
        archive.append(sample(step=1))
        archive.append(sample(step=2))
    before = path.read_bytes()
    code, first = read_archive_query(str(path), "/v2/archive/receipts?limit=1")
    assert code == 200
    assert first["schema"] == "biopeia.observation.archive-http.v1"
    assert first["has_more"] is True
    assert len(first["receipts"]) == 1
    assert first["receipts"][0]["receipt_sequence"] == 1
    assert "original_payload" not in first["receipts"][0]
    code, second = read_archive_query(str(path), "/v2/archive/receipts?after=1&limit=1")
    assert code == 200
    assert [r["receipt_sequence"] for r in second["receipts"]] == [2]
    assert second["has_more"] is False
    assert path.read_bytes() == before


def test_archive_http_rejects_unsupported_or_unbounded_queries(tmp_path):
    path = tmp_path / "archive.sqlite"
    with SQLiteObservationArchive(path, max_payload_bytes=100_000):
        pass
    for query in (
        "?run_id=x", "?world_tick=4", "?limit=0",
        f"?limit={MAX_PAGE + 1}", "?after=-1", "?after=1.2",
        "?owner=a&owner=b", "?family=", "?limit=1&unknown=2",
    ):
        code, _ = read_archive_query(str(path), "/v2/archive/receipts" + query)
        assert code == 400, query


def test_archive_http_capture_status_does_not_claim_complete_history(tmp_path):
    path = tmp_path / "archive.sqlite"
    with SQLiteObservationArchive(path, max_payload_bytes=100_000) as archive:
        archive.start_capture_session("open", initial_source_sequence=0)
        archive.append(sample(step=1), capture_id="open", source_sequence=1)
    code, catalog = read_archive_query(str(path), "/v2/archive/captures")
    assert code == 200
    assert catalog["captures"][0]["status"] != "closed_verified"
    code, coverage = read_archive_query(str(path), "/v2/archive/coverage?capture_id=open")
    assert code == 200
    assert coverage["coverage"]["complete"] is False
    assert coverage["coverage"]["closure_verified"] is False


def test_archive_http_missing_archive_fails_closed(tmp_path):
    code, body = read_archive_query(str(tmp_path / "missing.sqlite"), "/v2/archive/receipts")
    assert code == 503
    assert body["status"] == "archive_unavailable"

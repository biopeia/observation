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


def test_archive_http_response_byte_limit_boundary_and_overflow(monkeypatch):
    import json
    from observation import archive_http

    # JSON object overhead for {"x":"..."} is exactly eight UTF-8 bytes.
    at_limit = {"x": "a" * (archive_http.MAX_RESPONSE_BYTES - 8)}
    status, body = archive_http.encode_response(at_limit)
    assert status == 200
    assert len(body) == archive_http.MAX_RESPONSE_BYTES

    multibyte_at_limit = {"x": "é" * ((archive_http.MAX_RESPONSE_BYTES - 8) // 2)}
    status, body = archive_http.encode_response(multibyte_at_limit)
    assert status == 200
    assert len(body) == archive_http.MAX_RESPONSE_BYTES

    over_limit = {"x": "a" * (archive_http.MAX_RESPONSE_BYTES - 7)}
    status, body = archive_http.encode_response(over_limit)
    assert status == 413
    assert len(body) <= archive_http.MAX_RESPONSE_BYTES
    assert json.loads(body) == {
        "status": "response_too_large",
        "max_response_bytes": archive_http.MAX_RESPONSE_BYTES,
    }
    # Escaped controls expand to six output bytes each; preflight rejects
    # before JSONEncoder materializes that much larger token.
    assert archive_http.encode_bounded_json({"x": "\x01" * 200_000}) is None


def test_archive_http_oversized_response_rejects_without_poisoning_next_read(tmp_path, monkeypatch):
    import json
    import threading
    from http.client import HTTPConnection
    from observation import archive_http

    archive = tmp_path / "archive.sqlite"
    with SQLiteObservationArchive(archive, max_payload_bytes=100_000):
        pass
    server = archive_http.LoopbackArchiveServer(
        ("127.0.0.1", 0), archive_http.make_archive_handler(str(archive))
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        def request():
            connection = HTTPConnection("127.0.0.1", server.server_port, timeout=3)
            connection.request("GET", "/v2/archive/receipts")
            response = connection.getresponse()
            result = response.status, response.read()
            connection.close()
            return result

        monkeypatch.setattr(
            archive_http, "read_archive_query",
            lambda *_: (200, {"x": "a" * (archive_http.MAX_RESPONSE_BYTES + 1)}),
        )
        status, body = request()
        assert status == 413
        assert len(body) <= archive_http.MAX_RESPONSE_BYTES
        assert json.loads(body)["status"] == "response_too_large"

        monkeypatch.setattr(
            archive_http, "read_archive_query",
            lambda *_: (200, {"status": "ok"}),
        )
        status, body = request()
        assert status == 200
        assert json.loads(body) == {"status": "ok"}
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)

def test_non_sqlite_and_symlink_fail_closed(tmp_path):
    invalid = tmp_path / "invalid.sqlite"
    invalid.write_bytes(b"not a sqlite database")
    status, result = read_archive_query(str(invalid), "/v2/archive/receipts")
    assert status == 503
    assert result["status"] == "archive_invalid"
    alias = tmp_path / "alias.sqlite"
    alias.symlink_to(invalid)
    status, result = read_archive_query(str(alias), "/v2/archive/receipts")
    assert status == 503
    assert result["status"] == "archive_invalid"


def test_archive_http_security_guards_and_unexpected_error(tmp_path, monkeypatch):
    import json
    import threading
    from http.client import HTTPConnection
    from http.server import ThreadingHTTPServer
    from observation import archive_http

    archive = tmp_path / "archive.sqlite"
    with SQLiteObservationArchive(archive, max_payload_bytes=100_000):
        pass
    server = archive_http.LoopbackArchiveServer(
        ("127.0.0.1", 0), archive_http.make_archive_handler(str(archive))
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        port = server.server_port

        def request(method, path, headers=None):
            connection = HTTPConnection("127.0.0.1", port, timeout=3)
            connection.request(method, path, headers=headers or {})
            response = connection.getresponse()
            code = response.status
            body = response.read()
            connection.close()
            return code, body

        assert request("GET", "/v2/archive/captures")[0] == 200
        assert request("POST", "/v2/archive/captures")[0] == 405
        assert request("GET", "/v2/archive/captures", {"Host": "attacker.invalid"})[0] == 403
        assert request("GET", "/v2/archive/captures", {"Origin": "http://attacker.invalid"})[0] == 403

        def crash(_path, _target):
            raise RuntimeError("injected")

        monkeypatch.setattr(archive_http, "read_archive_query", crash)
        code, body = request("GET", "/v2/archive/receipts")
        assert code == 500
        assert json.loads(body)["status"] == "internal_error"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)

def test_archive_server_rejects_non_loopback_bind():
    import pytest
    from observation.archive_http import LoopbackArchiveServer, make_archive_handler
    with pytest.raises(ValueError, match="loopback"):
        LoopbackArchiveServer(("0.0.0.0", 0), make_archive_handler("unused.sqlite"))

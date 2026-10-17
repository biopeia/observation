"""Local read-only HTTP adapter for the bounded Observation archive.

Receipt order is not causal order. This service does not capture, mutate or
admit scientific evidence. It exposes metadata only, not family-owned payloads.
"""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

from .archive import ArchiveCorrupt, ArchiveError, ArchiveReader

MAX_PAGE = 50
MAX_QUERY_BYTES = 2048


def read_archive_query(archive_path: str, target: str) -> tuple[int, dict]:
    """Pure request dispatcher; each request opens a fresh read-only archive."""
    if len(target.encode("utf-8")) > MAX_QUERY_BYTES:
        return 414, {"status": "query_too_long"}
    url = urlsplit(target)
    if url.path not in {"/v2/archive/captures", "/v2/archive/receipts", "/v2/archive/coverage"}:
        return 404, {"status": "not_found"}
    try:
        params = parse_qs(url.query, keep_blank_values=True, strict_parsing=True)
    except ValueError:
        return 400, {"status": "invalid_query"}
    allowed = {
        "/v2/archive/captures": set(),
        "/v2/archive/receipts": {"after", "limit", "owner", "family", "revision"},
        "/v2/archive/coverage": {"capture_id"},
    }[url.path]
    if any(key not in allowed or len(values) != 1 for key, values in params.items()):
        return 400, {"status": "unsupported_query"}
    try:
        with ArchiveReader(archive_path) as reader:
            if url.path == "/v2/archive/captures":
                catalog = reader.capture_catalog()
                return 200, {"schema": "biopeia.observation.archive-http.v1",
                             "status": catalog.status,
                             "captures": [{"capture_id": s.capture_id, "status": s.status,
                                           "initial_source_sequence": s.initial_source_sequence,
                                           "final_source_sequence": s.final_source_sequence}
                                          for s in catalog.sessions]}
            if url.path == "/v2/archive/coverage":
                capture_id = params.get("capture_id", [""])[0]
                if not capture_id or len(capture_id) > 128:
                    return 400, {"status": "invalid_capture_id"}
                result = reader.capture_coverage(capture_id)
                coverage = result.coverage
                return 200, {"schema": "biopeia.observation.archive-http.v1",
                             "status": result.status,
                             "coverage": None if coverage is None else {
                                 "capture_id": coverage.capture_id, "status": coverage.status,
                                 "closure_verified": coverage.closure_verified,
                                 "complete": coverage.complete,
                                 "received_not_persisted": coverage.received_not_persisted,
                                 "known_source_gaps": coverage.known_source_gaps,
                                 "unverifiable_intervals": coverage.unverifiable_intervals}}
            def bounded_integer(key: str, default: int, maximum: int) -> int:
                raw = params.get(key, [str(default)])[0]
                if not raw.isascii() or not raw.isdecimal() or len(raw) > 15:
                    raise ValueError("invalid integer")
                value = int(raw)
                if value > maximum:
                    raise ValueError("integer exceeds bound")
                return value
            after = bounded_integer("after", 0, 2**53 - 1)
            limit = bounded_integer("limit", 25, MAX_PAGE)
            if limit < 1:
                raise ValueError("limit must be positive")
            filters = {key: params[key][0] for key in ("owner", "family", "revision") if key in params}
            if any(not value or len(value) > 256 for value in filters.values()):
                raise ValueError("invalid filter")
            page = reader.query_page(filters=filters, after_receipt_sequence=after, limit=limit)
            return 200, {"schema": "biopeia.observation.archive-http.v1",
                         "status": page.status, "has_more": page.has_more,
                         "next_after_receipt_sequence": page.next_after_receipt_sequence,
                         "identity_status": page.identity_status,
                         "receipts": [{
                             "receipt_sequence": r.receipt_sequence,
                             "capture_id": r.capture_id, "source_sequence": r.source_sequence,
                             "content_sha256": r.content_sha256, "payload_bytes": r.payload_bytes,
                             "authority": r.observation.authority.value,
                             "family": r.observation.family.qualified_name,
                             "revision": r.observation.family.contract.revision,
                         } for r in page.records]}
    except ValueError:
        return 400, {"status": "invalid_query"}
    except FileNotFoundError:
        return 503, {"status": "archive_unavailable"}
    except (ArchiveCorrupt, ArchiveError):
        return 503, {"status": "archive_invalid"}
    except OSError:
        return 503, {"status": "archive_unavailable"}


def make_archive_handler(archive_path: str):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.headers.get("Host") not in {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}:
                self.send_error(403)
                return
            origin = self.headers.get("Origin")
            if origin is not None:
                self.send_error(403)
                return
            status, payload = read_archive_query(archive_path, self.path)
            data = json.dumps(payload, separators=(",", ":"), allow_nan=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_POST(self):
            self.send_error(405)

        def log_message(self, *_args):
            pass

    return Handler


def serve_archive(archive_path: str, port: int = 4175) -> None:
    """Explicit opt-in operator entrypoint; never starts automatically."""
    with ThreadingHTTPServer(("127.0.0.1", port), make_archive_handler(archive_path)) as server:
        server.serve_forever()

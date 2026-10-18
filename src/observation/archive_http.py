"""Local read-only HTTP adapter for the bounded Observation archive.

Receipt order is not causal order. This service does not capture, mutate or
admit scientific evidence. It exposes metadata only, not family-owned payloads.
"""
from __future__ import annotations

import json
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit
from pathlib import Path

from .archive import ArchiveCorrupt, ArchiveError, ArchiveReader

MAX_PAGE = 50
MAX_QUERY_BYTES = 2048
MAX_RESPONSE_BYTES = 1_048_576


def _bounded_json_size(value: object, remaining: int) -> int | None:
    """Preflight JSON's compact UTF-8 size without materializing encoded tokens."""
    if isinstance(value, str):
        size = 2  # surrounding quotes
        for char in value:
            codepoint = ord(char)
            if char in {'"', "\\", "\b", "\f", "\n", "\r", "\t"}:
                size += 2
            elif codepoint < 0x20:
                size += 6  # \u00xx
            elif codepoint < 0x80:
                size += 1
            elif codepoint < 0x800:
                size += 2
            elif 0xD800 <= codepoint <= 0xDFFF:
                return None  # not valid UTF-8; fail closed
            elif codepoint < 0x10000:
                size += 3
            else:
                size += 4
            if size > remaining:
                return None
        return size if size <= remaining else None
    if value is None:
        return 4
    if value is True:
        return 4
    if value is False:
        return 5
    if isinstance(value, (int, float)):
        try:
            size = len(json.dumps(value, allow_nan=False).encode("ascii"))
            return size if size <= remaining else None
        except (ValueError, OverflowError):
            return None
    if isinstance(value, (list, tuple)):
        size = 2  # brackets
        if size > remaining:
            return None
        for index, item in enumerate(value):
            item_size = _bounded_json_size(item, remaining - size)
            if item_size is None:
                return None
            size += item_size + (index > 0)
            if size > remaining:
                return None
        return size
    if isinstance(value, dict):
        size = 2  # braces
        if size > remaining:
            return None
        for index, (key, item) in enumerate(value.items()):
            if not isinstance(key, str):
                return None
            key_size = _bounded_json_size(key, remaining - size)
            if key_size is None:
                return None
            item_size = _bounded_json_size(item, remaining - size - key_size - 1)
            if item_size is None:
                return None
            size += key_size + 1 + item_size + (index > 0)
            if size > remaining:
                return None
        return size
    return None


def encode_bounded_json(payload: dict) -> bytes | None:
    """Encode JSON only after a bounded, allocation-free size preflight."""
    if _bounded_json_size(payload, MAX_RESPONSE_BYTES) is None:
        return None
    encoder = json.JSONEncoder(separators=(",", ":"), allow_nan=False, ensure_ascii=False)
    chunks: list[bytes] = []
    size = 0
    for token in encoder.iterencode(payload):
        encoded = token.encode("utf-8")
        if size + len(encoded) > MAX_RESPONSE_BYTES:
            return None
        chunks.append(encoded)
        size += len(encoded)
    return b"".join(chunks)


def encode_response(payload: dict) -> tuple[int, bytes]:
    """Return a bounded body, or a complete explicit oversized rejection."""
    data = encode_bounded_json(payload)
    if data is not None:
        return 200, data
    rejection = json.dumps(
        {"status": "response_too_large", "max_response_bytes": MAX_RESPONSE_BYTES},
        separators=(",", ":"),
    ).encode("utf-8")
    return 413, rejection


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
        if Path(archive_path).is_symlink():
            return 503, {"status": "archive_invalid"}
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
    except sqlite3.DatabaseError:
        return 503, {"status": "archive_invalid"}
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
            try:
                status, payload = read_archive_query(archive_path, self.path)
            except Exception:
                status, payload = 500, {"status": "internal_error"}
            encoded_status, data = encode_response(payload)
            if encoded_status != 200 or status == 200:
                status = encoded_status
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


class LoopbackArchiveServer(ThreadingHTTPServer):
    def server_bind(self):
        if self.server_address[0] != '127.0.0.1':
            raise ValueError('archive adapter must bind to IPv4 loopback')
        super().server_bind()


def serve_archive(archive_path: str, port: int = 4175) -> None:
    """Explicit opt-in operator entrypoint; never starts automatically."""
    with LoopbackArchiveServer(("127.0.0.1", port), make_archive_handler(archive_path)) as server:
        server.serve_forever()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Opt-in loopback read-only Observation archive adapter")
    parser.add_argument("--archive", required=True, help="Existing local SQLite archive path")
    parser.add_argument("--port", type=int, default=4175)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("port must be between 1 and 65535")
    serve_archive(args.archive, args.port)

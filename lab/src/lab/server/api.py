"""All HTTP routes for the unified Symbiont Lab server."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from typing import Any, Callable
from urllib.parse import parse_qs, urlparse

from lab.observation.bus import ObservationBus
from lab.observation.observatory import (
    ObservatorySource,
    observatory_package_root,
    valid_instance_id,
)
from lab.server.sse import CLIENT_ERRORS as _CLIENT_ERRORS
from lab.server.sse import stream_fleet, stream_instance, stream_organism

_STATIC_TYPES: dict[str, str] = {
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".ico": "image/x-icon",
    ".svg": "image/svg+xml",
    ".png": "image/png",
}
_MAX_BODY_BYTES = 32768


def make_handler(
    observation_bus: ObservationBus,
    observatory_dir: Path | None,
    assets_dir: Path,
    *,
    source_status: Callable[[], dict[str, Any]] | None = None,
    body_catalog: Callable[[], list[dict[str, object]]] | None = None,
    organism_catalog: Callable[[], list[dict[str, Any]]] | None = None,
    run_catalog: Callable[[], list[dict[str, Any]]] | None = None,
    development_history_query: Callable[[str, int], dict[str, Any]] | None = None,
    physics_run_starter: Callable[[dict[str, Any]], dict[str, object]] | None = None,
    physics_run_stopper: Callable[[], bool] | None = None,
    organism_alias_setter: Callable[[str, str | None], dict[str, Any]] | None = None,
    causal_provenance_query: Callable[[str, str, int], dict[str, Any] | None] | None = None,
) -> type[BaseHTTPRequestHandler]:
    observatory_source = ObservatorySource(observatory_dir)

    class Handler(BaseHTTPRequestHandler):
        def handle(self) -> None:
            try:
                super().handle()
            except _CLIENT_ERRORS:
                pass

        def log_message(self, fmt: str, *args: object) -> None:
            pass

        def _security_headers(self) -> None:
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header(
                "Content-Security-Policy",
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline'; "
                "connect-src 'self'; "
                "img-src 'self' data:; "
                "font-src 'self'; "
                "object-src 'none'; "
                "base-uri 'none'; "
                "frame-ancestors 'none'",
            )

        def _json(self, status: int, payload: dict[str, Any]) -> None:
            body = json.dumps(payload, separators=(",", ":")).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self._security_headers()
            self.end_headers()
            self.wfile.write(body)

        def _static(self, path: Path) -> None:
            if not path.is_file():
                self._json(404, {"error": "not found"})
                return
            body = path.read_bytes()
            self.send_response(200)
            self.send_header(
                "Content-Type", _STATIC_TYPES.get(path.suffix.lower(), "application/octet-stream")
            )
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-cache")
            self._security_headers()
            self.end_headers()
            self.wfile.write(body)

        def _static_under(self, root: Path, relative: str) -> None:
            resolved_root = root.resolve()
            candidate = (resolved_root / relative).resolve()
            if not candidate.is_relative_to(resolved_root):
                self._json(404, {"error": "not found"})
                return
            self._static(candidate)

        def _body(self) -> dict[str, Any]:
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except (TypeError, ValueError) as exc:
                raise ValueError("invalid Content-Length") from exc
            if length < 0:
                raise ValueError("invalid Content-Length")
            if length > _MAX_BODY_BYTES:
                raise OverflowError("request body exceeds 32768 bytes")
            payload = json.loads(self.rfile.read(length) or b"{}")
            if not isinstance(payload, dict):
                raise ValueError("JSON object required")
            return payload

        def _origin_allowed(self) -> bool:
            origin = self.headers.get("Origin")
            if not origin:
                return True
            parsed = urlparse(origin)
            if parsed.scheme not in {"http", "https"}:
                return False
            if parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
                return False
            return parsed.netloc == (self.headers.get("Host") or "")

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            path = parsed.path

            if path in ("/", "/index.html"):
                self._static(assets_dir / "app.html")
                return
            if path.startswith("/assets/"):
                relative = path[len("/assets/") :]
                # Images live in the web package's assets/ directory while
                # the stylesheet and script bundle lives at its root.
                if relative.startswith("img/"):
                    relative = f"assets/{relative}"
                self._static_under(assets_dir, relative)
                return
            if path.startswith("/observatory/"):
                obs_root = observatory_package_root()
                if obs_root is None:
                    self._json(404, {"error": "not found"})
                    return
                self._static_under(obs_root, path[len("/observatory/") :])
                return

            if path == "/api/state":
                payload: dict[str, Any] = {}
                if source_status is not None:
                    payload["sources"] = source_status()
                self._json(200, payload)
                return
            if path == "/api/world-scene":
                self._json(200, {"scene": observation_bus.world_scene()})
                return
            if path == "/api/organism":
                self._stream_organism()
                return
            if path == "/api/organism/history":
                query = parse_qs(parsed.query, keep_blank_values=False)
                try:
                    limit = int((query.get("limit") or ["256"])[0])
                except ValueError:
                    self._json(400, {"error": "invalid history limit"})
                    return
                if limit < 1 or limit > 512:
                    self._json(400, {"error": "history limit must be between 1 and 512"})
                    return
                frames = observation_bus.recent_materialized("observed_frame", limit=limit)
                items = []
                for frame in frames:
                    items.append(
                        {
                            key: frame[key]
                            for key in (
                                "type",
                                "source",
                                "tick",
                                "organism_id",
                                "instance_id",
                                "run_id",
                                "body_id",
                                "embodiment_id",
                                "topology_revision",
                                "body",
                                "cognition",
                                "vitals",
                                "mind",
                                "provenance",
                            )
                            if key in frame
                        }
                    )
                self._json(200, {"items": items})
                return
            if path == "/api/organism/development-history":
                if development_history_query is None:
                    self._json(503, {"error": "Development history unavailable"})
                    return
                query = parse_qs(parsed.query, keep_blank_values=False)
                organism_id = str((query.get("organism_id") or [""])[0]).strip()
                try:
                    limit = int((query.get("limit") or ["2048"])[0])
                except ValueError:
                    self._json(400, {"error": "invalid development history limit"})
                    return
                if not organism_id or len(organism_id) > 256 or limit < 1 or limit > 2048:
                    self._json(400, {"error": "invalid development history query"})
                    return
                try:
                    payload = development_history_query(organism_id, limit)
                except (OSError, ValueError):
                    # A live telemetry writer can update append-only schema
                    # registries while a history reader is being constructed.
                    # Do not drop the HTTP connection or expose filesystem
                    # details; callers can retry this explicitly unavailable
                    # observer projection.
                    self._json(503, {"error": "development history temporarily unavailable"})
                    return
                self._json(200, payload)
                return
            if path == "/api/provenance/why":
                if causal_provenance_query is None:
                    self._json(503, {"error": "causal provenance unavailable"})
                    return
                query = parse_qs(parsed.query, keep_blank_values=False)
                kind = str((query.get("kind") or [""])[0]).strip()
                ref_id = str((query.get("id") or [""])[0]).strip()
                try:
                    depth = int((query.get("depth") or ["12"])[0])
                except ValueError:
                    self._json(400, {"error": "invalid provenance depth"})
                    return
                if (
                    not kind
                    or not ref_id
                    or len(kind) > 64
                    or len(ref_id) > 512
                    or depth < 1
                    or depth > 24
                ):
                    self._json(400, {"error": "invalid provenance reference"})
                    return
                payload = causal_provenance_query(kind, ref_id, depth)
                if payload is None:
                    self._json(404, {"error": "causal provenance not found"})
                    return
                self._json(200, payload)
                return
            if path == "/api/environments" and body_catalog is not None:
                from environment.physics3d.environments import ENVIRONMENT_NAMES

                self._json(200, {"items": list(ENVIRONMENT_NAMES)})
                return
            if path == "/api/run-definitions" and body_catalog is not None:
                from lab.experience import run_definition_catalog

                self._json(200, {"items": run_definition_catalog()})
                return
            if path == "/api/bodies" and body_catalog is not None:
                self._json(200, {"items": body_catalog()})
                return
            if path == "/api/organisms" and organism_catalog is not None:
                self._json(200, {"items": organism_catalog()})
                return
            if path == "/api/runs" and run_catalog is not None:
                self._json(200, {"items": run_catalog()})
                return

            if path == "/fleet":
                self._stream_fleet()
                return
            if path.startswith("/instances/"):
                instance_id = path[len("/instances/") :]
                if valid_instance_id(instance_id):
                    self._stream_instance(instance_id)
                    return
                self._json(404, {"error": "not found"})
                return
            if path.startswith("/api/instance/") and path.endswith("/manifest"):
                instance_id = path[len("/api/instance/") : -len("/manifest")]
                if observatory_dir and valid_instance_id(instance_id):
                    self._serve_manifest(instance_id)
                    return
                self._json(404, {"error": "not found"})
                return
            if path.startswith("/api/instance/") and path.endswith("/history-summary"):
                instance_id = path[len("/api/instance/") : -len("/history-summary")]
                if observatory_dir and valid_instance_id(instance_id):
                    self._serve_history_summary(instance_id)
                    return
                self._json(404, {"error": "not found"})
                return
            self._json(404, {"error": "not found"})

        def do_POST(self) -> None:  # noqa: N802
            if not self._origin_allowed():
                self._json(403, {"error": "untrusted origin"})
                return
            try:
                payload = self._body()
            except OverflowError as exc:
                self._json(413, {"error": str(exc)})
                return
            except (ValueError, json.JSONDecodeError) as exc:
                self._json(400, {"error": str(exc)})
                return

            path = urlparse(self.path).path
            if path == "/api/runs":
                if physics_run_starter is None:
                    self._json(503, {"error": "Physics3D run service unavailable"})
                    return
                try:
                    started = physics_run_starter(payload)
                except ValueError as exc:
                    self._json(400, {"error": str(exc)})
                    return
                except RuntimeError as exc:
                    self._json(409, {"error": str(exc)})
                    return
                self._json(202, {"started": True, **started})
                return
            if path == "/api/organisms/alias":
                if organism_alias_setter is None:
                    self._json(503, {"error": "organism catalog unavailable"})
                    return
                try:
                    result = organism_alias_setter(
                        str(payload.get("ref") or ""), payload.get("alias")
                    )
                except ValueError as exc:
                    self._json(400, {"error": str(exc)})
                    return
                self._json(200, result)
                return
            if path == "/api/runs/stop":
                if physics_run_stopper is None or not physics_run_stopper():
                    self._json(409, {"error": "no active Physics3D run"})
                    return
                self._json(202, {"stopping": True})
                return
            self._json(404, {"error": "not found"})

        def _stream_organism(self) -> None:
            stream_organism(self, observation_bus)

        def _stream_fleet(self) -> None:
            if not stream_fleet(self, observatory_source):
                self._json(503, {"error": "observatory not configured"})

        def _stream_instance(self, instance_id: str) -> None:
            if not stream_instance(self, observatory_source, instance_id):
                self._json(503, {"error": "observatory not configured"})

        def _serve_manifest(self, instance_id: str) -> None:
            payload = observatory_source.manifest(instance_id)
            if payload is None:
                self._json(404, {"error": "manifest not found"})
                return
            self._json(200, payload)

        def _serve_history_summary(self, instance_id: str) -> None:
            payload = observatory_source.history_summary(instance_id)
            if payload is None:
                self._json(404, {"error": "history summary not found"})
                return
            self._json(200, payload)

    return Handler

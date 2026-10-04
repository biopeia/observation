"""Real-browser regression for observation identity, reconnect and DOM freshness.

The GitHub Ubuntu runner already provides Chrome.  Keeping this test dependency-
free avoids adding a second JavaScript package manager or browser download to the
repository while still exercising native EventSource, ES modules and the real
Mind DOM.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

import pytest

ROOT = Path(__file__).resolve().parents[4]
WEB = ROOT / "lab/src/lab/workbench/web"


def _browser() -> str | None:
    for candidate in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        executable = shutil.which(candidate)
        if executable:
            return executable
    return None


FRAME_A = {
    "type": "observed_frame",
    "source": "physics3d",
    "run_id": "run-a",
    "organism_id": "organism-1",
    "tick": 10,
    "body": {"type": "body", "source": "physics3d", "run_id": "run-a", "tick": 10},
    "cognition": {
        "type": "cognition",
        "source": "physics3d",
        "run_id": "run-a",
        "tick": 10,
        "cognitive_concepts": 3,
        "predictor_count": 7,
    },
    "vitals": {
        "type": "vitals",
        "source": "physics3d",
        "run_id": "run-a",
        "tick": 10,
        "alive": True,
    },
    "mind": {
        "tick": 10,
        "display_id": "organism-1",
        "cognition": {"readouts": {}},
    },
}

FRAME_B = {
    "type": "observed_frame",
    "source": "physics3d",
    "run_id": "run-b",
    "organism_id": "organism-1",
    "tick": 11,
    "body": {"type": "body", "source": "physics3d", "run_id": "run-b", "tick": 11},
    # Counts are intentionally absent. The DOM must show unknown, not 7P from
    # run A and not a fabricated 0P from a non-observed topology.
    "cognition": {
        "type": "cognition",
        "source": "physics3d",
        "run_id": "run-b",
        "tick": 11,
    },
    "vitals": {
        "type": "vitals",
        "source": "physics3d",
        "run_id": "run-b",
        "tick": 11,
        "alive": True,
    },
    "mind": {
        "tick": 11,
        "display_id": "organism-1",
        "cognition": {"readouts": {}},
    },
}


class _Server(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, handler) -> None:
        super().__init__(address, handler)
        self.organism_connections = 0
        self.last_event_ids: list[str | None] = []


class _Handler(BaseHTTPRequestHandler):
    server: _Server

    def log_message(self, _format: str, *_args: object) -> None:
        return

    def _json(self, payload: dict) -> None:
        body = json.dumps(payload, separators=(",", ":")).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _asset(self, relative: str) -> None:
        path = (WEB / relative).resolve()
        if not path.is_relative_to(WEB.resolve()) or not path.is_file():
            self.send_error(404)
            return
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/javascript; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _frame(self, event_id: int, frame: dict) -> None:
        data = json.dumps(frame, separators=(",", ":"))
        # A short retry makes the browser reconnect within the bounded test.
        payload = f"retry: 100\nid: {event_id}\ndata: {data}\n\n".encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(payload)
        self.wfile.flush()

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path.startswith("/assets/"):
            self._asset(parsed.path[len("/assets/") :])
            return

        if parsed.path == "/api/organism/history":
            self._json({"items": []})
            return

        if parsed.path == "/api/state":
            self._json(
                {
                    "sources": {
                        "observatory": {"available": False},
                        "physics3d": {"state": "running", "run_id": "run-b"},
                    }
                }
            )
            return

        if parsed.path == "/api/organism":
            connection = self.server.organism_connections
            self.server.organism_connections += 1
            self.server.last_event_ids.append(self.headers.get("Last-Event-ID"))
            if connection == 0:
                self._frame(1, FRAME_A)
            else:
                self._frame(2, FRAME_B)
            # Closing the response deliberately exercises native EventSource
            # reconnection and Last-Event-ID propagation.
            self.close_connection = True
            return

        if parsed.path == "/":
            body = b"""<!doctype html>
<meta charset="utf-8">
<div id="mind-root"></div>
<div id="result" data-status="pending">pending</div>
<script type="module">
  import { mount } from '/assets/views/mind.js';
  const root = document.getElementById('mind-root');
  mount(root, {sources:{physics3d:{state:'running', run_id:'run-b'}}});
  const result = document.getElementById('result');
  const deadline = performance.now() + 4500;
  const check = () => {
    const cognition = document.getElementById('mind-t-cognition')?.textContent ?? '';
    const tick = document.getElementById('mind-t-tick')?.textContent ?? '';
    if (tick === 't11') {
      const pass = cognition.includes('—C') && cognition.includes('—P') && !cognition.includes('7P');
      result.dataset.status = pass ? 'pass' : 'fail';
      result.textContent = `${tick}|${cognition}`;
      return;
    }
    if (performance.now() >= deadline) {
      result.dataset.status = 'timeout';
      result.textContent = `${tick}|${cognition}`;
      return;
    }
    setTimeout(check, 50);
  };
  setTimeout(check, 50);
</script>
"""
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_error(404)


def test_native_eventsource_reconnect_cannot_mix_runs_in_the_dom() -> None:
    browser = _browser()
    if browser is None:
        pytest.skip("Chrome/Chromium is required for the real-browser Workbench regression")

    server = _Server(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    try:
        result = subprocess.run(
            [
                browser,
                "--headless=new",
                "--disable-gpu",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--virtual-time-budget=6000",
                "--dump-dom",
                f"http://{host}:{port}/",
            ],
            capture_output=True,
            text=True,
            timeout=25,
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2.0)

    assert result.returncode == 0, result.stderr
    assert 'id="result" data-status="pass"' in result.stdout, result.stdout[-4000:]
    assert server.organism_connections >= 2
    # This assertion comes from a real Chromium request, not a simulated
    # EventSource implementation.
    assert "1" in server.last_event_ids[1:]

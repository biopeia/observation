from __future__ import annotations

import json
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.error import HTTPError
from urllib.request import urlopen

import pytest

from lab.observation.bus import ObservationBus
from lab.server.api import make_handler


@pytest.fixture
def serve_api(tmp_path: Path):
    assets = tmp_path / "web"
    (assets / "assets" / "img").mkdir(parents=True)
    (assets / "assets" / "img" / "logo.png").write_bytes(b"png")
    handler = make_handler(
        ObservationBus(),
        None,
        assets,
        development_history_query=lambda _organism, _limit: {},
    )
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


def test_img_asset_route_serves_package_image(serve_api: str) -> None:
    with urlopen(f"{serve_api}/assets/img/logo.png") as response:
        assert response.status == 200
        assert response.read() == b"png"


def test_development_history_reader_error_is_http_503(tmp_path: Path) -> None:
    def fail(_organism: str, _limit: int) -> dict:
        raise ValueError("unknown binary path id: 4932")

    handler = make_handler(ObservationBus(), None, tmp_path, development_history_query=fail)
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        url = f"http://127.0.0.1:{server.server_port}/api/organism/development-history?organism_id=symbiont%3Atest"
        with pytest.raises(HTTPError) as raised:
            urlopen(url)
        assert raised.value.code == 503
        assert json.loads(raised.value.read()) == {
            "error": "development history temporarily unavailable"
        }
    finally:
        server.shutdown()
        thread.join()
        server.server_close()

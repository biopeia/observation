from __future__ import annotations

import time
import threading

from observation import LocalObservationArchiveCapture, ObservationPlane, SQLiteObservationArchive
from test_archive import sample


def wait_until(predicate, timeout: float = 2.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.01)
    assert predicate()


def test_capture_archives_only_subsequent_publications_without_blocking_plane(tmp_path) -> None:
    plane = ObservationPlane()
    plane.publish(sample(step=1))
    capture = LocalObservationArchiveCapture(
        plane, tmp_path / "archive.sqlite", max_payload_bytes=100_000
    )
    capture.start()
    assert capture.status().running

    plane.publish(sample(step=2))
    wait_until(lambda: capture.status().last_plane_sequence == 2)
    capture.stop()

    with SQLiteObservationArchive(tmp_path / "archive.sqlite", max_payload_bytes=100_000) as archive:
        records = archive.query()
    assert [record.observation.domain_time[0].value for record in records] == [2]
    assert records[0].capture_id
    assert records[0].source_sequence == 2


def test_capture_reports_storage_initialization_failure(tmp_path) -> None:
    plane = ObservationPlane()
    capture = LocalObservationArchiveCapture(
        plane, tmp_path / "missing" / "archive.sqlite", max_payload_bytes=100_000
    )
    try:
        capture.start()
    except RuntimeError as exc:
        assert "archive capture failed to initialize" in str(exc)
    else:
        raise AssertionError("missing archive parent must fail explicitly")
    assert capture.status().error is not None


def test_capture_stops_cleanly_and_does_not_retain_plane_subscription(tmp_path) -> None:
    plane = ObservationPlane()
    capture = LocalObservationArchiveCapture(
        plane, tmp_path / "archive.sqlite", max_payload_bytes=100_000
    )
    capture.start()
    assert len(plane._stream_subscribers) == 1
    capture.stop()
    assert len(plane._stream_subscribers) == 0
    assert not capture.status().running


def test_capture_persists_explicit_plane_delivery_gap(tmp_path, monkeypatch) -> None:
    from observation.archive import SQLiteObservationArchive

    plane = ObservationPlane(subscriber_queue_size=1)
    capture = LocalObservationArchiveCapture(
        plane, tmp_path / "archive.sqlite", max_payload_bytes=100_000
    )
    entered_append = threading.Event()
    release_append = threading.Event()
    original_append = SQLiteObservationArchive.append

    def slow_append(archive, observation, **kwargs):
        entered_append.set()
        assert release_append.wait(2)
        return original_append(archive, observation, **kwargs)

    monkeypatch.setattr(SQLiteObservationArchive, "append", slow_append)
    capture.start()
    plane.publish(sample(step=1))
    assert entered_append.wait(2)
    plane.publish(sample(step=2))
    plane.publish(sample(step=3))
    release_append.set()
    wait_until(lambda: capture.status().gap_sequence == 3)
    capture.stop()

    with SQLiteObservationArchive(tmp_path / "archive.sqlite", max_payload_bytes=100_000) as archive:
        status = archive.status()
        assert status.source_gaps == ((2, 3, "consumer_overflow"),)
        gap, = status.source_gap_records
        assert (gap.first_sequence, gap.last_sequence, gap.reason) == (2, 3, "consumer_overflow")
        assert gap.capture_id


def test_capture_stops_and_records_source_gap_when_archive_capacity_is_reached(tmp_path) -> None:
    plane = ObservationPlane()
    capture = LocalObservationArchiveCapture(
        plane, tmp_path / "archive.sqlite", max_payload_bytes=1
    )
    capture.start()

    plane.publish(sample(step=1))
    wait_until(lambda: not capture.status().running)
    status = capture.status()
    assert status.gap_sequence == 1
    assert status.gap_reason == "archive_capacity_reached"
    assert status.error is None
    capture.stop()

    with SQLiteObservationArchive(tmp_path / "archive.sqlite", max_payload_bytes=1) as archive:
        archive_status = archive.status()
    gap, = archive_status.source_gap_records
    assert gap.capture_id
    assert (gap.first_sequence, gap.last_sequence, gap.reason) == (
        1,
        1,
        "archive_capacity_reached",
    )

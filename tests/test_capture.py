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


def test_capture_capacity_gap_includes_queued_publications(tmp_path, monkeypatch) -> None:
    from observation.archive import SQLiteObservationArchive

    plane = ObservationPlane(subscriber_queue_size=3)
    capture = LocalObservationArchiveCapture(
        plane, tmp_path / "archive.sqlite", max_payload_bytes=1
    )
    entered_append = threading.Event()
    release_append = threading.Event()
    original_append = SQLiteObservationArchive.append

    def blocked_append(archive, observation, **kwargs):
        entered_append.set()
        assert release_append.wait(2)
        return original_append(archive, observation, **kwargs)

    monkeypatch.setattr(SQLiteObservationArchive, "append", blocked_append)
    capture.start()

    plane.publish(sample(step=1))
    assert entered_append.wait(2)
    plane.publish(sample(step=2))
    plane.publish(sample(step=3))
    release_append.set()
    wait_until(lambda: not capture.status().running)
    status = capture.status()
    assert status.gap_sequence == 3
    assert status.gap_reason == "archive_capacity_reached"
    assert status.error is None
    capture.stop()

    with SQLiteObservationArchive(tmp_path / "archive.sqlite", max_payload_bytes=1) as archive:
        archive_status = archive.status()
        session, = archive.capture_sessions()
        assert session.status == "failed"
        assert session.terminal_reason == "archive_capacity_reached"
    gap, = archive_status.source_gap_records
    assert gap.capture_id
    assert (gap.first_sequence, gap.last_sequence, gap.reason) == (
        1,
        3,
        "archive_capacity_reached",
    )


def test_capture_session_lifecycle_is_durable_and_does_not_claim_history_complete(tmp_path) -> None:
    path = tmp_path / "archive.sqlite"
    plane = ObservationPlane()
    plane.publish(sample(step=1))
    capture = LocalObservationArchiveCapture(plane, path, max_payload_bytes=100_000)
    capture.start()
    capture_id = capture.capture_id
    plane.publish(sample(step=2))
    wait_until(lambda: capture.status().last_plane_sequence == 2)
    capture.stop()

    with SQLiteObservationArchive(path, max_payload_bytes=100_000) as archive:
        session, = archive.capture_sessions()
        assert session.capture_id == capture_id
        assert session.initial_source_sequence == 1
        assert session.final_source_sequence == 2
        assert session.status == "stopped"
        assert session.terminal_reason is None


def test_interrupted_capture_remains_explicitly_unfinished_after_reopen(tmp_path) -> None:
    path = tmp_path / "archive.sqlite"
    with SQLiteObservationArchive(path, max_payload_bytes=100_000) as archive:
        archive.start_capture_session("capture-test", initial_source_sequence=7)

    # Reopening must not silently turn an unclosed capture into a complete one.
    with SQLiteObservationArchive(path, max_payload_bytes=100_000) as archive:
        session, = archive.capture_sessions()
        assert session.capture_id == "capture-test"
        assert session.initial_source_sequence == 7
        assert session.final_source_sequence is None
        assert session.status == "running"
        assert session.terminal_reason is None


def test_capture_session_terminal_transition_is_one_way(tmp_path) -> None:
    path = tmp_path / "archive.sqlite"
    with SQLiteObservationArchive(path, max_payload_bytes=100_000) as archive:
        archive.start_capture_session("capture-test", initial_source_sequence=0)
        archive.finish_capture_session(
            "capture-test",
            status="failed",
            reason="storage_error",
            final_source_sequence=2,
        )
        try:
            archive.finish_capture_session(
                "capture-test", status="stopped", final_source_sequence=2
            )
        except ValueError as exc:
            assert "already terminal" in str(exc)
        else:
            raise AssertionError("terminal capture status must not be overwritten")
        session, = archive.capture_sessions()
        assert session.status == "failed"
        assert session.final_source_sequence == 2
        assert session.terminal_reason == "storage_error"


def test_capture_final_source_sequence_cannot_precede_initial_watermark(tmp_path) -> None:
    path = tmp_path / "archive.sqlite"
    with SQLiteObservationArchive(path, max_payload_bytes=100_000) as archive:
        archive.start_capture_session("capture-test", initial_source_sequence=5)
        try:
            archive.finish_capture_session(
                "capture-test", final_source_sequence=4
            )
        except ValueError as exc:
            assert "cannot precede" in str(exc)
        else:
            raise AssertionError("final watermark cannot precede initial watermark")
        session, = archive.capture_sessions()
        assert session.status == "running"
        assert session.final_source_sequence is None

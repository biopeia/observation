from __future__ import annotations

import time
import threading
import subprocess
import sys
from pathlib import Path

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
        coverage = archive.capture_coverage(capture.capture_id)
        assert coverage.status == "closed_verified_with_persisted_loss"
        assert coverage.received_not_persisted == ((1, 3, "archive_capacity_reached"),)
        assert not coverage.complete
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
        coverage = archive.capture_coverage(capture_id)
        assert coverage.status == "closed_verified"
        assert coverage.closure_verified is True
        assert coverage.complete is True
        assert coverage.persisted_sequences == (2,)


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
        coverage = archive.capture_coverage("capture-test")
        assert coverage.status == "open_unverified"
        assert coverage.closure_verified is False
        assert coverage.complete is False
        assert coverage.unverifiable_intervals == ((8, None),)


def test_process_interruption_recovers_only_as_open_unverified(tmp_path) -> None:
    path = tmp_path / "archive.sqlite"
    code = """
import os, sys
sys.path.insert(0, sys.argv[2])
from observation import SQLiteObservationArchive
from test_archive import sample
archive = SQLiteObservationArchive(sys.argv[1], max_payload_bytes=100000)
archive.start_capture_session('crash-capture', initial_source_sequence=4)
archive.append(sample(step=5), capture_id='crash-capture', source_sequence=5)
os._exit(23)
"""
    result = subprocess.run(
        [sys.executable, "-c", code, str(path), str(Path(__file__).parent.resolve())],
        check=False,
    )
    assert result.returncode == 23
    with SQLiteObservationArchive(path, max_payload_bytes=100_000) as archive:
        session, = archive.capture_sessions()
        assert session.status == "running"
        assert session.final_source_sequence is None
        coverage = archive.capture_coverage("crash-capture")
        assert coverage.persisted_sequences == (5,)
        assert coverage.status == "open_unverified"
        assert coverage.unverifiable_intervals == ((6, None),)
        assert not coverage.complete


def test_sqlite_rolls_back_uncommitted_tail_after_process_interruption(tmp_path) -> None:
    path = tmp_path / "archive.sqlite"
    code = """
import os, sys
from observation import SQLiteObservationArchive
archive = SQLiteObservationArchive(sys.argv[1], max_payload_bytes=100000)
archive.start_capture_session('rollback-capture', initial_source_sequence=9)
archive._db.execute('BEGIN IMMEDIATE')
archive._db.execute("UPDATE archive_capture_sessions SET status='stopped', final_source_sequence=10 WHERE capture_id='rollback-capture'")
os._exit(24)
"""
    result = subprocess.run([sys.executable, "-c", code, str(path)], check=False)
    assert result.returncode == 24
    with SQLiteObservationArchive(path, max_payload_bytes=100_000) as archive:
        session, = archive.capture_sessions()
        assert session.status == "running"
        assert session.final_source_sequence is None
        coverage = archive.capture_coverage("rollback-capture")
        assert coverage.status == "open_unverified"
        assert coverage.unverifiable_intervals == ((10, None),)


def test_append_write_error_is_persisted_as_received_loss_not_success(tmp_path, monkeypatch) -> None:
    import sqlite3
    from observation.archive import SQLiteObservationArchive

    plane = ObservationPlane()
    capture = LocalObservationArchiveCapture(plane, tmp_path / "archive.sqlite", max_payload_bytes=100_000)
    original = SQLiteObservationArchive.append

    def fail_once(archive, observation, **kwargs):
        raise sqlite3.OperationalError("injected write failure")

    monkeypatch.setattr(SQLiteObservationArchive, "append", fail_once)
    capture.start()
    plane.publish(sample(step=1))
    wait_until(lambda: not capture.status().running)
    runtime = capture.status()
    assert runtime.last_plane_sequence == 1
    assert runtime.last_persisted_sequence is None
    assert runtime.gap_reason == "archive_write_failed"
    capture.stop()
    monkeypatch.setattr(SQLiteObservationArchive, "append", original)

    with SQLiteObservationArchive(tmp_path / "archive.sqlite", max_payload_bytes=100_000) as archive:
        session, = archive.capture_sessions()
        coverage = archive.capture_coverage(capture.capture_id)
        assert session.status == "failed"
        assert coverage.persisted_sequences == ()
        assert coverage.received_not_persisted == ((1, 1, "archive_write_failed"),)
        assert coverage.closure_verified is True
        assert coverage.complete is False


def test_failed_loss_marker_keeps_capture_open_and_unverifiable(tmp_path, monkeypatch) -> None:
    import sqlite3
    from observation.archive import SQLiteObservationArchive

    plane = ObservationPlane()
    capture = LocalObservationArchiveCapture(plane, tmp_path / "archive.sqlite", max_payload_bytes=100_000)

    def fail_append(archive, observation, **kwargs):
        raise sqlite3.OperationalError("injected append failure")

    def fail_gap(archive, *args, **kwargs):
        raise sqlite3.OperationalError("injected full-disk marker failure")

    monkeypatch.setattr(SQLiteObservationArchive, "append", fail_append)
    monkeypatch.setattr(SQLiteObservationArchive, "record_source_gap", fail_gap)
    capture.start()
    plane.publish(sample(step=1))
    wait_until(lambda: not capture.status().running)
    assert "loss marker failed" in capture.status().error

    with SQLiteObservationArchive(tmp_path / "archive.sqlite", max_payload_bytes=100_000) as archive:
        session, = archive.capture_sessions()
        assert session.status == "running"
        assert session.final_source_sequence is None
        coverage = archive.capture_coverage(capture.capture_id)
        assert coverage.status == "open_unverified"
        assert coverage.unverifiable_intervals == ((1, None),)
        assert not coverage.complete


def test_failed_rebase_marker_cannot_close_a_complete_prefix(tmp_path, monkeypatch) -> None:
    import sqlite3
    from observation.archive import SQLiteObservationArchive

    plane = ObservationPlane(subscriber_queue_size=1)
    capture = LocalObservationArchiveCapture(
        plane, tmp_path / "archive.sqlite", max_payload_bytes=100_000
    )
    entered_append = threading.Event()
    release_append = threading.Event()
    original_append = SQLiteObservationArchive.append

    def block_first_append(archive, observation, **kwargs):
        if not entered_append.is_set():
            entered_append.set()
            assert release_append.wait(2)
        return original_append(archive, observation, **kwargs)

    def fail_gap(archive, *args, **kwargs):
        raise sqlite3.OperationalError("injected gap marker failure")

    monkeypatch.setattr(SQLiteObservationArchive, "append", block_first_append)
    monkeypatch.setattr(SQLiteObservationArchive, "record_source_gap", fail_gap)
    capture.start()
    plane.publish(sample(step=1))
    assert entered_append.wait(2)
    plane.publish(sample(step=2))
    plane.publish(sample(step=3))
    release_append.set()
    wait_until(lambda: not capture.status().running)

    with SQLiteObservationArchive(tmp_path / "archive.sqlite", max_payload_bytes=100_000) as archive:
        session, = archive.capture_sessions()
        coverage = archive.capture_coverage(capture.capture_id)
        assert session.status == "running"
        assert session.final_source_sequence is None
        assert coverage.persisted_sequences == (1,)
        assert coverage.status == "open_unverified"
        assert not coverage.complete


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

"""Opt-in, bounded, non-blocking capture from an authorized ObservationPlane.

The capture worker archives only messages already accepted by the plane. It
does not participate in publication success, causal commits, or Lab evidence
custody. Queue overflow is surfaced as a gap marker; it is never represented as
complete history.
"""

from __future__ import annotations

import queue
import sqlite3
import threading
import uuid
from dataclasses import dataclass
from pathlib import Path

from .archive import ArchiveCapacityReached, ArchiveError, SQLiteObservationArchive
from .plane import ObservationPlane, PlaneMessage, PlaneRebaseRequired


@dataclass(frozen=True, slots=True)
class ArchiveCaptureStatus:
    running: bool
    last_plane_sequence: int | None
    last_persisted_sequence: int | None
    gap_sequence: int | None
    gap_reason: str | None
    error: str | None


class LocalObservationArchiveCapture:
    """Capture subsequent plane publications on a private worker thread.

    Capture is opt-in and begins at the plane's current sequence watermark;
    it does not bootstrap the materialized current view as if it were history.
    Any replay/queue loss is exposed in status. The worker owns its SQLite
    connection and closes it on exit. Call :meth:`stop` before opening the same
    database for queries.
    """

    def __init__(
        self,
        plane: ObservationPlane,
        path: str | Path,
        *,
        max_payload_bytes: int,
    ) -> None:
        self._plane = plane
        self._path = Path(path)
        self._max_payload_bytes = max_payload_bytes
        # Scopes source delivery sequence numbers to this capture instance.
        # It does not identify a World run, publication, or causal cut.
        self._capture_id = str(uuid.uuid4())
        self._subscription = None
        self._thread: threading.Thread | None = None
        self._ready = threading.Event()
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._last_plane_sequence: int | None = None
        self._last_persisted_sequence: int | None = None
        self._gap_sequence: int | None = None
        self._gap_reason: str | None = None
        self._error: str | None = None

    @property
    def capture_id(self) -> str:
        """Local capture-instance identity, not a World/run/cut identifier."""
        return self._capture_id

    def start(self, *, ready_timeout: float = 5.0) -> None:
        if self._thread is not None:
            raise RuntimeError("archive capture can only be started once")
        # Starting from a watermark explicitly avoids treating the plane's
        # latest-value materialization as complete event history. If bounded
        # replay cannot bridge a race, open_stream emits a rebase marker.
        watermark = self._plane.latest_sequence
        with self._lock:
            self._last_plane_sequence = watermark
        self._subscription = self._plane.open_stream(after_sequence=watermark)
        self._thread = threading.Thread(target=self._run, name="observation-archive-capture", daemon=True)
        self._thread.start()
        if not self._ready.wait(ready_timeout):
            self.stop()
            raise TimeoutError("archive capture worker did not become ready")
        with self._lock:
            error = self._error
        if error is not None:
            self.stop()
            raise RuntimeError(f"archive capture failed to initialize: {error}")

    def _run(self) -> None:
        assert self._subscription is not None
        session_started = False
        terminal_status = "stopped"
        terminal_reason = None
        persist_terminal = True
        try:
            with SQLiteObservationArchive(self._path, max_payload_bytes=self._max_payload_bytes) as archive:
                with self._lock:
                    initial_sequence = self._last_plane_sequence
                if initial_sequence is None:
                    initial_sequence = 0
                archive.start_capture_session(
                    self._capture_id, initial_source_sequence=initial_sequence
                )
                session_started = True
                self._ready.set()
                while True:
                    try:
                        item = self._subscription.queue.get(timeout=0.05)
                    except queue.Empty:
                        if self._stop.is_set():
                            break
                        continue
                    if isinstance(item, PlaneRebaseRequired):
                        with self._lock:
                            first_missing = (self._last_plane_sequence or 0) + 1
                        if first_missing <= item.sequence:
                            try:
                                archive.record_source_gap(
                                    first_missing, item.sequence, item.reason,
                                    capture_id=self._capture_id,
                                )
                            except (sqlite3.Error, OSError) as exc:
                                # The worker knows the source stream rebased,
                                # but cannot durably record the missing range.
                                # Do not persist a terminal watermark that
                                # would make the preceding prefix look complete.
                                persist_terminal = False
                                with self._lock:
                                    self._error = (
                                        f"source gap persistence failed: {type(exc).__name__}: {exc}"
                                    )
                                terminal_status = "failed"
                                terminal_reason = "source_gap_unverifiable"
                                break
                        with self._lock:
                            self._gap_sequence = item.sequence
                            self._gap_reason = item.reason
                            self._last_plane_sequence = item.sequence
                        continue
                    if not isinstance(item, PlaneMessage):
                        raise TypeError("unexpected ObservationPlane stream item")
                    with self._lock:
                        self._last_plane_sequence = item.sequence
                    try:
                        archive.append(
                            item.observation,
                            capture_id=self._capture_id,
                            source_sequence=item.sequence,
                        )
                        with self._lock:
                            self._last_persisted_sequence = item.sequence
                    except ArchiveCapacityReached:
                        # Capacity loss is a source-delivery gap for this
                        # capture. Stop accepting publications first, then
                        # account for messages already queued behind the
                        # failed append. Closing under the plane lock prevents
                        # a concurrent publisher from extending the queue
                        # after the watermark is measured.
                        reason = "archive_capacity_reached"
                        self._plane.close_stream(self._subscription)
                        last_lost_sequence = item.sequence
                        while True:
                            try:
                                queued = self._subscription.queue.get_nowait()
                            except queue.Empty:
                                break
                            if isinstance(queued, (PlaneMessage, PlaneRebaseRequired)):
                                last_lost_sequence = max(last_lost_sequence, queued.sequence)
                        try:
                            archive.record_source_gap(
                                item.sequence,
                                last_lost_sequence,
                                reason,
                                capture_id=self._capture_id,
                            )
                        except Exception as gap_exc:
                            # Capacity proves the current publication was not
                            # retained. If the capture-scoped loss marker also
                            # cannot be committed, do not write a terminal
                            # watermark: after restart the durable session must
                            # remain open/unverifiable rather than looking
                            # closed at a truncated boundary.
                            persist_terminal = False
                            with self._lock:
                                self._last_plane_sequence = last_lost_sequence
                                self._gap_sequence = last_lost_sequence
                                self._gap_reason = reason
                                self._error = (
                                    f"archive capacity reached; loss marker failed: "
                                    f"{type(gap_exc).__name__}: {gap_exc}"
                                )
                            terminal_status = "failed"
                            terminal_reason = "archive_capacity_gap_unverifiable"
                            break
                        with self._lock:
                            self._last_plane_sequence = last_lost_sequence
                            self._gap_sequence = last_lost_sequence
                            self._gap_reason = reason
                        terminal_status = "failed"
                        terminal_reason = reason
                        break
                    except (sqlite3.Error, OSError) as exc:
                        # A publication was received, but append did not
                        # return success. Record the loss only if the archive
                        # can durably commit its explicit marker. Otherwise
                        # leave the session running on disk: the attempted
                        # terminal watermark would hide an unverifiable tail.
                        reason = "archive_write_failed"
                        self._plane.close_stream(self._subscription)
                        last_lost_sequence = item.sequence
                        while True:
                            try:
                                queued = self._subscription.queue.get_nowait()
                            except queue.Empty:
                                break
                            if isinstance(queued, (PlaneMessage, PlaneRebaseRequired)):
                                last_lost_sequence = max(last_lost_sequence, queued.sequence)
                        try:
                            archive.record_source_gap(
                                item.sequence, last_lost_sequence, reason,
                                capture_id=self._capture_id,
                            )
                        except Exception as gap_exc:
                            persist_terminal = False
                            with self._lock:
                                self._error = (
                                    f"archive append failed: {type(exc).__name__}: {exc}; "
                                    f"loss marker failed: {type(gap_exc).__name__}: {gap_exc}"
                                )
                            terminal_status = "failed"
                            terminal_reason = "archive_write_failed_unverifiable"
                            break
                        with self._lock:
                            self._last_plane_sequence = last_lost_sequence
                            self._gap_sequence = last_lost_sequence
                            self._gap_reason = reason
                            self._error = f"{type(exc).__name__}: {exc}"
                        terminal_status = "failed"
                        terminal_reason = reason
                        break
                if terminal_status == "stopped" and self._error is not None:
                    terminal_status = "failed"
                    terminal_reason = self._error
        except Exception as exc:
            with self._lock:
                self._error = f"{type(exc).__name__}: {exc}"
            terminal_status = "failed"
            terminal_reason = self._error
        finally:
            self._ready.set()
            # The context manager has closed SQLite; reopen only to persist the
            # terminal state. If this write fails, the durable `running` state
            # remains an honest signal that lifecycle completion is unknown.
            if session_started and persist_terminal:
                try:
                    with SQLiteObservationArchive(
                        self._path, max_payload_bytes=self._max_payload_bytes
                    ) as archive:
                        with self._lock:
                            final_source_sequence = self._last_plane_sequence
                        if final_source_sequence is None:
                            final_source_sequence = initial_sequence
                        archive.finish_capture_session(
                            self._capture_id,
                            status=terminal_status,
                            reason=terminal_reason,
                            final_source_sequence=final_source_sequence,
                        )
                except Exception as exc:
                    with self._lock:
                        self._error = f"capture lifecycle persistence failed: {type(exc).__name__}: {exc}"
            if self._subscription is not None:
                self._plane.close_stream(self._subscription)

    def status(self) -> ArchiveCaptureStatus:
        with self._lock:
            return ArchiveCaptureStatus(
                # Include stopping/draining/persisting in the active lifecycle;
                # a stop request is not proof that the worker has finished.
                running=self._thread is not None and self._thread.is_alive(),
                last_plane_sequence=self._last_plane_sequence,
                last_persisted_sequence=self._last_persisted_sequence,
                gap_sequence=self._gap_sequence,
                gap_reason=self._gap_reason,
                error=self._error,
            )

    def stop(self, *, timeout: float = 5.0) -> None:
        if self._thread is None:
            return
        self._stop.set()
        if self._subscription is not None:
            self._plane.close_stream(self._subscription)
        self._thread.join(timeout)
        if self._thread.is_alive():
            raise TimeoutError("archive capture worker did not stop")

    def __enter__(self) -> LocalObservationArchiveCapture:
        self.start()
        return self

    def __exit__(self, *_: object) -> None:
        self.stop()


__all__ = ["ArchiveCaptureStatus", "LocalObservationArchiveCapture"]

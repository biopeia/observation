"""Opt-in, bounded, non-blocking capture from an authorized ObservationPlane.

The capture worker archives only messages already accepted by the plane. It
does not participate in publication success, causal commits, or Lab evidence
custody. Queue overflow is surfaced as a gap marker; it is never represented as
complete history.
"""

from __future__ import annotations

import queue
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
        self._gap_sequence: int | None = None
        self._gap_reason: str | None = None
        self._error: str | None = None

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
        try:
            with SQLiteObservationArchive(self._path, max_payload_bytes=self._max_payload_bytes) as archive:
                self._ready.set()
                while True:
                    try:
                        item = self._subscription.queue.get(timeout=0.05)
                    except queue.Empty:
                        if self._stop.is_set():
                            return
                        continue
                    if isinstance(item, PlaneRebaseRequired):
                        with self._lock:
                            first_missing = (self._last_plane_sequence or 0) + 1
                        if first_missing <= item.sequence:
                            archive.record_source_gap(
                                first_missing, item.sequence, item.reason, capture_id=self._capture_id
                            )
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
                    except ArchiveCapacityReached:
                        # Capacity loss is a source-delivery gap for this
                        # capture. Persist it in the capture's sequence space,
                        # expose it to the caller, and stop rather than drain
                        # and discard every later publication silently.
                        reason = "archive_capacity_reached"
                        archive.record_source_gap(
                            item.sequence,
                            item.sequence,
                            reason,
                            capture_id=self._capture_id,
                        )
                        with self._lock:
                            self._gap_sequence = item.sequence
                            self._gap_reason = reason
                        return
        except Exception as exc:
            with self._lock:
                self._error = f"{type(exc).__name__}: {exc}"
        finally:
            self._ready.set()
            if self._subscription is not None:
                self._plane.close_stream(self._subscription)

    def status(self) -> ArchiveCaptureStatus:
        with self._lock:
            return ArchiveCaptureStatus(
                running=self._thread is not None and self._thread.is_alive() and not self._stop.is_set(),
                last_plane_sequence=self._last_plane_sequence,
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

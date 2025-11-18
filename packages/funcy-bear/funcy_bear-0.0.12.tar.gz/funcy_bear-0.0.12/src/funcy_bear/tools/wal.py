"""A WAL( Write-Ahead Log) data structure implementation."""

from __future__ import annotations

from enum import StrEnum
import queue
from queue import Queue
from threading import Event, RLock, Thread
import time
from typing import TYPE_CHECKING, Any, Protocol, Self

from funcy_bear.files.jsonl.file_handler import JSONLFilehandler
from funcy_bear.files.text.file_handler import TextFileHandler
from funcy_bear.sentinels import EXIT_SIGNAL
from lazy_bear import LazyLoader

from .autosort_list import AutoSort

if TYPE_CHECKING:
    from collections.abc import Callable
    from contextlib import suppress
    from pathlib import Path
else:
    suppress = LazyLoader("contextlib").to("suppress")

_buffer_lock = RLock()


class Operation(StrEnum):
    """Enumeration of WAL operations."""

    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    COMMIT = "COMMIT"


class WALFlushMode(StrEnum):
    """WAL flush strategies."""

    IMMEDIATE = "immediate"
    BUFFERED = "buffered"


class GenericRecord(Protocol):
    """A generic record in the Write-Ahead Log."""

    txid: int
    op: Operation
    data: dict[str, Any] | None
    timestamp: Any | None

    def model_dump_json(self, exclude_none: bool = True) -> str:
        """Serialize the record to JSON string."""
        ...

    def create(*args, **kwargs) -> Self:
        """Factory method to create a new record instance."""
        ...


class WALConfig(Protocol):
    """Configuration for Write-Ahead Logging behavior.

    This controls the trade-off between safety and performance:
    - IMMEDIATE mode: Maximum safety, slower (good for low volume)
    - BUFFERED mode: Better performance, small crash window (good for high volume)
    """

    flush_mode: WALFlushMode
    auto_checkpoint: bool
    checkpoint_threshold: int
    flush_interval: float
    flush_batch_size: int
    on_flush_error: Callable[[Exception], None] | None

    def __init__(
        self,
        flush_mode: WALFlushMode = WALFlushMode.BUFFERED,
        auto_checkpoint: bool = True,
        checkpoint_threshold: int = 1000,
        flush_interval: float = 1.0,
        flush_batch_size: int = 100,
        on_flush_error: Callable[[Exception], None] | None = None,
    ) -> None:
        """Initialize WAL configuration."""
        ...

    @classmethod
    def validate_flush_mode(cls, v: str | WALFlushMode) -> WALFlushMode:
        """Validate and convert flush mode."""
        if isinstance(v, str):
            return WALFlushMode(v.lower())
        return v

    @classmethod
    def validate_flush_interval(cls, v: float) -> float:
        """Validate flush interval."""
        min_interval: float = 0.05
        max_interval: float = 60.0
        if not (min_interval <= v <= max_interval):
            raise ValueError("flush_interval must be between 0.05 and 60.0 seconds")
        return v

    @classmethod
    def validate_checkpoint_threshold(cls, v: int) -> int:
        """Validate checkpoint threshold."""
        min_threshold: int = 1
        max_threshold: int = 1000000
        if not (min_threshold <= v <= max_threshold):
            raise ValueError("checkpoint_threshold must be between 1 and 1000000")
        return v

    @classmethod
    def validate_flush_batch_size(cls, v: int) -> int:
        """Validate flush batch size."""
        min_size: int = 1
        max_size: int = 10000
        if not (min_size <= v <= max_size):
            raise ValueError("flush_batch_size must be between 1 and 10000")
        return v

    @classmethod
    def immediate(cls) -> WALConfig:
        """Preset for maximum safety (low volume workloads).

        Every write is immediately flushed to disk with fsync.
        Best for: Critical data, low volume, need maximum crash protection.
        """
        return cls(flush_mode=WALFlushMode.IMMEDIATE)

    @classmethod
    def buffered(
        cls,
        flush_interval: float = 0.1,
        flush_batch_size: int = 100,
    ) -> WALConfig:
        """Preset for balanced performance (high volume workloads).

        Batches writes in memory and flushes periodically.
        Best for: Bulk inserts, high volume, acceptable small crash window.

        Args:
            flush_interval: Seconds between flushes (default: 0.1 = 100ms)
            flush_batch_size: Operations before flush (default: 100)
        """
        return cls(
            flush_mode=WALFlushMode.BUFFERED,
            flush_interval=flush_interval,
            flush_batch_size=flush_batch_size,
        )

    @classmethod
    def high_throughput(cls) -> WALConfig:
        """Preset for maximum throughput (bulk operations).

        Aggressive batching for fastest writes.
        Best for: Data imports, batch processing, can tolerate crash window.
        """
        return cls(
            flush_mode=WALFlushMode.BUFFERED,
            flush_interval=1.0,  # Flush every second
            flush_batch_size=1000,  # Or every 1000 ops
        )

    def on_error(self, e: Exception) -> None:
        """Invoke the error callback if set.

        Args:
            e: The exception that occurred
        """
        if self.on_flush_error and callable(self.on_flush_error):
            self.on_flush_error(e)

    def model_copy(self) -> Self:
        """Create a shallow copy of the config."""
        raise NotImplementedError


class WriteAheadLog[T = GenericRecord]:
    """A simple Write-Ahead Log (WAL) implementation with configurable flush strategies."""

    record_type: type[T]

    def __init__(self, file: str | Path, record_t: type[T], config: WALConfig | None = None) -> None:
        """Initialize the Write-Ahead Log.

        Args:
            file: Path to WAL file
            record_t: Record class factory
            config: WAL configuration (uses buffered defaults if None)
        """
        self._log_queue: Queue[T] = Queue[T]()
        self._writer: TextFileHandler = TextFileHandler(file, touch=True)
        self._reader: JSONLFilehandler[dict] = JSONLFilehandler(file)
        self._thread: Thread | None = None
        self._flush_thread: Thread | None = None
        self._running: bool = False
        self._stop_event: Event = Event()
        self.record_type = record_t
        self.config: WALConfig = config or WALConfig.buffered()
        self._op_count: int = 0
        self._buffer: list[str] = []

    def commit(self, txid: int) -> bool:
        """Log a COMMIT operation to the WAL.

        Args:
            txid: The transaction ID to commit

        Returns:
            True if the commit operation was successfully logged
        """
        record_type: GenericRecord = self.record_type  # pyright: ignore[reportAssignmentType]
        try:
            self._log_queue.put(record_type.create(txid=txid, op=Operation.COMMIT))  # pyright: ignore[reportArgumentType]
            return True
        except Exception:
            return False

    def add_op(self, txid: int, op: Operation | str, data: dict[str, Any]) -> bool:
        """Log an operation to the WAL.

        Args:
            txid: The transaction ID
            op: The operation to log (Operation enum or string)
            data: The data associated with the operation

        Returns:
            True if the operation was successfully logged
        """
        record_type: GenericRecord = self.record_type  # pyright: ignore[reportAssignmentType]
        try:
            if isinstance(op, str):
                op = Operation(op)
            record: T = record_type.create(txid=txid, op=op, data=data)  # pyright: ignore[reportAssignmentType]
            self._log_queue.put(record)
            return True
        except ValueError as e:
            raise ValueError(f"Invalid operation '{op}': {e}") from e

    def _write(self, record: GenericRecord) -> None:
        """Write a single WAL record to the file.

        Behavior depends on flush_mode:
        - IMMEDIATE: fsync after every write (slow, maximum safety)
        - BUFFERED: batch in memory, flush periodically (fast, small crash window)

        Args:
            record: The WALRecord to write
        """
        with _buffer_lock:
            try:
                serialized: str = record.model_dump_json(exclude_none=True)
                if self.config.flush_mode == WALFlushMode.IMMEDIATE:
                    self._writer.append(serialized, force=True)  # flush to disk immediately
                elif self.config.flush_mode == WALFlushMode.BUFFERED:
                    # TODO(bear): Consider adding memory limit in addition to batch size.
                    # In high-throughput scenarios with large records, the buffer could
                    # consume significant memory before hitting batch_size threshold.
                    # Could track buffer size in bytes and flush when exceeding limit.
                    self._buffer.append(serialized)
                    self._op_count += 1

                    if self._op_count >= self.config.flush_batch_size:  # Flush if batch size reached
                        self._flush_buffer()

            except Exception as e:
                raise OSError(f"Failed to write WAL record {record}: {e}") from e

    def _flush_buffer(self) -> None:
        """Flush buffered WAL records to disk."""
        if not self._buffer:
            return
        with _buffer_lock:
            try:
                for line in self._buffer:
                    self._writer.append(line, force=False)
                self._writer.flush()  # Single fsync for entire batch
                self._buffer.clear()
                self._op_count = 0
            except Exception as e:
                raise OSError(f"Failed to flush WAL buffer: {e}") from e

    def read_all(self, sort_key: Callable[[dict], Any] | None = None) -> AutoSort[dict]:
        """Read all WAL records from the file.

        Basically this would be used during recovery to replay the log.

        Args:
            sort_key: Optional callable to sort records (default: by timestamp, txid)

        Returns:
            A list of WALRecord objects read from the file
        """

        def _default_key(r: dict) -> tuple[int, ...]:
            """Default sort key: (timestamp, txid)."""
            return r.get("timestamp", 0), r.get("txid", 0)

        records: AutoSort[dict] = AutoSort(key=sort_key or _default_key)
        try:
            records.extend(self._reader.readlines())
            return records
        except Exception as e:
            raise OSError(f"Failed to read WAL records: {e}") from e

    def _loop(self) -> None:
        """Write log records to the file."""
        q: Queue = self._log_queue
        has_task_done: bool = hasattr(q, "task_done")
        while True:
            try:
                record: T = q.get()
                if record is EXIT_SIGNAL:
                    self._flush_buffer()
                    if has_task_done:
                        q.task_done()
                    break
                self._write(record)  # pyright: ignore[reportArgumentType]
                if has_task_done:
                    q.task_done()
            except queue.Empty:
                continue

    def _flush_loop(self) -> None:
        """Periodically flush WAL buffer in BUFFERED mode."""
        if self.config.flush_mode != WALFlushMode.BUFFERED:
            return

        while not self._stop_event.is_set():  # Wait for flush_interval or stop signal
            if self._stop_event.wait(timeout=self.config.flush_interval):
                break  # Stop event set, exit

            if self._buffer:
                # TODO(bear): Improve error handling - log errors, implement retry logic,
                # or expose flush failures through a callback/event system
                with suppress(Exception):
                    self._flush_buffer()

    def start(self) -> None:
        """Start the WAL logging threads."""
        if self._thread is not None and self._thread.is_alive():
            raise RuntimeError("WAL listener already started")

        self._stop_event.clear()
        self._running = True

        self._thread = t = Thread(target=self._loop)
        t.daemon = True
        t.start()

        if self.config.flush_mode == WALFlushMode.BUFFERED:
            self._flush_thread = ft = Thread(target=self._flush_loop)
            ft.daemon = True
            ft.start()

    def stop(self) -> None:
        """Stop the WAL threads and flush remaining buffer."""
        self._stop_event.set()
        self._running = False

        if self._flush_thread is not None:
            self._flush_thread.join(timeout=1.0)
            self._flush_thread = None

        if self._thread is not None:
            self.enqueue_sentinel()
            self._thread.join()
            self._thread = None

    def clear(self) -> None:
        """Clear the WAL file.

        This should happen after it is confirmed that all operations are committed.
        """
        self._writer.clear()

    def enqueue_sentinel(self) -> None:
        """Enqueue a sentinel object to stop thread."""
        self._log_queue.put(EXIT_SIGNAL)  # pyright: ignore[reportArgumentType]

    def wait_for_idle(self, timeout: float = 5.0, flush_buffer: bool = True) -> bool:
        """Wait for all queued operations to be processed.

        Useful for testing to ensure WAL operations are flushed to disk
        before checking file contents.

        Args:
            timeout: Maximum time to wait in seconds (default: 5.0)
            flush_buffer: If True, also flush buffer in BUFFERED mode (default: True)

        Returns:
            True if queue became empty within timeout, False otherwise
        """
        start_time: float = time.time()
        while not self._log_queue.empty():
            if time.time() - start_time > timeout:
                return False
            time.sleep(0.001)  # avoid busy waiting

        if flush_buffer and self.config.flush_mode == WALFlushMode.BUFFERED:
            self._flush_buffer()  # In BUFFERED mode, also flush any pending buffer

        time.sleep(0.01)  # tiny bit more time for final disk sync
        return True

    def __enter__(self) -> Self:
        """Enter the context manager."""
        self.start()
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        """Exit the context manager."""
        self.stop()

"""
RTD Server Protocol Client using ZeroMQ
Supports sending commands to xllify RTD server via ZeroMQ DEALER socket
"""

from typing import Union, List, Callable, Optional, Any
from dataclasses import dataclass
from enum import Enum
import threading
import logging
import atexit

logger = logging.getLogger(__name__)

try:
    import zmq
except ImportError:
    raise ImportError("This module requires pyzmq. Install with: pip install pyzmq")


# Type aliases matching C++ implementation
# C++: using CellValue = std::variant<double, bool, std::wstring>;
CellValue = Union[float, bool, str, None]
"""A single Excel cell value: float, bool, str, or None (displays as empty cell)"""

# C++: using Matrix = std::vector<std::vector<CellValue>>;
Matrix = List[List[CellValue]]
"""A 2D array/matrix of cell values for Excel ranges (cells can be float, bool, str, or None)"""

# Type hint for values that can be sent to Excel
# Note: We use Any for DataFrame to avoid requiring pandas as a dependency
ExcelValue = Union[CellValue, Matrix, Any]
"""
Any value that can be returned to Excel:
- CellValue: Single cell (float, bool, str)
- Matrix: 2D array/range
- pandas.DataFrame: Automatically converted to Matrix with headers (optional dependency)
"""


class RTDCommand(Enum):
    """RTD protocol commands"""

    UPDATE = "U"
    COMPLETE = "C"
    DIRTY = "D"
    DIRTY_COMPLETE = "DC"
    BULK = "B"
    BULK_COMPLETE = "BC"
    PING = "PING"
    EVICTALL = "EVICTALL"


@dataclass
class TopicUpdate:
    """Single topic update for bulk operations"""

    topic: Union[str, int]  # Topic name or ID
    value: Union[str, float, int]


def _dataframe_to_matrix(df) -> Matrix:
    """
    Convert pandas DataFrame to Matrix format with column headers.

    Args:
        df: pandas DataFrame to convert

    Returns:
        Matrix with first row as column headers, subsequent rows as data

    Note:
        - NaN/None values are converted to empty strings
        - Numeric types (int, float) are converted to float
        - Boolean values are preserved
        - All other types are converted to strings
        - DataFrame index is ignored
    """
    # Import pandas locally (optional dependency)
    try:
        import pandas as pd
        import numpy as np
    except ImportError:
        raise ImportError(
            "pandas is required to serialize DataFrames. Install with: pip install pandas"
        )

    # Start with column headers
    headers: List[CellValue] = [str(col) for col in df.columns]
    result: Matrix = [headers]

    # Convert each row
    for _, row in df.iterrows():
        row_data: List[CellValue] = []
        for val in row:
            # Handle missing values
            if pd.isna(val):
                row_data.append("")
            # Check bool before numeric (bool is subclass of int)
            elif isinstance(val, (bool, np.bool_)):
                row_data.append(bool(val))
            elif isinstance(val, (np.integer, np.floating)):
                row_data.append(float(val))
            elif isinstance(val, (int, float)):
                row_data.append(float(val))
            else:
                row_data.append(str(val))
        result.append(row_data)

    return result


def _serialize_value(value: Any) -> str:
    """
    Serialize a value with type prefix

    Type prefixes: i: (int), d: (double), b: (bool), s: (string), n: (null/none), m: (matrix), e: (error)

    Args:
        value: Single value, 2D matrix, or pandas DataFrame

    Returns:
        Type-prefixed string

    Example:
        42 -> "i:42"
        42.5 -> "d:42.5"
        True -> "b:true"
        "hello" -> "s:hello"
        None -> "n:"
        [[1, 1.5, True]] -> "m:i:1\nd:1.5\nb:true"
        pd.DataFrame(...) -> "m:..." (converted to matrix with headers)
        Exception("error") -> "e:error"
        "#ERROR: msg" -> "e:#ERROR: msg"
    """
    # Check if value is an Exception or error string
    if isinstance(value, BaseException):
        # Exception instance - serialize as error with message
        return f"e:{str(value)}"

    # Check for error strings (starting with #ERROR, #VALUE!, #N/A, etc.)
    if isinstance(value, str) and value.startswith("#"):
        return f"e:{value}"

    try:
        import pandas as pd

        if isinstance(value, pd.DataFrame):
            # Convert DataFrame to matrix format with headers
            value = _dataframe_to_matrix(value)
    except ImportError:
        pass

    # Check for 2D matrix (list of lists)
    if isinstance(value, list) and len(value) > 0 and isinstance(value[0], list):
        # Format: m:rows,cols\nd:1\nd:2\nd:3\nd:4\ns:bob
        rows = len(value)
        # Calculate maximum columns across all rows to handle irregular matrices
        cols = max(len(row) for row in value) if rows > 0 else 0

        # Check if numpy is available for type checking
        try:
            import numpy as np

            has_numpy = True
        except ImportError:
            has_numpy = False

        # Flatten matrix to newline-separated cells (row-major order)
        cells = [f"{rows},{cols}"]  # First line is dimensions
        for row in value:
            for cell in row:
                # Handle None as null type
                if cell is None:
                    cells.append("n:")
                # Handle NaN as null type (if numpy is available)
                elif has_numpy and isinstance(cell, (float, np.floating)) and np.isnan(cell):
                    cells.append("n:")
                # Check bool before numeric (bool is subclass of int)
                elif isinstance(cell, bool):
                    cells.append(f"b:{str(cell).lower()}")
                # Handle numpy bool types
                elif has_numpy and isinstance(cell, np.bool_):
                    cells.append(f"b:{str(bool(cell)).lower()}")
                # Handle integer types (check int before float since we want to preserve type)
                elif isinstance(cell, int):
                    cells.append(f"i:{cell}")
                elif has_numpy and isinstance(cell, np.integer):
                    cells.append(f"i:{int(cell)}")
                # Handle float types
                elif isinstance(cell, float):
                    cells.append(f"d:{cell}")
                elif has_numpy and isinstance(cell, np.floating):
                    cells.append(f"d:{float(cell)}")
                else:
                    # Convert to string
                    cells.append(f"s:{str(cell)}")
            # Pad shorter rows with null values to match column count
            for _ in range(cols - len(row)):
                cells.append("n:")
        return "m:" + "\n".join(cells)

    # Scalar values
    # Handle None as null type
    if value is None:
        return "n:"

    # Check for NaN - also serialize as null
    try:
        import numpy as np

        if isinstance(value, (float, np.floating)) and np.isnan(value):
            return "n:"
    except ImportError:
        # No numpy, check for regular float NaN
        if isinstance(value, float):
            import math

            if math.isnan(value):
                return "n:"

    # Check bool before numeric (bool is subclass of int)
    if isinstance(value, bool):
        return f"b:{str(value).lower()}"

    # Check for numpy types if available
    try:
        import numpy as np

        if isinstance(value, np.bool_):
            return f"b:{str(bool(value)).lower()}"
        elif isinstance(value, np.integer):
            return f"i:{int(value)}"
        elif isinstance(value, np.floating):
            return f"d:{float(value)}"
    except ImportError:
        pass

    # Handle standard numeric types (check int before float to preserve type)
    if isinstance(value, int):
        return f"i:{value}"
    elif isinstance(value, float):
        return f"d:{value}"
    else:
        return f"s:{str(value)}"


class RTDClient:
    """Client for communicating with xllify RTD server via ZeroMQ DEALER socket"""

    # ZeroMQ TCP endpoint for RTD server ROUTER socket (ipc:// not supported on Windows)
    ZMQ_ROUTER_ENDPOINT = "tcp://127.0.0.1:55555"
    REQUEST_TIMEOUT_MS = 1500  # 1 second timeout for requests

    def __init__(
        self,
        enable_batching: bool = True,
        batch_size: int = 250,
        batch_timeout_ms: int = 5,
        min_batch_size: int = 50,
    ):
        """
        Initialize RTD client with optional batching support

        Args:
            enable_batching: Enable automatic batching of complete() calls (default: False for immediate sends)
            batch_size: Maximum number of calls to batch together before auto-flush (default: 50)
            batch_timeout_ms: Maximum time to wait before flushing batch in milliseconds (default: 10)
            min_batch_size: Minimum batch size to enable timer-based flushing (default: 10)
                           If queue is smaller, sends immediately instead of waiting for timer
        """
        self.enable_batching = enable_batching
        self.batch_size = batch_size
        self.batch_timeout_ms = batch_timeout_ms
        self.min_batch_size = min_batch_size

        # ZeroMQ context and socket (lazy initialization)
        self._context: Optional[zmq.Context] = None
        self._dealer: Optional[zmq.Socket] = None
        self._socket_lock = threading.Lock()
        self._connected = False

        # Batch queue for complete() calls
        self._batch_queue: List[tuple[Union[str, int], Union[str, float, int]]] = []
        self._batch_lock = threading.Lock()
        self._batch_timer: Optional[threading.Timer] = None

        # Register cleanup on exit
        atexit.register(self.close)

    def _ensure_connected(self) -> bool:
        """Ensure ZeroMQ DEALER socket is connected (lazy initialization)"""
        if self._connected:
            return True

        with self._socket_lock:
            if self._connected:
                return True

            try:
                # Create context and DEALER socket
                self._context = zmq.Context()
                self._dealer = self._context.socket(zmq.DEALER)

                # Set socket options
                self._dealer.setsockopt(zmq.LINGER, 0)  # Don't wait on close
                self._dealer.setsockopt(zmq.RCVTIMEO, self.REQUEST_TIMEOUT_MS)
                self._dealer.setsockopt(zmq.SNDTIMEO, self.REQUEST_TIMEOUT_MS)

                # # Set buffer sizes for large messages (32MB buffers - supports ~1M cells)
                # buffer_size = 32 * 1024 * 1024  # 32MB
                # self._dealer.setsockopt(zmq.SNDBUF, buffer_size)
                # self._dealer.setsockopt(zmq.RCVBUF, buffer_size)

                # # Set high water marks (queue depth before blocking)
                # hwm = 100  # Reasonable queue depth
                # self._dealer.setsockopt(zmq.SNDHWM, hwm)
                # self._dealer.setsockopt(zmq.RCVHWM, hwm)

                # Connect to RTD server
                self._dealer.connect(self.ZMQ_ROUTER_ENDPOINT)
                self._connected = True
                return True

            except Exception as e:
                logger.debug(f"Failed to connect to RTD server: {e}")
                self._connected = False
                return False

    def _send_command(self, frames: List[str]) -> bool:
        """
        Send a command to the RTD server via ZeroMQ

        Args:
            frames: List of message frames [command, topic, value, ...]

        Returns:
            True if command was sent and acknowledged successfully
        """
        if not self._ensure_connected():
            logger.warning("Failed to connect to RTD server")
            return False

        with self._socket_lock:
            try:
                # Send multipart message
                # Use send() with explicit UTF-8 encoding to preserve tabs and special chars
                for i, frame in enumerate(frames):
                    flags = zmq.SNDMORE if i < len(frames) - 1 else 0
                    self._dealer.send(frame.encode("utf-8"), flags)

                # Receive response: [status, message]
                status = self._dealer.recv_string()
                message = self._dealer.recv_string()

                if status == "OK":
                    logger.debug(f"Command successful: {frames[0]} (frames={len(frames)})")
                    return True
                else:
                    logger.error(f"RTD command '{frames[0]}' failed: {message}")
                    return False

            except zmq.Again:
                # Timeout is normal if RTD server hasn't started yet (no Excel RTD calls yet)
                logger.warning("Timeout waiting for RTD server response (may not be started yet)")
                self._connected = False  # Mark as disconnected, will retry next time
                return False
            except Exception as e:
                logger.error(f"ZeroMQ error sending command '{frames[0]}': {e}", exc_info=True)
                self._connected = False
                return False

    def update(self, topic: Union[str, int], value: Union[str, float, int]) -> bool:
        """
        Update a single RTD topic

        Args:
            topic: Topic name (string) or ID (int)
            value: New value (string, float, or int)

        Example:
            client.update("priceData", 42.5)
            client.update(123, "hello world")
        """
        return self._send_command(["U", str(topic), str(value)])

    def _flush_batch(self):
        """Flush the current batch of complete() calls"""
        with self._batch_lock:
            if not self._batch_queue:
                return

            # Cancel pending timer
            if self._batch_timer:
                try:
                    self._batch_timer.cancel()
                except:
                    pass  # Timer may have already fired
                self._batch_timer = None

            # Make a copy of the queue and clear it
            batch_copy = list(self._batch_queue)
            self._batch_queue.clear()

        # Send bulk complete command outside of lock
        updates = [TopicUpdate(topic, value) for topic, value in batch_copy]
        return self.bulk_update(updates, auto_complete=True)

    def complete_matrix(self, topic: Union[str, int], matrix: Matrix) -> bool:
        """
        Mark topic as complete with a matrix value (2D array)
        Serializes matrix to type-prefixed format: m:d:1.5\\tb:true\\ts:hello

        Args:
            topic: Topic name (string) or ID (int)
            matrix: 2D list of values (numbers, booleans, strings)

        Example:
            client.complete_matrix("results", [[1.5, True, "hello"], [2.0, False, "world"]])
        """
        serialized = _serialize_value(matrix)
        return self._send_command(["C", str(topic), serialized])

    def complete(self, topic: Union[str, int], value: ExcelValue) -> bool:
        """
        Mark topic as complete with final value
        Triggers cache notification to all subscribed clients via PUB socket
        All values are serialized with type prefixes (d:, b:, s:, m:)

        When batching is enabled, calls are automatically batched together.
        For small batches (< min_batch_size), sends immediately to avoid delays.
        For larger batches, flushes when batch_size is reached or batch_timeout_ms elapses.

        Args:
            topic: Topic name (string) or ID (int)
            value: Final value (scalar, 2D matrix, or pandas DataFrame)

        Example:
            client.complete("calculation", 100.0)  # Sends as "d:100.0"
            client.complete("status", "DONE")      # Sends as "s:DONE"
            client.complete("flag", True)          # Sends as "b:true"
            client.complete("matrix", [[1, 2]])    # Sends as "m:d:1\td:2"
            client.complete("data", df)            # DataFrame with headers (requires pandas)
        """
        serialized = _serialize_value(value)

        if not self.enable_batching:
            # Direct send without batching
            return self._send_command(["C", str(topic), serialized])

        # Add to batch queue (store serialized value)
        should_flush = False
        with self._batch_lock:
            self._batch_queue.append((topic, serialized))
            queue_size = len(self._batch_queue)

            # Start timer on first item
            if queue_size == 1 and self._batch_timer is None:
                self._batch_timer = threading.Timer(
                    self.batch_timeout_ms / 1000.0, self._flush_batch
                )
                self._batch_timer.daemon = True
                self._batch_timer.start()

            # Flush immediately when batch is full
            if queue_size >= self.batch_size:
                should_flush = True

        # Flush outside of lock to avoid deadlock
        if should_flush:
            self._flush_batch()

        return True

    def dirty(self, topic: Union[str, int]) -> bool:
        """
        Mark topic as dirty (needs refresh) without changing value

        Args:
            topic: Topic name (string) or ID (int)

        Example:
            client.dirty("myTopic")
            client.dirty(123)
        """
        return self._send_command(["D", str(topic), ""])

    def dirty_complete(self, topic: Union[str, int]) -> bool:
        """
        Mark topic as dirty and complete (for in-process cache updates)

        Note: This is an optimization for in-process updates where the value
        is already in RTDCache. External processes should use complete() instead.

        Args:
            topic: Topic name (string) or ID (int)

        Example:
            client.dirty_complete("myTopic")
        """
        return self._send_command(["DC", str(topic), ""])

    def bulk_update(self, updates: List[TopicUpdate], auto_complete: bool = True) -> bool:
        """
        Update multiple topics in a single bulk operation
        More efficient than individual updates
        Values are automatically serialized with type prefixes

        Args:
            updates: List of TopicUpdate objects
            auto_complete: If True, marks all topics as complete and triggers cache broadcast (default: True)

        Example:
            # Mark all as complete (default behavior)
            client.bulk_update([
                TopicUpdate("price", 42.5),
                TopicUpdate("status", "Processing"),
                TopicUpdate(789, 100)
            ])

            # Just update without completing
            client.bulk_update([
                TopicUpdate("price", 42.5),
            ], auto_complete=False)
        """
        # Build bulk message: ["BC", "count", "topic1", "value1", "topic2", "value2", ...]
        # Or ["B", "count", ...] for bulk update without complete
        cmd = "BC" if auto_complete else "B"
        frames = [cmd, str(len(updates))]
        for update in updates:
            frames.append(str(update.topic))
            # Serialize value if not already serialized (check for type prefix)
            value_str = str(update.value)
            if not (len(value_str) >= 2 and value_str[1] == ":"):
                # Not yet serialized, serialize it
                value_str = _serialize_value(update.value)
            frames.append(value_str)

        return self._send_command(frames)

    def flush(self):
        """
        Manually flush any pending batched complete() calls
        Useful when you want to ensure all pending updates are sent immediately
        """
        self._flush_batch()

    def ping(self) -> bool:
        """
        Send a ping to check if RTD server is alive

        Returns:
            True if server responded
        """
        return self._send_command(["PING", ""])

    def evict_all(self) -> bool:
        """
        Evict all topics from the cache
        Broadcasts cache eviction for all registered topics

        Returns:
            True if command was successful

        Example:
            client.evict_all()
        """
        return self._send_command(["EVICTALL"])

    def close(self):
        """Close the ZeroMQ connection and flush any pending batches"""
        # Flush any pending batches before closing
        try:
            self._flush_batch()
        except:
            pass

        # Cancel any pending timers
        with self._batch_lock:
            if self._batch_timer:
                try:
                    self._batch_timer.cancel()
                except:
                    pass
                self._batch_timer = None

        # Close sockets
        with self._socket_lock:
            if self._dealer:
                self._dealer.close()
                self._dealer = None
            if self._context:
                self._context.term()
                self._context = None
            self._connected = False

    def __enter__(self):
        """Context manager support"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup"""
        self.close()

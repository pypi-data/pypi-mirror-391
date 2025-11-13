"""Network Buffer Implementation.

Provides buffering for network I/O with size limits.
"""

from __future__ import annotations
from typing import Optional
import io


class Buffer:
    """Network buffer with size limits."""

    def __init__(self, max_size: int = 65536):
        self.max_size = max_size
        self._buffer = io.BytesIO()
        self._size = 0

    def write(self, data: bytes) -> int:
        """Write data to buffer."""
        if not data:
            return 0

        if self._size + len(data) > self.max_size:
            raise BufferError(f"Buffer full: {self._size + len(data)} > {self.max_size}")

        pos = self._buffer.tell()
        self._buffer.seek(0, io.SEEK_END)
        self._buffer.write(data)
        self._buffer.seek(pos)

        self._size += len(data)
        return len(data)

    def read(self, size: int = -1) -> bytes:
        """Read data from buffer."""
        if size < 0:
            size = self._size

        data = self._buffer.read(size)
        self._size -= len(data)

        # Compact buffer if empty
        if self._size == 0:
            self._buffer = io.BytesIO()

        return data

    def peek(self, size: int = -1) -> bytes:
        """Peek at data without consuming it."""
        pos = self._buffer.tell()
        data = self.read(size)
        self._buffer.seek(pos)
        self._size += len(data)
        return data

    def clear(self) -> None:
        """Clear the buffer."""
        self._buffer = io.BytesIO()
        self._size = 0

    @property
    def size(self) -> int:
        """Current buffer size."""
        return self._size

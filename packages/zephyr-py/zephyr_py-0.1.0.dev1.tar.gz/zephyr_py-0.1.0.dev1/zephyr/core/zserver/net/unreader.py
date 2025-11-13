from typing import Optional, List, Union
from io import BytesIO
from .exceptions import BufferOverflowError
from .constants import DEFAULT_BUFFER_SIZE


class UnReader:
    """
    A buffer implementation that supports pushing back read data.
    This is essential for parsing HTTP messages where lookahead might be needed.
    """

    def __init__(self, sock, max_buffer: int = DEFAULT_BUFFER_SIZE):
        """
        Initialize UnReader with a socket-like object and buffer size limit.

        Args:
            sock: Socket-like object supporting read/recv operations
            max_buffer: Maximum size of the internal buffer
        """
        self.sock = sock
        self.max_buffer = max_buffer
        self._buffer: List[bytes] = []
        self._buffer_size = 0
        self._pos = 0

    def read(self, size: Optional[int] = None) -> bytes:
        """
        Read up to size bytes from the buffer or underlying socket.

        Args:
            size: Number of bytes to read, or None for all available

        Returns:
            Bytes read from buffer or socket
        """
        if size is not None and size <= 0:
            return b""

        data = []
        data_length = 0

        # Read from buffer first
        while self._buffer and (size is None or data_length < size):
            chunk = self._buffer[0]
            remaining = len(chunk) - self._pos

            if size is None:
                data.append(chunk[self._pos :])
                data_length += remaining
                self._buffer.pop(0)
                self._pos = 0
            else:
                can_read = min(remaining, size - data_length)
                data.append(chunk[self._pos : self._pos + can_read])
                data_length += can_read

                if can_read == remaining:
                    self._buffer.pop(0)
                    self._pos = 0
                else:
                    self._pos += can_read

        self._buffer_size -= data_length

        # Read from socket if needed and size is specified
        if size is not None and data_length < size:
            remaining = size - data_length
            chunk = self._read_from_socket(remaining)
            if chunk:
                data.append(chunk)

        return b"".join(data)

    def readline(self, max_length: Optional[int] = None) -> bytes:
        """
        Read until newline or max_length bytes have been read.

        Args:
            max_length: Maximum number of bytes to read

        Returns:
            Line including newline character(s)
        """
        data = []
        data_length = 0

        while True:
            # Read one byte at a time until we find a newline
            byte = self.read(1)
            if not byte:
                break

            data.append(byte)
            data_length += 1

            if max_length and data_length >= max_length:
                break

            if byte == b"\n":
                break

        return b"".join(data)

    def unread(self, data: Union[bytes, bytearray]) -> None:
        """
        Push data back into the buffer to be read again.

        Args:
            data: Bytes to push back into buffer

        Raises:
            BufferOverflowError: If pushing back would exceed buffer size limit
        """
        if not data:
            return

        new_size = self._buffer_size + len(data)
        if new_size > self.max_buffer:
            raise BufferOverflowError(f"Buffer overflow: {new_size} bytes exceeds maximum of {self.max_buffer}")

        self._buffer.insert(0, bytes(data))
        self._buffer_size = new_size
        self._pos = 0

    def _read_from_socket(self, size: int) -> bytes:
        """
        Read directly from the underlying socket.

        Args:
            size: Number of bytes to read

        Returns:
            Bytes read from socket
        """
        try:
            if isinstance(self.sock, BytesIO):
                return self.sock.read(size)
            return self.sock.recv(size)
        except (BlockingIOError, AttributeError):
            return b""

    def peek(self, size: int = 1) -> bytes:
        """
        Peek at the next bytes without consuming them.

        Args:
            size: Number of bytes to peek

        Returns:
            Bytes peeked from buffer
        """
        data = self.read(size)
        if data:
            self.unread(data)
        return data

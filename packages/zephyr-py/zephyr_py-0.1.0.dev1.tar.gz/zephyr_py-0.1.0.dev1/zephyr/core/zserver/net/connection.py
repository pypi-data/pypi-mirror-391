"""Network Connection Management.

Handles network connections with buffering and flow control.
"""

from __future__ import annotations
import asyncio
from typing import Optional, Union
from .buffer import Buffer
from .flow_control import FlowControl


class Connection:
    """Network connection wrapper with flow control."""

    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, buffer_size: int = 65536):
        self.reader = reader
        self.writer = writer
        self.buffer = Buffer(max_size=buffer_size)
        self.flow_control = FlowControl(writer.transport)
        self._closed = False

    @property
    def closed(self) -> bool:
        """Check if connection is closed."""
        return self._closed or self.writer.is_closing()

    async def read(self, n: int = -1) -> bytes:
        """Read data from connection with flow control."""
        if self.closed:
            raise ConnectionError("Connection closed")

        # Wait if backpressure applied
        await self.flow_control.drain()

        try:
            data = await self.reader.read(n)
            if not data:  # EOF
                await self.close()
                return b""

            # Update flow control
            self.flow_control.update_read(len(data))
            return data

        except Exception as e:
            await self.close()
            raise ConnectionError(f"Read error: {e}")

    async def write(self, data: Union[bytes, bytearray]) -> None:
        """Write data to connection with flow control."""
        if self.closed:
            raise ConnectionError("Connection closed")

        try:
            # Apply write backpressure if needed
            await self.flow_control.drain()

            self.writer.write(data)
            await self.writer.drain()

            # Update flow control
            # self.flow_control.update_write(len(data))

        except Exception as e:
            await self.close()
            raise ConnectionError(f"Write error: {e}")

    async def close(self) -> None:
        """Close the connection."""
        if not self._closed:
            self._closed = True
            self.writer.close()
            try:
                await self.writer.wait_closed()
            except Exception:
                pass  # Ignore errors during close

    def get_extra_info(self, name: str) -> Optional[Any]:
        """Get transport information."""
        return self.writer.get_extra_info(name)

    @property
    def peer(self) -> str:
        """Get peer address."""
        addr = self.get_extra_info("peername")
        if not addr:
            return "Unknown"
        return f"{addr[0]}:{addr[1]}"

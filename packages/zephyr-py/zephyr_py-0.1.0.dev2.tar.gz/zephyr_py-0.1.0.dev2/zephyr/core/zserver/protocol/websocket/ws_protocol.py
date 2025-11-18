"""WebSocket protocol implementation using websockets library.

Author: A M (am@bbdevs.com)

Created At: 13 Nov 2025
"""

import asyncio
import struct
from typing import Any

from zephyr._types import ASGIApplication, Scope
from zephyr.core.logging import get_logger, TRACE_LOG_LEVEL
from zephyr.core.zserver.config import ServerConfig
from zephyr.core.zserver.state import ServerState

# WebSocket opcodes
OPCODE_CONTINUATION = 0x0
OPCODE_TEXT = 0x1
OPCODE_BINARY = 0x2
OPCODE_CLOSE = 0x8
OPCODE_PING = 0x9
OPCODE_PONG = 0xA


class WebSocketProtocol(asyncio.Protocol):
    """WebSocket protocol handler that bridges websockets library with ASGI."""

    def __init__(
        self,
        config: ServerConfig,
        server_state: ServerState,
        app_state: dict[str, Any],
        _loop: asyncio.AbstractEventLoop | None = None,
    ) -> None:
        """Initialize WebSocket protocol.

        Args:
            config: Server configuration
            server_state: Server state
            app_state: Application state
            _loop: Event loop (optional)
        """
        if not config.loaded:
            config.load()

        self.config = config
        self.app: ASGIApplication = config.app
        self.loop = _loop or asyncio.get_event_loop()
        self.logger = get_logger(self.__class__.__name__)

        # Server state
        self.server_state = server_state
        self.app_state = app_state
        self.connections = server_state.connections
        self.tasks = server_state.tasks

        # Connection state
        self.transport: asyncio.Transport | None = None
        self.client: tuple[str, int] | None = None
        self.server: tuple[str, int] | None = None

        # ASGI state
        self.scope: Scope | None = None
        self.handshake_complete = False
        self.closed = False

        # WebSocket frame parsing
        self.frame_buffer = bytearray()
        self.current_opcode: int | None = None
        self.current_payload = bytearray()

        # Message queues for ASGI
        self.receive_queue: asyncio.Queue = asyncio.Queue()
        self.send_queue: asyncio.Queue = asyncio.Queue()

        # Tasks
        self.asgi_task: asyncio.Task | None = None
        self.sender_task: asyncio.Task | None = None

    def connection_made(self, transport: asyncio.Transport) -> None:  # type: ignore[override]
        """Called when connection is established.

        Args:
            transport: The transport for this connection
        """
        self.logger.debug("WebSocket connection made")
        self.transport = transport
        self.connections.add(self)

        # Get connection info
        socket_info = transport.get_extra_info("socket")
        if socket_info:
            try:
                self.server = socket_info.getsockname()
                self.client = socket_info.getpeername()
            except OSError:
                pass

        if self.logger.level <= TRACE_LOG_LEVEL:
            prefix = "%s:%d - " % self.client if self.client else ""
            self.logger.log(TRACE_LOG_LEVEL, "%sWebSocket connection made", prefix)

        # Handshake is done by HTTP protocol before transfer
        # Don't send 101 response here
        self.logger.debug("WebSocket protocol active, handshake already complete")

    def _send_handshake_response(self) -> None:
        """Send the WebSocket handshake response (101 Switching Protocols)."""
        if not self.scope or not self.transport:
            return

        # Get the Sec-WebSocket-Key from headers
        ws_key = None
        for name, value in self.scope.get("headers", []):
            if name == b"sec-websocket-key":
                ws_key = value
                break

        if not ws_key:
            self.logger.error("Missing Sec-WebSocket-Key header")
            self._close_connection(1002)
            return

        # Calculate accept key
        import base64
        import hashlib

        accept_key = base64.b64encode(hashlib.sha1(ws_key + b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11").digest())

        # Build 101 response
        response = [
            b"HTTP/1.1 101 Switching Protocols\r\n",
            b"Upgrade: websocket\r\n",
            b"Connection: Upgrade\r\n",
            b"Sec-WebSocket-Accept: ",
            accept_key,
            b"\r\n",
            b"\r\n",
        ]

        self.transport.write(b"".join(response))
        self.handshake_complete = True
        self.logger.debug("WebSocket handshake complete")

    def connection_lost(self, exc: Exception | None) -> None:
        """Called when connection is lost.

        Args:
            exc: Exception if connection lost due to error
        """
        self.connections.discard(self)
        self.closed = True

        if self.logger.level <= TRACE_LOG_LEVEL:
            prefix = "%s:%d - " % self.client if self.client else ""
            self.logger.log(TRACE_LOG_LEVEL, "%sWebSocket connection lost", prefix)

        # Cancel tasks
        if self.asgi_task and not self.asgi_task.done():
            self.asgi_task.cancel()
        if self.sender_task and not self.sender_task.done():
            self.sender_task.cancel()

        # Put disconnect message in queue
        if not self.receive_queue.empty() or self.handshake_complete:
            try:
                self.receive_queue.put_nowait({"type": "websocket.disconnect", "code": 1006})
            except asyncio.QueueFull:
                pass

    def data_received(self, data: bytes) -> None:
        """Called when data is received - parse WebSocket frames.

        Args:
            data: Received data
        """
        if not self.handshake_complete:
            self.logger.warning("Received data before handshake complete")
            return

        self.frame_buffer.extend(data)

        try:
            while self._parse_frame():
                pass  # Continue parsing frames
        except Exception as exc:
            self.logger.error("Error parsing WebSocket frame: %s", exc, exc_info=True)
            self._close_connection(1002)  # Protocol error

    def _parse_frame(self) -> bool:
        """Parse a single WebSocket frame from buffer.

        Returns:
            True if a frame was parsed, False if need more data
        """
        self.logger.debug("Parsing frame from buffer: %s", self.frame_buffer)
        if len(self.frame_buffer) < 2:
            self.logger.debug("Not enough data to parse frame")
            return False

        # Parse frame header
        byte1, byte2 = self.frame_buffer[0], self.frame_buffer[1]
        fin = (byte1 & 0x80) != 0
        opcode = byte1 & 0x0F
        masked = (byte2 & 0x80) != 0
        payload_len = byte2 & 0x7F

        # Calculate header size
        header_size = 2
        offset = 2

        # Extended payload length
        if payload_len == 126:
            if len(self.frame_buffer) < 4:
                return False
            payload_len = struct.unpack(">H", self.frame_buffer[2:4])[0]
            offset = 4
            header_size = 4
        elif payload_len == 127:
            if len(self.frame_buffer) < 10:
                return False
            payload_len = struct.unpack(">Q", self.frame_buffer[2:10])[0]
            offset = 10
            header_size = 10

        # Masking key
        masking_key = None
        if masked:
            if len(self.frame_buffer) < offset + 4:
                return False
            masking_key = self.frame_buffer[offset : offset + 4]
            offset += 4
            header_size += 4

        # Check if we have complete frame
        frame_size = header_size + payload_len
        if len(self.frame_buffer) < frame_size:
            return False

        # Extract payload
        payload = bytearray(self.frame_buffer[offset : offset + payload_len])

        # Unmask payload if needed
        if masked and masking_key:
            for i in range(len(payload)):
                payload[i] ^= masking_key[i % 4]

        # Remove frame from buffer
        self.frame_buffer = self.frame_buffer[frame_size:]

        # Process frame
        self._process_frame(opcode, bytes(payload), fin)

        return True

    def _process_frame(self, opcode: int, payload: bytes, fin: bool) -> None:
        """Process a parsed WebSocket frame.

        Args:
            opcode: Frame opcode
            payload: Frame payload
            fin: FIN bit
        """
        self.logger.debug("Processing frame: opcode=%d, payload_len=%d, fin=%s", opcode, len(payload), fin)

        if opcode == OPCODE_TEXT:
            # Text frame
            try:
                text = payload.decode("utf-8")
                self.logger.info("Received text message: %s", text)
                self.receive_queue.put_nowait(
                    {
                        "type": "websocket.receive",
                        "text": text,
                    }
                )
                self.logger.debug("Put text message in receive queue")
            except UnicodeDecodeError:
                self.logger.error("Invalid UTF-8 in text frame")
                self._close_connection(1007)  # Invalid frame payload data

        elif opcode == OPCODE_BINARY:
            # Binary frame
            self.receive_queue.put_nowait(
                {
                    "type": "websocket.receive",
                    "bytes": payload,
                }
            )

        elif opcode == OPCODE_CLOSE:
            # Close frame
            code = 1000
            reason = ""
            if len(payload) >= 2:
                code = struct.unpack(">H", payload[:2])[0]
                if len(payload) > 2:
                    reason = payload[2:].decode("utf-8", errors="replace")
            self.receive_queue.put_nowait(
                {
                    "type": "websocket.disconnect",
                    "code": code,
                    "reason": reason,
                }
            )
            self.closed = True
            self._close_connection(code, reason)

        elif opcode == OPCODE_PING:
            # Ping frame - send pong
            self.logger.debug("Received ping frame")
            self._send_pong(payload)

        elif opcode == OPCODE_PONG:
            # Pong frame - ignore
            self.logger.debug("Received pong frame")
            pass

        else:
            self.logger.warning("Unknown WebSocket opcode: %d", opcode)

    def _send_pong(self, payload: bytes) -> None:
        """Send a pong frame in response to ping.

        Args:
            payload: Payload from ping frame
        """
        if not self.transport:
            return

        # Build pong frame
        frame = bytearray()
        frame.append(0x80 | OPCODE_PONG)  # FIN + PONG opcode

        payload_len = len(payload)
        if payload_len < 126:
            frame.append(payload_len)
        elif payload_len < 65536:
            frame.append(126)
            frame.extend(struct.pack(">H", payload_len))
        else:
            frame.append(127)
            frame.extend(struct.pack(">Q", payload_len))

        frame.extend(payload)
        self.transport.write(bytes(frame))

    def _close_connection(self, code: int = 1000, reason: str = "") -> None:
        """Close WebSocket connection.

        Args:
            code: Close code
            reason: Close reason
        """
        if self.closed:
            return

        self.closed = True

        if self.transport:
            try:
                # Send close frame
                close_payload = struct.pack(">H", code) + reason.encode("utf-8")
                frame = bytearray()
                frame.append(0x80 | OPCODE_CLOSE)  # FIN + CLOSE opcode

                payload_len = len(close_payload)
                if payload_len < 126:
                    frame.append(payload_len)
                elif payload_len < 65536:
                    frame.append(126)
                    frame.extend(struct.pack(">H", payload_len))
                else:
                    frame.append(127)
                    frame.extend(struct.pack(">Q", payload_len))

                frame.extend(close_payload)
                self.transport.write(bytes(frame))
            except Exception as exc:
                self.logger.debug("Error sending close frame: %s", exc)

        # Close transport
        if self.transport:
            self.transport.close()

    async def asgi_receive(self) -> dict:
        """ASGI receive callable.

        Returns:
            ASGI message dict
        """
        self.logger.debug("ASGI receive called")
        data = await self.receive_queue.get()
        self.logger.debug("ASGI receive returned: %s", data)
        return data

    async def asgi_send(self, message: dict) -> None:
        """ASGI send callable.

        Args:
            message: ASGI message to send
        """
        await self.send_queue.put(message)

    async def sender_loop(self) -> None:
        """Background task to send messages from ASGI app."""
        try:
            while not self.closed:
                try:
                    message = await asyncio.wait_for(self.send_queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue

                if not self.transport:
                    break

                try:
                    message_type = message["type"]

                    if message_type == "websocket.accept":
                        # Accept is handled by initial handshake
                        self.logger.debug("WebSocket accepted")

                    elif message_type == "websocket.send":
                        # Send data frame
                        if "text" in message:
                            payload = message["text"].encode("utf-8")
                            opcode = OPCODE_TEXT
                        elif "bytes" in message:
                            payload = message["bytes"]
                            opcode = OPCODE_BINARY
                        else:
                            self.logger.warning("websocket.send message missing text or bytes")
                            continue

                        # Build WebSocket frame
                        frame = bytearray()
                        frame.append(0x80 | opcode)  # FIN + opcode

                        payload_len = len(payload)
                        if payload_len < 126:
                            frame.append(payload_len)
                        elif payload_len < 65536:
                            frame.append(126)
                            frame.extend(struct.pack(">H", payload_len))
                        else:
                            frame.append(127)
                            frame.extend(struct.pack(">Q", payload_len))

                        frame.extend(payload)
                        self.transport.write(bytes(frame))

                    elif message_type == "websocket.close":
                        # Close connection
                        code = message.get("code", 1000)
                        reason = message.get("reason", "")
                        self._close_connection(code, reason)
                        break

                except Exception as exc:
                    self.logger.error("Error sending message: %s", exc, exc_info=True)
                    self._close_connection(1011)
                    break

        except Exception as exc:
            self.logger.error("Sender loop error: %s", exc, exc_info=True)

    async def run_asgi(self) -> None:
        """Run the ASGI application."""
        if not self.scope:
            self.logger.error("Cannot run ASGI: scope not set")
            return

        self.logger.info("Starting ASGI app for WebSocket path: %s", self.scope.get("path"))

        try:
            # Start sender task
            self.sender_task = self.loop.create_task(self.sender_loop())

            # Put connect message
            await self.receive_queue.put({"type": "websocket.connect"})
            self.logger.debug("Put websocket.connect message in queue")

            # Run ASGI app
            self.logger.debug("Calling ASGI app with scope: %s", self.scope.get("type"))
            await self.app(self.scope, self.asgi_receive, self.asgi_send)
            self.logger.debug("ASGI app completed")

        except Exception as exc:
            self.logger.error("ASGI application error: %s", exc, exc_info=True)
            self._close_connection(1011)
        finally:
            # Cancel sender task
            if self.sender_task and not self.sender_task.done():
                self.sender_task.cancel()
                try:
                    await self.sender_task
                except asyncio.CancelledError:
                    pass

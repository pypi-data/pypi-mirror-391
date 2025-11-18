import enum
import json
from typing import Any

from zephyr._types import Scope, Receive, Send, Message
from zephyr.app.requests import HTTPConnection
from zephyr.core.logging import get_logger


class WebSocketState(enum.Enum):
    CONNECTING = 0
    CONNECTED = 1
    DISCONNECTED = 2
    RESPONSE = 3


class WebSocketDisconnect(Exception):
    def __init__(self, code: int = 1000, reason: str | None = None) -> None:
        self.code = code
        self.reason = reason or ""


class WebSocket(HTTPConnection):
    def __init__(self, scope: Scope, receive: Receive, send: Send) -> None:
        super().__init__(scope)
        assert scope["type"] == "websocket"
        self.logger = get_logger("zephyr.app.websockets")
        self._receive = receive
        self._send = send
        self.client_state = WebSocketState.CONNECTING
        self.application_state = WebSocketState.CONNECTING

    async def accept(
        self,
        subprotocol: str | None = None,
        headers: list[tuple[bytes, bytes]] | None = None,
    ) -> None:
        """Accept the WebSocket connection.

        Args:
            subprotocol: Optional subprotocol to use
            headers: Optional additional headers to send
        """
        if self.client_state != WebSocketState.CONNECTING:
            msg = "WebSocket already connected"
            raise RuntimeError(msg)

        # First, receive the websocket.connect message
        connect_message = await self._receive()
        if connect_message["type"] != "websocket.connect":
            msg = f"Expected websocket.connect, got {connect_message['type']}"
            raise RuntimeError(msg)

        message: dict[str, Any] = {"type": "websocket.accept"}
        if subprotocol:
            message["subprotocol"] = subprotocol
        if headers:
            message["headers"] = headers

        await self._send(message)
        self.client_state = WebSocketState.CONNECTED
        self.application_state = WebSocketState.CONNECTED

    async def receive(self) -> Message:
        """Receive a message from the WebSocket.

        Returns:
            ASGI message dict

        Raises:
            WebSocketDisconnect: If connection is closed
        """
        if self.client_state == WebSocketState.CONNECTING:
            msg = "WebSocket not yet connected"
            raise RuntimeError(msg)

        message = await self._receive()
        if message["type"] == "websocket.disconnect":
            self.client_state = WebSocketState.DISCONNECTED
            raise WebSocketDisconnect(message.get("code", 1000), message.get("reason", ""))

        return message

    async def receive_text(self) -> str:
        """Receive a text message from the WebSocket.

        Returns:
            Text message as string

        Raises:
            WebSocketDisconnect: If connection is closed
            RuntimeError: If message is not text
        """
        message = await self.receive()
        if "text" not in message:
            msg = "Expected text message, got bytes"
            raise RuntimeError(msg)
        return message["text"]

    async def receive_bytes(self) -> bytes:
        """Receive a binary message from the WebSocket.

        Returns:
            Binary message as bytes

        Raises:
            WebSocketDisconnect: If connection is closed
            RuntimeError: If message is not binary
        """
        message = await self.receive()
        if "bytes" not in message:
            msg = "Expected bytes message, got text"
            raise RuntimeError(msg)
        return message["bytes"]

    async def receive_json(self, mode: str = "text") -> Any:
        """Receive a JSON message from the WebSocket.

        Args:
            mode: Either "text" or "binary"

        Returns:
            Parsed JSON data

        Raises:
            WebSocketDisconnect: If connection is closed
            json.JSONDecodeError: If message is not valid JSON
        """
        if mode == "text":
            text = await self.receive_text()
            return json.loads(text)
        else:
            data = await self.receive_bytes()
            return json.loads(data.decode("utf-8"))

    async def send(self, message: Message) -> None:
        """Send a raw ASGI message to the WebSocket.

        Args:
            message: ASGI message dict
        """
        if self.application_state != WebSocketState.CONNECTED:
            msg = "WebSocket not connected"
            raise RuntimeError(msg)
        await self._send(message)

    async def send_text(self, data: str) -> None:
        """Send a text message to the WebSocket.

        Args:
            data: Text message to send
        """
        await self.send({"type": "websocket.send", "text": data})

    async def send_bytes(self, data: bytes) -> None:
        """Send a binary message to the WebSocket.

        Args:
            data: Binary message to send
        """
        await self.send({"type": "websocket.send", "bytes": data})

    async def send_json(self, data: Any, mode: str = "text") -> None:
        """Send a JSON message to the WebSocket.

        Args:
            data: Data to serialize as JSON
            mode: Either "text" or "binary"
        """
        if mode == "text":
            text = json.dumps(data)
            await self.send_text(text)
        else:
            bytes_data = json.dumps(data).encode("utf-8")
            await self.send_bytes(bytes_data)

    async def close(self, code: int = 1000, reason: str | None = None) -> None:
        """Close the WebSocket connection.

        Args:
            code: Close code (default 1000 for normal closure)
            reason: Optional close reason
        """
        if self.application_state == WebSocketState.DISCONNECTED:
            return

        self.application_state = WebSocketState.DISCONNECTED
        message: dict[str, Any] = {"type": "websocket.close", "code": code}
        if reason:
            message["reason"] = reason
        await self._send(message)

    async def iter_text(self):
        """Async iterator that yields text messages.

        Yields:
            Text messages as strings

        Raises:
            WebSocketDisconnect: When connection is closed
        """
        try:
            while True:
                yield await self.receive_text()
        except WebSocketDisconnect:
            pass

    async def iter_bytes(self):
        """Async iterator that yields binary messages.

        Yields:
            Binary messages as bytes

        Raises:
            WebSocketDisconnect: When connection is closed
        """
        try:
            while True:
                yield await self.receive_bytes()
        except WebSocketDisconnect:
            pass

    async def iter_json(self):
        """Async iterator that yields JSON messages.

        Yields:
            Parsed JSON data

        Raises:
            WebSocketDisconnect: When connection is closed
        """
        try:
            while True:
                yield await self.receive_json()
        except WebSocketDisconnect:
            pass

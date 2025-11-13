import enum

from zephyr._types import Scope, Receive, Send
from zephyr.app.requests import HTTPConnection


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
        self._receive = receive
        self._send = send
        self.client_state = WebSocketState.CONNECTING
        self.application_state = WebSocketState.CONNECTING

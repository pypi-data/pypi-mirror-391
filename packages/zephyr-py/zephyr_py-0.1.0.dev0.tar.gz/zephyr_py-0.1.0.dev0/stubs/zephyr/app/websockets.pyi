import enum
from _typeshed import Incomplete
from zephyr._types import Receive as Receive, Scope as Scope, Send as Send
from zephyr.app.requests import HTTPConnection as HTTPConnection

class WebSocketState(enum.Enum):
    CONNECTING = 0
    CONNECTED = 1
    DISCONNECTED = 2
    RESPONSE = 3

class WebSocketDisconnect(Exception):
    code: Incomplete
    reason: Incomplete
    def __init__(self, code: int = 1000, reason: str | None = None) -> None: ...

class WebSocket(HTTPConnection):
    client_state: Incomplete
    application_state: Incomplete
    def __init__(self, scope: Scope, receive: Receive, send: Send) -> None: ...

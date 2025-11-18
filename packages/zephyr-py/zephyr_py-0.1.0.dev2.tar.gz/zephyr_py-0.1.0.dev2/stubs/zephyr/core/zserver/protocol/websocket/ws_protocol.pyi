"""Type stubs for zephyr.core.zserver.protocol.websocket.ws_protocol module."""

import asyncio
from typing import Any

from websockets.server import ServerProtocol

from zephyr._types import ASGIApplication, Scope
from zephyr.core.logging import Logger
from zephyr.core.zserver.config import ServerConfig
from zephyr.core.zserver.state import ServerState

class WebSocketProtocol(asyncio.Protocol):
    config: ServerConfig
    app: ASGIApplication
    loop: asyncio.AbstractEventLoop
    logger: Logger
    server_state: ServerState
    app_state: dict[str, Any]
    connections: set[Any]
    tasks: set[Any]
    transport: asyncio.Transport | None
    ws: ServerProtocol | None
    client: tuple[str, int] | None
    server: tuple[str, int] | None
    scope: Scope | None
    handshake_complete: bool
    closed: bool
    receive_queue: asyncio.Queue
    send_queue: asyncio.Queue
    asgi_task: asyncio.Task | None
    sender_task: asyncio.Task | None

    def __init__(
        self,
        config: ServerConfig,
        server_state: ServerState,
        app_state: dict[str, Any],
        _loop: asyncio.AbstractEventLoop | None = None,
    ) -> None: ...
    def connection_made(self, transport: asyncio.Transport) -> None: ...  # type: ignore[override]
    def connection_lost(self, exc: Exception | None) -> None: ...
    def data_received(self, data: bytes) -> None: ...
    async def asgi_receive(self) -> dict: ...
    async def asgi_send(self, message: dict) -> None: ...
    async def sender_loop(self) -> None: ...
    async def run_asgi(self) -> None: ...

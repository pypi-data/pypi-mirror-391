import contextlib
import socket
from _typeshed import Incomplete
from collections.abc import Generator
from zephyr.core.logging import get_logger as get_logger
from zephyr.core.zserver.config import ServerConfig as ServerConfig
from zephyr.core.zserver.lifespan import Lifespan as Lifespan
from zephyr.core.zserver.protocol.http.http import HTTPProtocol as HTTPProtocol
from zephyr.core.zserver.state import ServerState as ServerState

HANDLED_SIGNALS: Incomplete

class Server:
    logger: Incomplete
    config: Incomplete
    server_state: Incomplete
    started: bool
    should_exit: bool
    force_exit: bool
    lifespan: Incomplete
    captured_sigs: list[int]
    def __init__(self, config: ServerConfig) -> None: ...
    def run(self, sockets: list[socket.socket] | None = None) -> None: ...
    async def serve(self, sockets: list[socket.socket] | None = None) -> None: ...
    servers: Incomplete
    async def startup(self, sockets: list[socket.socket] | None = None) -> None: ...
    async def shutdown(self, sockets: list[socket.socket] | None = None) -> None: ...
    async def main_loop(self) -> None: ...
    @contextlib.contextmanager
    def capture_signals(self) -> Generator[None, None, None]: ...

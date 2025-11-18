import asyncio
import contextlib
import os
import signal
import socket
import sys
import threading
from collections.abc import Generator
from types import FrameType

from zephyr.core.logging import get_logger
from zephyr.core.zserver.config import ServerConfig
from zephyr.core.zserver.lifespan import Lifespan
from zephyr.core.zserver.protocol.http.http import HTTPProtocol
from zephyr.core.zserver.state import ServerState

HANDLED_SIGNALS = (
    signal.SIGINT,  # Unix signal 2. Sent by Ctrl+C.
    signal.SIGTERM,  # Unix signal 15. Sent by `kill <pid>`.
)
if sys.platform == "win32":  # pragma: py-not-win32
    HANDLED_SIGNALS += (signal.SIGBREAK,)  # Windows signal 21. Sent by Ctrl+Break.


class Server:
    def __init__(self, config: ServerConfig):
        self.logger = get_logger("ZServer")
        self.config = config
        self.server_state = ServerState()

        self.started = False
        self.started = False
        self.should_exit = False
        self.force_exit = False

        self.lifespan = Lifespan(config)

        self.logger.info("Server initialized: %s, %s", f"handler={config.app}", f"config={config}")

        self.captured_sigs: list[int] = []

    def run(self, sockets: list[socket.socket] | None = None) -> None:
        self.config.setup_event_loop()
        return asyncio.run(self.serve(sockets=sockets))

    async def serve(self, sockets: list[socket.socket] | None = None) -> None:
        with self.capture_signals():
            await self._serve(sockets)

    async def _serve(self, sockets: list[socket.socket] | None = None) -> None:
        pid = os.getpid()
        self.logger.info(f"Started zserver process [{pid}]")

        self.logger.debug("==== SERVER STARTING UP =====")
        self.logger.debug(f"Process ID: {pid}")

        await self.startup(sockets)
        if self.should_exit:
            print("Server should exit, returning early")
            return

        await self.main_loop()
        await self.shutdown(sockets)

        self.logger.info(f"Stopped zserver process [{pid}]")

    async def startup(self, sockets: list[socket.socket] | None = None) -> None:
        await self.lifespan.startup()
        if self.lifespan.should_exit:
            self.should_exit = True
            return

        config = self.config
        self.logger.info(f"Server started at http://{self.config.host}:{self.config.port}")

        def create_protocol(
            _loop: asyncio.AbstractEventLoop | None = None,
        ) -> asyncio.Protocol:
            return HTTPProtocol(  # type: ignore[call-arg]
                config=config,
                server_state=self.server_state,
                app_state=self.lifespan.state,
                _loop=_loop,
            )

        loop = asyncio.get_running_loop()

        try:
            server = await loop.create_server(
                create_protocol,
                host=config.host,
                port=config.port,
                backlog=config.backlog,
            )

        except OSError as exc:
            self.logger.error(exc)
            await self.lifespan.shutdown()
            sys.exit(1)

        assert server.sockets is not None
        listeners = server.sockets
        self.servers = [server]
        # self.logger.info(f"Server started at http://{self.config.host}:{self.config.port}")

    async def shutdown(self, sockets: list[socket.socket] | None = None) -> None:
        self.logger.info("Shutting down")

        # Stop accepting new connections.
        for server in self.servers:
            server.close()
        for sock in sockets or []:
            sock.close()  # pragma: full coverage

        # Request shutdown on all existing connections.
        for connection in list(self.server_state.connections):
            connection.shutdown()
        await asyncio.sleep(0.1)

        # When 3.10 is not supported anymore, use `async with asyncio.timeout(...):`.
        try:
            await asyncio.wait_for(
                self._wait_tasks_to_complete(),
                timeout=self.config.timeout_graceful_shutdown,
            )
        except asyncio.TimeoutError:
            self.logger.error(
                "Cancel %s running task(s), timeout graceful shutdown exceeded",
                len(self.server_state.tasks),
            )
            for t in self.server_state.tasks:
                t.cancel(msg="Task cancelled, timeout graceful shutdown exceeded")

        # Send the lifespan shutdown event, and wait for application shutdown.
        if not self.force_exit:
            await self.lifespan.shutdown()

    async def main_loop(self) -> None:
        """Main zserver loop."""
        try:
            while not self.should_exit:
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            self.should_exit = True
        except KeyboardInterrupt:
            self.should_exit = True
            if self.force_exit:
                raise

    @contextlib.contextmanager
    def capture_signals(self) -> Generator[None, None, None]:
        if threading.current_thread() is not threading.main_thread():
            yield
            return

        # Define signals to handle
        signals = (signal.SIGINT, signal.SIGTERM)
        if sys.platform == "win32":
            signals += (signal.SIGBREAK,)

        # Store original handlers
        original_handlers = {}

        def handle_signal(sig: int, frame: FrameType | None) -> None:
            """Inner signal handler."""
            if sig == signal.SIGINT:
                # Handle Ctrl+C
                if self.should_exit:
                    # Second Ctrl+C, force exit
                    self.force_exit = True
                    sys.exit(1)
                else:
                    # First Ctrl+C, graceful shutdown
                    print("\nShutting down gracefully (Ctrl+C again to force)")
                    self.should_exit = True
            else:
                # Other signals
                self.should_exit = True
                self.force_exit = True

        try:
            # Set up signal handlers
            for sig in signals:
                original_handlers[sig] = signal.signal(sig, handle_signal)
            yield
        finally:
            # Restore original handlers
            for sig, handler in original_handlers.items():
                signal.signal(sig, handler)

            # If we're force exiting, do it now
            if self.force_exit:
                sys.exit(1)

    async def _wait_tasks_to_complete(self) -> None:
        # Wait for existing connections to finish sending responses.
        if self.server_state.connections and not self.force_exit:
            msg = "Waiting for connections to close. (CTRL+C to force quit)"
            self.logger.info(msg)
            while self.server_state.connections and not self.force_exit:
                await asyncio.sleep(0.1)

        # Wait for existing tasks to complete.
        if self.server_state.tasks and not self.force_exit:
            msg = "Waiting for background tasks to complete. (CTRL+C to force quit)"
            self.logger.info(msg)
            while self.server_state.tasks and not self.force_exit:
                await asyncio.sleep(0.1)

        for server in self.servers:
            await server.wait_closed()


if __name__ == "__main__":

    async def app(sc, receive, send):
        """Example request handler."""
        if "path" in sc:
            if sc["path"] == "/hello":
                d = {
                    "status": 200,
                    "headers": {b"content-type": b"application/json"},
                    "body": {"content": f"Hello! You requested: {sc['path']}"},
                }

            else:
                d = {
                    "type": "http.response.start",
                    "status": 200,
                    "headers": {b"content-type": b"text/plain"},
                    "body": f"Hello! You requested: {sc['path']}".encode(),
                }
            await send(d)
            d = {
                "type": "http.response.body",
                "status": 200,
                "headers": {b"content-type": b"text/plain"},
                "body": f"Hello! You requested: {sc['path']}".encode(),
            }

            await send(d)

    server_config = ServerConfig(app)
    server = Server(server_config)
    server.run()

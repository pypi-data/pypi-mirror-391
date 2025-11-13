import asyncio

Protocols = type[asyncio.Protocol]


class ServerState:
    """
    Shared servers state that is available between all protocol instances.
    """

    def __init__(self) -> None:
        self.total_requests = 0
        self.requests_handled = 0
        self.errors = 0
        self.connections: set[Protocols] = set()
        self.protocols: set[Protocols] = set()
        self.tasks: set[asyncio.Task[None]] = set()
        self.default_headers: list[tuple[bytes, bytes]] = []

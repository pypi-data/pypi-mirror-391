import asyncio

Protocols = type[asyncio.Protocol]

class ServerState:
    total_requests: int
    requests_handled: int
    errors: int
    connections: set[Protocols]
    protocols: set[Protocols]
    tasks: set[asyncio.Task[None]]
    default_headers: list[tuple[bytes, bytes]]
    def __init__(self) -> None: ...

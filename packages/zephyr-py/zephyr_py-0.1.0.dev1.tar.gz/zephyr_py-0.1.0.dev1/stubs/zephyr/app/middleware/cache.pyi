from _typeshed import Incomplete
from zephyr._types import ASGIApp as ASGIApp, Receive as Receive, Scope as Scope, Send as Send
from zephyr.app.middleware.base import BaseMiddleware as BaseMiddleware
from zephyr.app.requests import Request as Request
from zephyr.app.responses import Response as Response

class CacheMiddleware(BaseMiddleware):
    ttl: Incomplete
    max_size: Incomplete
    def __init__(self, app: ASGIApp, ttl: int = 300, max_size: int = 1000) -> None: ...
    async def process_request(self, request, call_next): ...

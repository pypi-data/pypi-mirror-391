from _typeshed import Incomplete
from zephyr._types import ASGIApp as ASGIApp, Receive as Receive, Scope as Scope, Send as Send
from zephyr.app.middleware.base import BaseMiddleware as BaseMiddleware
from zephyr.app.requests import Request as Request
from zephyr.app.responses import JSONResponse as JSONResponse, Response as Response

class RateLimitMiddleware(BaseMiddleware):
    requests: Incomplete
    window: Incomplete
    storage: Incomplete
    def __init__(self, app: ASGIApp, requests: int = 1000, window: int = 60, storage: str = 'memory') -> None: ...
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None: ...

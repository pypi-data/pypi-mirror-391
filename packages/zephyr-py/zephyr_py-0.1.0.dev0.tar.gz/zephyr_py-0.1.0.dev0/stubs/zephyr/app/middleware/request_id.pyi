from _typeshed import Incomplete
from zephyr._types import ASGIApp as ASGIApp, Receive as Receive, Scope as Scope, Send as Send
from zephyr.app.middleware.base import BaseMiddleware as BaseMiddleware
from zephyr.app.requests import Request as Request
from zephyr.app.responses import Response as Response

class RequestIDMiddleware(BaseMiddleware):
    header_name: Incomplete
    def __init__(self, app: ASGIApp, header_name: str = 'X-Request-ID') -> None: ...
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None: ...

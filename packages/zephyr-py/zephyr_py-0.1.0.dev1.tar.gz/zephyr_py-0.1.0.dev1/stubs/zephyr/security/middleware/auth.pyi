from _typeshed import Incomplete
from zephyr._types import ASGIApp as ASGIApp, Receive as Receive, Scope as Scope, Send as Send
from zephyr.app.middleware.base import BaseMiddleware as BaseMiddleware
from zephyr.security.backends import AuthenticationBackend as AuthenticationBackend, AuthenticationError as AuthenticationError
from zephyr.security.user import AnonymousUser as AnonymousUser

class BearerAuthMiddleware(BaseMiddleware):
    backend: Incomplete
    exclude_paths: Incomplete
    def __init__(self, app: ASGIApp, backend: AuthenticationBackend, exclude_paths: list[str] | None = None) -> None: ...
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None: ...

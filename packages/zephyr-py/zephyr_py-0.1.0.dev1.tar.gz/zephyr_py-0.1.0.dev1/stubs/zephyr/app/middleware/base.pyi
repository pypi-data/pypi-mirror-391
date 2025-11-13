from _typeshed import Incomplete
from collections.abc import Iterator
from typing import Any, ParamSpec, Protocol
from zephyr._types import ASGIApp as ASGIApp, Receive as Receive, Scope as Scope, Send as Send

P = ParamSpec('P')

class _MiddlewareFactory(Protocol[P]):
    def __call__(self, app: ASGIApp, /, *args: P.args, **kwargs: P.kwargs) -> ASGIApp: ...

class Middleware:
    cls: Incomplete
    args: Incomplete
    kwargs: Incomplete
    def __init__(self, cls: _MiddlewareFactory[P], *args: P.args, **kwargs: P.kwargs) -> None: ...
    def __iter__(self) -> Iterator[Any]: ...

class BaseMiddleware:
    app: Incomplete
    def __init__(self, app: ASGIApp) -> None: ...
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None: ...

from __future__ import annotations

import sys
from collections.abc import Iterator
from typing import Any, Protocol

if sys.version_info >= (3, 10):  # pragma: no cover
    from typing import ParamSpec
else:  # pragma: no cover
    from typing_extensions import ParamSpec

from zephyr._types import ASGIApp, Scope, Receive, Send

P = ParamSpec("P")


class _MiddlewareFactory(Protocol[P]):
    def __call__(self, app: ASGIApp, /, *args: P.args, **kwargs: P.kwargs) -> ASGIApp: ...  # pragma: no cover


class Middleware:
    def __init__(
        self,
        cls: _MiddlewareFactory[P],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> None:
        self.cls = cls
        self.args = args
        self.kwargs = kwargs

    def __iter__(self) -> Iterator[Any]:
        as_tuple = (self.cls, self.args, self.kwargs)
        return iter(as_tuple)

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        args_strings = [f"{value!r}" for value in self.args]
        option_strings = [f"{key}={value!r}" for key, value in self.kwargs.items()]
        name = getattr(self.cls, "__name__", "")
        args_repr = ", ".join([name] + args_strings + option_strings)
        return f"{class_name}({args_repr})"


class BaseMiddleware:
    """
    Base class for all Zephyr middleware.

    Provides common ASGI middleware functionality and type safety.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        ASGI middleware entry point.

        Override this method in subclasses to implement middleware logic.
        """
        await self.app(scope, receive, send)

    def _is_http_request(self, scope: Scope) -> bool:
        """Check if the scope is an HTTP request."""
        return scope["type"] == "http"

    def _get_headers(self, scope: Scope) -> dict[bytes, bytes]:
        """Extract headers from ASGI scope."""
        return dict(scope.get("headers", []))

    def _set_headers(self, headers: list[tuple[bytes, bytes]], name: str, value: str) -> list[tuple[bytes, bytes]]:
        """Add or update a header in the headers list."""
        name_bytes = name.lower().encode()
        value_bytes = value.encode()

        # Remove existing header if present
        headers = [(n, v) for n, v in headers if n != name_bytes]

        # Add new header
        headers.append((name_bytes, value_bytes))
        return headers

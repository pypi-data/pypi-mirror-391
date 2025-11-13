from __future__ import annotations

import typing

from zephyr.app._utils import is_async_callable
from zephyr.app.concurrency import run_in_threadpool
from zephyr.app.exceptions import HTTPException
from zephyr.app.requests import Request
from zephyr._types import ASGIApp, ExceptionHandler, Message, Receive, Scope, Send

# from zephyr.app.websockets import WebSocket

ExceptionHandlers = dict[typing.Any, ExceptionHandler]
StatusHandlers = dict[int, ExceptionHandler]


def _lookup_exception_handler(exc_handlers: ExceptionHandlers, exc: Exception) -> ExceptionHandler | None:
    for cls in type(exc).__mro__:
        if cls in exc_handlers:
            return exc_handlers[cls]
    return None


def wrap_app_handling_exceptions(app: ASGIApp, conn: Request | WebSocket) -> ASGIApp:
    exception_handlers: ExceptionHandlers
    status_handlers: StatusHandlers
    try:
        exception_handlers, status_handlers = conn.scope["zephyr.exception_handlers"]
    except KeyError:
        exception_handlers, status_handlers = {}, {}

    async def wrapped_app(scope: Scope, receive: Receive, send: Send) -> None:
        response_started = False

        async def sender(message: Message) -> None:
            nonlocal response_started

            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        try:
            await app(scope, receive, sender)
        except Exception as exc:
            handler = None

            if isinstance(exc, HTTPException):
                handler = status_handlers.get(exc.status_code)

            if handler is None:
                handler = _lookup_exception_handler(exception_handlers, exc)

            if handler is None:
                raise exc

            if response_started:
                raise RuntimeError("Caught handled exception, but response already started.") from exc

            if is_async_callable(handler):
                response = await handler(conn, exc)
            else:
                response = await run_in_threadpool(handler, conn, exc)  # type: ignore
            if response is not None:
                await response(scope, receive, sender)

    return wrapped_app

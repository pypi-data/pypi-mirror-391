import typing
from zephyr._types import ASGIApp as ASGIApp, ExceptionHandler as ExceptionHandler, Message as Message, Receive as Receive, Scope as Scope, Send as Send
from zephyr.app._utils import is_async_callable as is_async_callable
from zephyr.app.concurrency import run_in_threadpool as run_in_threadpool
from zephyr.app.exceptions import HTTPException as HTTPException
from zephyr.app.requests import Request as Request

ExceptionHandlers = dict[typing.Any, ExceptionHandler]
StatusHandlers = dict[int, ExceptionHandler]

def wrap_app_handling_exceptions(app: ASGIApp, conn: Request | WebSocket) -> ASGIApp: ...

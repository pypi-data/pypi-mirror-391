from _typeshed import Incomplete
from collections.abc import Callable as Callable
from typing_extensions import Annotated
from zephyr._types import ASGIApp as ASGIApp, AppType as AppType, Lifespan as Lifespan, Receive as Receive, Scope as Scope, Send as Send
from zephyr.app import routing as routing
from zephyr.app._utils import generate_unique_id as generate_unique_id
from zephyr.app.datastructures import Default as Default, State as State
from zephyr.app.middleware import Middleware as Middleware
from zephyr.app.requests import Request as Request
from zephyr.app.responses import Response as Response
from zephyr.app.routing import BaseRoute as BaseRoute
from zephyr.conf import settings as settings
from zephyr.core.logging import get_logger as get_logger

class Zephyr:
    logger: Incomplete
    debug: Incomplete
    title: Incomplete
    version: Incomplete
    description: Incomplete
    root_path: Incomplete
    router: routing.Router
    state: Incomplete
    exception_handlers: Incomplete
    user_middleware: Incomplete
    middleware_stack: ASGIApp | None
    def __init__(self, *, debug: bool | None = None, routes: Annotated[list[BaseRoute] | None, None, None] = None, title: Annotated[str, None] = 'Zephyr', version: str = '1.0.0', description: str | None = None, root_path: str = '', lifespan: Annotated[Lifespan[AppType] | None, None] = None, generate_unique_id_function: Annotated[Callable[[routing.Route], str], None] = ...) -> None: ...
    def build_middleware_stack(self) -> ASGIApp: ...
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None: ...
    def get(self, path: str, *, status_code: int | None = None): ...
    def put(self, path: str, *, status_code: int | None = None): ...
    def post(self, path: str, *, status_code: int | None = None): ...
    def delete(self, path: str, *, status_code: int | None = None): ...
    def middleware(self, middleware_class, *args, **kwargs): ...
    def add_middleware(self, middleware_class, *args, **kwargs): ...
    def use_cors(self, **kwargs): ...

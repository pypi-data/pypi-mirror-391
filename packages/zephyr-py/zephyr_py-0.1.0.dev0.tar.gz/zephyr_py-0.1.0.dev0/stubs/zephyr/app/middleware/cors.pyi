from _typeshed import Incomplete
from collections.abc import Sequence
from zephyr._types import ASGIApp as ASGIApp, Receive as Receive, Scope as Scope, Send as Send
from zephyr.app.datastructures import Headers as Headers, MutableHeaders as MutableHeaders
from zephyr.app.requests import Request as Request
from zephyr.app.responses import PlainTextResponse as PlainTextResponse, Response as Response
from zephyr.core.logging.logger import get_logger as get_logger

ALL_METHODS: Incomplete
SAFELISTED_HEADERS: Incomplete

class CORSMiddleware:
    app: Incomplete
    allow_origins: Incomplete
    allow_methods: Incomplete
    allow_headers: Incomplete
    allow_all_origins: Incomplete
    allow_all_headers: Incomplete
    preflight_explicit_allow_origin: Incomplete
    allow_origin_regex: Incomplete
    simple_headers: Incomplete
    preflight_headers: Incomplete
    def __init__(self, app: ASGIApp, allow_origins: Sequence[str] = (), allow_methods: Sequence[str] = ('GET',), allow_headers: Sequence[str] = (), allow_credentials: bool = False, allow_origin_regex: str | None = None, expose_headers: Sequence[str] = (), max_age: int = 600) -> None: ...
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None: ...
    def is_allowed_origin(self, origin: str) -> bool: ...
    def preflight_response(self, request_headers: Headers) -> Response: ...
    async def simple_response(self, scope: Scope, receive: Receive, send: Send, request_headers: Headers) -> None: ...
    async def send(self, message: Message, send: Send, request_headers: Headers) -> None: ...
    @staticmethod
    def allow_explicit_origin(headers: MutableHeaders, origin: str) -> None: ...

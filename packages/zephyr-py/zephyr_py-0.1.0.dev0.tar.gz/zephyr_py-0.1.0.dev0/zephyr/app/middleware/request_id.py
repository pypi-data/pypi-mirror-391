"""Request ID middleware for Zephyr applications."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from zephyr.app.middleware.base import BaseMiddleware

if TYPE_CHECKING:
    from zephyr._types import ASGIApp, Scope, Receive, Send
    from zephyr.app.requests import Request
    from zephyr.app.responses import Response


class RequestIDMiddleware(BaseMiddleware):
    """
    Middleware that adds a unique request ID to each request.

    The request ID is added to:
    - Request headers as 'X-Request-ID'
    - Response headers as 'X-Request-ID'
    - Request state for access in route handlers
    """

    def __init__(self, app: ASGIApp, header_name: str = "X-Request-ID") -> None:
        super().__init__(app)
        self.header_name = header_name

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if not self._is_http_request(scope):
            await self.app(scope, receive, send)
            return

        # Generate or get request ID
        headers = self._get_headers(scope)
        request_id = headers.get(self.header_name.lower().encode())
        if not request_id:
            request_id = str(uuid.uuid4())
        else:
            request_id = request_id.decode()

        # Add to scope for access in handlers
        scope["state"] = scope.get("state", {})
        scope["state"]["request_id"] = request_id

        # Process request
        async def send_wrapper(message: dict[str, object]) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers = self._set_headers(headers, self.header_name, request_id)
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_wrapper)

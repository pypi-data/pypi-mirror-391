"""Rate limiting middleware for Zephyr applications."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from zephyr.app.middleware.base import BaseMiddleware
from zephyr.app.responses import JSONResponse

if TYPE_CHECKING:
    from zephyr._types import ASGIApp, Scope, Receive, Send
    from zephyr.app.requests import Request
    from zephyr.app.responses import Response


class RateLimitMiddleware(BaseMiddleware):
    """
    Simple in-memory rate limiting middleware.

    Tracks requests per client IP and enforces rate limits.
    """

    def __init__(self, app: ASGIApp, requests: int = 1000, window: int = 60, storage: str = "memory") -> None:
        super().__init__(app)
        self.requests = requests
        self.window = window
        self.storage = storage

        # Simple in-memory storage
        self._requests: dict[str, list[float]] = {}

    def _is_rate_limited(self, client_ip: str) -> bool:
        """Check if client is rate limited."""
        now = time.time()

        # Clean old requests outside the window
        if client_ip in self._requests:
            self._requests[client_ip] = [
                req_time for req_time in self._requests[client_ip] if now - req_time < self.window
            ]
        else:
            self._requests[client_ip] = []

        # Check if limit exceeded
        if len(self._requests[client_ip]) >= self.requests:
            return True

        # Add current request
        self._requests[client_ip].append(now)
        return False

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if not self._is_http_request(scope):
            await self.app(scope, receive, send)
            return

        # Get client IP from headers
        headers = self._get_headers(scope)
        client_ip = self._get_client_ip_from_headers(headers)

        if self._is_rate_limited(client_ip):
            # Send rate limit response
            response_body = (
                b'{"error": "Rate limit exceeded", "message": "Too many requests", "retry_after": '
                + str(self.window).encode()
                + b"}"
            )

            await send(
                {
                    "type": "http.response.start",
                    "status": 429,
                    "headers": [
                        [b"content-type", b"application/json"],
                        [b"retry-after", str(self.window).encode()],
                    ],
                }
            )
            await send(
                {
                    "type": "http.response.body",
                    "body": response_body,
                }
            )
            return

        # Process request normally
        await self.app(scope, receive, send)

    def _get_client_ip_from_headers(self, headers: dict[bytes, bytes]) -> str:
        """Get client IP from ASGI headers."""
        # Check X-Forwarded-For header
        forwarded_for = headers.get(b"x-forwarded-for")
        if forwarded_for:
            return forwarded_for.decode().split(",")[0].strip()

        # Check X-Real-IP header
        real_ip = headers.get(b"x-real-ip")
        if real_ip:
            return real_ip.decode()

        # Fallback to direct connection (would need to be passed from server)
        return "unknown"

"""WebSocket CSP middleware to allow browser WebSocket connections.

Author: A M (am@bbdevs.com)

Created At: 13 Nov 2025
"""

from zephyr._types import Scope, Receive, Send, ASGIApp
from zephyr.app.middleware.base import BaseMiddleware


class WebSocketCSPMiddleware(BaseMiddleware):
    """WebSocket CSP middleware to allow browser WebSocket connections."""

    def __init__(self, app: ASGIApp) -> None:
        """Initialize the WebSocket CSP middleware."""
        super().__init__(app)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Call the WebSocket CSP middleware."""
        self.logger.debug("Calling WebSocket CSP middleware, scope: %s", scope)
        if scope["type"] != "http":
            self.logger.debug("Scope is not an HTTP request, skipping WebSocket CSP middleware")
            await self.app(scope, receive, send)
            return

        async def send_with_csp(message):
            """Send the message with the WebSocket CSP headers."""
            self.logger.debug("Sending message with WebSocket CSP headers")
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                # Add WebSocket-friendly CSP headers
                headers.append(
                    (
                        b"content-security-policy",
                        b"default-src 'self'; connect-src 'self' ws: wss: http: https:; "
                        b"script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; "
                        b"img-src 'self' data: http: https:;",
                    )
                )
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_with_csp)

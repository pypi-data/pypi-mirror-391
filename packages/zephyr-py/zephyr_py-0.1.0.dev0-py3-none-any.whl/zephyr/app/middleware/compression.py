"""Compression middleware for Zephyr applications."""

from __future__ import annotations

import gzip
from typing import TYPE_CHECKING

from zephyr.app.middleware.base import BaseMiddleware

if TYPE_CHECKING:
    from zephyr._types import ASGIApp, Scope, Receive, Send
    from zephyr.app.requests import Request
    from zephyr.app.responses import Response


class CompressionMiddleware(BaseMiddleware):
    """
    Gzip compression middleware.

    Compresses response content when the client supports it.
    """

    def __init__(self, app: ASGIApp, minimum_size: int = 500) -> None:
        super().__init__(app)
        self.minimum_size = minimum_size

    def _should_compress(self, request: Request, response: Response) -> bool:
        """Check if response should be compressed."""
        # Check if client accepts gzip
        accept_encoding = request.headers.get("Accept-Encoding", "")
        if "gzip" not in accept_encoding:
            return False

        # Check content type
        content_type = response.headers.get("Content-Type", "")
        if not content_type.startswith(("text/", "application/json", "application/javascript")):
            return False

        # Check content length
        content_length = response.headers.get("Content-Length")
        if content_length and int(content_length) < self.minimum_size:
            return False

        return True

    async def process_request(self, request, call_next):
        response = await call_next(request)

        if self._should_compress(request, response):
            # Get response body
            body = b""
            if hasattr(response, "body_iterator"):
                async for chunk in response.body_iterator:
                    body += chunk
            elif hasattr(response, "body"):
                body = response.body
            else:
                return response

            # Compress the body
            compressed_body = gzip.compress(body)

            # Update response
            response.body = compressed_body
            response.headers["Content-Encoding"] = "gzip"
            response.headers["Content-Length"] = str(len(compressed_body))

        return response

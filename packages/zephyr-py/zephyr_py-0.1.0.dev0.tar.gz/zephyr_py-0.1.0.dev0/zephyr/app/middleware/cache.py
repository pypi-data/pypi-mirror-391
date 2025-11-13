"""Cache middleware for Zephyr applications."""

from __future__ import annotations

import hashlib
import time
from typing import TYPE_CHECKING

from zephyr.app.middleware.base import BaseMiddleware

if TYPE_CHECKING:
    from zephyr._types import ASGIApp, Scope, Receive, Send
    from zephyr.app.requests import Request
    from zephyr.app.responses import Response


class CacheMiddleware(BaseMiddleware):
    """
    Simple in-memory cache middleware.

    Caches GET requests based on URL and query parameters.
    """

    def __init__(self, app: ASGIApp, ttl: int = 300, max_size: int = 1000) -> None:
        super().__init__(app)
        self.ttl = ttl
        self.max_size = max_size
        self._cache: dict[str, tuple[object, float]] = {}

    def _get_cache_key(self, request) -> str:
        """Generate cache key from request."""
        # Use URL and query parameters
        url = str(getattr(request, "url", request.path))
        key = hashlib.md5(url.encode()).hexdigest()
        return f"cache:{key}"

    def _is_cacheable(self, request, response) -> bool:
        """Check if response should be cached."""
        # Only cache GET requests
        if request.method != "GET":
            return False

        # Only cache successful responses
        if response.status_code != 200:
            return False

        # Check cache control headers
        cache_control = response.headers.get("Cache-Control", "")
        if "no-cache" in cache_control or "no-store" in cache_control:
            return False

        return True

    def _get_cached_response(self, cache_key: str) -> object | None:
        """Get cached response if valid."""
        if cache_key not in self._cache:
            return None

        response, timestamp = self._cache[cache_key]

        # Check if expired
        if time.time() - timestamp > self.ttl:
            del self._cache[cache_key]
            return None

        return response

    def _cache_response(self, cache_key: str, response) -> None:
        """Cache response."""
        # Simple LRU: remove oldest if at max size
        if len(self._cache) >= self.max_size:
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][1])
            del self._cache[oldest_key]

        self._cache[cache_key] = (response, time.time())

    async def process_request(self, request, call_next):
        # Only process GET requests
        if request.method != "GET":
            return await call_next(request)

        cache_key = self._get_cache_key(request)

        # Check cache
        cached_response = self._get_cached_response(cache_key)
        if cached_response:
            return cached_response

        # Process request
        response = await call_next(request)

        # Cache if appropriate
        if self._is_cacheable(request, response):
            self._cache_response(cache_key, response)

        return response

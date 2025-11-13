"""Tracing middleware for Zephyr applications."""

from __future__ import annotations

import time
import uuid
from typing import TYPE_CHECKING

from zephyr.app.middleware.base import BaseMiddleware

if TYPE_CHECKING:
    from zephyr._types import ASGIApp, Scope, Receive, Send
    from zephyr.app.requests import Request
    from zephyr.app.responses import Response


class TracingMiddleware(BaseMiddleware):
    """
    Basic tracing middleware for request tracking.

    Adds trace IDs and timing information to requests.
    """

    def __init__(self, app: ASGIApp, trace_header: str = "X-Trace-ID") -> None:
        super().__init__(app)
        self.trace_header = trace_header
        self.traces: dict[str, dict[str, object]] = {}

    def _generate_trace_id(self) -> str:
        """Generate a unique trace ID."""
        return str(uuid.uuid4())

    def _get_trace_id(self, request) -> str:
        """Get trace ID from headers or generate new one."""
        trace_id = request.headers.get(self.trace_header)
        if not trace_id:
            trace_id = self._generate_trace_id()
        return trace_id

    def _start_trace(self, trace_id: str, request) -> None:
        """Start tracing for a request."""
        self.traces[trace_id] = {
            "start_time": time.time(),
            "method": request.method,
            "path": request.path,
            "headers": dict(request.headers),
            "query_params": dict(getattr(request, "query_params", {})),
        }

    def _end_trace(self, trace_id: str, response) -> None:
        """End tracing for a request."""
        if trace_id in self.traces:
            self.traces[trace_id].update(
                {
                    "end_time": time.time(),
                    "duration": time.time() - self.traces[trace_id]["start_time"],
                    "status_code": response.status_code,
                }
            )

    def _cleanup_old_traces(self) -> None:
        """Remove old traces to prevent memory leaks."""
        current_time = time.time()
        to_remove = [
            trace_id
            for trace_id, trace in self.traces.items()
            if current_time - trace.get("start_time", 0) > 3600  # 1 hour
        ]
        for trace_id in to_remove:
            del self.traces[trace_id]

    async def process_request(self, request, call_next):
        """Process incoming request."""
        trace_id = self._get_trace_id(request)
        self._start_trace(trace_id, request)

        # Add trace ID to request state
        request.state.trace_id = trace_id

        # Add trace ID to response headers
        response = await call_next(request)
        response.headers[self.trace_header] = trace_id

        self._end_trace(trace_id, response)
        self._cleanup_old_traces()

        return response

    def get_trace(self, trace_id: str) -> dict[str, object]:
        """Get trace information by ID."""
        return self.traces.get(trace_id, {})

    def get_all_traces(self) -> dict[str, dict[str, object]]:
        """Get all traces."""
        return self.traces.copy()

"""Metrics middleware for Zephyr applications."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from zephyr.app.middleware.base import BaseMiddleware

if TYPE_CHECKING:
    from zephyr._types import ASGIApp, Scope, Receive, Send
    from zephyr.app.requests import Request
    from zephyr.app.responses import Response


class MetricsMiddleware(BaseMiddleware):
    """
    Basic metrics collection middleware.

    Collects request count, response time, and status codes.
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self.metrics = {
            "requests_total": 0,
            "requests_by_status": {},
            "requests_by_method": {},
            "response_times": [],
            "active_requests": 0,
        }

    def _record_metrics(self, request, response, duration: float):
        """Record metrics for the request."""
        # Increment total requests
        self.metrics["requests_total"] += 1

        # Record by status code
        status = str(response.status_code)
        self.metrics["requests_by_status"][status] = self.metrics["requests_by_status"].get(status, 0) + 1

        # Record by method
        method = request.method
        self.metrics["requests_by_method"][method] = self.metrics["requests_by_method"].get(method, 0) + 1

        # Record response time
        self.metrics["response_times"].append(duration)

        # Keep only last 1000 response times
        if len(self.metrics["response_times"]) > 1000:
            self.metrics["response_times"] = self.metrics["response_times"][-1000:]

    def get_metrics(self) -> dict:
        """Get current metrics."""
        metrics = self.metrics.copy()

        # Calculate average response time
        if metrics["response_times"]:
            metrics["avg_response_time"] = sum(metrics["response_times"]) / len(metrics["response_times"])
        else:
            metrics["avg_response_time"] = 0

        return metrics

    def reset_metrics(self):
        """Reset all metrics."""
        self.metrics = {
            "requests_total": 0,
            "requests_by_status": {},
            "requests_by_method": {},
            "response_times": [],
            "active_requests": 0,
        }

    async def process_request(self, request, call_next):
        start_time = time.time()
        self.metrics["active_requests"] += 1

        try:
            response = await call_next(request)
            return response
        finally:
            duration = time.time() - start_time
            self.metrics["active_requests"] -= 1
            self._record_metrics(request, response, duration)

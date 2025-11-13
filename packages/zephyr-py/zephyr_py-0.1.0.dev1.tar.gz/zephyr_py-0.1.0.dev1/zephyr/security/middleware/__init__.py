"""
Authentication middleware for Zephyr.

Provides middleware for handling authentication in ASGI applications.
"""

from .auth import BearerAuthMiddleware

__all__ = [
    "BearerAuthMiddleware",
]

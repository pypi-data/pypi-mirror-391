"""
Bearer authentication middleware for Zephyr.

Extracts Bearer tokens from Authorization header and authenticates users.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from zephyr.app.middleware.base import BaseMiddleware
from zephyr.security.backends import AuthenticationBackend, AuthenticationError
from zephyr.security.user import AnonymousUser

if TYPE_CHECKING:
    from zephyr._types import ASGIApp, Scope, Receive, Send


class BearerAuthMiddleware(BaseMiddleware):
    """
    Bearer token authentication middleware.

    Extracts Bearer tokens from Authorization header, authenticates users,
    and sets user information in the ASGI scope.
    """

    def __init__(self, app: ASGIApp, backend: AuthenticationBackend, exclude_paths: list[str] | None = None) -> None:
        """
        Initialize Bearer authentication middleware.

        Args:
            app: ASGI application
            backend: Authentication backend to use
            exclude_paths: List of paths to exclude from authentication
        """
        super().__init__(app)
        self.backend = backend
        self.exclude_paths = exclude_paths or []

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Process request and authenticate user.

        Args:
            scope: ASGI scope
            receive: ASGI receive callable
            send: ASGI send callable
        """
        if not self._is_http_request(scope):
            await self.app(scope, receive, send)
            return

        # Check if path should be excluded from authentication
        path = scope.get("path", "")
        if self._should_exclude_path(path):
            # Set anonymous user for excluded paths
            scope["user"] = AnonymousUser()
            scope["auth"] = {"authenticated": False, "method": None}
            await self.app(scope, receive, send)
            return

        # Extract Bearer token from Authorization header
        token = self._extract_bearer_token(scope)

        if not token:
            # No token provided, set anonymous user
            scope["user"] = AnonymousUser()
            scope["auth"] = {"authenticated": False, "method": None}
            await self.app(scope, receive, send)
            return

        try:
            # Authenticate user
            user = await self.backend.authenticate(token)

            if user:
                # Authentication successful
                scope["user"] = user
                scope["auth"] = {"authenticated": True, "method": "bearer", "token": token, "user_id": user.id}
            else:
                # Authentication failed
                scope["user"] = AnonymousUser()
                scope["auth"] = {"authenticated": False, "method": "bearer", "error": "Invalid token"}

        except AuthenticationError as e:
            # Authentication error
            scope["user"] = AnonymousUser()
            scope["auth"] = {"authenticated": False, "method": "bearer", "error": str(e)}
        except Exception as e:
            # Unexpected error
            scope["user"] = AnonymousUser()
            scope["auth"] = {"authenticated": False, "method": "bearer", "error": "Authentication failed"}

        await self.app(scope, receive, send)

    def _should_exclude_path(self, path: str) -> bool:
        """
        Check if path should be excluded from authentication.

        Args:
            path: Request path

        Returns:
            True if path should be excluded, False otherwise
        """
        if not path:
            return False

        # Check exact matches
        if path in self.exclude_paths:
            return True

        # Check prefix matches
        for exclude_path in self.exclude_paths:
            if path.startswith(exclude_path):
                return True

        return False

    def _extract_bearer_token(self, scope: Scope) -> str | None:
        """
        Extract Bearer token from Authorization header.

        Args:
            scope: ASGI scope

        Returns:
            Bearer token if found, None otherwise
        """
        headers = self._get_headers(scope)

        # Look for Authorization header
        auth_header = headers.get(b"authorization")
        if not auth_header:
            return None

        # Decode header value
        try:
            auth_value = auth_header.decode("utf-8")
        except UnicodeDecodeError:
            return None

        # Check for Bearer token
        if not auth_value.lower().startswith("bearer "):
            return None

        # Extract token
        token = auth_value[7:].strip()  # Remove "Bearer " prefix
        if not token:
            return None

        return token

"""
Authentication backends for Zephyr.

Provides pluggable authentication backends for different authentication methods.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .jwt import JWTManager
from .tokens import TokenManager
from .user import User, AnonymousUser

if TYPE_CHECKING:
    from zephyr._types import ASGIApp, Scope, Receive, Send


class AuthenticationError(Exception):
    """Base authentication error."""

    pass


class AuthenticationBackend:
    """
    Base authentication backend.

    All authentication backends must inherit from this class and implement
    the authenticate method.
    """

    async def authenticate(self, token: str) -> User | None:
        """
        Authenticate token and return User or None.

        Args:
            token: Authentication token

        Returns:
            User object if authentication successful, None otherwise

        Raises:
            AuthenticationError: If authentication fails
        """
        raise NotImplementedError("Subclasses must implement authenticate method")

    async def get_user(self, user_id: str) -> User | None:
        """
        Load user by ID.

        Args:
            user_id: User identifier

        Returns:
            User object if found, None otherwise
        """
        # Default implementation returns None
        # Subclasses should override to load from database/cache
        return None


class JWTAuthenticationBackend(AuthenticationBackend):
    """
    JWT-based authentication backend.

    Authenticates users using JWT tokens with blacklist checking.
    """

    def __init__(self, jwt_manager: JWTManager, token_manager: TokenManager) -> None:
        """
        Initialize JWT authentication backend.

        Args:
            jwt_manager: JWT manager instance
            token_manager: Token manager instance
        """
        self.jwt_manager = jwt_manager
        self.token_manager = token_manager

    async def authenticate(self, token: str) -> User | None:
        """
        Verify JWT, check blacklist, load user.

        Args:
            token: JWT token string

        Returns:
            User object if authentication successful, None otherwise

        Raises:
            AuthenticationError: If authentication fails
        """
        if not token:
            return None

        try:
            # Verify token
            payload = await self.jwt_manager.verify_token(token, "access")

            # Check if token is revoked
            if await self.token_manager.is_revoked(token):
                return None

            # Load user
            user = await self.get_user(payload.sub)
            if not user:
                return None

            # Check if user is active
            if not user.is_active:
                return None

            return user

        except Exception as e:
            # Log error but don't expose details
            raise AuthenticationError(f"Authentication failed: {e}") from e

    async def get_user(self, user_id: str) -> User | None:
        """
        Load user from database/cache.

        Args:
            user_id: User identifier

        Returns:
            User object if found, None otherwise
        """
        # This is a simplified implementation
        # In a real application, you would:
        # 1. Query database/cache for user
        # 2. Load user roles and permissions
        # 3. Return User object

        # For now, return a mock user
        # In production, replace with actual user loading logic
        if user_id:
            return User(
                id=user_id,
                username=f"user_{user_id}",
                email=f"user_{user_id}@example.com",
                is_active=True,
                is_superuser=False,
                roles=["user"],
                permissions=["read"],
                mfa_enabled=False,
            )

        return None


class TokenAuthenticationBackend(AuthenticationBackend):
    """
    API token-based authentication backend.

    Authenticates users using simple API tokens (not JWT).
    """

    def __init__(self, token_validator: callable[[str], bool]) -> None:
        """
        Initialize token authentication backend.

        Args:
            token_validator: Function to validate API tokens
        """
        self.token_validator = token_validator

    async def authenticate(self, token: str) -> User | None:
        """
        Validate API token and return user.

        Args:
            token: API token string

        Returns:
            User object if authentication successful, None otherwise
        """
        if not token:
            return None

        try:
            # Validate token
            if not self.token_validator(token):
                return None

            # Extract user ID from token (simplified)
            # In a real implementation, you would decode the token
            # to get the user ID
            user_id = f"token_user_{hash(token) % 10000}"

            # Load user
            user = await self.get_user(user_id)
            if not user:
                return None

            # Check if user is active
            if not user.is_active:
                return None

            return user

        except Exception as e:
            raise AuthenticationError(f"Token authentication failed: {e}") from e

    async def get_user(self, user_id: str) -> User | None:
        """
        Load user by ID.

        Args:
            user_id: User identifier

        Returns:
            User object if found, None otherwise
        """
        # Simplified implementation
        if user_id:
            return User(
                id=user_id,
                username=f"token_user_{user_id}",
                email=f"token_user_{user_id}@example.com",
                is_active=True,
                is_superuser=False,
                roles=["api_user"],
                permissions=["api_access"],
                mfa_enabled=False,
            )

        return None


class NoAuthenticationBackend(AuthenticationBackend):
    """
    No authentication backend.

    Always returns AnonymousUser for testing or public endpoints.
    """

    async def authenticate(self, token: str) -> User | None:
        """
        Always return AnonymousUser.

        Args:
            token: Authentication token (ignored)

        Returns:
            AnonymousUser instance
        """
        return AnonymousUser()

    async def get_user(self, user_id: str) -> User | None:
        """
        Always return AnonymousUser.

        Args:
            user_id: User identifier (ignored)

        Returns:
            AnonymousUser instance
        """
        return AnonymousUser()

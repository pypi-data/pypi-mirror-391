"""
Token management and blacklisting for Zephyr.

Provides token revocation, blacklisting, and cleanup capabilities.
"""

from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING

from .jwt import JWTManager, JWTError

if TYPE_CHECKING:
    pass


class TokenError(Exception):
    """Base token error."""

    pass


class TokenBlacklistError(TokenError):
    """Token blacklist error."""

    pass


class TokenManagerError(TokenError):
    """Token manager error."""

    pass


class TokenBlacklist:
    """
    Token blacklist for revoking JWT tokens.

    Provides in-memory token blacklisting with automatic cleanup
    of expired tokens. Can be extended to use Redis or database backends.
    """

    def __init__(self, backend: str = "memory") -> None:
        """
        Initialize token blacklist.

        Args:
            backend: Backend type ("memory", "redis", "database")
        """
        self.backend = backend
        self._blacklist: dict[str, int] = {}  # jti -> expiration timestamp
        self._lock = asyncio.Lock()

    async def add(self, jti: str, exp: int) -> None:
        """
        Add token to blacklist with expiration.

        Args:
            jti: JWT ID (unique token identifier)
            exp: Token expiration timestamp

        Raises:
            TokenBlacklistError: If adding to blacklist fails
        """
        if not jti:
            raise TokenBlacklistError("JTI cannot be empty")

        if exp <= int(time.time()):
            # Token already expired, no need to blacklist
            return

        try:
            async with self._lock:
                self._blacklist[jti] = exp
        except Exception as e:
            raise TokenBlacklistError(f"Failed to add token to blacklist: {e}") from e

    async def is_blacklisted(self, jti: str) -> bool:
        """
        Check if token is blacklisted.

        Args:
            jti: JWT ID to check

        Returns:
            True if token is blacklisted, False otherwise
        """
        if not jti:
            return False

        try:
            async with self._lock:
                if jti not in self._blacklist:
                    return False

                # Check if token has expired
                exp = self._blacklist[jti]
                if exp <= int(time.time()):
                    # Remove expired token
                    del self._blacklist[jti]
                    return False

                return True
        except Exception:
            # On error, assume not blacklisted to avoid blocking valid requests
            return False

    async def cleanup_expired(self) -> int:
        """
        Remove expired tokens from blacklist.

        Returns:
            Number of tokens removed
        """
        now = int(time.time())
        removed_count = 0

        try:
            async with self._lock:
                expired_jtis = [jti for jti, exp in self._blacklist.items() if exp <= now]

                for jti in expired_jtis:
                    del self._blacklist[jti]
                    removed_count += 1

                return removed_count
        except Exception as e:
            raise TokenBlacklistError(f"Failed to cleanup expired tokens: {e}") from e

    async def remove(self, jti: str) -> bool:
        """
        Remove specific token from blacklist.

        Args:
            jti: JWT ID to remove

        Returns:
            True if token was removed, False if not found
        """
        if not jti:
            return False

        try:
            async with self._lock:
                if jti in self._blacklist:
                    del self._blacklist[jti]
                    return True
                return False
        except Exception as e:
            raise TokenBlacklistError(f"Failed to remove token from blacklist: {e}") from e

    async def clear(self) -> int:
        """
        Clear all tokens from blacklist.

        Returns:
            Number of tokens removed
        """
        try:
            async with self._lock:
                count = len(self._blacklist)
                self._blacklist.clear()
                return count
        except Exception as e:
            raise TokenBlacklistError(f"Failed to clear blacklist: {e}") from e

    async def get_blacklist_size(self) -> int:
        """
        Get current blacklist size.

        Returns:
            Number of tokens in blacklist
        """
        try:
            async with self._lock:
                return len(self._blacklist)
        except Exception:
            return 0


class TokenManager:
    """
    Token manager for JWT token lifecycle management.

    Provides token revocation, user token management, and integration
    with JWT manager and blacklist.
    """

    def __init__(self, jwt_manager: JWTManager, blacklist: TokenBlacklist) -> None:
        """
        Initialize token manager.

        Args:
            jwt_manager: JWT manager instance
            blacklist: Token blacklist instance
        """
        self.jwt_manager = jwt_manager
        self.blacklist = blacklist

    async def revoke_token(self, token: str) -> None:
        """
        Revoke token by adding to blacklist.

        Args:
            token: JWT token to revoke

        Raises:
            TokenManagerError: If token revocation fails
        """
        try:
            # Decode token to get JTI and expiration
            payload = await self.jwt_manager.decode_token(token, verify=False)

            # Add to blacklist
            await self.blacklist.add(payload.jti, payload.exp)
        except JWTError as e:
            raise TokenManagerError(f"Failed to revoke token: {e}") from e
        except Exception as e:
            raise TokenManagerError(f"Token revocation failed: {e}") from e

    async def revoke_all_user_tokens(self, user_id: str) -> int:
        """
        Revoke all tokens for a specific user.

        Note: This is a simplified implementation. In production, you would
        need to track user tokens in a database or cache to efficiently
        revoke all tokens for a user.

        Args:
            user_id: User identifier

        Returns:
            Number of tokens revoked (0 in this implementation)

        Raises:
            TokenManagerError: If revocation fails
        """
        # In a real implementation, you would:
        # 1. Query database/cache for all tokens belonging to user
        # 2. Add each token JTI to blacklist
        # 3. Return count of revoked tokens

        # For now, return 0 as we don't track user tokens
        return 0

    async def is_revoked(self, token: str) -> bool:
        """
        Check if token is revoked.

        Args:
            token: JWT token to check

        Returns:
            True if token is revoked, False otherwise

        Raises:
            TokenManagerError: If check fails
        """
        try:
            # Decode token to get JTI
            payload = await self.jwt_manager.decode_token(token, verify=False)

            # Check blacklist
            return await self.blacklist.is_blacklisted(payload.jti)
        except JWTError as e:
            raise TokenManagerError(f"Failed to check token revocation: {e}") from e
        except Exception as e:
            raise TokenManagerError(f"Token revocation check failed: {e}") from e

    async def cleanup_expired_tokens(self) -> int:
        """
        Cleanup expired tokens from blacklist.

        Returns:
            Number of tokens removed
        """
        try:
            return await self.blacklist.cleanup_expired()
        except Exception as e:
            raise TokenManagerError(f"Failed to cleanup expired tokens: {e}") from e

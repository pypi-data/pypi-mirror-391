"""
Password hashing and verification for Zephyr.

Provides secure password hashing using bcrypt with constant-time comparison.
"""

from __future__ import annotations

import secrets
from typing import TYPE_CHECKING

from passlib.context import CryptContext
from passlib.exc import InvalidHashError

if TYPE_CHECKING:
    pass


class PasswordError(Exception):
    """Base password error."""

    pass


class PasswordHashError(PasswordError):
    """Password hashing error."""

    pass


class PasswordVerificationError(PasswordError):
    """Password verification error."""

    pass


class PasswordHasher:
    """
    Secure password hasher using bcrypt.

    Provides password hashing, verification, and rehashing capabilities
    with constant-time comparison to prevent timing attacks.
    """

    def __init__(self, schemes: list[str] = ["bcrypt"], deprecated: list[str] = []) -> None:
        """
        Initialize password hasher.

        Args:
            schemes: List of hashing schemes to use (in order of preference)
            deprecated: List of deprecated schemes to check for rehashing
        """
        self.context = CryptContext(
            schemes=schemes,
            deprecated=deprecated,
            bcrypt__rounds=12,  # Secure default
            bcrypt__min_rounds=10,  # Minimum acceptable rounds
            bcrypt__max_rounds=15,  # Maximum rounds for performance
            bcrypt__truncate_error=True,  # Truncate passwords longer than 72 bytes
        )

    async def hash_password(self, password: str) -> str:
        """
        Hash password using bcrypt with automatic salt generation.

        Args:
            password: Plain text password

        Returns:
            Hashed password string

        Raises:
            PasswordHashError: If hashing fails
        """
        if not password:
            raise PasswordHashError("Password cannot be empty")

        # Truncate password if too long for bcrypt (72 bytes max)
        if len(password.encode("utf-8")) > 72:
            password = password[:72]

        try:
            return self.context.hash(password)
        except Exception as e:
            raise PasswordHashError(f"Password hashing failed: {e}") from e

    async def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify password using constant-time comparison.

        Args:
            password: Plain text password to verify
            password_hash: Stored password hash

        Returns:
            True if password matches, False otherwise

        Raises:
            PasswordVerificationError: If verification fails due to invalid hash
        """
        if not password:
            return False

        if not password_hash:
            return False

        try:
            return self.context.verify(password, password_hash)
        except InvalidHashError as e:
            raise PasswordVerificationError(f"Invalid password hash: {e}") from e
        except Exception as e:
            raise PasswordVerificationError(f"Password verification failed: {e}") from e

    async def needs_rehash(self, password_hash: str) -> bool:
        """
        Check if hash needs upgrade (algorithm changed or rounds increased).

        Args:
            password_hash: Current password hash

        Returns:
            True if password needs rehashing, False otherwise

        Raises:
            PasswordVerificationError: If hash is invalid
        """
        try:
            return self.context.needs_update(password_hash)
        except InvalidHashError as e:
            raise PasswordVerificationError(f"Invalid password hash: {e}") from e
        except Exception as e:
            raise PasswordVerificationError(f"Rehash check failed: {e}") from e

    async def generate_salt(self, length: int = 32) -> str:
        """
        Generate cryptographically secure random salt.

        Args:
            length: Salt length in bytes

        Returns:
            Base64-encoded salt string
        """
        return secrets.token_urlsafe(length)

    def get_scheme_info(self, password_hash: str) -> dict[str, object]:
        """
        Get information about the hashing scheme used.

        Args:
            password_hash: Password hash to analyze

        Returns:
            Dictionary with scheme information
        """
        try:
            return self.context.identify(password_hash)
        except Exception:
            return {"scheme": "unknown", "error": "Unable to identify scheme"}

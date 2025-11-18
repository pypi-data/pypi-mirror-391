"""
JWT (JSON Web Token) implementation for Zephyr.

Provides JWT token creation, validation, and management with full type safety.
"""

from __future__ import annotations

import time
import uuid
from typing import TYPE_CHECKING

from jose import JWTError, jwt
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from zephyr._types import ASGIApp, Scope, Receive, Send


class JWTError(Exception):
    """Base JWT error."""

    pass


class JWTExpiredError(JWTError):
    """JWT token has expired."""

    pass


class JWTInvalidError(JWTError):
    """JWT token is invalid."""

    pass


class JWTConfig(BaseModel):
    """JWT configuration."""

    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    secret_key: str = Field(..., description="Secret key for JWT signing")
    issuer: str | None = None
    audience: str | None = None


class JWTPayload(BaseModel):
    """JWT payload structure."""

    sub: str = Field(..., description="Subject (user_id)")
    exp: int = Field(..., description="Expiration timestamp")
    iat: int = Field(..., description="Issued at timestamp")
    jti: str = Field(..., description="JWT ID (unique identifier)")
    type: str = Field(..., description="Token type: 'access' or 'refresh'")
    scope: list[str] = Field(default_factory=list, description="Token scopes")
    extra: dict[str, object] = Field(default_factory=dict, description="Extra claims")


class JWTManager:
    """
    JWT token manager for creating, validating, and managing JWT tokens.

    Provides secure token generation with proper expiration, claims validation,
    and error handling.
    """

    def __init__(self, config: JWTConfig) -> None:
        """
        Initialize JWT manager.

        Args:
            config: JWT configuration
        """
        self.config = config

    async def create_access_token(
        self, user_id: str, scope: list[str] | None = None, extra_claims: dict[str, object] | None = None
    ) -> str:
        """
        Create JWT access token with expiration and claims.

        Args:
            user_id: User identifier
            scope: Token scopes (permissions)
            extra_claims: Additional claims to include

        Returns:
            JWT access token string

        Raises:
            JWTError: If token creation fails
        """
        now = int(time.time())
        expire = now + (self.config.access_token_expire_minutes * 60)

        payload = {
            "sub": user_id,
            "exp": expire,
            "iat": now,
            "jti": str(uuid.uuid4()),
            "type": "access",
            "scope": scope or [],
            **(extra_claims or {}),
        }

        # Add optional claims
        if self.config.issuer:
            payload["iss"] = self.config.issuer
        if self.config.audience:
            payload["aud"] = self.config.audience

        try:
            return jwt.encode(payload, self.config.secret_key, algorithm=self.config.algorithm)
        except Exception as e:
            raise JWTError(f"Failed to create access token: {e}") from e

    async def create_refresh_token(self, user_id: str) -> str:
        """
        Create long-lived refresh token.

        Args:
            user_id: User identifier

        Returns:
            JWT refresh token string

        Raises:
            JWTError: If token creation fails
        """
        now = int(time.time())
        expire = now + (self.config.refresh_token_expire_days * 24 * 60 * 60)

        payload = {"sub": user_id, "exp": expire, "iat": now, "jti": str(uuid.uuid4()), "type": "refresh"}

        # Add optional claims
        if self.config.issuer:
            payload["iss"] = self.config.issuer
        if self.config.audience:
            payload["aud"] = self.config.audience

        try:
            return jwt.encode(payload, self.config.secret_key, algorithm=self.config.algorithm)
        except Exception as e:
            raise JWTError(f"Failed to create refresh token: {e}") from e

    async def verify_token(self, token: str, token_type: str = "access") -> JWTPayload:
        """
        Verify token signature and expiration.

        Args:
            token: JWT token string
            token_type: Expected token type ("access" or "refresh")

        Returns:
            Decoded JWT payload

        Raises:
            JWTExpiredError: If token has expired
            JWTInvalidError: If token is invalid or malformed
            JWTError: For other verification errors
        """
        try:
            # Decode and verify token
            payload = jwt.decode(
                token,
                self.config.secret_key,
                algorithms=[self.config.algorithm],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_aud": self.config.audience is not None,
                    "verify_iss": self.config.issuer is not None,
                },
                audience=self.config.audience,
                issuer=self.config.issuer,
            )

            # Validate token type
            if payload.get("type") != token_type:
                raise JWTInvalidError(f"Invalid token type: expected {token_type}")

            # Create JWTPayload object
            return JWTPayload(
                sub=payload["sub"],
                exp=payload["exp"],
                iat=payload["iat"],
                jti=payload["jti"],
                type=payload["type"],
                scope=payload.get("scope", []),
                extra={
                    k: v
                    for k, v in payload.items()
                    if k not in ["sub", "exp", "iat", "jti", "type", "scope", "iss", "aud"]
                },
            )

        except jwt.ExpiredSignatureError as e:
            raise JWTExpiredError("Token has expired") from e
        except jwt.JWTError as e:
            raise JWTInvalidError(f"Invalid token: {e}") from e
        except Exception as e:
            raise JWTError(f"Token verification failed: {e}") from e

    async def decode_token(self, token: str, verify: bool = True) -> JWTPayload:
        """
        Decode token without verification (for inspection).

        Args:
            token: JWT token string
            verify: Whether to verify signature and expiration

        Returns:
            Decoded JWT payload

        Raises:
            JWTError: If token decoding fails
        """
        try:
            if verify:
                return await self.verify_token(token)

            # Decode without verification
            payload = jwt.decode(
                token,
                self.config.secret_key,
                algorithms=[self.config.algorithm],
                options={"verify_signature": False, "verify_exp": False},
            )

            return JWTPayload(
                sub=payload["sub"],
                exp=payload["exp"],
                iat=payload["iat"],
                jti=payload["jti"],
                type=payload["type"],
                scope=payload.get("scope", []),
                extra={
                    k: v
                    for k, v in payload.items()
                    if k not in ["sub", "exp", "iat", "jti", "type", "scope", "iss", "aud"]
                },
            )

        except Exception as e:
            raise JWTError(f"Token decoding failed: {e}") from e

    async def refresh_access_token(self, refresh_token: str) -> tuple[str, str]:
        """
        Exchange refresh token for new access + refresh tokens.

        Args:
            refresh_token: Valid refresh token

        Returns:
            Tuple of (new_access_token, new_refresh_token)

        Raises:
            JWTExpiredError: If refresh token has expired
            JWTInvalidError: If refresh token is invalid
            JWTError: For other errors
        """
        # Verify refresh token
        payload = await self.verify_token(refresh_token, "refresh")

        # Create new tokens
        new_access_token = await self.create_access_token(payload.sub, payload.scope)
        new_refresh_token = await self.create_refresh_token(payload.sub)

        return new_access_token, new_refresh_token

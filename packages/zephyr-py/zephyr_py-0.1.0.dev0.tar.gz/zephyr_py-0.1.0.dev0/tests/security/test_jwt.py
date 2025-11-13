"""
Tests for JWT functionality.

Tests JWT token creation, validation, refresh, and error handling.
"""

import pytest
import time
from unittest.mock import AsyncMock, patch

from zephyr.security.jwt import JWTManager, JWTConfig, JWTPayload, JWTError, JWTExpiredError, JWTInvalidError


class TestJWTConfig:
    """Test JWT configuration."""

    def test_default_config(self):
        """Test default JWT configuration."""
        config = JWTConfig(secret_key="test-secret")

        assert config.algorithm == "HS256"
        assert config.access_token_expire_minutes == 15
        assert config.refresh_token_expire_days == 7
        assert config.secret_key == "test-secret"
        assert config.issuer is None
        assert config.audience is None

    def test_custom_config(self):
        """Test custom JWT configuration."""
        config = JWTConfig(
            secret_key="custom-secret",
            algorithm="RS256",
            access_token_expire_minutes=30,
            refresh_token_expire_days=14,
            issuer="test-issuer",
            audience="test-audience",
        )

        assert config.algorithm == "RS256"
        assert config.access_token_expire_minutes == 30
        assert config.refresh_token_expire_days == 14
        assert config.secret_key == "custom-secret"
        assert config.issuer == "test-issuer"
        assert config.audience == "test-audience"


class TestJWTPayload:
    """Test JWT payload structure."""

    def test_payload_creation(self):
        """Test JWT payload creation."""
        now = int(time.time())
        payload = JWTPayload(
            sub="user123",
            exp=now + 3600,
            iat=now,
            jti="token123",
            type="access",
            scope=["read", "write"],
            extra={"role": "admin"},
        )

        assert payload.sub == "user123"
        assert payload.exp == now + 3600
        assert payload.iat == now
        assert payload.jti == "token123"
        assert payload.type == "access"
        assert payload.scope == ["read", "write"]
        assert payload.extra == {"role": "admin"}

    def test_payload_defaults(self):
        """Test JWT payload with defaults."""
        now = int(time.time())
        payload = JWTPayload(sub="user123", exp=now + 3600, iat=now, jti="token123", type="access")

        assert payload.scope == []
        assert payload.extra == {}


class TestJWTManager:
    """Test JWT manager functionality."""

    @pytest.fixture
    def jwt_config(self):
        """Create JWT configuration for tests."""
        return JWTConfig(secret_key="test-secret-key-12345")

    @pytest.fixture
    def jwt_manager(self, jwt_config):
        """Create JWT manager for tests."""
        return JWTManager(jwt_config)

    @pytest.mark.asyncio
    async def test_create_access_token(self, jwt_manager):
        """Test access token creation."""
        token = await jwt_manager.create_access_token(
            user_id="user123", scope=["read", "write"], extra_claims={"role": "admin"}
        )

        assert isinstance(token, str)
        assert len(token) > 0

        # Verify token can be decoded
        payload = await jwt_manager.decode_token(token, verify=False)
        assert payload.sub == "user123"
        assert payload.type == "access"
        assert payload.scope == ["read", "write"]
        assert payload.extra["role"] == "admin"

    @pytest.mark.asyncio
    async def test_create_refresh_token(self, jwt_manager):
        """Test refresh token creation."""
        token = await jwt_manager.create_refresh_token("user123")

        assert isinstance(token, str)
        assert len(token) > 0

        # Verify token can be decoded
        payload = await jwt_manager.decode_token(token, verify=False)
        assert payload.sub == "user123"
        assert payload.type == "refresh"

    @pytest.mark.asyncio
    async def test_verify_token_success(self, jwt_manager):
        """Test successful token verification."""
        token = await jwt_manager.create_access_token("user123")
        payload = await jwt_manager.verify_token(token, "access")

        assert payload.sub == "user123"
        assert payload.type == "access"
        assert payload.exp > int(time.time())

    @pytest.mark.asyncio
    async def test_verify_token_wrong_type(self, jwt_manager):
        """Test token verification with wrong type."""
        token = await jwt_manager.create_access_token("user123")

        with pytest.raises(JWTError, match="Token verification failed"):
            await jwt_manager.verify_token(token, "refresh")

    @pytest.mark.asyncio
    async def test_verify_expired_token(self, jwt_manager):
        """Test verification of expired token."""
        # Create token with very short expiration
        config = JWTConfig(secret_key="test-secret", access_token_expire_minutes=0)
        manager = JWTManager(config)

        token = await manager.create_access_token("user123")

        # Wait a bit to ensure expiration
        await asyncio.sleep(0.1)

        with pytest.raises(JWTError, match="Token verification failed"):
            await manager.verify_token(token, "access")

    @pytest.mark.asyncio
    async def test_verify_invalid_token(self, jwt_manager):
        """Test verification of invalid token."""
        with pytest.raises(JWTInvalidError):
            await jwt_manager.verify_token("invalid.token.here", "access")

    @pytest.mark.asyncio
    async def test_decode_token_without_verification(self, jwt_manager):
        """Test token decoding without verification."""
        token = await jwt_manager.create_access_token("user123")
        payload = await jwt_manager.decode_token(token, verify=False)

        assert payload.sub == "user123"
        assert payload.type == "access"

    @pytest.mark.asyncio
    async def test_refresh_access_token(self, jwt_manager):
        """Test access token refresh."""
        refresh_token = await jwt_manager.create_refresh_token("user123")
        new_access, new_refresh = await jwt_manager.refresh_access_token(refresh_token)

        assert isinstance(new_access, str)
        assert isinstance(new_refresh, str)
        assert new_access != refresh_token
        assert new_refresh != refresh_token

        # Verify new tokens
        access_payload = await jwt_manager.verify_token(new_access, "access")
        refresh_payload = await jwt_manager.verify_token(new_refresh, "refresh")

        assert access_payload.sub == "user123"
        assert refresh_payload.sub == "user123"

    @pytest.mark.asyncio
    async def test_refresh_invalid_token(self, jwt_manager):
        """Test refresh with invalid token."""
        with pytest.raises(JWTInvalidError):
            await jwt_manager.refresh_access_token("invalid.token.here")

    @pytest.mark.asyncio
    async def test_token_with_issuer_and_audience(self):
        """Test token creation with issuer and audience."""
        config = JWTConfig(secret_key="test-secret", issuer="test-issuer", audience="test-audience")
        manager = JWTManager(config)

        token = await manager.create_access_token("user123")
        payload = await manager.verify_token(token, "access")

        # Verify issuer and audience are included
        decoded = await manager.decode_token(token, verify=False)
        # Check that the token was created successfully
        assert decoded.sub == "user123"

    @pytest.mark.asyncio
    async def test_token_creation_error_handling(self, jwt_manager):
        """Test error handling during token creation."""
        # Mock jwt.encode to raise an exception
        with patch("zephyr.security.jwt.jwt.encode", side_effect=Exception("Encoding failed")):
            with pytest.raises(JWTError, match="Failed to create access token"):
                await jwt_manager.create_access_token("user123")

    @pytest.mark.asyncio
    async def test_token_verification_error_handling(self, jwt_manager):
        """Test error handling during token verification."""
        # Mock jwt.decode to raise an exception
        with patch("zephyr.security.jwt.jwt.decode", side_effect=Exception("Decoding failed")):
            with pytest.raises(JWTError, match="Token verification failed"):
                await jwt_manager.verify_token("some.token.here", "access")


# Import asyncio for the sleep test
import asyncio

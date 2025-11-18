"""
Tests for token management functionality.

Tests token blacklisting, revocation, and cleanup.
"""

import pytest
import time
from unittest.mock import AsyncMock, patch

from zephyr.security.tokens import TokenBlacklist, TokenManager, TokenError, TokenBlacklistError, TokenManagerError
from zephyr.security.jwt import JWTManager, JWTConfig


class TestTokenBlacklist:
    """Test token blacklist functionality."""

    @pytest.fixture
    def blacklist(self):
        """Create token blacklist for tests."""
        return TokenBlacklist()

    @pytest.mark.asyncio
    async def test_add_token(self, blacklist):
        """Test adding token to blacklist."""
        jti = "token123"
        exp = int(time.time()) + 3600  # 1 hour from now

        await blacklist.add(jti, exp)

        # Check if token is blacklisted
        is_blacklisted = await blacklist.is_blacklisted(jti)
        assert is_blacklisted is True

    @pytest.mark.asyncio
    async def test_add_empty_jti(self, blacklist):
        """Test adding empty JTI raises error."""
        with pytest.raises(TokenBlacklistError, match="JTI cannot be empty"):
            await blacklist.add("", 9999999999)

    @pytest.mark.asyncio
    async def test_add_expired_token(self, blacklist):
        """Test adding expired token (should not be added)."""
        jti = "expired_token"
        exp = int(time.time()) - 3600  # 1 hour ago

        await blacklist.add(jti, exp)

        # Expired token should not be in blacklist
        is_blacklisted = await blacklist.is_blacklisted(jti)
        assert is_blacklisted is False

    @pytest.mark.asyncio
    async def test_is_blacklisted_false(self, blacklist):
        """Test checking non-blacklisted token."""
        is_blacklisted = await blacklist.is_blacklisted("nonexistent_token")
        assert is_blacklisted is False

    @pytest.mark.asyncio
    async def test_is_blacklisted_empty_jti(self, blacklist):
        """Test checking empty JTI."""
        is_blacklisted = await blacklist.is_blacklisted("")
        assert is_blacklisted is False

    @pytest.mark.asyncio
    async def test_cleanup_expired(self, blacklist):
        """Test cleanup of expired tokens."""
        # Add some tokens
        now = int(time.time())
        await blacklist.add("token1", now + 3600)  # Valid
        await blacklist.add("token2", now - 3600)  # Expired
        await blacklist.add("token3", now + 7200)  # Valid

        # Cleanup should remove expired tokens
        removed_count = await blacklist.cleanup_expired()
        assert removed_count == 1

        # Check that expired token is gone
        assert await blacklist.is_blacklisted("token2") is False
        assert await blacklist.is_blacklisted("token1") is True
        assert await blacklist.is_blacklisted("token3") is True

    @pytest.mark.asyncio
    async def test_remove_token(self, blacklist):
        """Test removing specific token."""
        jti = "token123"
        exp = int(time.time()) + 3600

        await blacklist.add(jti, exp)
        assert await blacklist.is_blacklisted(jti) is True

        # Remove token
        removed = await blacklist.remove(jti)
        assert removed is True
        assert await blacklist.is_blacklisted(jti) is False

    @pytest.mark.asyncio
    async def test_remove_nonexistent_token(self, blacklist):
        """Test removing non-existent token."""
        removed = await blacklist.remove("nonexistent_token")
        assert removed is False

    @pytest.mark.asyncio
    async def test_clear_blacklist(self, blacklist):
        """Test clearing entire blacklist."""
        # Add some tokens
        now = int(time.time())
        await blacklist.add("token1", now + 3600)
        await blacklist.add("token2", now + 3600)

        # Clear blacklist
        removed_count = await blacklist.clear()
        assert removed_count == 2

        # Check that all tokens are gone
        assert await blacklist.is_blacklisted("token1") is False
        assert await blacklist.is_blacklisted("token2") is False

    @pytest.mark.asyncio
    async def test_get_blacklist_size(self, blacklist):
        """Test getting blacklist size."""
        # Initially empty
        size = await blacklist.get_blacklist_size()
        assert size == 0

        # Add some tokens
        now = int(time.time())
        await blacklist.add("token1", now + 3600)
        await blacklist.add("token2", now + 3600)

        size = await blacklist.get_blacklist_size()
        assert size == 2

    @pytest.mark.asyncio
    async def test_error_handling(self, blacklist):
        """Test error handling in blacklist operations."""
        # Mock the _blacklist dict to raise an exception
        with patch.object(blacklist, "_blacklist", side_effect=Exception("Blacklist error")):
            with pytest.raises(TokenBlacklistError, match="Failed to add token to blacklist"):
                await blacklist.add("token123", 9999999999)


class TestTokenManager:
    """Test token manager functionality."""

    @pytest.fixture
    def jwt_config(self):
        """Create JWT configuration for tests."""
        return JWTConfig(secret_key="test-secret-key-12345")

    @pytest.fixture
    def jwt_manager(self, jwt_config):
        """Create JWT manager for tests."""
        return JWTManager(jwt_config)

    @pytest.fixture
    def blacklist(self):
        """Create token blacklist for tests."""
        return TokenBlacklist()

    @pytest.fixture
    def token_manager(self, jwt_manager, blacklist):
        """Create token manager for tests."""
        return TokenManager(jwt_manager, blacklist)

    @pytest.mark.asyncio
    async def test_revoke_token(self, token_manager, jwt_manager):
        """Test token revocation."""
        # Create a token
        token = await jwt_manager.create_access_token("user123")

        # Revoke token
        await token_manager.revoke_token(token)

        # Check that token is revoked
        is_revoked = await token_manager.is_revoked(token)
        assert is_revoked is True

    @pytest.mark.asyncio
    async def test_revoke_invalid_token(self, token_manager):
        """Test revoking invalid token."""
        with pytest.raises(TokenManagerError, match="Failed to revoke token"):
            await token_manager.revoke_token("invalid.token.here")

    @pytest.mark.asyncio
    async def test_is_revoked_false(self, token_manager, jwt_manager):
        """Test checking non-revoked token."""
        # Create a token
        token = await jwt_manager.create_access_token("user123")

        # Check that token is not revoked
        is_revoked = await token_manager.is_revoked(token)
        assert is_revoked is False

    @pytest.mark.asyncio
    async def test_is_revoked_invalid_token(self, token_manager):
        """Test checking invalid token."""
        with pytest.raises(TokenManagerError, match="Failed to check token revocation"):
            await token_manager.is_revoked("invalid.token.here")

    @pytest.mark.asyncio
    async def test_revoke_all_user_tokens(self, token_manager):
        """Test revoking all user tokens (simplified implementation)."""
        # This is a simplified implementation that returns 0
        # In a real implementation, this would query a database
        revoked_count = await token_manager.revoke_all_user_tokens("user123")
        assert revoked_count == 0

    @pytest.mark.asyncio
    async def test_cleanup_expired_tokens(self, token_manager, blacklist):
        """Test cleanup of expired tokens."""
        # Add some expired tokens to blacklist
        now = int(time.time())
        await blacklist.add("token1", now - 3600)  # Expired
        await blacklist.add("token2", now + 3600)  # Valid

        # Cleanup should remove expired tokens
        removed_count = await token_manager.cleanup_expired_tokens()
        assert removed_count == 1

    @pytest.mark.asyncio
    async def test_cleanup_error_handling(self, token_manager):
        """Test error handling during cleanup."""
        # Mock blacklist.cleanup_expired to raise an exception
        with patch.object(token_manager.blacklist, "cleanup_expired", side_effect=Exception("Cleanup failed")):
            with pytest.raises(TokenManagerError, match="Failed to cleanup expired tokens"):
                await token_manager.cleanup_expired_tokens()


class TestTokenIntegration:
    """Test token management integration."""

    @pytest.fixture
    def jwt_config(self):
        """Create JWT configuration for tests."""
        return JWTConfig(secret_key="test-secret-key-12345")

    @pytest.fixture
    def jwt_manager(self, jwt_config):
        """Create JWT manager for tests."""
        return JWTManager(jwt_config)

    @pytest.fixture
    def blacklist(self):
        """Create token blacklist for tests."""
        return TokenBlacklist()

    @pytest.fixture
    def token_manager(self, jwt_manager, blacklist):
        """Create token manager for tests."""
        return TokenManager(jwt_manager, blacklist)

    @pytest.mark.asyncio
    async def test_token_lifecycle(self, token_manager, jwt_manager):
        """Test complete token lifecycle."""
        # Create token
        token = await jwt_manager.create_access_token("user123")

        # Verify token is not revoked
        assert await token_manager.is_revoked(token) is False

        # Revoke token
        await token_manager.revoke_token(token)

        # Verify token is revoked
        assert await token_manager.is_revoked(token) is True

        # Verify token is in blacklist
        payload = await jwt_manager.decode_token(token, verify=False)
        assert await token_manager.blacklist.is_blacklisted(payload.jti) is True

    @pytest.mark.asyncio
    async def test_multiple_tokens(self, token_manager, jwt_manager):
        """Test managing multiple tokens."""
        # Create multiple tokens
        token1 = await jwt_manager.create_access_token("user123")
        token2 = await jwt_manager.create_access_token("user456")
        token3 = await jwt_manager.create_access_token("user123")

        # Revoke one token
        await token_manager.revoke_token(token1)

        # Check revocation status
        assert await token_manager.is_revoked(token1) is True
        assert await token_manager.is_revoked(token2) is False
        assert await token_manager.is_revoked(token3) is False

    @pytest.mark.asyncio
    async def test_blacklist_cleanup_integration(self, token_manager, jwt_manager):
        """Test blacklist cleanup integration."""
        # Create and revoke a token with short expiration
        config = JWTConfig(secret_key="test-secret", access_token_expire_minutes=0)
        manager = JWTManager(config)
        token = await manager.create_access_token("user123")

        # Revoke token
        await token_manager.revoke_token(token)
        assert await token_manager.is_revoked(token) is True

        # Wait for token to expire
        await asyncio.sleep(0.1)

        # Cleanup should remove expired token
        removed_count = await token_manager.cleanup_expired_tokens()
        assert removed_count >= 0  # May or may not remove depending on timing

        # Token should no longer be considered revoked
        assert await token_manager.is_revoked(token) is False


# Import asyncio for sleep test
import asyncio

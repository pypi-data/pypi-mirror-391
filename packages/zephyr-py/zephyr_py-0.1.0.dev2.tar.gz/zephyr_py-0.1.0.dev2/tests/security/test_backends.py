"""
Tests for authentication backends.

Tests JWT, Token, and NoAuth authentication backends.
"""

import pytest
from unittest.mock import AsyncMock, patch

from zephyr.security.backends import (
    AuthenticationBackend,
    JWTAuthenticationBackend,
    TokenAuthenticationBackend,
    NoAuthenticationBackend,
    AuthenticationError,
)
from zephyr.security.jwt import JWTManager, JWTConfig
from zephyr.security.tokens import TokenManager, TokenBlacklist
from zephyr.security.user import User, AnonymousUser


class TestAuthenticationBackend:
    """Test base authentication backend."""

    @pytest.mark.asyncio
    async def test_authenticate_not_implemented(self):
        """Test that base backend raises NotImplementedError."""
        backend = AuthenticationBackend()

        with pytest.raises(NotImplementedError, match="Subclasses must implement authenticate method"):
            await backend.authenticate("token")

    @pytest.mark.asyncio
    async def test_get_user_returns_none(self):
        """Test that base backend get_user returns None."""
        backend = AuthenticationBackend()

        user = await backend.get_user("user123")
        assert user is None


class TestJWTAuthenticationBackend:
    """Test JWT authentication backend."""

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

    @pytest.fixture
    def backend(self, jwt_manager, token_manager):
        """Create JWT authentication backend for tests."""
        return JWTAuthenticationBackend(jwt_manager, token_manager)

    @pytest.mark.asyncio
    async def test_authenticate_success(self, backend, jwt_manager):
        """Test successful authentication."""
        # Create a valid token
        token = await jwt_manager.create_access_token("user123")

        # Authenticate user
        user = await backend.authenticate(token)

        assert user is not None
        assert isinstance(user, User)
        assert user.id == "user123"

    @pytest.mark.asyncio
    async def test_authenticate_empty_token(self, backend):
        """Test authentication with empty token."""
        user = await backend.authenticate("")
        assert user is None

    @pytest.mark.asyncio
    async def test_authenticate_none_token(self, backend):
        """Test authentication with None token."""
        user = await backend.authenticate(None)
        assert user is None

    @pytest.mark.asyncio
    async def test_authenticate_invalid_token(self, backend):
        """Test authentication with invalid token."""
        with pytest.raises(AuthenticationError, match="Authentication failed"):
            await backend.authenticate("invalid.token.here")

    @pytest.mark.asyncio
    async def test_authenticate_revoked_token(self, backend, jwt_manager, token_manager):
        """Test authentication with revoked token."""
        # Create and revoke token
        token = await jwt_manager.create_access_token("user123")
        await token_manager.revoke_token(token)

        # Authentication should fail
        user = await backend.authenticate(token)
        assert user is None

    @pytest.mark.asyncio
    async def test_authenticate_inactive_user(self, backend, jwt_manager):
        """Test authentication with inactive user."""
        # Mock get_user to return inactive user
        with patch.object(
            backend,
            "get_user",
            return_value=User(id="user123", username="testuser", email="test@example.com", is_active=False),
        ):
            token = await jwt_manager.create_access_token("user123")
            user = await backend.authenticate(token)
            assert user is None

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, backend, jwt_manager):
        """Test authentication when user is not found."""
        # Mock get_user to return None
        with patch.object(backend, "get_user", return_value=None):
            token = await jwt_manager.create_access_token("user123")
            user = await backend.authenticate(token)
            assert user is None

    @pytest.mark.asyncio
    async def test_get_user_mock_implementation(self, backend):
        """Test get_user mock implementation."""
        user = await backend.get_user("user123")

        assert user is not None
        assert isinstance(user, User)
        assert user.id == "user123"
        assert user.username == "user_user123"
        assert user.email == "user_user123@example.com"

    @pytest.mark.asyncio
    async def test_get_user_nonexistent(self, backend):
        """Test get_user with nonexistent user."""
        user = await backend.get_user("")
        assert user is None

    @pytest.mark.asyncio
    async def test_authenticate_error_handling(self, backend):
        """Test error handling during authentication."""
        # Mock jwt_manager.verify_token to raise an exception
        with patch.object(backend.jwt_manager, "verify_token", side_effect=Exception("JWT error")):
            with pytest.raises(AuthenticationError, match="Authentication failed"):
                await backend.authenticate("some.token.here")


class TestTokenAuthenticationBackend:
    """Test token authentication backend."""

    @pytest.fixture
    def token_validator(self):
        """Create token validator for tests."""

        def validator(token):
            return token == "valid_token"

        return validator

    @pytest.fixture
    def backend(self, token_validator):
        """Create token authentication backend for tests."""
        return TokenAuthenticationBackend(token_validator)

    @pytest.mark.asyncio
    async def test_authenticate_success(self, backend):
        """Test successful authentication with valid token."""
        user = await backend.authenticate("valid_token")

        assert user is not None
        assert isinstance(user, User)
        assert user.username.startswith("token_user_")

    @pytest.mark.asyncio
    async def test_authenticate_invalid_token(self, backend):
        """Test authentication with invalid token."""
        user = await backend.authenticate("invalid_token")
        assert user is None

    @pytest.mark.asyncio
    async def test_authenticate_empty_token(self, backend):
        """Test authentication with empty token."""
        user = await backend.authenticate("")
        assert user is None

    @pytest.mark.asyncio
    async def test_authenticate_none_token(self, backend):
        """Test authentication with None token."""
        user = await backend.authenticate(None)
        assert user is None

    @pytest.mark.asyncio
    async def test_authenticate_inactive_user(self, backend):
        """Test authentication with inactive user."""
        # Mock get_user to return inactive user
        with patch.object(
            backend,
            "get_user",
            return_value=User(id="user123", username="testuser", email="test@example.com", is_active=False),
        ):
            user = await backend.authenticate("valid_token")
            assert user is None

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, backend):
        """Test authentication when user is not found."""
        # Mock get_user to return None
        with patch.object(backend, "get_user", return_value=None):
            user = await backend.authenticate("valid_token")
            assert user is None

    @pytest.mark.asyncio
    async def test_authenticate_error_handling(self, backend):
        """Test error handling during authentication."""
        # Mock token_validator to raise an exception
        with patch.object(backend, "token_validator", side_effect=Exception("Validation error")):
            with pytest.raises(AuthenticationError, match="Token authentication failed"):
                await backend.authenticate("some_token")

    @pytest.mark.asyncio
    async def test_get_user_success(self, backend):
        """Test get_user with valid user ID."""
        user = await backend.get_user("user123")

        assert user is not None
        assert isinstance(user, User)
        assert user.id == "user123"
        assert user.username == "token_user_user123"
        assert user.email == "token_user_user123@example.com"

    @pytest.mark.asyncio
    async def test_get_user_empty_id(self, backend):
        """Test get_user with empty user ID."""
        user = await backend.get_user("")
        assert user is None

    @pytest.mark.asyncio
    async def test_get_user_none_id(self, backend):
        """Test get_user with None user ID."""
        user = await backend.get_user(None)
        assert user is None


class TestNoAuthenticationBackend:
    """Test no authentication backend."""

    @pytest.fixture
    def backend(self):
        """Create no authentication backend for tests."""
        return NoAuthenticationBackend()

    @pytest.mark.asyncio
    async def test_authenticate_returns_anonymous(self, backend):
        """Test that authenticate always returns AnonymousUser."""
        user = await backend.authenticate("any_token")

        assert user is not None
        assert isinstance(user, AnonymousUser)
        assert user.is_anonymous is True
        assert user.is_authenticated is False

    @pytest.mark.asyncio
    async def test_authenticate_ignores_token(self, backend):
        """Test that authenticate ignores token value."""
        user1 = await backend.authenticate("token1")
        user2 = await backend.authenticate("token2")
        user3 = await backend.authenticate(None)

        # All should return AnonymousUser
        assert isinstance(user1, AnonymousUser)
        assert isinstance(user2, AnonymousUser)
        assert isinstance(user3, AnonymousUser)

    @pytest.mark.asyncio
    async def test_get_user_returns_anonymous(self, backend):
        """Test that get_user always returns AnonymousUser."""
        user = await backend.get_user("any_user_id")

        assert user is not None
        assert isinstance(user, AnonymousUser)
        assert user.is_anonymous is True
        assert user.is_authenticated is False

    @pytest.mark.asyncio
    async def test_get_user_ignores_user_id(self, backend):
        """Test that get_user ignores user ID value."""
        user1 = await backend.get_user("user1")
        user2 = await backend.get_user("user2")
        user3 = await backend.get_user(None)

        # All should return AnonymousUser
        assert isinstance(user1, AnonymousUser)
        assert isinstance(user2, AnonymousUser)
        assert isinstance(user3, AnonymousUser)


class TestBackendIntegration:
    """Test authentication backend integration."""

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

    @pytest.fixture
    def jwt_backend(self, jwt_manager, token_manager):
        """Create JWT authentication backend for tests."""
        return JWTAuthenticationBackend(jwt_manager, token_manager)

    @pytest.mark.asyncio
    async def test_jwt_backend_full_flow(self, jwt_backend, jwt_manager):
        """Test complete JWT authentication flow."""
        # Create token
        token = await jwt_manager.create_access_token("user123", ["read", "write"])

        # Authenticate
        user = await jwt_backend.authenticate(token)

        assert user is not None
        assert user.id == "user123"
        assert user.is_authenticated is True
        assert user.is_anonymous is False

    @pytest.mark.asyncio
    async def test_token_backend_full_flow(self):
        """Test complete token authentication flow."""

        def validator(token):
            return token.startswith("valid_")

        backend = TokenAuthenticationBackend(validator)

        # Test valid token
        user = await backend.authenticate("valid_token123")
        assert user is not None
        assert user.is_authenticated is True

        # Test invalid token
        user = await backend.authenticate("invalid_token123")
        assert user is None

    @pytest.mark.asyncio
    async def test_no_auth_backend_consistency(self):
        """Test that no auth backend is consistent."""
        backend = NoAuthenticationBackend()

        # Multiple calls should return consistent results
        user1 = await backend.authenticate("token1")
        user2 = await backend.authenticate("token2")
        user3 = await backend.get_user("user1")
        user4 = await backend.get_user("user2")

        # All should be AnonymousUser
        for user in [user1, user2, user3, user4]:
            assert isinstance(user, AnonymousUser)
            assert user.is_anonymous is True
            assert user.is_authenticated is False

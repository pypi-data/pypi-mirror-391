"""
Integration tests for authentication system.

Tests complete authentication flows and component integration.
"""

import pytest
import time
from unittest.mock import AsyncMock, patch

from zephyr.security.jwt import JWTManager, JWTConfig
from zephyr.security.tokens import TokenManager, TokenBlacklist
from zephyr.security.password import PasswordHasher
from zephyr.security.user import User, AnonymousUser
from zephyr.security.backends import JWTAuthenticationBackend
from zephyr.security.middleware.auth import BearerAuthMiddleware


class TestAuthenticationIntegration:
    """Test complete authentication system integration."""

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
    def password_hasher(self):
        """Create password hasher for tests."""
        return PasswordHasher()

    @pytest.fixture
    def auth_backend(self, jwt_manager, token_manager):
        """Create JWT authentication backend for tests."""
        return JWTAuthenticationBackend(jwt_manager, token_manager)

    @pytest.fixture
    def mock_app(self):
        """Create mock ASGI app for tests."""
        return AsyncMock()

    @pytest.fixture
    def auth_middleware(self, mock_app, auth_backend):
        """Create Bearer auth middleware for tests."""
        return BearerAuthMiddleware(mock_app, auth_backend)

    @pytest.mark.asyncio
    async def test_complete_auth_flow(self, jwt_manager, password_hasher, auth_backend, auth_middleware):
        """Test complete authentication flow from password to middleware."""
        # 1. Hash password
        password = "secure_password_123"
        password_hash = await password_hasher.hash_password(password)

        # 2. Create user
        user = User(
            id="user123",
            username="testuser",
            email="test@example.com",
            is_active=True,
            roles=["user", "admin"],
            permissions=["read", "write", "delete"],
        )

        # 3. Create access token
        access_token = await jwt_manager.create_access_token(
            user_id=user.id, scope=["read", "write"], extra_claims={"role": "admin"}
        )

        # 4. Create refresh token
        refresh_token = await jwt_manager.create_refresh_token(user.id)

        # 5. Verify tokens
        access_payload = await jwt_manager.verify_token(access_token, "access")
        refresh_payload = await jwt_manager.verify_token(refresh_token, "refresh")

        assert access_payload.sub == user.id
        assert refresh_payload.sub == user.id

        # 6. Test authentication backend
        authenticated_user = await auth_backend.authenticate(access_token)
        assert authenticated_user is not None
        assert authenticated_user.id == user.id

        # 7. Test middleware
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/protected",
            "headers": [(b"authorization", f"Bearer {access_token}".encode())],
            "query_string": b"",
            "client": ("127.0.0.1", 12345),
            "server": ("localhost", 8000),
        }
        receive = AsyncMock()
        send = AsyncMock()

        await auth_middleware(scope, receive, send)

        # Verify middleware set user in scope
        call_scope = auth_middleware.app.call_args[0][0]
        assert "user" in call_scope
        assert call_scope["user"].id == user.id
        assert call_scope["auth"]["authenticated"] is True

    @pytest.mark.asyncio
    async def test_token_refresh_flow(self, jwt_manager, token_manager):
        """Test token refresh flow."""
        # Create initial tokens
        access_token = await jwt_manager.create_access_token("user123")
        refresh_token = await jwt_manager.create_refresh_token("user123")

        # Refresh tokens
        new_access, new_refresh = await jwt_manager.refresh_access_token(refresh_token)

        # Verify new tokens are different
        assert new_access != access_token
        assert new_refresh != refresh_token

        # Verify new tokens work
        access_payload = await jwt_manager.verify_token(new_access, "access")
        refresh_payload = await jwt_manager.verify_token(new_refresh, "refresh")

        assert access_payload.sub == "user123"
        assert refresh_payload.sub == "user123"

    @pytest.mark.asyncio
    async def test_token_revocation_flow(self, jwt_manager, token_manager, auth_backend):
        """Test token revocation flow."""
        # Create and authenticate with token
        token = await jwt_manager.create_access_token("user123")
        user = await auth_backend.authenticate(token)
        assert user is not None

        # Revoke token
        await token_manager.revoke_token(token)

        # Verify token is revoked
        is_revoked = await token_manager.is_revoked(token)
        assert is_revoked is True

        # Verify authentication fails
        user = await auth_backend.authenticate(token)
        assert user is None

    @pytest.mark.asyncio
    async def test_password_verification_flow(self, password_hasher):
        """Test password verification flow."""
        # Hash password
        password = "my_secure_password"
        password_hash = await password_hasher.hash_password(password)

        # Verify correct password
        is_valid = await password_hasher.verify_password(password, password_hash)
        assert is_valid is True

        # Verify wrong password
        is_valid = await password_hasher.verify_password("wrong_password", password_hash)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_user_permissions_flow(self):
        """Test user permissions flow."""
        # Create user with roles and permissions
        user = User(
            id="user123",
            username="testuser",
            email="test@example.com",
            roles=["admin", "user"],
            permissions=["read", "write", "delete"],
        )

        # Test permission checks
        assert await user.has_permission("read") is True
        assert await user.has_permission("write") is True
        assert await user.has_permission("nonexistent") is False

        # Test role checks
        assert await user.has_role("admin") is True
        assert await user.has_role("user") is True
        assert await user.has_role("nonexistent") is False

        # Test any/all checks
        assert await user.has_any_permission(["read", "nonexistent"]) is True
        assert await user.has_all_permissions(["read", "write"]) is True
        assert await user.has_all_permissions(["read", "nonexistent"]) is False

    @pytest.mark.asyncio
    async def test_anonymous_user_flow(self):
        """Test anonymous user flow."""
        # Create anonymous user
        anon_user = AnonymousUser()

        # Test properties
        assert anon_user.is_authenticated is False
        assert anon_user.is_anonymous is True

        # Test permission/role checks always return False
        assert await anon_user.has_permission("any_permission") is False
        assert await anon_user.has_role("any_role") is False
        assert await anon_user.has_any_permission(["perm1", "perm2"]) is False
        assert await anon_user.has_all_permissions(["perm1", "perm2"]) is False

    @pytest.mark.asyncio
    async def test_middleware_exclusion_flow(self, auth_middleware):
        """Test middleware exclusion flow."""
        # Set up excluded paths
        auth_middleware.exclude_paths = ["/health", "/metrics", "/docs"]

        # Test excluded paths
        for path in ["/health", "/metrics", "/docs"]:
            scope = {
                "type": "http",
                "method": "GET",
                "path": path,
                "headers": [(b"authorization", b"Bearer valid_token")],
                "query_string": b"",
                "client": ("127.0.0.1", 12345),
                "server": ("localhost", 8000),
            }
            receive = AsyncMock()
            send = AsyncMock()

            await auth_middleware(scope, receive, send)

            # Verify user is anonymous for excluded paths
            call_scope = auth_middleware.app.call_args[0][0]
            assert isinstance(call_scope["user"], AnonymousUser)
            assert call_scope["auth"]["authenticated"] is False

    @pytest.mark.asyncio
    async def test_error_handling_flow(self, jwt_manager, auth_backend):
        """Test error handling throughout the flow."""
        # Test invalid token
        with pytest.raises(Exception):  # JWTInvalidError
            await jwt_manager.verify_token("invalid.token.here", "access")

        # Test authentication with invalid token
        with pytest.raises(Exception):  # AuthenticationError
            await auth_backend.authenticate("invalid.token.here")

        # Test empty token
        user = await auth_backend.authenticate("")
        assert user is None

        user = await auth_backend.authenticate(None)
        assert user is None

    @pytest.mark.asyncio
    async def test_concurrent_authentication(self, jwt_manager, auth_backend):
        """Test concurrent authentication requests."""
        import asyncio

        # Create multiple tokens
        tokens = []
        for i in range(5):
            token = await jwt_manager.create_access_token(f"user{i}")
            tokens.append(token)

        # Authenticate concurrently
        async def authenticate_token(token):
            return await auth_backend.authenticate(token)

        # Run concurrent authentications
        results = await asyncio.gather(*[authenticate_token(token) for token in tokens])

        # Verify all authentications succeeded
        assert len(results) == 5
        for i, user in enumerate(results):
            assert user is not None
            assert user.id == f"user{i}"

    @pytest.mark.asyncio
    async def test_token_expiration_flow(self, jwt_config, auth_backend):
        """Test token expiration flow."""
        # Create JWT manager with very short expiration
        config = JWTConfig(secret_key="test-secret", access_token_expire_minutes=0)
        manager = JWTManager(config)
        token_manager = TokenManager(manager, TokenBlacklist())
        backend = JWTAuthenticationBackend(manager, token_manager)

        # Create token
        token = await manager.create_access_token("user123")

        # Wait for token to expire
        await asyncio.sleep(0.1)

        # Verify token is expired
        with pytest.raises(Exception):  # JWTExpiredError
            await manager.verify_token(token, "access")

        # Verify authentication fails
        with pytest.raises(Exception):  # AuthenticationError
            await backend.authenticate(token)

    @pytest.mark.asyncio
    async def test_blacklist_cleanup_flow(self, jwt_manager, token_manager, blacklist):
        """Test blacklist cleanup flow."""
        # Create and revoke some tokens
        tokens = []
        for i in range(3):
            token = await jwt_manager.create_access_token(f"user{i}")
            await token_manager.revoke_token(token)
            tokens.append(token)

        # Verify tokens are blacklisted
        for token in tokens:
            assert await token_manager.is_revoked(token) is True

        # Cleanup expired tokens (if any)
        removed_count = await token_manager.cleanup_expired_tokens()
        assert removed_count >= 0  # May or may not remove depending on timing

    @pytest.mark.asyncio
    async def test_middleware_scope_preservation(self, auth_middleware):
        """Test that middleware preserves original scope data."""
        # Create scope with custom data
        original_scope = {
            "type": "http",
            "method": "POST",
            "path": "/api/users",
            "headers": [
                (b"authorization", b"Bearer valid_token"),
                (b"content-type", b"application/json"),
                (b"x-custom-header", b"custom-value"),
            ],
            "query_string": b"param=value",
            "client": ("192.168.1.100", 54321),
            "server": ("api.example.com", 443),
            "custom_field": "custom_data",
            "nested": {"key": "value"},
        }

        receive = AsyncMock()
        send = AsyncMock()

        await auth_middleware(original_scope, receive, send)

        # Verify original scope data is preserved
        call_scope = auth_middleware.app.call_args[0][0]
        assert call_scope["type"] == "http"
        assert call_scope["method"] == "POST"
        assert call_scope["path"] == "/api/users"
        assert call_scope["query_string"] == b"param=value"
        assert call_scope["client"] == ("192.168.1.100", 54321)
        assert call_scope["server"] == ("api.example.com", 443)
        assert call_scope["custom_field"] == "custom_data"
        assert call_scope["nested"] == {"key": "value"}

        # Verify headers are preserved
        assert (b"content-type", b"application/json") in call_scope["headers"]
        assert (b"x-custom-header", b"custom-value") in call_scope["headers"]

        # Verify auth data is added
        assert "user" in call_scope
        assert "auth" in call_scope
        assert call_scope["auth"]["authenticated"] is False  # No valid token


# Import asyncio for concurrent tests
import asyncio

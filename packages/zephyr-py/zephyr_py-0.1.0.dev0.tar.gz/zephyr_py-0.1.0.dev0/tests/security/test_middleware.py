"""
Tests for security middleware.

Tests Bearer authentication middleware and ASGI integration.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from zephyr.security.middleware.auth import BearerAuthMiddleware
from zephyr.security.backends import AuthenticationBackend
from zephyr.security.user import User, AnonymousUser


class MockAuthenticationBackend(AuthenticationBackend):
    """Mock authentication backend for testing."""

    def __init__(self, return_user=None, raise_error=None):
        self.return_user = return_user
        self.raise_error = raise_error

    async def authenticate(self, token: str):
        if self.raise_error:
            raise self.raise_error
        return self.return_user

    async def get_user(self, user_id: str):
        return self.return_user


class TestBearerAuthMiddleware:
    """Test Bearer authentication middleware."""

    @pytest.fixture
    def mock_app(self):
        """Create mock ASGI app."""
        return AsyncMock()

    @pytest.fixture
    def mock_backend(self):
        """Create mock authentication backend."""
        return MockAuthenticationBackend()

    @pytest.fixture
    def middleware(self, mock_app, mock_backend):
        """Create Bearer auth middleware for tests."""
        return BearerAuthMiddleware(mock_app, mock_backend)

    @pytest.fixture
    def scope(self):
        """Create ASGI scope for tests."""
        return {
            "type": "http",
            "method": "GET",
            "path": "/test",
            "headers": [],
            "query_string": b"",
            "client": ("127.0.0.1", 12345),
            "server": ("localhost", 8000),
        }

    @pytest.fixture
    def receive(self):
        """Create ASGI receive function."""
        return AsyncMock()

    @pytest.fixture
    def send(self):
        """Create ASGI send function."""
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_middleware_initialization(self, mock_app, mock_backend):
        """Test middleware initialization."""
        middleware = BearerAuthMiddleware(mock_app, mock_backend)

        assert middleware.app == mock_app
        assert middleware.backend == mock_backend
        assert middleware.exclude_paths == []

    @pytest.mark.asyncio
    async def test_middleware_with_exclude_paths(self, mock_app, mock_backend):
        """Test middleware with excluded paths."""
        exclude_paths = ["/health", "/metrics"]
        middleware = BearerAuthMiddleware(mock_app, mock_backend, exclude_paths)

        assert middleware.exclude_paths == exclude_paths

    @pytest.mark.asyncio
    async def test_extract_bearer_token_success(self, middleware):
        """Test successful Bearer token extraction."""
        headers = [(b"authorization", b"Bearer valid_token_123"), (b"content-type", b"application/json")]

        token = middleware._extract_bearer_token(headers)
        assert token == "valid_token_123"

    @pytest.mark.asyncio
    async def test_extract_bearer_token_no_header(self, middleware):
        """Test Bearer token extraction with no authorization header."""
        headers = [(b"content-type", b"application/json"), (b"user-agent", b"test-client")]

        token = middleware._extract_bearer_token(headers)
        assert token is None

    @pytest.mark.asyncio
    async def test_extract_bearer_token_wrong_scheme(self, middleware):
        """Test Bearer token extraction with wrong authorization scheme."""
        headers = [(b"authorization", b"Basic dGVzdDp0ZXN0"), (b"content-type", b"application/json")]

        token = middleware._extract_bearer_token(headers)
        assert token is None

    @pytest.mark.asyncio
    async def test_extract_bearer_token_malformed(self, middleware):
        """Test Bearer token extraction with malformed header."""
        headers = [(b"authorization", b"Bearer"), (b"content-type", b"application/json")]

        token = middleware._extract_bearer_token(headers)
        assert token is None

    @pytest.mark.asyncio
    async def test_extract_bearer_token_case_insensitive(self, middleware):
        """Test Bearer token extraction is case insensitive."""
        headers = [(b"authorization", b"bearer valid_token_123"), (b"content-type", b"application/json")]

        token = middleware._extract_bearer_token(headers)
        assert token == "valid_token_123"

    @pytest.mark.asyncio
    async def test_is_excluded_path_true(self, middleware):
        """Test path exclusion check returns True."""
        middleware.exclude_paths = ["/health", "/metrics", "/docs"]

        assert middleware._is_excluded_path("/health") is True
        assert middleware._is_excluded_path("/metrics") is True
        assert middleware._is_excluded_path("/docs") is True

    @pytest.mark.asyncio
    async def test_is_excluded_path_false(self, middleware):
        """Test path exclusion check returns False."""
        middleware.exclude_paths = ["/health", "/metrics"]

        assert middleware._is_excluded_path("/api/users") is False
        assert middleware._is_excluded_path("/admin") is False
        assert middleware._is_excluded_path("/") is False

    @pytest.mark.asyncio
    async def test_is_excluded_path_empty_list(self, middleware):
        """Test path exclusion check with empty exclude list."""
        middleware.exclude_paths = []

        assert middleware._is_excluded_path("/any/path") is False

    @pytest.mark.asyncio
    async def test_call_http_scope_success(self, middleware, scope, receive, send):
        """Test middleware call with successful authentication."""
        # Setup
        user = User(id="user123", username="testuser", email="test@example.com")
        middleware.backend.return_user = user
        scope["headers"] = [(b"authorization", b"Bearer valid_token")]

        # Call middleware
        await middleware(scope, receive, send)

        # Verify app was called with user in scope
        middleware.app.assert_called_once()
        call_scope = middleware.app.call_args[0][0]
        assert "user" in call_scope
        assert call_scope["user"] == user
        assert "auth" in call_scope
        assert call_scope["auth"]["authenticated"] is True
        assert call_scope["auth"]["user_id"] == "user123"

    @pytest.mark.asyncio
    async def test_call_http_scope_no_token(self, middleware, scope, receive, send):
        """Test middleware call with no token."""
        # Setup
        scope["headers"] = [(b"content-type", b"application/json")]

        # Call middleware
        await middleware(scope, receive, send)

        # Verify app was called with anonymous user
        middleware.app.assert_called_once()
        call_scope = middleware.app.call_args[0][0]
        assert "user" in call_scope
        assert isinstance(call_scope["user"], AnonymousUser)
        assert "auth" in call_scope
        assert call_scope["auth"]["authenticated"] is False
        assert call_scope["auth"]["user_id"] is None

    @pytest.mark.asyncio
    async def test_call_http_scope_authentication_failed(self, middleware, scope, receive, send):
        """Test middleware call with authentication failure."""
        # Setup
        middleware.backend.raise_error = Exception("Auth failed")
        scope["headers"] = [(b"authorization", b"Bearer invalid_token")]

        # Call middleware
        await middleware(scope, receive, send)

        # Verify app was called with anonymous user
        middleware.app.assert_called_once()
        call_scope = middleware.app.call_args[0][0]
        assert "user" in call_scope
        assert isinstance(call_scope["user"], AnonymousUser)
        assert "auth" in call_scope
        assert call_scope["auth"]["authenticated"] is False

    @pytest.mark.asyncio
    async def test_call_http_scope_excluded_path(self, middleware, scope, receive, send):
        """Test middleware call with excluded path."""
        # Setup
        middleware.exclude_paths = ["/health"]
        scope["path"] = "/health"
        scope["headers"] = [(b"authorization", b"Bearer valid_token")]

        # Call middleware
        await middleware(scope, receive, send)

        # Verify app was called without authentication
        middleware.app.assert_called_once()
        call_scope = middleware.app.call_args[0][0]
        assert "user" in call_scope
        assert isinstance(call_scope["user"], AnonymousUser)
        assert "auth" in call_scope
        assert call_scope["auth"]["authenticated"] is False

    @pytest.mark.asyncio
    async def test_call_non_http_scope(self, middleware, receive, send):
        """Test middleware call with non-HTTP scope."""
        # Setup
        scope = {"type": "websocket", "path": "/ws"}

        # Call middleware
        await middleware(scope, receive, send)

        # Verify app was called without modification
        middleware.app.assert_called_once()
        call_scope = middleware.app.call_args[0][0]
        assert call_scope == scope

    @pytest.mark.asyncio
    async def test_call_websocket_scope(self, middleware, receive, send):
        """Test middleware call with WebSocket scope."""
        # Setup
        scope = {"type": "websocket", "path": "/ws", "headers": [(b"authorization", b"Bearer valid_token")]}
        user = User(id="user123", username="testuser", email="test@example.com")
        middleware.backend.return_user = user

        # Call middleware
        await middleware(scope, receive, send)

        # Verify app was called with user in scope
        middleware.app.assert_called_once()
        call_scope = middleware.app.call_args[0][0]
        assert "user" in call_scope
        assert call_scope["user"] == user
        assert "auth" in call_scope
        assert call_scope["auth"]["authenticated"] is True

    @pytest.mark.asyncio
    async def test_call_with_authentication_error(self, middleware, scope, receive, send):
        """Test middleware call with authentication error."""
        # Setup
        from zephyr.security.backends import AuthenticationError

        middleware.backend.raise_error = AuthenticationError("Invalid token")
        scope["headers"] = [(b"authorization", b"Bearer invalid_token")]

        # Call middleware
        await middleware(scope, receive, send)

        # Verify app was called with anonymous user
        middleware.app.assert_called_once()
        call_scope = middleware.app.call_args[0][0]
        assert "user" in call_scope
        assert isinstance(call_scope["user"], AnonymousUser)
        assert "auth" in call_scope
        assert call_scope["auth"]["authenticated"] is False

    @pytest.mark.asyncio
    async def test_call_with_general_error(self, middleware, scope, receive, send):
        """Test middleware call with general error."""
        # Setup
        middleware.backend.raise_error = Exception("Unexpected error")
        scope["headers"] = [(b"authorization", b"Bearer token")]

        # Call middleware
        await middleware(scope, receive, send)

        # Verify app was called with anonymous user
        middleware.app.assert_called_once()
        call_scope = middleware.app.call_args[0][0]
        assert "user" in call_scope
        assert isinstance(call_scope["user"], AnonymousUser)
        assert "auth" in call_scope
        assert call_scope["auth"]["authenticated"] is False

    @pytest.mark.asyncio
    async def test_call_preserves_original_scope(self, middleware, scope, receive, send):
        """Test that middleware preserves original scope data."""
        # Setup
        original_headers = [(b"content-type", b"application/json")]
        scope["headers"] = original_headers
        scope["custom_field"] = "custom_value"

        # Call middleware
        await middleware(scope, receive, send)

        # Verify original scope data is preserved
        middleware.app.assert_called_once()
        call_scope = middleware.app.call_args[0][0]
        assert call_scope["headers"] == original_headers
        assert call_scope["custom_field"] == "custom_value"
        assert call_scope["type"] == "http"
        assert call_scope["method"] == "GET"
        assert call_scope["path"] == "/test"

    @pytest.mark.asyncio
    async def test_call_multiple_authorization_headers(self, middleware, scope, receive, send):
        """Test middleware with multiple authorization headers."""
        # Setup
        user = User(id="user123", username="testuser", email="test@example.com")
        middleware.backend.return_user = user
        scope["headers"] = [
            (b"authorization", b"Basic dGVzdDp0ZXN0"),
            (b"authorization", b"Bearer valid_token"),
            (b"content-type", b"application/json"),
        ]

        # Call middleware
        await middleware(scope, receive, send)

        # Verify Bearer token was used
        middleware.app.assert_called_once()
        call_scope = middleware.app.call_args[0][0]
        assert "user" in call_scope
        assert call_scope["user"] == user
        assert call_scope["auth"]["authenticated"] is True


class TestBearerAuthMiddlewareIntegration:
    """Test Bearer auth middleware integration scenarios."""

    @pytest.mark.asyncio
    async def test_middleware_chain(self):
        """Test middleware in a chain."""
        # Create mock app
        mock_app = AsyncMock()

        # Create middleware chain
        backend1 = MockAuthenticationBackend()
        backend2 = MockAuthenticationBackend()

        middleware1 = BearerAuthMiddleware(mock_app, backend1)
        middleware2 = BearerAuthMiddleware(middleware1, backend2)

        # Test that the chain works
        scope = {"type": "http", "path": "/test", "headers": [(b"authorization", b"Bearer token")]}
        receive = AsyncMock()
        send = AsyncMock()

        await middleware2(scope, receive, send)

        # Verify the chain was called
        assert middleware1.app.call_count == 1
        assert mock_app.call_count == 1

    @pytest.mark.asyncio
    async def test_middleware_with_different_backends(self):
        """Test middleware with different authentication backends."""
        # Create backends that return different users
        backend1 = MockAuthenticationBackend(return_user=User(id="user1", username="user1", email="user1@example.com"))
        backend2 = MockAuthenticationBackend(return_user=User(id="user2", username="user2", email="user2@example.com"))

        # Test each backend
        for backend, expected_user_id in [(backend1, "user1"), (backend2, "user2")]:
            middleware = BearerAuthMiddleware(AsyncMock(), backend)
            scope = {"type": "http", "path": "/test", "headers": [(b"authorization", b"Bearer token")]}
            receive = AsyncMock()
            send = AsyncMock()

            await middleware(scope, receive, send)

            # Verify correct user was set
            call_scope = middleware.app.call_args[0][0]
            assert call_scope["user"].id == expected_user_id

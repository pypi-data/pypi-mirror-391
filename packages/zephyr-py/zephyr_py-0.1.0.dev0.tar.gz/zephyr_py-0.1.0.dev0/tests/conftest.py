"""
Pytest configuration and shared fixtures.

Provides common fixtures and configuration for all tests.
"""

import pytest
import asyncio
from typing import Generator

from zephyr.security.jwt import JWTManager, JWTConfig
from zephyr.security.tokens import TokenManager, TokenBlacklist
from zephyr.security.password import PasswordHasher
from zephyr.security.user import User, AnonymousUser
from zephyr.security.backends import JWTAuthenticationBackend, NoAuthenticationBackend
from zephyr.security.middleware.auth import BearerAuthMiddleware


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def jwt_config():
    """Create JWT configuration for tests."""
    return JWTConfig(secret_key="test-secret-key-12345")


@pytest.fixture
def jwt_manager(jwt_config):
    """Create JWT manager for tests."""
    return JWTManager(jwt_config)


@pytest.fixture
def blacklist():
    """Create token blacklist for tests."""
    return TokenBlacklist()


@pytest.fixture
def token_manager(jwt_manager, blacklist):
    """Create token manager for tests."""
    return TokenManager(jwt_manager, blacklist)


@pytest.fixture
def password_hasher():
    """Create password hasher for tests."""
    return PasswordHasher()


@pytest.fixture
def auth_backend(jwt_manager, token_manager):
    """Create JWT authentication backend for tests."""
    return JWTAuthenticationBackend(jwt_manager, token_manager)


@pytest.fixture
def no_auth_backend():
    """Create no authentication backend for tests."""
    return NoAuthenticationBackend()


@pytest.fixture
def mock_app():
    """Create mock ASGI app for tests."""
    return asyncio.create_task(lambda: None)


@pytest.fixture
def auth_middleware(mock_app, auth_backend):
    """Create Bearer auth middleware for tests."""
    return BearerAuthMiddleware(mock_app, auth_backend)


@pytest.fixture
def test_user():
    """Create test user for tests."""
    return User(
        id="test_user_123",
        username="testuser",
        email="test@example.com",
        is_active=True,
        is_superuser=False,
        roles=["user", "admin"],
        permissions=["read", "write", "delete"],
        mfa_enabled=False,
    )


@pytest.fixture
def anonymous_user():
    """Create anonymous user for tests."""
    return AnonymousUser()


@pytest.fixture
def superuser():
    """Create superuser for tests."""
    return User(
        id="super_user_123",
        username="superuser",
        email="super@example.com",
        is_active=True,
        is_superuser=True,
        roles=["superuser"],
        permissions=[],
        mfa_enabled=True,
    )


@pytest.fixture
def inactive_user():
    """Create inactive user for tests."""
    return User(
        id="inactive_user_123",
        username="inactiveuser",
        email="inactive@example.com",
        is_active=False,
        is_superuser=False,
        roles=["user"],
        permissions=["read"],
        mfa_enabled=False,
    )


@pytest.fixture
def http_scope():
    """Create HTTP ASGI scope for tests."""
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
def websocket_scope():
    """Create WebSocket ASGI scope for tests."""
    return {
        "type": "websocket",
        "path": "/ws",
        "headers": [],
        "query_string": b"",
        "client": ("127.0.0.1", 12345),
        "server": ("localhost", 8000),
    }


@pytest.fixture
def receive():
    """Create ASGI receive function for tests."""
    return asyncio.create_task(lambda: None)


@pytest.fixture
def send():
    """Create ASGI send function for tests."""
    return asyncio.create_task(lambda: None)


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom settings."""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "security: marks tests as security-related")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add unit marker to tests in test_*.py files
        if "test_" in item.nodeid and "integration" not in item.nodeid:
            item.add_marker(pytest.mark.unit)

        # Add security marker to tests in security/ directory
        if "security" in item.nodeid:
            item.add_marker(pytest.mark.security)

        # Add integration marker to tests in test_integration.py
        if "test_integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)


# Test data fixtures
@pytest.fixture
def sample_tokens():
    """Create sample tokens for testing."""
    return {
        "valid_access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyMTIzIiwidHlwZSI6ImFjY2VzcyIsImV4cCI6OTk5OTk5OTk5fQ.invalid_signature",
        "valid_refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyMTIzIiwidHlwZSI6InJlZnJlc2giLCJleHAiOjk5OTk5OTk5OX0.invalid_signature",
        "invalid": "invalid.token.here",
        "expired": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyMTIzIiwidHlwZSI6ImFjY2VzcyIsImV4cCI6MH0.invalid_signature",
        "malformed": "not.a.jwt",
        "empty": "",
    }


@pytest.fixture
def sample_passwords():
    """Create sample passwords for testing."""
    return {
        "valid": "secure_password_123",
        "short": "123",
        "long": "a" * 100,
        "empty": "",
        "special_chars": "P@ssw0rd!@#$%^&*()",
        "unicode": "пароль123",
        "common": "password",
        "weak": "123456",
    }


@pytest.fixture
def sample_users():
    """Create sample users for testing."""
    return {
        "admin": User(
            id="admin_123",
            username="admin",
            email="admin@example.com",
            is_active=True,
            is_superuser=True,
            roles=["admin", "superuser"],
            permissions=["*"],
            mfa_enabled=True,
        ),
        "user": User(
            id="user_123",
            username="user",
            email="user@example.com",
            is_active=True,
            is_superuser=False,
            roles=["user"],
            permissions=["read", "write"],
            mfa_enabled=False,
        ),
        "guest": User(
            id="guest_123",
            username="guest",
            email="guest@example.com",
            is_active=True,
            is_superuser=False,
            roles=["guest"],
            permissions=["read"],
            mfa_enabled=False,
        ),
        "inactive": User(
            id="inactive_123",
            username="inactive",
            email="inactive@example.com",
            is_active=False,
            is_superuser=False,
            roles=["user"],
            permissions=["read"],
            mfa_enabled=False,
        ),
    }


@pytest.fixture
def sample_roles():
    """Create sample roles for testing."""
    return {
        "admin": {"name": "admin", "description": "Administrator role", "permissions": ["*"]},
        "user": {"name": "user", "description": "Regular user role", "permissions": ["read", "write"]},
        "guest": {"name": "guest", "description": "Guest user role", "permissions": ["read"]},
        "moderator": {
            "name": "moderator",
            "description": "Moderator role",
            "permissions": ["read", "write", "moderate"],
        },
    }


@pytest.fixture
def sample_permissions():
    """Create sample permissions for testing."""
    return {
        "read": "Read access to resources",
        "write": "Write access to resources",
        "delete": "Delete access to resources",
        "moderate": "Moderate content",
        "admin": "Administrative access",
        "api_access": "API access",
        "user_management": "User management access",
        "system_config": "System configuration access",
    }

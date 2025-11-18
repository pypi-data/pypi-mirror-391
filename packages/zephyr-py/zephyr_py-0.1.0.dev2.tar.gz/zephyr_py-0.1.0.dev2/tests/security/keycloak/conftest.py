"""
Pytest fixtures for Keycloak tests.

Provides mock Keycloak server responses, sample tokens, and test data.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock
import httpx

from zephyr.security.keycloak.config import KeycloakConfig, KeycloakRealmConfig
from zephyr.security.keycloak.models import (
    KeycloakToken,
    KeycloakUser,
    KeycloakUserInfo,
    KeycloakRole,
    KeycloakGroup,
    KeycloakClient as KeycloakClientModel,
)


@pytest.fixture
def keycloak_config():
    """Keycloak configuration fixture."""
    return KeycloakConfig(
        server_url="https://keycloak.example.com",
        realm="test-realm",
        client_id="test-client",
        client_secret="test-secret",
        public_client=False,
        admin_username="admin",
        admin_password="admin-password",
    )


@pytest.fixture
def public_keycloak_config():
    """Public client Keycloak configuration fixture."""
    return KeycloakConfig(
        server_url="https://keycloak.example.com",
        realm="test-realm",
        client_id="test-public-client",
        public_client=True,
    )


@pytest.fixture
def realm_config():
    """Realm configuration fixture."""
    return KeycloakRealmConfig(
        realm="test-realm",
        display_name="Test Realm",
        enabled=True,
        registration_allowed=True,
        access_token_lifespan=300,
        refresh_token_lifespan=1800,
    )


@pytest.fixture
def sample_token():
    """Sample Keycloak token fixture."""
    return KeycloakToken(
        access_token="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.test",
        token_type="Bearer",
        expires_in=300,
        refresh_token="refresh_token_value",
        refresh_expires_in=1800,
        id_token="id_token_value",
        scope="openid profile email",
        session_state="session_state_value",
    )


@pytest.fixture
def sample_user():
    """Sample Keycloak user fixture."""
    return KeycloakUser(
        id="user-123",
        username="testuser",
        email="test@example.com",
        email_verified=True,
        first_name="Test",
        last_name="User",
        enabled=True,
        created_timestamp=int(datetime.utcnow().timestamp() * 1000),
        realm_roles=["user", "admin"],
        groups=["/test-group"],
    )


@pytest.fixture
def sample_user_info():
    """Sample UserInfo response fixture."""
    return KeycloakUserInfo(
        sub="user-123",
        email="test@example.com",
        email_verified=True,
        preferred_username="testuser",
        given_name="Test",
        family_name="User",
        name="Test User",
    )


@pytest.fixture
def sample_role():
    """Sample Keycloak role fixture."""
    return KeycloakRole(
        id="role-123",
        name="test-role",
        description="Test role",
        composite=False,
        client_role=False,
    )


@pytest.fixture
def sample_group():
    """Sample Keycloak group fixture."""
    return KeycloakGroup(
        id="group-123",
        name="test-group",
        path="/test-group",
        realm_roles=["user"],
    )


@pytest.fixture
def sample_client():
    """Sample Keycloak client fixture."""
    return KeycloakClientModel(
        id="client-uuid-123",
        client_id="test-client",
        name="Test Client",
        enabled=True,
        public_client=False,
        redirect_uris=["https://example.com/callback"],
        web_origins=["https://example.com"],
    )


@pytest.fixture
def mock_token_response():
    """Mock token endpoint response."""
    return {
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.test",
        "token_type": "Bearer",
        "expires_in": 300,
        "refresh_token": "refresh_token_value",
        "refresh_expires_in": 1800,
        "id_token": "id_token_value",
        "scope": "openid profile email",
        "session_state": "session_state_value",
    }


@pytest.fixture
def mock_userinfo_response():
    """Mock userinfo endpoint response."""
    return {
        "sub": "user-123",
        "email": "test@example.com",
        "email_verified": True,
        "preferred_username": "testuser",
        "given_name": "Test",
        "family_name": "User",
        "name": "Test User",
    }


@pytest.fixture
def mock_jwks_response():
    """Mock JWKS endpoint response."""
    return {
        "keys": [
            {
                "kid": "test-key-id",
                "kty": "RSA",
                "alg": "RS256",
                "use": "sig",
                "n": "test-modulus",
                "e": "AQAB",
            }
        ]
    }


@pytest.fixture
def mock_well_known_response():
    """Mock well-known configuration response."""
    return {
        "issuer": "https://keycloak.example.com/realms/test-realm",
        "authorization_endpoint": "https://keycloak.example.com/realms/test-realm/protocol/openid-connect/auth",
        "token_endpoint": "https://keycloak.example.com/realms/test-realm/protocol/openid-connect/token",
        "userinfo_endpoint": "https://keycloak.example.com/realms/test-realm/protocol/openid-connect/userinfo",
        "jwks_uri": "https://keycloak.example.com/realms/test-realm/protocol/openid-connect/certs",
        "end_session_endpoint": "https://keycloak.example.com/realms/test-realm/protocol/openid-connect/logout",
    }


@pytest.fixture
def mock_http_client(mock_token_response, mock_userinfo_response, mock_jwks_response):
    """Mock HTTP client for Keycloak requests."""
    client = AsyncMock(spec=httpx.AsyncClient)

    # Mock token endpoint
    token_response = Mock(spec=httpx.Response)
    token_response.status_code = 200
    token_response.json.return_value = mock_token_response

    # Mock userinfo endpoint
    userinfo_response = Mock(spec=httpx.Response)
    userinfo_response.status_code = 200
    userinfo_response.json.return_value = mock_userinfo_response

    # Mock JWKS endpoint
    jwks_response = Mock(spec=httpx.Response)
    jwks_response.status_code = 200
    jwks_response.json.return_value = mock_jwks_response

    # Configure mock to return appropriate response based on URL
    async def mock_post(url, **kwargs):
        if "token" in url:
            return token_response
        return Mock(status_code=404)

    async def mock_get(url, **kwargs):
        if "userinfo" in url:
            return userinfo_response
        elif "certs" in url:
            return jwks_response
        return Mock(status_code=404)

    client.post = mock_post
    client.get = mock_get
    client.aclose = AsyncMock()

    return client

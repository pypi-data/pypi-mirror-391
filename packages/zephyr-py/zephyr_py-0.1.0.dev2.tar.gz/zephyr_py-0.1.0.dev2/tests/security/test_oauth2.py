"""
Tests for OAuth2 server implementation.

Tests OAuth2 flows, endpoints, and security features.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from zephyr.security.oauth2 import (
    OAuth2Server,
    OAuth2Config,
    OAuth2Client,
    OAuth2AccessToken,
    OAuth2RefreshToken,
    OAuth2AuthorizationCode,
    OAuth2DeviceCode,
)
from zephyr.security.oauth2.exceptions import (
    InvalidClientError,
    InvalidGrantError,
    InvalidRequestError,
    InvalidScopeError,
    UnsupportedGrantTypeError,
    UnsupportedResponseTypeError,
    AccessDeniedError,
)


class TestOAuth2Config:
    """Test OAuth2 configuration."""

    def test_default_config(self):
        """Test default OAuth2 configuration."""
        config = OAuth2Config()

        assert config.server_name == "Zephyr OAuth2 Server"
        assert config.server_url == "http://localhost:8000"
        assert config.access_token_lifetime == 3600
        assert config.refresh_token_lifetime == 86400 * 7
        assert config.authorization_code_lifetime == 600
        assert config.device_code_lifetime == 1800
        assert config.access_token_type == "Bearer"
        assert "authorization_code" in config.supported_grant_types
        assert "client_credentials" in config.supported_grant_types
        assert "refresh_token" in config.supported_grant_types
        assert "device_code" in config.supported_grant_types
        assert "code" in config.supported_response_types
        assert "token" in config.supported_response_types
        assert "read" in config.default_scopes
        assert "read" in config.supported_scopes
        assert config.require_pkce is True
        assert "S256" in config.supported_code_challenge_methods
        assert "plain" in config.supported_code_challenge_methods

    def test_custom_config(self):
        """Test custom OAuth2 configuration."""
        config = OAuth2Config(
            server_name="Custom OAuth2 Server",
            server_url="https://auth.example.com",
            access_token_lifetime=7200,
            refresh_token_lifetime=86400 * 14,
            supported_grant_types=["authorization_code", "client_credentials"],
            supported_scopes=["read", "write", "admin"],
            require_pkce=False,
            allow_implicit_grant=True,
        )

        assert config.server_name == "Custom OAuth2 Server"
        assert config.server_url == "https://auth.example.com"
        assert config.access_token_lifetime == 7200
        assert config.refresh_token_lifetime == 86400 * 14
        assert config.supported_grant_types == ["authorization_code", "client_credentials"]
        assert config.supported_scopes == ["read", "write", "admin"]
        assert config.require_pkce is False
        assert config.allow_implicit_grant is True

    def test_config_validation(self):
        """Test configuration validation."""
        # Test invalid access token type
        with pytest.raises(ValueError, match="Access token type must be 'Bearer' or 'MAC'"):
            OAuth2Config(access_token_type="Invalid")

        # Test invalid grant type
        with pytest.raises(ValueError, match="Invalid grant type"):
            OAuth2Config(supported_grant_types=["invalid_grant"])

        # Test invalid response type
        with pytest.raises(ValueError, match="Invalid response type"):
            OAuth2Config(supported_response_types=["invalid_response"])

        # Test invalid code challenge method
        with pytest.raises(ValueError, match="Invalid code challenge method"):
            OAuth2Config(supported_code_challenge_methods=["invalid_method"])

        # Test invalid log level
        with pytest.raises(ValueError, match="Invalid log level"):
            OAuth2Config(log_level="invalid")

    def test_config_methods(self):
        """Test configuration utility methods."""
        config = OAuth2Config()

        # Test grant type support
        assert config.is_grant_type_supported("authorization_code") is True
        assert config.is_grant_type_supported("invalid_grant") is False

        # Test response type support
        assert config.is_response_type_supported("code") is True
        assert config.is_response_type_supported("invalid_response") is False

        # Test scope support
        assert config.is_scope_supported("read") is True
        assert config.is_scope_supported("invalid_scope") is False

        # Test code challenge method support
        assert config.is_code_challenge_method_supported("S256") is True
        assert config.is_code_challenge_method_supported("invalid_method") is False

        # Test token lifetime
        assert config.get_token_lifetime("access_token") == 3600
        assert config.get_token_lifetime("refresh_token") == 86400 * 7
        assert config.get_token_lifetime("authorization_code") == 600
        assert config.get_token_lifetime("device_code") == 1800

        # Test endpoint URLs
        assert config.get_endpoint_url("authorization") == "http://localhost:8000/oauth/authorize"
        assert config.get_endpoint_url("token") == "http://localhost:8000/oauth/token"
        assert config.get_endpoint_url("revocation") == "http://localhost:8000/oauth/revoke"
        assert config.get_endpoint_url("introspection") == "http://localhost:8000/oauth/introspect"


class TestOAuth2Server:
    """Test OAuth2 server functionality."""

    @pytest.fixture
    def config(self):
        """Create OAuth2 configuration for tests."""
        return OAuth2Config(
            server_url="http://localhost:8000",
            access_token_lifetime=3600,
            refresh_token_lifetime=86400,
            authorization_code_lifetime=600,
            device_code_lifetime=1800,
        )

    @pytest.fixture
    def server(self, config):
        """Create OAuth2 server for tests."""
        return OAuth2Server(config)

    def test_server_initialization(self, server, config):
        """Test server initialization."""
        assert server.config == config
        assert server.flow_manager is not None
        assert server.logger is not None

    def test_create_client(self, server):
        """Test client creation."""
        client = server.create_client(
            client_name="Test Client",
            client_type="confidential",
            redirect_uris=["http://localhost:3000/callback"],
            grant_types=["authorization_code", "client_credentials"],
            response_types=["code"],
            scopes=["read", "write"],
        )

        assert isinstance(client, OAuth2Client)
        assert client.client_name == "Test Client"
        assert client.client_type == "confidential"
        assert client.redirect_uris == ["http://localhost:3000/callback"]
        assert "authorization_code" in client.grant_types
        assert "client_credentials" in client.grant_types
        assert "code" in client.response_types
        assert "read" in client.scopes
        assert "write" in client.scopes
        assert client.is_active is True
        assert client.is_valid() is True

    def test_create_public_client(self, server):
        """Test public client creation."""
        client = server.create_client(client_name="Public Client", client_type="public")

        assert client.client_type == "public"
        assert client.client_secret == ""  # Public clients don't have secrets

    def test_get_client(self, server):
        """Test client retrieval."""
        client = server.create_client("Test Client")

        retrieved_client = server.get_client(client.client_id)
        assert retrieved_client == client

        # Test non-existent client
        non_existent = server.get_client("non-existent")
        assert non_existent is None

    def test_authenticate_client_success(self, server):
        """Test successful client authentication."""
        client = server.create_client("Test Client", client_type="confidential")

        authenticated = server.authenticate_client(client.client_id, client.client_secret)
        assert authenticated == client

    def test_authenticate_client_invalid_id(self, server):
        """Test client authentication with invalid ID."""
        with pytest.raises(InvalidClientError, match="Client not found"):
            server.authenticate_client("invalid-id", "secret")

    def test_authenticate_client_invalid_secret(self, server):
        """Test client authentication with invalid secret."""
        client = server.create_client("Test Client", client_type="confidential")

        with pytest.raises(InvalidClientError, match="Invalid client secret"):
            server.authenticate_client(client.client_id, "invalid-secret")

    def test_authenticate_client_missing_secret(self, server):
        """Test client authentication with missing secret for confidential client."""
        client = server.create_client("Test Client", client_type="confidential")

        with pytest.raises(InvalidClientError, match="Client secret required for confidential clients"):
            server.authenticate_client(client.client_id, None)

    def test_authenticate_public_client(self, server):
        """Test public client authentication."""
        client = server.create_client("Public Client", client_type="public")

        authenticated = server.authenticate_client(client.client_id)
        assert authenticated == client

    def test_handle_authorization_request_success(self, server):
        """Test successful authorization request."""
        client = server.create_client(
            "Test Client", redirect_uris=["http://localhost:3000/callback"], response_types=["code"]
        )

        result = server.handle_authorization_request(
            client_id=client.client_id,
            response_type="code",
            redirect_uri="http://localhost:3000/callback",
            scope="read write",
        )

        assert result["type"] == "redirect"
        assert "code=" in result["url"]
        assert "state" not in result or result["state"] is None

    def test_handle_authorization_request_with_state(self, server):
        """Test authorization request with state parameter."""
        client = server.create_client(
            "Test Client", redirect_uris=["http://localhost:3000/callback"], response_types=["code"]
        )

        result = server.handle_authorization_request(
            client_id=client.client_id,
            response_type="code",
            redirect_uri="http://localhost:3000/callback",
            scope="read",
            state="test-state",
        )

        assert result["type"] == "redirect"
        assert "state=test-state" in result["url"]

    def test_handle_authorization_request_invalid_client(self, server):
        """Test authorization request with invalid client."""
        result = server.handle_authorization_request(
            client_id="invalid-client", response_type="code", redirect_uri="http://localhost:3000/callback"
        )

        assert result["type"] == "redirect"
        assert "error=invalid_client" in result["url"]

    def test_handle_authorization_request_invalid_response_type(self, server):
        """Test authorization request with invalid response type."""
        client = server.create_client("Test Client")

        result = server.handle_authorization_request(
            client_id=client.client_id, response_type="invalid_type", redirect_uri="http://localhost:3000/callback"
        )

        assert result["type"] == "redirect"
        assert "error=unsupported_response_type" in result["url"]

    def test_handle_authorization_request_invalid_redirect_uri(self, server):
        """Test authorization request with invalid redirect URI."""
        client = server.create_client("Test Client", redirect_uris=["http://localhost:3000/callback"])

        result = server.handle_authorization_request(
            client_id=client.client_id, response_type="code", redirect_uri="http://malicious.com/callback"
        )

        assert result["type"] == "redirect"
        assert "error=invalid_request" in result["url"]

    def test_handle_token_request_authorization_code(self, server):
        """Test token request with authorization code grant."""
        client = server.create_client("Test Client", grant_types=["authorization_code"])

        # Create authorization code
        auth_code = server.flow_manager.flows["authorization_code"].create_authorization_code(
            client=client, user_id="user123", redirect_uri="http://localhost:3000/callback", scopes=["read", "write"]
        )
        server._authorization_codes[auth_code.code] = auth_code

        result = server.handle_token_request(
            grant_type="authorization_code",
            client_id=client.client_id,
            client_secret=client.client_secret,
            code=auth_code.code,
            redirect_uri="http://localhost:3000/callback",
        )

        assert "access_token" in result
        assert "token_type" in result
        assert "expires_in" in result
        assert "refresh_token" in result
        assert "scope" in result
        assert result["token_type"] == "Bearer"
        assert result["expires_in"] == 3600

    def test_handle_token_request_client_credentials(self, server):
        """Test token request with client credentials grant."""
        client = server.create_client("Test Client", grant_types=["client_credentials"])

        result = server.handle_token_request(
            grant_type="client_credentials",
            client_id=client.client_id,
            client_secret=client.client_secret,
            scope="read write",
        )

        assert "access_token" in result
        assert "token_type" in result
        assert "expires_in" in result
        assert "scope" in result
        assert "refresh_token" not in result  # Client credentials doesn't return refresh token
        assert result["token_type"] == "Bearer"
        assert result["expires_in"] == 3600

    def test_handle_token_request_refresh_token(self, server):
        """Test token request with refresh token grant."""
        client = server.create_client("Test Client", grant_types=["refresh_token"])

        # Create refresh token
        refresh_token = server.flow_manager.flows["refresh_token"].create_refresh_token(
            client=client, user_id="user123", scopes=["read", "write"]
        )
        server._refresh_tokens[refresh_token.token] = refresh_token

        result = server.handle_token_request(
            grant_type="refresh_token",
            client_id=client.client_id,
            client_secret=client.client_secret,
            refresh_token=refresh_token.token,
            scope="read",
        )

        assert "access_token" in result
        assert "token_type" in result
        assert "expires_in" in result
        assert "refresh_token" in result
        assert "scope" in result
        assert result["token_type"] == "Bearer"
        assert result["expires_in"] == 3600

    def test_handle_token_request_invalid_grant_type(self, server):
        """Test token request with invalid grant type."""
        client = server.create_client("Test Client")

        result = server.handle_token_request(
            grant_type="invalid_grant", client_id=client.client_id, client_secret=client.client_secret
        )

        assert "error" in result
        assert result["error"] == "unsupported_grant_type"

    def test_handle_token_request_missing_client_id(self, server):
        """Test token request with missing client ID."""
        result = server.handle_token_request(grant_type="client_credentials")

        assert "error" in result
        assert result["error"] == "invalid_request"

    def test_handle_token_request_invalid_client(self, server):
        """Test token request with invalid client."""
        result = server.handle_token_request(
            grant_type="client_credentials", client_id="invalid-client", client_secret="secret"
        )

        assert "error" in result
        assert result["error"] == "invalid_client"

    def test_get_access_token(self, server):
        """Test access token retrieval."""
        client = server.create_client("Test Client")

        # Create access token
        access_token = server.flow_manager.flows["client_credentials"].create_access_token(
            client=client, scopes=["read"]
        )
        server._access_tokens[access_token.token] = access_token

        retrieved = server.get_access_token(access_token.token)
        assert retrieved == access_token

        # Test non-existent token
        non_existent = server.get_access_token("non-existent")
        assert non_existent is None

    def test_revoke_access_token(self, server):
        """Test access token revocation."""
        client = server.create_client("Test Client")

        # Create access token
        access_token = server.flow_manager.flows["client_credentials"].create_access_token(
            client=client, scopes=["read"]
        )
        server._access_tokens[access_token.token] = access_token

        # Revoke token
        revoked = server.revoke_access_token(access_token.token)
        assert revoked is True
        assert access_token.is_revoked is True

        # Test revoking non-existent token
        not_revoked = server.revoke_access_token("non-existent")
        assert not_revoked is False

    def test_revoke_refresh_token(self, server):
        """Test refresh token revocation."""
        client = server.create_client("Test Client")

        # Create refresh token
        refresh_token = server.flow_manager.flows["refresh_token"].create_refresh_token(
            client=client, user_id="user123", scopes=["read"]
        )
        server._refresh_tokens[refresh_token.token] = refresh_token

        # Revoke token
        revoked = server.revoke_refresh_token(refresh_token.token)
        assert revoked is True
        assert refresh_token.is_revoked is True

        # Test revoking non-existent token
        not_revoked = server.revoke_refresh_token("non-existent")
        assert not_revoked is False

    def test_introspect_token(self, server):
        """Test token introspection."""
        client = server.create_client("Test Client")

        # Create access token
        access_token = server.flow_manager.flows["client_credentials"].create_access_token(
            client=client, scopes=["read", "write"]
        )
        server._access_tokens[access_token.token] = access_token

        # Introspect valid token
        result = server.introspect_token(access_token.token)
        assert result["active"] is True
        assert result["client_id"] == client.client_id
        assert result["user_id"] is None  # Client credentials flow
        assert result["scope"] == "read write"
        assert result["token_type"] == "Bearer"
        assert "exp" in result
        assert "iat" in result

        # Introspect invalid token
        invalid_result = server.introspect_token("invalid-token")
        assert invalid_result["active"] is False

    def test_introspect_revoked_token(self, server):
        """Test introspection of revoked token."""
        client = server.create_client("Test Client")

        # Create and revoke access token
        access_token = server.flow_manager.flows["client_credentials"].create_access_token(
            client=client, scopes=["read"]
        )
        server._access_tokens[access_token.token] = access_token
        access_token.revoke()

        # Introspect revoked token
        result = server.introspect_token(access_token.token)
        assert result["active"] is False


class TestOAuth2Flows:
    """Test OAuth2 flows functionality."""

    @pytest.fixture
    def config(self):
        """Create OAuth2 configuration for tests."""
        return OAuth2Config()

    @pytest.fixture
    def client(self):
        """Create OAuth2 client for tests."""
        return OAuth2Client(
            client_id="test-client",
            client_secret="test-secret",
            client_name="Test Client",
            client_type="confidential",
            redirect_uris=["http://localhost:3000/callback"],
            grant_types=["authorization_code", "client_credentials"],
            response_types=["code"],
            scopes=["read", "write"],
        )

    def test_authorization_code_flow(self, config, client):
        """Test authorization code flow."""
        flow = config.flow_manager.flows["authorization_code"]

        # Create authorization code
        auth_code = flow.create_authorization_code(
            client=client, user_id="user123", redirect_uri="http://localhost:3000/callback", scopes=["read", "write"]
        )

        assert isinstance(auth_code, OAuth2AuthorizationCode)
        assert auth_code.client_id == client.client_id
        assert auth_code.user_id == "user123"
        assert auth_code.redirect_uri == "http://localhost:3000/callback"
        assert auth_code.scopes == ["read", "write"]
        assert auth_code.is_valid() is True

    def test_client_credentials_flow(self, config, client):
        """Test client credentials flow."""
        flow = config.flow_manager.flows["client_credentials"]

        # Create access token
        access_token = flow.create_access_token(client=client, scopes=["read", "write"])

        assert isinstance(access_token, OAuth2AccessToken)
        assert access_token.client_id == client.client_id
        assert access_token.user_id is None  # No user in client credentials flow
        assert access_token.scopes == ["read", "write"]
        assert access_token.is_valid() is True

    def test_pkce_flow(self, config):
        """Test PKCE flow."""
        flow = config.flow_manager.pkce_flow

        # Generate code verifier and challenge
        code_verifier = flow.generate_code_verifier()
        code_challenge = flow.generate_code_challenge(code_verifier, "S256")

        assert isinstance(code_verifier, str)
        assert isinstance(code_challenge, str)
        assert len(code_verifier) > 0
        assert len(code_challenge) > 0

        # Validate code challenge
        is_valid = flow.validate_code_challenge(code_challenge, code_verifier, "S256")
        assert is_valid is True

    def test_device_flow(self, config, client):
        """Test device flow."""
        flow = config.flow_manager.flows["device_code"]

        # Create device code
        device_code = flow.create_device_code(client=client, scopes=["read", "write"])

        assert isinstance(device_code, OAuth2DeviceCode)
        assert device_code.client_id == client.client_id
        assert device_code.scopes == ["read", "write"]
        assert device_code.is_valid() is True
        assert device_code.is_authorized is False

    def test_refresh_token_flow(self, config, client):
        """Test refresh token flow."""
        flow = config.flow_manager.flows["refresh_token"]

        # Create refresh token
        refresh_token = flow.create_refresh_token(client=client, user_id="user123", scopes=["read", "write"])

        assert isinstance(refresh_token, OAuth2RefreshToken)
        assert refresh_token.client_id == client.client_id
        assert refresh_token.user_id == "user123"
        assert refresh_token.scopes == ["read", "write"]
        assert refresh_token.is_valid() is True

    def test_flow_validation(self, config, client):
        """Test flow validation."""
        # Test valid client
        flow = config.flow_manager.flows["authorization_code"]
        flow.validate_client(client, "authorization_code")

        # Test invalid grant type
        with pytest.raises(UnsupportedGrantTypeError):
            flow.validate_client(client, "invalid_grant")

        # Test scope validation
        scopes = flow.validate_scope("read write", client)
        assert scopes == ["read", "write"]

        # Test invalid scope
        with pytest.raises(InvalidScopeError):
            flow.validate_scope("invalid_scope", client)

        # Test redirect URI validation
        flow.validate_redirect_uri("http://localhost:3000/callback", client)

        # Test invalid redirect URI
        with pytest.raises(InvalidRedirectUriError):
            flow.validate_redirect_uri("http://malicious.com/callback", client)


class TestOAuth2Models:
    """Test OAuth2 models functionality."""

    def test_oauth2_client_creation(self):
        """Test OAuth2 client creation."""
        client = OAuth2Client(
            client_id="test-client",
            client_secret="test-secret",
            client_name="Test Client",
            client_type="confidential",
            redirect_uris=["http://localhost:3000/callback"],
            grant_types=["authorization_code"],
            response_types=["code"],
            scopes=["read", "write"],
        )

        assert client.client_id == "test-client"
        assert client.client_secret == "test-secret"
        assert client.client_name == "Test Client"
        assert client.client_type == "confidential"
        assert client.redirect_uris == ["http://localhost:3000/callback"]
        assert client.grant_types == ["authorization_code"]
        assert client.response_types == ["code"]
        assert client.scopes == ["read", "write"]
        assert client.is_active is True
        assert client.is_valid() is True

    def test_oauth2_client_validation(self):
        """Test OAuth2 client validation."""
        # Test invalid client type
        with pytest.raises(ValueError, match="Client type must be 'confidential' or 'public'"):
            OAuth2Client(client_id="test", client_secret="secret", client_name="Test", client_type="invalid")

        # Test invalid redirect URI
        with pytest.raises(ValueError, match="Invalid redirect URI"):
            OAuth2Client(client_id="test", client_secret="secret", client_name="Test", redirect_uris=["invalid-uri"])

        # Test invalid grant type
        with pytest.raises(ValueError, match="Invalid grant type"):
            OAuth2Client(client_id="test", client_secret="secret", client_name="Test", grant_types=["invalid_grant"])

        # Test invalid response type
        with pytest.raises(ValueError, match="Invalid response type"):
            OAuth2Client(
                client_id="test", client_secret="secret", client_name="Test", response_types=["invalid_response"]
            )

    def test_oauth2_client_methods(self):
        """Test OAuth2 client utility methods."""
        client = OAuth2Client(
            client_id="test-client",
            client_secret="test-secret",
            client_name="Test Client",
            redirect_uris=["http://localhost:3000/callback"],
            grant_types=["authorization_code"],
            response_types=["code"],
            scopes=["read", "write"],
        )

        # Test redirect URI validation
        assert client.is_redirect_uri_allowed("http://localhost:3000/callback") is True
        assert client.is_redirect_uri_allowed("http://malicious.com/callback") is False

        # Test grant type validation
        assert client.is_grant_type_allowed("authorization_code") is True
        assert client.is_grant_type_allowed("client_credentials") is False

        # Test response type validation
        assert client.is_response_type_allowed("code") is True
        assert client.is_response_type_allowed("token") is False

        # Test scope validation
        assert client.is_scope_allowed("read") is True
        assert client.is_scope_allowed("admin") is False
        assert client.is_scope_allowed("read write") is True
        assert client.is_scope_allowed("read admin") is False

    def test_oauth2_access_token(self):
        """Test OAuth2 access token."""
        from datetime import datetime, timedelta

        token = OAuth2AccessToken(
            token="test-token",
            token_type="Bearer",
            client_id="test-client",
            user_id="user123",
            scopes=["read", "write"],
            expires_at=datetime.utcnow() + timedelta(hours=1),
        )

        assert token.token == "test-token"
        assert token.token_type == "Bearer"
        assert token.client_id == "test-client"
        assert token.user_id == "user123"
        assert token.scopes == ["read", "write"]
        assert token.is_valid() is True
        assert token.is_revoked is False

        # Test scope checking
        assert token.has_scope("read") is True
        assert token.has_scope("admin") is False
        assert token.has_any_scope(["read", "admin"]) is True
        assert token.has_all_scopes(["read", "write"]) is True
        assert token.has_all_scopes(["read", "admin"]) is False

        # Test revocation
        token.revoke()
        assert token.is_revoked is True
        assert token.is_valid() is False

    def test_oauth2_refresh_token(self):
        """Test OAuth2 refresh token."""
        from datetime import datetime, timedelta

        token = OAuth2RefreshToken(
            token="test-refresh-token",
            client_id="test-client",
            user_id="user123",
            scopes=["read", "write"],
            expires_at=datetime.utcnow() + timedelta(days=7),
        )

        assert token.token == "test-refresh-token"
        assert token.client_id == "test-client"
        assert token.user_id == "user123"
        assert token.scopes == ["read", "write"]
        assert token.is_valid() is True
        assert token.is_revoked is False

        # Test scope checking
        assert token.has_scope("read") is True
        assert token.has_scope("admin") is False
        assert token.has_any_scope(["read", "admin"]) is True
        assert token.has_all_scopes(["read", "write"]) is True
        assert token.has_all_scopes(["read", "admin"]) is False

        # Test revocation
        token.revoke()
        assert token.is_revoked is True
        assert token.is_valid() is False

    def test_oauth2_authorization_code(self):
        """Test OAuth2 authorization code."""
        from datetime import datetime, timedelta

        code = OAuth2AuthorizationCode(
            code="test-code",
            client_id="test-client",
            user_id="user123",
            redirect_uri="http://localhost:3000/callback",
            scopes=["read", "write"],
            expires_at=datetime.utcnow() + timedelta(minutes=10),
        )

        assert code.code == "test-code"
        assert code.client_id == "test-client"
        assert code.user_id == "user123"
        assert code.redirect_uri == "http://localhost:3000/callback"
        assert code.scopes == ["read", "write"]
        assert code.is_valid() is True
        assert code.is_used is False

        # Test marking as used
        code.mark_as_used()
        assert code.is_used is True
        assert code.is_valid() is False

    def test_oauth2_device_code(self):
        """Test OAuth2 device code."""
        from datetime import datetime, timedelta

        device = OAuth2DeviceCode(
            device_code="test-device-code",
            user_code="ABC123",
            client_id="test-client",
            scopes=["read", "write"],
            expires_at=datetime.utcnow() + timedelta(minutes=30),
        )

        assert device.device_code == "test-device-code"
        assert device.user_code == "ABC123"
        assert device.client_id == "test-client"
        assert device.scopes == ["read", "write"]
        assert device.is_valid() is True
        assert device.is_authorized is False

        # Test authorization
        device.authorize("user123")
        assert device.user_id == "user123"
        assert device.is_authorized is True

        # Test expiration
        device.expire()
        assert device.is_expired is True
        assert device.is_valid() is False

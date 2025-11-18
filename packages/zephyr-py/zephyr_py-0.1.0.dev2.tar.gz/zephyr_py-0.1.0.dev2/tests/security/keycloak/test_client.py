"""
Tests for Keycloak OAuth2/OIDC client.

Tests authentication flows, token operations, and user info retrieval.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
import httpx

from zephyr.security.keycloak.client import KeycloakClient
from zephyr.security.keycloak.exceptions import (
    KeycloakAuthenticationError,
    KeycloakConnectionError,
    KeycloakInvalidTokenError,
    KeycloakExpiredTokenError,
)


class TestKeycloakClient:
    """Test Keycloak client."""

    @pytest.mark.asyncio
    async def test_client_initialization(self, keycloak_config):
        """Test client initialization."""
        async with KeycloakClient(keycloak_config) as client:
            assert client.config == keycloak_config
            assert client.http_client is not None

    def test_get_authorization_url(self, keycloak_config):
        """Test authorization URL generation."""
        client = KeycloakClient(keycloak_config)
        url = client.get_authorization_url(redirect_uri="https://example.com/callback", state="test-state")

        assert "https://keycloak.example.com/realms/test-realm/protocol/openid-connect/auth" in url
        assert "client_id=test-client" in url
        assert "redirect_uri=https%3A%2F%2Fexample.com%2Fcallback" in url
        assert "state=test-state" in url
        assert "scope=openid+profile+email" in url

    def test_get_authorization_url_custom_scopes(self, keycloak_config):
        """Test authorization URL with custom scopes."""
        client = KeycloakClient(keycloak_config)
        url = client.get_authorization_url(redirect_uri="https://example.com/callback", scopes=["openid", "custom"])

        assert "scope=openid+custom" in url

    @pytest.mark.asyncio
    async def test_exchange_code_for_token_success(self, keycloak_config, mock_token_response):
        """Test successful code exchange."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = Mock(spec=httpx.Response)
            mock_response.status_code = 200
            mock_response.json.return_value = mock_token_response

            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            async with KeycloakClient(keycloak_config) as client:
                client.http_client = mock_client

                token = await client.exchange_code_for_token(
                    code="test-code", redirect_uri="https://example.com/callback"
                )

                assert token.access_token == mock_token_response["access_token"]
                assert token.token_type == "Bearer"
                assert token.expires_in == 300

    @pytest.mark.asyncio
    async def test_exchange_code_for_token_failure(self, keycloak_config):
        """Test failed code exchange."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = Mock(spec=httpx.Response)
            mock_response.status_code = 400
            mock_response.text = "Invalid code"

            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            async with KeycloakClient(keycloak_config) as client:
                client.http_client = mock_client

                with pytest.raises(KeycloakAuthenticationError):
                    await client.exchange_code_for_token(
                        code="invalid-code", redirect_uri="https://example.com/callback"
                    )

    @pytest.mark.asyncio
    async def test_exchange_code_with_pkce(self, keycloak_config, mock_token_response):
        """Test code exchange with PKCE."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = Mock(spec=httpx.Response)
            mock_response.status_code = 200
            mock_response.json.return_value = mock_token_response

            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            async with KeycloakClient(keycloak_config) as client:
                client.http_client = mock_client

                token = await client.exchange_code_for_token(
                    code="test-code", redirect_uri="https://example.com/callback", code_verifier="test-verifier"
                )

                assert token.access_token == mock_token_response["access_token"]

    @pytest.mark.asyncio
    async def test_refresh_token_success(self, keycloak_config, mock_token_response):
        """Test successful token refresh."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = Mock(spec=httpx.Response)
            mock_response.status_code = 200
            mock_response.json.return_value = mock_token_response

            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            async with KeycloakClient(keycloak_config) as client:
                client.http_client = mock_client

                token = await client.refresh_token("refresh_token_value")

                assert token.access_token == mock_token_response["access_token"]

    @pytest.mark.asyncio
    async def test_get_user_info_success(self, keycloak_config, mock_userinfo_response):
        """Test successful user info retrieval."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = Mock(spec=httpx.Response)
            mock_response.status_code = 200
            mock_response.json.return_value = mock_userinfo_response

            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            async with KeycloakClient(keycloak_config) as client:
                client.http_client = mock_client

                user_info = await client.get_user_info("access_token")

                assert user_info.sub == "user-123"
                assert user_info.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_logout_success(self, keycloak_config):
        """Test successful logout."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = Mock(spec=httpx.Response)
            mock_response.status_code = 204

            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            async with KeycloakClient(keycloak_config) as client:
                client.http_client = mock_client

                await client.logout("refresh_token_value")

                # Should not raise exception

    @pytest.mark.asyncio
    async def test_introspect_token_success(self, keycloak_config):
        """Test successful token introspection."""
        introspection_response = {"active": True, "sub": "user-123", "exp": 1234567890}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = Mock(spec=httpx.Response)
            mock_response.status_code = 200
            mock_response.json.return_value = introspection_response

            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            async with KeycloakClient(keycloak_config) as client:
                client.http_client = mock_client

                result = await client.introspect_token("test_token")

                assert result["active"] is True
                assert result["sub"] == "user-123"

    @pytest.mark.asyncio
    async def test_get_jwks_success(self, keycloak_config, mock_jwks_response):
        """Test successful JWKS retrieval."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = Mock(spec=httpx.Response)
            mock_response.status_code = 200
            mock_response.json.return_value = mock_jwks_response

            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            async with KeycloakClient(keycloak_config) as client:
                client.http_client = mock_client

                jwks = await client.get_jwks()

                assert "keys" in jwks
                assert len(jwks["keys"]) == 1

    @pytest.mark.asyncio
    async def test_get_jwks_cached(self, keycloak_config, mock_jwks_response):
        """Test JWKS caching."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = Mock(spec=httpx.Response)
            mock_response.status_code = 200
            mock_response.json.return_value = mock_jwks_response

            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            async with KeycloakClient(keycloak_config) as client:
                client.http_client = mock_client

                # First call
                jwks1 = await client.get_jwks()

                # Second call should use cache
                jwks2 = await client.get_jwks()

                assert jwks1 == jwks2
                # Should only call once due to caching
                assert mock_client.get.call_count == 1

    @pytest.mark.asyncio
    async def test_get_well_known_config(self, keycloak_config, mock_well_known_response):
        """Test getting well-known configuration."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = Mock(spec=httpx.Response)
            mock_response.status_code = 200
            mock_response.json.return_value = mock_well_known_response

            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            async with KeycloakClient(keycloak_config) as client:
                client.http_client = mock_client

                config = await client.get_well_known_config()

                assert "issuer" in config
                assert "authorization_endpoint" in config
                assert "token_endpoint" in config

    def test_generate_pkce_challenge(self, keycloak_config):
        """Test PKCE challenge generation."""
        client = KeycloakClient(keycloak_config)

        verifier, challenge = client.generate_pkce_challenge()

        assert verifier is not None
        assert challenge is not None
        assert len(verifier) > 0
        assert len(challenge) > 0

    def test_generate_pkce_challenge_with_verifier(self, keycloak_config):
        """Test PKCE challenge generation with provided verifier."""
        client = KeycloakClient(keycloak_config)

        custom_verifier = "custom_verifier_value"
        verifier, challenge = client.generate_pkce_challenge(custom_verifier)

        assert verifier == custom_verifier
        assert challenge is not None

    @pytest.mark.asyncio
    async def test_connection_error(self, keycloak_config):
        """Test connection error handling."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.post.side_effect = httpx.RequestError("Connection failed")
            mock_client_class.return_value = mock_client

            async with KeycloakClient(keycloak_config) as client:
                client.http_client = mock_client

                with pytest.raises(KeycloakConnectionError):
                    await client.exchange_code_for_token(code="test-code", redirect_uri="https://example.com/callback")

"""
Tests for Keycloak SSO provider integration.

Tests SSO provider functionality and user mapping.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch

from zephyr.security.keycloak.provider import KeycloakSSOProvider
from zephyr.security.keycloak.models import KeycloakToken, KeycloakUserInfo
from zephyr.security.sso.models import SSOUser


class TestKeycloakSSOProvider:
    """Test Keycloak SSO provider."""

    def test_provider_initialization(self, keycloak_config):
        """Test provider initialization."""
        provider = KeycloakSSOProvider(keycloak_config)

        assert provider.keycloak_config == keycloak_config
        assert provider.keycloak_client is not None

    def test_get_provider_name(self, keycloak_config):
        """Test provider name."""
        provider = KeycloakSSOProvider(keycloak_config)

        assert provider.get_provider_name() == "keycloak"

    def test_get_authorization_url(self, keycloak_config):
        """Test authorization URL generation."""
        provider = KeycloakSSOProvider(keycloak_config)

        url = provider.get_authorization_url(state="test-state", redirect_uri="https://example.com/callback")

        assert "https://keycloak.example.com" in url
        assert "state=test-state" in url

    def test_get_authorization_url_missing_redirect_uri(self, keycloak_config):
        """Test authorization URL without redirect URI."""
        provider = KeycloakSSOProvider(keycloak_config)

        with pytest.raises(ValueError):
            provider.get_authorization_url(state="test-state")

    @pytest.mark.asyncio
    async def test_exchange_code_for_token_success(self, keycloak_config, sample_token):
        """Test successful code exchange."""
        provider = KeycloakSSOProvider(keycloak_config)

        with patch.object(provider.keycloak_client, "exchange_code_for_token") as mock_exchange:
            mock_exchange.return_value = sample_token

            # Set redirect_uri in config for test
            provider.config["redirect_uri"] = "https://example.com/callback"

            token_data = await provider.exchange_code_for_token("test-code", "test-state")

            assert token_data["access_token"] == sample_token.access_token
            assert token_data["token_type"] == sample_token.token_type

    @pytest.mark.asyncio
    async def test_get_user_info_success(self, keycloak_config, sample_user_info):
        """Test successful user info retrieval."""
        provider = KeycloakSSOProvider(keycloak_config)

        with patch.object(provider.keycloak_client, "get_user_info") as mock_get_user:
            mock_get_user.return_value = sample_user_info

            user_data = await provider.get_user_info("access_token")

            assert user_data["sub"] == sample_user_info.sub
            assert user_data["email"] == sample_user_info.email

    def test_map_user_data(self, keycloak_config):
        """Test user data mapping."""
        provider = KeycloakSSOProvider(keycloak_config)

        user_data = {
            "sub": "user-123",
            "email": "test@example.com",
            "email_verified": True,
            "preferred_username": "testuser",
            "given_name": "Test",
            "family_name": "User",
            "name": "Test User",
        }

        sso_user = provider.map_user_data(user_data)

        assert isinstance(sso_user, SSOUser)
        assert sso_user.id == "user-123"
        assert sso_user.email == "test@example.com"
        assert sso_user.username == "testuser"
        assert sso_user.first_name == "Test"
        assert sso_user.last_name == "User"
        assert sso_user.display_name == "Test User"
        assert sso_user.is_verified is True
        assert sso_user.provider == "keycloak"

    def test_map_user_data_custom_mapping(self):
        """Test user data mapping with custom mapping."""
        from zephyr.security.keycloak.config import KeycloakConfig

        config = KeycloakConfig(
            server_url="https://keycloak.example.com",
            realm="test-realm",
            client_id="test-client",
            client_secret="test-secret",
            user_mapping={
                "id": "user_id",
                "email": "user_email",
                "username": "user_name",
            },
        )

        provider = KeycloakSSOProvider(config)

        user_data = {
            "user_id": "user-123",
            "user_email": "test@example.com",
            "user_name": "testuser",
        }

        sso_user = provider.map_user_data(user_data)

        assert sso_user.id == "user-123"
        assert sso_user.email == "test@example.com"
        assert sso_user.username == "testuser"

    @pytest.mark.asyncio
    async def test_authenticate_success(self, keycloak_config, sample_token, sample_user_info):
        """Test successful authentication flow."""
        provider = KeycloakSSOProvider(keycloak_config)
        provider.config["redirect_uri"] = "https://example.com/callback"

        with (
            patch.object(provider.keycloak_client, "exchange_code_for_token") as mock_exchange,
            patch.object(provider.keycloak_client, "get_user_info") as mock_get_user,
        ):
            mock_exchange.return_value = sample_token
            mock_get_user.return_value = sample_user_info

            result = await provider.authenticate("test-code", "test-state")

            assert result.success is True
            assert result.user is not None
            assert result.user.email == sample_user_info.email
            assert result.provider == "keycloak"
            assert result.state == "test-state"

    @pytest.mark.asyncio
    async def test_authenticate_failure(self, keycloak_config):
        """Test authentication failure."""
        provider = KeycloakSSOProvider(keycloak_config)
        provider.config["redirect_uri"] = "https://example.com/callback"

        with patch.object(provider.keycloak_client, "exchange_code_for_token") as mock_exchange:
            mock_exchange.side_effect = Exception("Authentication failed")

            result = await provider.authenticate("test-code", "test-state")

            assert result.success is False
            assert result.error is not None
            assert "Authentication failed" in result.error

    @pytest.mark.asyncio
    async def test_logout_success(self, keycloak_config):
        """Test successful logout."""
        provider = KeycloakSSOProvider(keycloak_config)

        with patch.object(provider.keycloak_client, "logout") as mock_logout:
            mock_logout.return_value = None

            await provider.logout("refresh_token", "https://example.com")

            mock_logout.assert_called_once_with(refresh_token="refresh_token", redirect_uri="https://example.com")

    @pytest.mark.asyncio
    async def test_refresh_token_success(self, keycloak_config, sample_token):
        """Test successful token refresh."""
        provider = KeycloakSSOProvider(keycloak_config)

        with patch.object(provider.keycloak_client, "refresh_token") as mock_refresh:
            mock_refresh.return_value = sample_token

            token_data = await provider.refresh_token("refresh_token")

            assert token_data["access_token"] == sample_token.access_token

    @pytest.mark.asyncio
    async def test_validate_token_success(self, keycloak_config):
        """Test successful token validation."""
        provider = KeycloakSSOProvider(keycloak_config)

        claims = {
            "sub": "user-123",
            "exp": 1234567890,
            "iat": 1234567000,
        }

        with patch.object(provider.keycloak_client, "validate_token") as mock_validate:
            mock_validate.return_value = claims

            result = await provider.validate_token("access_token")

            assert result["sub"] == "user-123"

    @pytest.mark.asyncio
    async def test_close(self, keycloak_config):
        """Test closing provider."""
        provider = KeycloakSSOProvider(keycloak_config)

        with patch.object(provider.keycloak_client, "close") as mock_close:
            await provider.close()

            mock_close.assert_called_once()

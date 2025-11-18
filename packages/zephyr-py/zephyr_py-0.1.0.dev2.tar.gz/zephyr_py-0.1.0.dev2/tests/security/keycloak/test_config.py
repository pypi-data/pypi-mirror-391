"""
Tests for Keycloak configuration.

Tests configuration validation, URL generation, and settings.
"""

import pytest
from pydantic import ValidationError

from zephyr.security.keycloak.config import KeycloakConfig, KeycloakRealmConfig


class TestKeycloakConfig:
    """Test Keycloak configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        config = KeycloakConfig(
            server_url="https://keycloak.example.com",
            realm="test-realm",
            client_id="test-client",
            client_secret="test-secret",
        )

        assert config.server_url == "https://keycloak.example.com"
        assert config.realm == "test-realm"
        assert config.client_id == "test-client"
        assert config.client_secret == "test-secret"
        assert config.public_client is False
        assert config.verify_token_signature is True
        assert config.default_scopes == ["openid", "profile", "email"]
        assert config.timeout == 30
        assert config.verify_ssl is True

    def test_public_client_config(self):
        """Test public client configuration."""
        config = KeycloakConfig(
            server_url="https://keycloak.example.com",
            realm="test-realm",
            client_id="test-client",
            public_client=True,
        )

        assert config.public_client is True
        assert config.client_secret is None

    def test_confidential_client_requires_secret(self):
        """Test that confidential clients require a secret."""
        with pytest.raises(ValidationError):
            KeycloakConfig(
                server_url="https://keycloak.example.com",
                realm="test-realm",
                client_id="test-client",
                public_client=False,
            )

    def test_server_url_normalization(self):
        """Test server URL normalization."""
        config = KeycloakConfig(
            server_url="https://keycloak.example.com/",
            realm="test-realm",
            client_id="test-client",
            client_secret="test-secret",
        )

        assert config.server_url == "https://keycloak.example.com"

    def test_server_url_validation(self):
        """Test server URL validation."""
        with pytest.raises(ValidationError):
            KeycloakConfig(
                server_url="invalid-url",
                realm="test-realm",
                client_id="test-client",
                client_secret="test-secret",
            )

    def test_get_realm_url(self, keycloak_config):
        """Test realm URL generation."""
        url = keycloak_config.get_realm_url()
        assert url == "https://keycloak.example.com/realms/test-realm"

    def test_get_authorization_endpoint(self, keycloak_config):
        """Test authorization endpoint URL generation."""
        url = keycloak_config.get_authorization_endpoint()
        assert url == "https://keycloak.example.com/realms/test-realm/protocol/openid-connect/auth"

    def test_get_token_endpoint(self, keycloak_config):
        """Test token endpoint URL generation."""
        url = keycloak_config.get_token_endpoint()
        assert url == "https://keycloak.example.com/realms/test-realm/protocol/openid-connect/token"

    def test_get_userinfo_endpoint(self, keycloak_config):
        """Test userinfo endpoint URL generation."""
        url = keycloak_config.get_userinfo_endpoint()
        assert url == "https://keycloak.example.com/realms/test-realm/protocol/openid-connect/userinfo"

    def test_get_jwks_uri(self, keycloak_config):
        """Test JWKS URI generation."""
        url = keycloak_config.get_jwks_uri()
        assert url == "https://keycloak.example.com/realms/test-realm/protocol/openid-connect/certs"

    def test_get_end_session_endpoint(self, keycloak_config):
        """Test logout endpoint URL generation."""
        url = keycloak_config.get_end_session_endpoint()
        assert url == "https://keycloak.example.com/realms/test-realm/protocol/openid-connect/logout"

    def test_get_introspection_endpoint(self, keycloak_config):
        """Test introspection endpoint URL generation."""
        url = keycloak_config.get_introspection_endpoint()
        assert url == "https://keycloak.example.com/realms/test-realm/protocol/openid-connect/token/introspect"

    def test_get_admin_url(self, keycloak_config):
        """Test admin API URL generation."""
        url = keycloak_config.get_admin_url()
        assert url == "https://keycloak.example.com/admin/realms/test-realm"

    def test_get_admin_token_endpoint(self, keycloak_config):
        """Test admin token endpoint URL generation."""
        url = keycloak_config.get_admin_token_endpoint()
        assert url == "https://keycloak.example.com/realms/master/protocol/openid-connect/token"

    def test_get_well_known_url(self, keycloak_config):
        """Test well-known configuration URL generation."""
        url = keycloak_config.get_well_known_url()
        assert url == "https://keycloak.example.com/realms/test-realm/.well-known/openid-configuration"

    def test_custom_endpoints(self):
        """Test custom endpoint URLs."""
        config = KeycloakConfig(
            server_url="https://keycloak.example.com",
            realm="test-realm",
            client_id="test-client",
            client_secret="test-secret",
            authorization_endpoint="https://custom.example.com/auth",
            token_endpoint="https://custom.example.com/token",
        )

        assert config.get_authorization_endpoint() == "https://custom.example.com/auth"
        assert config.get_token_endpoint() == "https://custom.example.com/token"

    def test_user_mapping(self, keycloak_config):
        """Test user mapping configuration."""
        assert "id" in keycloak_config.user_mapping
        assert "email" in keycloak_config.user_mapping
        assert "username" in keycloak_config.user_mapping

    def test_custom_user_mapping(self):
        """Test custom user mapping."""
        custom_mapping = {
            "id": "user_id",
            "email": "user_email",
        }

        config = KeycloakConfig(
            server_url="https://keycloak.example.com",
            realm="test-realm",
            client_id="test-client",
            client_secret="test-secret",
            user_mapping=custom_mapping,
        )

        assert config.user_mapping == custom_mapping


class TestKeycloakRealmConfig:
    """Test Keycloak realm configuration."""

    def test_default_realm_config(self):
        """Test default realm configuration."""
        config = KeycloakRealmConfig(realm="test-realm")

        assert config.realm == "test-realm"
        assert config.enabled is True
        assert config.registration_allowed is False
        assert config.access_token_lifespan == 300
        assert config.refresh_token_lifespan == 1800
        assert config.ssl_required == "external"

    def test_custom_realm_config(self, realm_config):
        """Test custom realm configuration."""
        assert realm_config.realm == "test-realm"
        assert realm_config.display_name == "Test Realm"
        assert realm_config.enabled is True
        assert realm_config.registration_allowed is True
        assert realm_config.access_token_lifespan == 300
        assert realm_config.refresh_token_lifespan == 1800

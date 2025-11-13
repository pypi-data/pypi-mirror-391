"""
Tests for SSO implementation.

Tests SSO providers, manager, and authentication flows.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from zephyr.security.sso import (
    SSOManager,
    SSOConfig,
    SSOUser,
    SSOAuthState,
    SSOAuthResult,
    GoogleSSOProvider,
    GitHubSSOProvider,
    MicrosoftSSOProvider,
    AppleSSOProvider,
    SAMLSSOProvider,
    GenericOAuth2SSOProvider,
)
from zephyr.security.sso.config import (
    GoogleSSOConfig,
    GitHubSSOConfig,
    MicrosoftSSOConfig,
    AppleSSOConfig,
    SAMLSSOConfig,
    GenericOAuth2SSOConfig,
)
from zephyr.security.sso.exceptions import (
    SSOProviderNotFoundError,
    SSOUnsupportedProviderError,
    SSOConfigError,
)


class TestSSOConfig:
    """Test SSO configuration."""

    def test_default_config(self):
        """Test default SSO configuration."""
        config = SSOConfig()

        assert config.enabled is True
        assert config.auto_register is True
        assert config.auto_activate is True
        assert config.require_email_verification is False
        assert config.state_lifetime == 600
        assert config.token_lifetime == 3600
        assert config.max_login_attempts == 5
        assert config.lockout_duration == 300
        assert config.session_lifetime == 86400
        assert config.session_secure is True
        assert config.session_httponly is True
        assert config.session_samesite == "lax"
        assert config.success_redirect_url == "/"
        assert config.error_redirect_url == "/login?error=sso_error"
        assert config.logout_redirect_url == "/"
        assert config.enable_logging is True
        assert config.log_level == "INFO"
        assert config.enable_metrics is True
        assert config.rate_limit_requests == 100
        assert config.rate_limit_window == 60

    def test_custom_config(self):
        """Test custom SSO configuration."""
        config = SSOConfig(
            enabled=False,
            auto_register=False,
            auto_activate=False,
            require_email_verification=True,
            state_lifetime=300,
            token_lifetime=1800,
            max_login_attempts=3,
            lockout_duration=600,
            session_lifetime=43200,
            session_secure=False,
            session_httponly=False,
            session_samesite="strict",
            success_redirect_url="/dashboard",
            error_redirect_url="/login?error=sso_failed",
            logout_redirect_url="/logout",
            enabled_providers=["google", "github"],
            log_level="DEBUG",
        )

        assert config.enabled is False
        assert config.auto_register is False
        assert config.auto_activate is False
        assert config.require_email_verification is True
        assert config.state_lifetime == 300
        assert config.token_lifetime == 1800
        assert config.max_login_attempts == 3
        assert config.lockout_duration == 600
        assert config.session_lifetime == 43200
        assert config.session_secure is False
        assert config.session_httponly is False
        assert config.session_samesite == "strict"
        assert config.success_redirect_url == "/dashboard"
        assert config.error_redirect_url == "/login?error=sso_failed"
        assert config.logout_redirect_url == "/logout"
        assert config.enabled_providers == ["google", "github"]
        assert config.log_level == "DEBUG"

    def test_config_validation(self):
        """Test configuration validation."""
        # Test invalid SameSite attribute
        with pytest.raises(ValueError, match="SameSite must be one of"):
            SSOConfig(session_samesite="invalid")

        # Test invalid log level
        with pytest.raises(ValueError, match="Log level must be one of"):
            SSOConfig(log_level="invalid")

        # Test invalid provider
        with pytest.raises(ValueError, match="Invalid provider"):
            SSOConfig(enabled_providers=["invalid_provider"])

    def test_config_methods(self):
        """Test configuration utility methods."""
        config = SSOConfig(
            enabled_providers=["google", "github"],
            providers={
                "google": {"client_id": "test", "client_secret": "secret"},
                "github": {"client_id": "test", "client_secret": "secret"},
            },
        )

        # Test provider enabled check
        assert config.is_provider_enabled("google") is True
        assert config.is_provider_enabled("microsoft") is False

        # Test provider config
        google_config = config.get_provider_config("google")
        assert google_config is not None
        assert google_config["client_id"] == "test"

        # Test non-existent provider config
        microsoft_config = config.get_provider_config("microsoft")
        assert microsoft_config is None

        # Test enable/disable provider
        config.enable_provider("microsoft")
        assert config.is_provider_enabled("microsoft") is True

        config.disable_provider("google")
        assert config.is_provider_enabled("google") is False

        # Test redirect URLs
        assert config.get_redirect_url("success") == "/"
        assert config.get_redirect_url("error") == "/login?error=sso_error"
        assert config.get_redirect_url("logout") == "/logout"

        # Test session config
        session_config = config.get_session_config()
        assert session_config["lifetime"] == 86400
        assert session_config["secure"] is True
        assert session_config["httponly"] is True
        assert session_config["samesite"] == "lax"

        # Test rate limit config
        rate_limit_config = config.get_rate_limit_config()
        assert rate_limit_config["requests"] == 100
        assert rate_limit_config["window"] == 60

        # Test CORS config
        cors_config = config.get_cors_config()
        assert cors_config["origins"] == []
        assert cors_config["methods"] == ["GET", "POST", "OPTIONS"]
        assert cors_config["headers"] == ["Content-Type", "Authorization", "X-Requested-With"]


class TestSSOUser:
    """Test SSO user model."""

    def test_user_creation(self):
        """Test SSO user creation."""
        user = SSOUser(
            id="user123",
            provider="google",
            provider_user_id="google123",
            email="user@example.com",
            username="user",
            first_name="John",
            last_name="Doe",
            display_name="John Doe",
            avatar_url="https://example.com/avatar.jpg",
            locale="en-US",
            timezone="America/New_York",
            is_verified=True,
            is_active=True,
        )

        assert user.id == "user123"
        assert user.provider == "google"
        assert user.provider_user_id == "google123"
        assert user.email == "user@example.com"
        assert user.username == "user"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.display_name == "John Doe"
        assert user.avatar_url == "https://example.com/avatar.jpg"
        assert user.locale == "en-US"
        assert user.timezone == "America/New_York"
        assert user.is_verified is True
        assert user.is_active is True

    def test_user_validation(self):
        """Test SSO user validation."""
        # Test invalid email
        with pytest.raises(ValueError, match="Invalid email format"):
            SSOUser(id="user123", provider="google", provider_user_id="google123", email="invalid-email")

        # Test invalid provider
        with pytest.raises(ValueError, match="Invalid provider"):
            SSOUser(id="user123", provider="invalid_provider", provider_user_id="google123", email="user@example.com")

    def test_user_methods(self):
        """Test SSO user utility methods."""
        user = SSOUser(
            id="user123",
            provider="google",
            provider_user_id="google123",
            email="user@example.com",
            first_name="John",
            last_name="Doe",
            display_name="John Doe",
            avatar_url="https://example.com/avatar.jpg",
        )

        # Test get_full_name
        assert user.get_full_name() == "John Doe"

        # Test get_avatar_url
        avatar_url = user.get_avatar_url(128)
        assert "sz=128" in avatar_url

        # Test to_dict
        user_dict = user.to_dict()
        assert user_dict["id"] == "user123"
        assert user_dict["provider"] == "google"
        assert user_dict["email"] == "user@example.com"
        assert user_dict["first_name"] == "John"
        assert user_dict["last_name"] == "Doe"


class TestSSOAuthState:
    """Test SSO authentication state model."""

    def test_auth_state_creation(self):
        """Test authentication state creation."""
        from datetime import datetime, timedelta

        state = SSOAuthState(
            state="test-state",
            provider="google",
            redirect_url="/dashboard",
            user_id="user123",
            expires_at=datetime.utcnow() + timedelta(minutes=10),
        )

        assert state.state == "test-state"
        assert state.provider == "google"
        assert state.redirect_url == "/dashboard"
        assert state.user_id == "user123"
        assert state.is_used is False
        assert state.is_valid() is True

    def test_auth_state_expiration(self):
        """Test authentication state expiration."""
        from datetime import datetime, timedelta

        # Test expired state
        expired_state = SSOAuthState(
            state="expired-state", provider="google", expires_at=datetime.utcnow() - timedelta(minutes=1)
        )

        assert expired_state.is_expired() is True
        assert expired_state.is_valid() is False

        # Test used state
        used_state = SSOAuthState(
            state="used-state", provider="google", expires_at=datetime.utcnow() + timedelta(minutes=10)
        )
        used_state.mark_as_used()

        assert used_state.is_used is True
        assert used_state.is_valid() is False


class TestSSOAuthResult:
    """Test SSO authentication result model."""

    def test_success_result(self):
        """Test successful authentication result."""
        user = SSOUser(id="user123", provider="google", provider_user_id="google123", email="user@example.com")

        result = SSOAuthResult.success_result(
            user=user, provider="google", state="test-state", redirect_url="/dashboard"
        )

        assert result.success is True
        assert result.user == user
        assert result.provider == "google"
        assert result.state == "test-state"
        assert result.redirect_url == "/dashboard"
        assert result.error is None
        assert result.error_code is None

    def test_error_result(self):
        """Test failed authentication result."""
        result = SSOAuthResult.error_result(
            provider="google", error="Authentication failed", error_code="auth_error", state="test-state"
        )

        assert result.success is False
        assert result.user is None
        assert result.provider == "google"
        assert result.state == "test-state"
        assert result.error == "Authentication failed"
        assert result.error_code == "auth_error"

    def test_result_to_dict(self):
        """Test result to dictionary conversion."""
        user = SSOUser(id="user123", provider="google", provider_user_id="google123", email="user@example.com")

        result = SSOAuthResult.success_result(user=user, provider="google", state="test-state")

        result_dict = result.to_dict()
        assert result_dict["success"] is True
        assert result_dict["provider"] == "google"
        assert result_dict["state"] == "test-state"
        assert "user" in result_dict
        assert result_dict["user"]["id"] == "user123"


class TestSSOProviders:
    """Test SSO provider implementations."""

    def test_google_sso_provider(self):
        """Test Google SSO provider."""
        config = GoogleSSOConfig(
            client_id="test-client-id",
            client_secret="test-client-secret",
            redirect_uri="http://localhost:3000/callback",
        )

        provider = GoogleSSOProvider(config)

        assert provider.get_provider_name() == "google"

        # Test authorization URL
        auth_url = provider.get_authorization_url("test-state")
        assert "https://accounts.google.com/o/oauth2/v2/auth" in auth_url
        assert "client_id=test-client-id" in auth_url
        assert "state=test-state" in auth_url

    def test_github_sso_provider(self):
        """Test GitHub SSO provider."""
        config = GitHubSSOConfig(
            client_id="test-client-id",
            client_secret="test-client-secret",
            redirect_uri="http://localhost:3000/callback",
        )

        provider = GitHubSSOProvider(config)

        assert provider.get_provider_name() == "github"

        # Test authorization URL
        auth_url = provider.get_authorization_url("test-state")
        assert "https://github.com/login/oauth/authorize" in auth_url
        assert "client_id=test-client-id" in auth_url
        assert "state=test-state" in auth_url

    def test_microsoft_sso_provider(self):
        """Test Microsoft SSO provider."""
        config = MicrosoftSSOConfig(
            client_id="test-client-id",
            client_secret="test-client-secret",
            redirect_uri="http://localhost:3000/callback",
        )

        provider = MicrosoftSSOProvider(config)

        assert provider.get_provider_name() == "microsoft"

        # Test authorization URL
        auth_url = provider.get_authorization_url("test-state")
        assert "https://login.microsoftonline.com/common/oauth2/v2.0/authorize" in auth_url
        assert "client_id=test-client-id" in auth_url
        assert "state=test-state" in auth_url

    def test_apple_sso_provider(self):
        """Test Apple SSO provider."""
        config = AppleSSOConfig(
            client_id="test-client-id",
            client_secret="test-client-secret",
            redirect_uri="http://localhost:3000/callback",
            team_id="test-team-id",
            key_id="test-key-id",
            private_key="test-private-key",
        )

        provider = AppleSSOProvider(config)

        assert provider.get_provider_name() == "apple"

        # Test authorization URL
        auth_url = provider.get_authorization_url("test-state")
        assert "https://appleid.apple.com/auth/authorize" in auth_url
        assert "client_id=test-client-id" in auth_url
        assert "state=test-state" in auth_url

    def test_saml_sso_provider(self):
        """Test SAML SSO provider."""
        config = SAMLSSOConfig(
            entity_id="test-entity-id", sso_url="https://saml.example.com/sso", x509_cert="test-cert"
        )

        provider = SAMLSSOProvider(config)

        assert provider.get_provider_name() == "saml"

        # Test authorization URL
        auth_url = provider.get_authorization_url("test-state")
        assert auth_url == "https://saml.example.com/sso"

    def test_generic_oauth2_sso_provider(self):
        """Test generic OAuth2 SSO provider."""
        config = GenericOAuth2SSOConfig(
            client_id="test-client-id",
            client_secret="test-client-secret",
            redirect_uri="http://localhost:3000/callback",
            authorization_url="https://oauth.example.com/authorize",
            token_url="https://oauth.example.com/token",
            user_info_url="https://oauth.example.com/userinfo",
        )

        provider = GenericOAuth2SSOProvider(config)

        assert provider.get_provider_name() == "generic_oauth2"

        # Test authorization URL
        auth_url = provider.get_authorization_url("test-state")
        assert "https://oauth.example.com/authorize" in auth_url
        assert "client_id=test-client-id" in auth_url
        assert "state=test-state" in auth_url


class TestSSOManager:
    """Test SSO manager functionality."""

    @pytest.fixture
    def config(self):
        """Create SSO configuration for tests."""
        return SSOConfig(
            enabled_providers=["google", "github"],
            providers={
                "google": {
                    "client_id": "google-client-id",
                    "client_secret": "google-client-secret",
                    "redirect_uri": "http://localhost:3000/callback",
                },
                "github": {
                    "client_id": "github-client-id",
                    "client_secret": "github-client-secret",
                    "redirect_uri": "http://localhost:3000/callback",
                },
            },
        )

    @pytest.fixture
    def manager(self, config):
        """Create SSO manager for tests."""
        return SSOManager(config)

    def test_manager_initialization(self, manager, config):
        """Test SSO manager initialization."""
        assert manager.config == config
        assert manager.logger is not None
        assert len(manager.providers) == 2
        assert "google" in manager.providers
        assert "github" in manager.providers

    def test_get_provider(self, manager):
        """Test getting SSO provider."""
        google_provider = manager.get_provider("google")
        assert google_provider is not None
        assert google_provider.get_provider_name() == "google"

        github_provider = manager.get_provider("github")
        assert github_provider is not None
        assert github_provider.get_provider_name() == "github"

    def test_get_provider_not_found(self, manager):
        """Test getting non-existent provider."""
        with pytest.raises(SSOProviderNotFoundError):
            manager.get_provider("microsoft")

    def test_get_available_providers(self, manager):
        """Test getting available providers."""
        providers = manager.get_available_providers()
        assert "google" in providers
        assert "github" in providers
        assert len(providers) == 2

    def test_is_provider_available(self, manager):
        """Test checking if provider is available."""
        assert manager.is_provider_available("google") is True
        assert manager.is_provider_available("github") is True
        assert manager.is_provider_available("microsoft") is False

    def test_create_auth_state(self, manager):
        """Test creating authentication state."""
        state = manager.create_auth_state(provider="google", redirect_url="/dashboard", user_id="user123")

        assert state.provider == "google"
        assert state.redirect_url == "/dashboard"
        assert state.user_id == "user123"
        assert state.is_valid() is True
        assert state.state in manager.auth_states

    def test_create_auth_state_invalid_provider(self, manager):
        """Test creating auth state with invalid provider."""
        with pytest.raises(SSOProviderNotFoundError):
            manager.create_auth_state(provider="microsoft")

    def test_get_auth_state(self, manager):
        """Test getting authentication state."""
        state = manager.create_auth_state(provider="google")

        retrieved_state = manager.get_auth_state(state.state)
        assert retrieved_state == state

        # Test non-existent state
        non_existent = manager.get_auth_state("non-existent")
        assert non_existent is None

    def test_mark_auth_state_used(self, manager):
        """Test marking auth state as used."""
        state = manager.create_auth_state(provider="google")

        manager.mark_auth_state_used(state.state)

        retrieved_state = manager.get_auth_state(state.state)
        assert retrieved_state.is_used is True

    def test_get_authorization_url(self, manager):
        """Test getting authorization URL."""
        auth_url = manager.get_authorization_url(provider="google", redirect_url="/dashboard")

        assert "https://accounts.google.com/o/oauth2/v2/auth" in auth_url
        assert "client_id=google-client-id" in auth_url
        assert "state=" in auth_url

    def test_get_authorization_url_invalid_provider(self, manager):
        """Test getting authorization URL with invalid provider."""
        with pytest.raises(SSOProviderNotFoundError):
            manager.get_authorization_url(provider="microsoft")

    @pytest.mark.asyncio
    async def test_authenticate_success(self, manager):
        """Test successful authentication."""
        # Mock provider authenticate method
        mock_user = SSOUser(id="user123", provider="google", provider_user_id="google123", email="user@example.com")

        mock_result = SSOAuthResult.success_result(user=mock_user, provider="google", state="test-state")

        with patch.object(manager.providers["google"], "authenticate", return_value=mock_result):
            result = await manager.authenticate(provider="google", code="test-code", state="test-state")

            assert result.success is True
            assert result.user == mock_user
            assert result.provider == "google"

    @pytest.mark.asyncio
    async def test_authenticate_invalid_state(self, manager):
        """Test authentication with invalid state."""
        result = await manager.authenticate(provider="google", code="test-code", state="invalid-state")

        assert result.success is False
        assert "Invalid or expired state parameter" in result.error

    @pytest.mark.asyncio
    async def test_authenticate_provider_mismatch(self, manager):
        """Test authentication with provider mismatch."""
        state = manager.create_auth_state(provider="google")

        result = await manager.authenticate(provider="github", code="test-code", state=state.state)

        assert result.success is False
        assert "Provider mismatch" in result.error

    def test_get_provider_info(self, manager):
        """Test getting provider information."""
        info = manager.get_provider_info("google")

        assert info["name"] == "google"
        assert info["display_name"] == "Google"
        assert info["is_enabled"] is True
        assert info["is_configured"] is True

    def test_get_provider_info_not_found(self, manager):
        """Test getting provider info for non-existent provider."""
        with pytest.raises(SSOProviderNotFoundError):
            manager.get_provider_info("microsoft")

    def test_get_all_providers_info(self, manager):
        """Test getting all providers information."""
        providers_info = manager.get_all_providers_info()

        assert len(providers_info) == 2
        provider_names = [info["name"] for info in providers_info]
        assert "google" in provider_names
        assert "github" in provider_names

    def test_cleanup_expired_states(self, manager):
        """Test cleaning up expired states."""
        # Create expired state
        from datetime import datetime, timedelta

        expired_state = SSOAuthState(
            state="expired-state", provider="google", expires_at=datetime.utcnow() - timedelta(minutes=1)
        )
        manager.auth_states["expired-state"] = expired_state

        # Create valid state
        valid_state = manager.create_auth_state(provider="google")

        # Cleanup expired states
        cleaned_count = manager.cleanup_expired_states()

        assert cleaned_count == 1
        assert "expired-state" not in manager.auth_states
        assert valid_state.state in manager.auth_states

    def test_get_stats(self, manager):
        """Test getting manager statistics."""
        stats = manager.get_stats()

        assert stats["total_providers"] == 2
        assert stats["enabled_providers"] == ["google", "github"]
        assert stats["active_states"] >= 0
        assert "config" in stats

    @pytest.mark.asyncio
    async def test_close(self, manager):
        """Test closing manager."""
        await manager.close()

        # Providers should be closed
        assert len(manager.providers) == 0
        assert len(manager.auth_states) == 0

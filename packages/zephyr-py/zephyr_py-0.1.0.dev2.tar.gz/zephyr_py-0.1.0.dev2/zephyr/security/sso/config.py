"""
SSO configuration management.

Defines configuration options for SSO providers and authentication flows.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, validator


class SSOConfig(BaseModel):
    """SSO configuration model."""

    # General settings
    enabled: bool = Field(default=True, description="Whether SSO is enabled")
    default_provider: Optional[str] = Field(default=None, description="Default SSO provider")
    auto_register: bool = Field(default=True, description="Auto-register new users")
    auto_activate: bool = Field(default=True, description="Auto-activate new users")
    require_email_verification: bool = Field(default=False, description="Require email verification")

    # Security settings
    state_lifetime: int = Field(default=600, description="Authentication state lifetime in seconds")
    token_lifetime: int = Field(default=3600, description="SSO token lifetime in seconds")
    max_login_attempts: int = Field(default=5, description="Maximum login attempts per minute")
    lockout_duration: int = Field(default=300, description="Account lockout duration in seconds")

    # Session settings
    session_lifetime: int = Field(default=86400, description="Session lifetime in seconds")
    session_secure: bool = Field(default=True, description="Use secure session cookies")
    session_httponly: bool = Field(default=True, description="Use HTTP-only session cookies")
    session_samesite: str = Field(default="lax", description="SameSite attribute for session cookies")

    # Provider settings
    providers: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Provider configurations")
    enabled_providers: List[str] = Field(default_factory=list, description="Enabled provider names")

    # User mapping settings
    default_user_mapping: Dict[str, str] = Field(
        default_factory=lambda: {
            "id": "sub",
            "email": "email",
            "username": "preferred_username",
            "first_name": "given_name",
            "last_name": "family_name",
            "display_name": "name",
            "avatar_url": "picture",
            "locale": "locale",
            "timezone": "zoneinfo",
            "is_verified": "email_verified",
        },
        description="Default user attribute mapping",
    )

    # Callback settings
    success_redirect_url: str = Field(default="/", description="Default success redirect URL")
    error_redirect_url: str = Field(default="/login?error=sso_error", description="Default error redirect URL")
    logout_redirect_url: str = Field(default="/", description="Default logout redirect URL")

    # Logging and monitoring
    enable_logging: bool = Field(default=True, description="Enable SSO logging")
    log_level: str = Field(default="INFO", description="Log level for SSO operations")
    enable_metrics: bool = Field(default=True, description="Enable SSO metrics collection")

    # Rate limiting
    rate_limit_requests: int = Field(default=100, description="Rate limit requests per minute")
    rate_limit_window: int = Field(default=60, description="Rate limit window in seconds")

    # CORS settings
    allowed_origins: List[str] = Field(default_factory=list, description="Allowed CORS origins")
    allowed_methods: List[str] = Field(default=["GET", "POST", "OPTIONS"], description="Allowed CORS methods")
    allowed_headers: List[str] = Field(
        default=["Content-Type", "Authorization", "X-Requested-With"], description="Allowed CORS headers"
    )

    # Custom settings
    custom_settings: Dict[str, Any] = Field(default_factory=dict, description="Custom settings")

    @validator("session_samesite")
    def validate_session_samesite(cls, v: str) -> str:
        """Validate SameSite attribute."""
        valid_values = {"strict", "lax", "none"}
        if v.lower() not in valid_values:
            raise ValueError(f"SameSite must be one of: {valid_values}")
        return v.lower()

    @validator("log_level")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()

    @validator("enabled_providers")
    def validate_enabled_providers(cls, v: List[str]) -> List[str]:
        """Validate enabled providers."""
        valid_providers = {"google", "github", "microsoft", "apple", "saml", "generic_oauth2", "keycloak"}
        for provider in v:
            if provider.lower() not in valid_providers:
                raise ValueError(f"Invalid provider: {provider}")
        return [p.lower() for p in v]

    def is_provider_enabled(self, provider: str) -> bool:
        """Check if provider is enabled."""
        return provider.lower() in self.enabled_providers

    def get_provider_config(self, provider: str) -> Optional[Dict[str, Any]]:
        """Get provider configuration."""
        return self.providers.get(provider.lower())

    def set_provider_config(self, provider: str, config: Dict[str, Any]) -> None:
        """Set provider configuration."""
        self.providers[provider.lower()] = config

    def enable_provider(self, provider: str) -> None:
        """Enable provider."""
        provider = provider.lower()
        if provider not in self.enabled_providers:
            self.enabled_providers.append(provider)

    def disable_provider(self, provider: str) -> None:
        """Disable provider."""
        provider = provider.lower()
        if provider in self.enabled_providers:
            self.enabled_providers.remove(provider)

    def get_user_mapping(self, provider: str) -> Dict[str, str]:
        """Get user mapping for provider."""
        provider_config = self.get_provider_config(provider)
        if provider_config and "user_mapping" in provider_config:
            return provider_config["user_mapping"]
        return self.default_user_mapping

    def get_redirect_url(self, url_type: str) -> str:
        """Get redirect URL by type."""
        if url_type == "success":
            return self.success_redirect_url
        elif url_type == "error":
            return self.error_redirect_url
        elif url_type == "logout":
            return self.logout_redirect_url
        else:
            return self.success_redirect_url

    def is_secure_session(self) -> bool:
        """Check if session should be secure."""
        return self.session_secure

    def get_session_config(self) -> Dict[str, Any]:
        """Get session configuration."""
        return {
            "lifetime": self.session_lifetime,
            "secure": self.session_secure,
            "httponly": self.session_httponly,
            "samesite": self.session_samesite,
        }

    def get_rate_limit_config(self) -> Dict[str, int]:
        """Get rate limiting configuration."""
        return {"requests": self.rate_limit_requests, "window": self.rate_limit_window}

    def get_cors_config(self) -> Dict[str, List[str]]:
        """Get CORS configuration."""
        return {"origins": self.allowed_origins, "methods": self.allowed_methods, "headers": self.allowed_headers}

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            # Add custom encoders if needed
        }


class GoogleSSOConfig(BaseModel):
    """Google SSO configuration."""

    client_id: str = Field(..., description="Google OAuth client ID")
    client_secret: str = Field(..., description="Google OAuth client secret")
    redirect_uri: str = Field(..., description="OAuth redirect URI")
    scopes: List[str] = Field(default=["openid", "profile", "email"], description="OAuth scopes")
    hosted_domain: Optional[str] = Field(default=None, description="Hosted domain restriction")
    access_type: str = Field(default="offline", description="OAuth access type")
    prompt: str = Field(default="consent", description="OAuth prompt parameter")
    include_granted_scopes: bool = Field(default=True, description="Include granted scopes")
    user_mapping: Dict[str, str] = Field(
        default_factory=lambda: {
            "id": "sub",
            "email": "email",
            "username": "preferred_username",
            "first_name": "given_name",
            "last_name": "family_name",
            "display_name": "name",
            "avatar_url": "picture",
            "locale": "locale",
            "timezone": "zoneinfo",
            "is_verified": "email_verified",
        },
        description="User attribute mapping",
    )


class GitHubSSOConfig(BaseModel):
    """GitHub SSO configuration."""

    client_id: str = Field(..., description="GitHub OAuth client ID")
    client_secret: str = Field(..., description="GitHub OAuth client secret")
    redirect_uri: str = Field(..., description="OAuth redirect URI")
    scopes: List[str] = Field(default=["user:email"], description="OAuth scopes")
    allow_signup: bool = Field(default=True, description="Allow new user signup")
    user_mapping: Dict[str, str] = Field(
        default_factory=lambda: {
            "id": "id",
            "email": "email",
            "username": "login",
            "first_name": "name",
            "last_name": "name",
            "display_name": "name",
            "avatar_url": "avatar_url",
            "locale": "locale",
            "timezone": "timezone",
            "is_verified": "email_verified",
        },
        description="User attribute mapping",
    )


class MicrosoftSSOConfig(BaseModel):
    """Microsoft SSO configuration."""

    client_id: str = Field(..., description="Microsoft OAuth client ID")
    client_secret: str = Field(..., description="Microsoft OAuth client secret")
    redirect_uri: str = Field(..., description="OAuth redirect URI")
    tenant: str = Field(default="common", description="Azure AD tenant")
    scopes: List[str] = Field(default=["openid", "profile", "email"], description="OAuth scopes")
    response_mode: str = Field(default="query", description="OAuth response mode")
    response_type: str = Field(default="code", description="OAuth response type")
    user_mapping: Dict[str, str] = Field(
        default_factory=lambda: {
            "id": "sub",
            "email": "email",
            "username": "preferred_username",
            "first_name": "given_name",
            "last_name": "family_name",
            "display_name": "name",
            "avatar_url": "picture",
            "locale": "locale",
            "timezone": "zoneinfo",
            "is_verified": "email_verified",
        },
        description="User attribute mapping",
    )


class AppleSSOConfig(BaseModel):
    """Apple SSO configuration."""

    client_id: str = Field(..., description="Apple OAuth client ID")
    client_secret: str = Field(..., description="Apple OAuth client secret")
    redirect_uri: str = Field(..., description="OAuth redirect URI")
    team_id: str = Field(..., description="Apple Developer Team ID")
    key_id: str = Field(..., description="Apple Developer Key ID")
    private_key: str = Field(..., description="Apple Developer Private Key")
    scopes: List[str] = Field(default=["name", "email"], description="OAuth scopes")
    response_mode: str = Field(default="form_post", description="OAuth response mode")
    user_mapping: Dict[str, str] = Field(
        default_factory=lambda: {
            "id": "sub",
            "email": "email",
            "username": "email",
            "first_name": "given_name",
            "last_name": "family_name",
            "display_name": "name",
            "is_verified": "email_verified",
        },
        description="User attribute mapping",
    )


class SAMLSSOConfig(BaseModel):
    """SAML SSO configuration."""

    entity_id: str = Field(..., description="SAML entity ID")
    sso_url: str = Field(..., description="SAML SSO URL")
    slo_url: Optional[str] = Field(default=None, description="SAML SLO URL")
    x509_cert: str = Field(..., description="SAML X.509 certificate")
    private_key: Optional[str] = Field(default=None, description="SAML private key")
    name_id_format: str = Field(
        default="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress", description="Name ID format"
    )
    attribute_mapping: Dict[str, str] = Field(
        default_factory=lambda: {
            "id": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier",
            "email": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress",
            "username": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name",
            "first_name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname",
            "last_name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname",
            "display_name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name",
            "is_verified": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress",
        },
        description="SAML attribute mapping",
    )
    sign_requests: bool = Field(default=True, description="Sign SAML requests")
    encrypt_assertions: bool = Field(default=False, description="Encrypt SAML assertions")
    want_assertions_signed: bool = Field(default=True, description="Require signed assertions")
    want_response_signed: bool = Field(default=True, description="Require signed responses")


class GenericOAuth2SSOConfig(BaseModel):
    """Generic OAuth2 SSO configuration."""

    client_id: str = Field(..., description="OAuth2 client ID")
    client_secret: str = Field(..., description="OAuth2 client secret")
    redirect_uri: str = Field(..., description="OAuth2 redirect URI")
    authorization_url: str = Field(..., description="OAuth2 authorization URL")
    token_url: str = Field(..., description="OAuth2 token URL")
    user_info_url: str = Field(..., description="User info API URL")
    jwks_url: Optional[str] = Field(default=None, description="JWKS URL for token verification")
    issuer: Optional[str] = Field(default=None, description="OAuth2 issuer")
    audience: Optional[str] = Field(default=None, description="OAuth2 audience")
    scopes: List[str] = Field(default=["openid", "profile", "email"], description="OAuth2 scopes")
    response_type: str = Field(default="code", description="OAuth2 response type")
    response_mode: str = Field(default="query", description="OAuth2 response mode")
    user_mapping: Dict[str, str] = Field(
        default_factory=lambda: {
            "id": "sub",
            "email": "email",
            "username": "preferred_username",
            "first_name": "given_name",
            "last_name": "family_name",
            "display_name": "name",
            "avatar_url": "picture",
            "locale": "locale",
            "timezone": "zoneinfo",
            "is_verified": "email_verified",
        },
        description="User attribute mapping",
    )

"""
Keycloak configuration management.

Defines configuration options for Keycloak integration including OAuth2/OIDC and Admin API settings.
"""

from typing import Any
from pydantic import BaseModel, Field, validator


class KeycloakConfig(BaseModel):
    """Keycloak configuration model."""

    # Server settings
    server_url: str = Field(..., description="Keycloak server URL (e.g., https://keycloak.example.com)")
    realm: str = Field(..., description="Keycloak realm name")

    # Client type (must be before client_secret for validator order)
    public_client: bool = Field(default=False, description="Whether this is a public client")

    # Client settings
    client_id: str = Field(..., description="OAuth2 client ID")
    client_secret: str | None = Field(default=None, description="OAuth2 client secret (for confidential clients)")

    # OAuth2/OIDC endpoints (auto-constructed if not provided)
    authorization_endpoint: str | None = Field(default=None, description="Authorization endpoint URL")
    token_endpoint: str | None = Field(default=None, description="Token endpoint URL")
    userinfo_endpoint: str | None = Field(default=None, description="UserInfo endpoint URL")
    jwks_uri: str | None = Field(default=None, description="JWKS URI for token validation")
    end_session_endpoint: str | None = Field(default=None, description="Logout endpoint URL")
    introspection_endpoint: str | None = Field(default=None, description="Token introspection endpoint URL")

    # Token settings
    verify_token_signature: bool = Field(default=True, description="Verify token signatures using JWKS")
    verify_token_audience: bool = Field(default=True, description="Verify token audience claim")
    verify_token_expiry: bool = Field(default=True, description="Verify token expiry")
    token_leeway: int = Field(default=0, description="Leeway in seconds for token expiry validation")

    # Scopes
    default_scopes: list[str] = Field(default=["openid", "profile", "email"], description="Default OAuth2 scopes")

    # Admin API settings
    admin_username: str | None = Field(default=None, description="Admin username for Admin API")
    admin_password: str | None = Field(default=None, description="Admin password for Admin API")
    admin_client_id: str = Field(default="admin-cli", description="Admin client ID")
    admin_realm: str = Field(default="master", description="Admin realm (usually 'master')")

    # Connection settings
    timeout: int = Field(default=30, description="HTTP request timeout in seconds")
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")

    # User mapping
    user_mapping: dict[str, str] = Field(
        default_factory=lambda: {
            "id": "sub",
            "email": "email",
            "username": "preferred_username",
            "first_name": "given_name",
            "last_name": "family_name",
            "display_name": "name",
            "is_verified": "email_verified",
        },
        description="User attribute mapping from Keycloak to application",
    )

    # Auto-registration
    auto_register: bool = Field(default=True, description="Auto-register new users from Keycloak")
    auto_activate: bool = Field(default=True, description="Auto-activate new users")

    # Custom settings
    custom_settings: dict[str, Any] = Field(default_factory=dict, description="Custom settings")

    @validator("server_url")
    def validate_server_url(cls, v: str) -> str:
        """Validate and normalize server URL."""
        v = v.rstrip("/")
        if not v.startswith(("http://", "https://")):
            raise ValueError("Server URL must start with http:// or https://")
        return v

    @validator("client_secret", always=True)
    def validate_client_secret(cls, v: str | None, values: dict[str, Any]) -> str | None:
        """Validate client secret based on client type."""
        public_client = values.get("public_client", False)
        if not public_client and not v:
            raise ValueError("Client secret is required for confidential clients")
        return v

    def get_realm_url(self) -> str:
        """Get realm base URL."""
        return f"{self.server_url}/realms/{self.realm}"

    def get_authorization_endpoint(self) -> str:
        """Get authorization endpoint URL."""
        if self.authorization_endpoint:
            return self.authorization_endpoint
        return f"{self.get_realm_url()}/protocol/openid-connect/auth"

    def get_token_endpoint(self) -> str:
        """Get token endpoint URL."""
        if self.token_endpoint:
            return self.token_endpoint
        return f"{self.get_realm_url()}/protocol/openid-connect/token"

    def get_userinfo_endpoint(self) -> str:
        """Get userinfo endpoint URL."""
        if self.userinfo_endpoint:
            return self.userinfo_endpoint
        return f"{self.get_realm_url()}/protocol/openid-connect/userinfo"

    def get_jwks_uri(self) -> str:
        """Get JWKS URI."""
        if self.jwks_uri:
            return self.jwks_uri
        return f"{self.get_realm_url()}/protocol/openid-connect/certs"

    def get_end_session_endpoint(self) -> str:
        """Get logout endpoint URL."""
        if self.end_session_endpoint:
            return self.end_session_endpoint
        return f"{self.get_realm_url()}/protocol/openid-connect/logout"

    def get_introspection_endpoint(self) -> str:
        """Get token introspection endpoint URL."""
        if self.introspection_endpoint:
            return self.introspection_endpoint
        return f"{self.get_realm_url()}/protocol/openid-connect/token/introspect"

    def get_admin_url(self) -> str:
        """Get admin API base URL."""
        return f"{self.server_url}/admin/realms/{self.realm}"

    def get_admin_token_endpoint(self) -> str:
        """Get admin token endpoint URL."""
        return f"{self.server_url}/realms/{self.admin_realm}/protocol/openid-connect/token"

    def get_well_known_url(self) -> str:
        """Get OpenID Connect discovery URL."""
        return f"{self.get_realm_url()}/.well-known/openid-configuration"

    class Config:
        """Pydantic configuration."""

        json_encoders = {}


class KeycloakRealmConfig(BaseModel):
    """Keycloak realm configuration."""

    realm: str = Field(..., description="Realm name")
    display_name: str | None = Field(default=None, description="Display name")
    enabled: bool = Field(default=True, description="Whether realm is enabled")

    # Registration settings
    registration_allowed: bool = Field(default=False, description="Allow user registration")
    registration_email_as_username: bool = Field(default=False, description="Use email as username")

    # Login settings
    login_with_email_allowed: bool = Field(default=True, description="Allow login with email")
    duplicate_emails_allowed: bool = Field(default=False, description="Allow duplicate emails")

    # Password policy
    password_policy: str | None = Field(default=None, description="Password policy")

    # Token settings
    access_token_lifespan: int = Field(default=300, description="Access token lifespan in seconds")
    refresh_token_lifespan: int = Field(default=1800, description="Refresh token lifespan in seconds")

    # SSL settings
    ssl_required: str = Field(default="external", description="SSL requirement (none, external, all)")

    class Config:
        """Pydantic configuration."""

        json_encoders = {}

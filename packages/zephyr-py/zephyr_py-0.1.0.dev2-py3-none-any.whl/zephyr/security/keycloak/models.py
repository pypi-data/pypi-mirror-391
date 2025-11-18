"""
Keycloak data models.

Defines data models for Keycloak entities including users, tokens, roles, and groups.
"""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class KeycloakToken(BaseModel):
    """Keycloak token response model."""

    access_token: str = Field(..., description="Access token")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    refresh_token: str | None = Field(default=None, description="Refresh token")
    refresh_expires_in: int | None = Field(default=None, description="Refresh token expiration in seconds")
    id_token: str | None = Field(default=None, description="OpenID Connect ID token")
    scope: str | None = Field(default=None, description="Granted scopes")
    session_state: str | None = Field(default=None, description="Session state")

    # Computed fields
    issued_at: datetime = Field(default_factory=datetime.utcnow, description="Token issue time")

    class Config:
        """Pydantic configuration."""

        json_encoders = {datetime: lambda v: v.isoformat()}

    def is_expired(self) -> bool:
        """Check if access token is expired."""
        elapsed = (datetime.utcnow() - self.issued_at).total_seconds()
        return elapsed >= self.expires_in

    def is_refresh_expired(self) -> bool:
        """Check if refresh token is expired."""
        if not self.refresh_token or not self.refresh_expires_in:
            return True
        elapsed = (datetime.utcnow() - self.issued_at).total_seconds()
        return elapsed >= self.refresh_expires_in


class KeycloakUser(BaseModel):
    """Keycloak user model."""

    id: str | None = Field(default=None, description="User ID")
    username: str = Field(..., description="Username")
    email: str | None = Field(default=None, description="Email address")
    email_verified: bool = Field(default=False, description="Whether email is verified")
    first_name: str | None = Field(default=None, description="First name")
    last_name: str | None = Field(default=None, description="Last name")
    enabled: bool = Field(default=True, description="Whether user is enabled")

    # Timestamps
    created_timestamp: int | None = Field(default=None, description="Creation timestamp (milliseconds)")

    # Attributes
    attributes: dict[str, list[str]] = Field(default_factory=dict, description="User attributes")

    # Groups and roles
    groups: list[str] = Field(default_factory=list, description="User groups")
    realm_roles: list[str] = Field(default_factory=list, description="Realm roles")
    client_roles: dict[str, list[str]] = Field(default_factory=dict, description="Client roles")

    # Credentials
    credentials: list[dict[str, Any]] = Field(default_factory=list, description="User credentials")

    # Required actions
    required_actions: list[str] = Field(default_factory=list, description="Required actions")

    class Config:
        """Pydantic configuration."""

        json_encoders = {}

    def get_full_name(self) -> str:
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or self.username

    def has_role(self, role: str) -> bool:
        """Check if user has a specific realm role."""
        return role in self.realm_roles

    def has_client_role(self, client: str, role: str) -> bool:
        """Check if user has a specific client role."""
        return client in self.client_roles and role in self.client_roles[client]


class KeycloakRole(BaseModel):
    """Keycloak role model."""

    id: str | None = Field(default=None, description="Role ID")
    name: str = Field(..., description="Role name")
    description: str | None = Field(default=None, description="Role description")
    composite: bool = Field(default=False, description="Whether role is composite")
    client_role: bool = Field(default=False, description="Whether role is a client role")
    container_id: str | None = Field(default=None, description="Container ID (realm or client)")

    # Composite roles
    composites: dict[str, list[str]] = Field(default_factory=dict, description="Composite roles")

    # Attributes
    attributes: dict[str, list[str]] = Field(default_factory=dict, description="Role attributes")

    class Config:
        """Pydantic configuration."""

        json_encoders = {}


class KeycloakGroup(BaseModel):
    """Keycloak group model."""

    id: str | None = Field(default=None, description="Group ID")
    name: str = Field(..., description="Group name")
    path: str | None = Field(default=None, description="Group path")

    # Subgroups
    sub_groups: list["KeycloakGroup"] = Field(default_factory=list, description="Subgroups")

    # Attributes
    attributes: dict[str, list[str]] = Field(default_factory=dict, description="Group attributes")

    # Roles
    realm_roles: list[str] = Field(default_factory=list, description="Realm roles")
    client_roles: dict[str, list[str]] = Field(default_factory=dict, description="Client roles")

    class Config:
        """Pydantic configuration."""

        json_encoders = {}


class KeycloakClient(BaseModel):
    """Keycloak client model."""

    id: str | None = Field(default=None, description="Client ID (UUID)")
    client_id: str = Field(..., description="Client identifier")
    name: str | None = Field(default=None, description="Client name")
    description: str | None = Field(default=None, description="Client description")
    enabled: bool = Field(default=True, description="Whether client is enabled")

    # Client type
    public_client: bool = Field(default=False, description="Whether client is public")
    bearer_only: bool = Field(default=False, description="Whether client is bearer-only")

    # URLs
    root_url: str | None = Field(default=None, description="Root URL")
    base_url: str | None = Field(default=None, description="Base URL")
    redirect_uris: list[str] = Field(default_factory=list, description="Valid redirect URIs")
    web_origins: list[str] = Field(default_factory=list, description="Web origins")

    # Protocol
    protocol: str = Field(default="openid-connect", description="Protocol")

    # Settings
    standard_flow_enabled: bool = Field(default=True, description="Standard flow enabled")
    implicit_flow_enabled: bool = Field(default=False, description="Implicit flow enabled")
    direct_access_grants_enabled: bool = Field(default=True, description="Direct access grants enabled")
    service_accounts_enabled: bool = Field(default=False, description="Service accounts enabled")

    # Attributes
    attributes: dict[str, str] = Field(default_factory=dict, description="Client attributes")

    class Config:
        """Pydantic configuration."""

        json_encoders = {}


class KeycloakRealm(BaseModel):
    """Keycloak realm model."""

    id: str | None = Field(default=None, description="Realm ID")
    realm: str = Field(..., description="Realm name")
    display_name: str | None = Field(default=None, description="Display name")
    display_name_html: str | None = Field(default=None, description="Display name HTML")
    enabled: bool = Field(default=True, description="Whether realm is enabled")

    # SSL settings
    ssl_required: str = Field(default="external", description="SSL requirement")

    # Registration
    registration_allowed: bool = Field(default=False, description="Registration allowed")
    registration_email_as_username: bool = Field(default=False, description="Use email as username")

    # Login settings
    login_with_email_allowed: bool = Field(default=True, description="Login with email allowed")
    duplicate_emails_allowed: bool = Field(default=False, description="Duplicate emails allowed")

    # Token settings
    access_token_lifespan: int = Field(default=300, description="Access token lifespan (seconds)")
    refresh_token_lifespan: int = Field(default=1800, description="Refresh token lifespan (seconds)")

    class Config:
        """Pydantic configuration."""

        json_encoders = {}


class KeycloakUserInfo(BaseModel):
    """Keycloak UserInfo endpoint response."""

    sub: str = Field(..., description="Subject identifier")
    email: str | None = Field(default=None, description="Email address")
    email_verified: bool = Field(default=False, description="Email verified")
    preferred_username: str | None = Field(default=None, description="Preferred username")
    given_name: str | None = Field(default=None, description="Given name")
    family_name: str | None = Field(default=None, description="Family name")
    name: str | None = Field(default=None, description="Full name")

    # Additional claims
    locale: str | None = Field(default=None, description="Locale")
    zoneinfo: str | None = Field(default=None, description="Timezone")

    # Custom attributes
    attributes: dict[str, Any] = Field(default_factory=dict, description="Additional attributes")

    class Config:
        """Pydantic configuration."""

        extra = "allow"  # Allow additional fields
        json_encoders = {}


# Update forward references
KeycloakGroup.model_rebuild()

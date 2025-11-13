"""
SSO data models.

Defines all SSO-related data models including users, providers, and authentication states.
"""

import secrets
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

from pydantic import BaseModel, Field, validator


class SSOUser(BaseModel):
    """SSO user model."""

    id: str = Field(..., description="Unique user identifier")
    provider: str = Field(..., description="SSO provider name")
    provider_user_id: str = Field(..., description="User ID from SSO provider")
    email: str = Field(..., description="User email address")
    username: Optional[str] = Field(default=None, description="Username")
    first_name: Optional[str] = Field(default=None, description="First name")
    last_name: Optional[str] = Field(default=None, description="Last name")
    display_name: Optional[str] = Field(default=None, description="Display name")
    avatar_url: Optional[str] = Field(default=None, description="Avatar URL")
    locale: Optional[str] = Field(default=None, description="User locale")
    timezone: Optional[str] = Field(default=None, description="User timezone")
    is_verified: bool = Field(default=False, description="Whether email is verified")
    is_active: bool = Field(default=True, description="Whether user is active")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    last_login_at: Optional[datetime] = Field(default=None, description="Last login timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional user metadata")
    provider_data: Dict[str, Any] = Field(default_factory=dict, description="Raw provider data")

    @validator("email")
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        if "@" not in v or "." not in v.split("@")[1]:
            raise ValueError("Invalid email format")
        return v.lower()

    @validator("provider")
    def validate_provider(cls, v: str) -> str:
        """Validate provider name."""
        valid_providers = {"google", "github", "microsoft", "apple", "saml", "generic_oauth2", "keycloak"}
        if v.lower() not in valid_providers:
            raise ValueError(f"Invalid provider: {v}")
        return v.lower()

    def get_full_name(self) -> str:
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.display_name:
            return self.display_name
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.username or self.email.split("@")[0]

    def get_avatar_url(self, size: int = 64) -> Optional[str]:
        """Get avatar URL with specified size."""
        if not self.avatar_url:
            return None

        # Add size parameter for common providers
        if "google" in self.provider and "googleusercontent.com" in self.avatar_url:
            return f"{self.avatar_url}?sz={size}"
        elif "github" in self.provider and "github.com" in self.avatar_url:
            return f"{self.avatar_url}?s={size}"
        elif "microsoft" in self.provider and "graph.microsoft.com" in self.avatar_url:
            return f"{self.avatar_url}?size={size}"
        else:
            return self.avatar_url

    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary."""
        return {
            "id": self.id,
            "provider": self.provider,
            "provider_user_id": self.provider_user_id,
            "email": self.email,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "display_name": self.display_name,
            "avatar_url": self.avatar_url,
            "locale": self.locale,
            "timezone": self.timezone,
            "is_verified": self.is_verified,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "metadata": self.metadata,
            "provider_data": self.provider_data,
        }

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class SSOProviderInfo(BaseModel):
    """SSO provider information model."""

    name: str = Field(..., description="Provider name")
    display_name: str = Field(..., description="Human-readable provider name")
    description: str = Field(..., description="Provider description")
    icon_url: Optional[str] = Field(default=None, description="Provider icon URL")
    color: Optional[str] = Field(default=None, description="Provider brand color")
    website_url: Optional[str] = Field(default=None, description="Provider website URL")
    documentation_url: Optional[str] = Field(default=None, description="Provider documentation URL")
    supported_scopes: List[str] = Field(default_factory=list, description="Supported OAuth scopes")
    supported_claims: List[str] = Field(default_factory=list, description="Supported user claims")
    is_enabled: bool = Field(default=True, description="Whether provider is enabled")
    is_configured: bool = Field(default=False, description="Whether provider is configured")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional provider metadata")

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class SSOProviderConfig(BaseModel):
    """SSO provider configuration model."""

    provider: str = Field(..., description="Provider name")
    client_id: str = Field(..., description="OAuth client ID")
    client_secret: str = Field(..., description="OAuth client secret")
    redirect_uri: str = Field(..., description="OAuth redirect URI")
    scopes: List[str] = Field(default_factory=list, description="OAuth scopes")
    authorization_url: str = Field(..., description="OAuth authorization URL")
    token_url: str = Field(..., description="OAuth token URL")
    user_info_url: str = Field(..., description="User info API URL")
    jwks_url: Optional[str] = Field(default=None, description="JWKS URL for token verification")
    issuer: Optional[str] = Field(default=None, description="OAuth issuer")
    audience: Optional[str] = Field(default=None, description="OAuth audience")
    is_enabled: bool = Field(default=True, description="Whether provider is enabled")
    auto_register: bool = Field(default=True, description="Whether to auto-register new users")
    auto_activate: bool = Field(default=True, description="Whether to auto-activate new users")
    require_email_verification: bool = Field(default=False, description="Whether to require email verification")
    user_mapping: Dict[str, str] = Field(default_factory=dict, description="User attribute mapping")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional configuration metadata")

    @validator("provider")
    def validate_provider(cls, v: str) -> str:
        """Validate provider name."""
        valid_providers = {"google", "github", "microsoft", "apple", "saml", "generic_oauth2", "keycloak"}
        if v.lower() not in valid_providers:
            raise ValueError(f"Invalid provider: {v}")
        return v.lower()

    @validator("redirect_uri")
    def validate_redirect_uri(cls, v: str) -> str:
        """Validate redirect URI."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("Redirect URI must start with http:// or https://")
        return v

    def get_authorization_url(self, state: str, additional_params: Optional[Dict[str, str]] = None) -> str:
        """Get OAuth authorization URL."""
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(self.scopes),
            "state": state,
        }

        if additional_params:
            params.update(additional_params)

        return f"{self.authorization_url}?{urlencode(params)}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary (excluding secrets)."""
        return {
            "provider": self.provider,
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scopes": self.scopes,
            "authorization_url": self.authorization_url,
            "token_url": self.token_url,
            "user_info_url": self.user_info_url,
            "jwks_url": self.jwks_url,
            "issuer": self.issuer,
            "audience": self.audience,
            "is_enabled": self.is_enabled,
            "auto_register": self.auto_register,
            "auto_activate": self.auto_activate,
            "require_email_verification": self.require_email_verification,
            "user_mapping": self.user_mapping,
            "metadata": self.metadata,
        }

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class SSOAuthState(BaseModel):
    """SSO authentication state model."""

    state: str = Field(..., description="Unique state identifier")
    provider: str = Field(..., description="SSO provider name")
    redirect_url: Optional[str] = Field(default=None, description="Redirect URL after authentication")
    user_id: Optional[str] = Field(default=None, description="User ID if already authenticated")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    expires_at: datetime = Field(..., description="Expiration timestamp")
    is_used: bool = Field(default=False, description="Whether state has been used")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional state metadata")

    def is_expired(self) -> bool:
        """Check if state has expired."""
        return datetime.utcnow() > self.expires_at

    def is_valid(self) -> bool:
        """Check if state is valid (not used and not expired)."""
        return not self.is_used and not self.is_expired()

    def mark_as_used(self) -> None:
        """Mark state as used."""
        self.is_used = True

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class SSOAuthResult(BaseModel):
    """SSO authentication result model."""

    success: bool = Field(..., description="Whether authentication was successful")
    user: Optional[SSOUser] = Field(default=None, description="Authenticated user")
    provider: str = Field(..., description="SSO provider name")
    state: Optional[str] = Field(default=None, description="Authentication state")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    error_code: Optional[str] = Field(default=None, description="Error code if failed")
    redirect_url: Optional[str] = Field(default=None, description="Redirect URL after authentication")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional result metadata")

    @classmethod
    def success_result(
        cls,
        user: SSOUser,
        provider: str,
        state: Optional[str] = None,
        redirect_url: Optional[str] = None,
        **kwargs: Any,
    ) -> "SSOAuthResult":
        """Create successful authentication result."""
        return cls(success=True, user=user, provider=provider, state=state, redirect_url=redirect_url, metadata=kwargs)

    @classmethod
    def error_result(
        cls, provider: str, error: str, error_code: Optional[str] = None, state: Optional[str] = None, **kwargs: Any
    ) -> "SSOAuthResult":
        """Create failed authentication result."""
        return cls(success=False, provider=provider, state=state, error=error, error_code=error_code, metadata=kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        result = {
            "success": self.success,
            "provider": self.provider,
            "state": self.state,
            "redirect_url": self.redirect_url,
            "metadata": self.metadata,
        }

        if self.user:
            result["user"] = self.user.to_dict()

        if self.error:
            result["error"] = self.error
            result["error_code"] = self.error_code

        return result

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class SSOToken(BaseModel):
    """SSO token model."""

    access_token: str = Field(..., description="OAuth access token")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    refresh_token: Optional[str] = Field(default=None, description="OAuth refresh token")
    scope: Optional[str] = Field(default=None, description="Token scope")
    id_token: Optional[str] = Field(default=None, description="OpenID Connect ID token")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    expires_at: datetime = Field(..., description="Expiration timestamp")
    provider: str = Field(..., description="SSO provider name")
    user_id: Optional[str] = Field(default=None, description="User ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional token metadata")

    def is_expired(self) -> bool:
        """Check if token has expired."""
        return datetime.utcnow() > self.expires_at

    def is_valid(self) -> bool:
        """Check if token is valid (not expired)."""
        return not self.is_expired()

    def get_remaining_time(self) -> int:
        """Get remaining time until expiration in seconds."""
        if self.is_expired():
            return 0
        return int((self.expires_at - datetime.utcnow()).total_seconds())

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


def generate_state() -> str:
    """Generate a random state parameter."""
    return secrets.token_urlsafe(32)


def generate_nonce() -> str:
    """Generate a random nonce parameter."""
    return secrets.token_urlsafe(16)


def create_auth_state(
    provider: str,
    expires_in: int = 600,
    redirect_url: Optional[str] = None,
    user_id: Optional[str] = None,
    **kwargs: Any,
) -> SSOAuthState:
    """Create authentication state."""
    state = generate_state()
    expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

    return SSOAuthState(
        state=state,
        provider=provider,
        redirect_url=redirect_url,
        user_id=user_id,
        expires_at=expires_at,
        metadata=kwargs,
    )

"""
OAuth2 data models.

Defines all OAuth2-related data models including clients, tokens, grants, and scopes.
"""

import secrets
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from pydantic import BaseModel, Field, validator


class OAuth2Scope(BaseModel):
    """OAuth2 scope model."""

    name: str = Field(..., description="Scope name")
    description: str = Field(..., description="Human-readable scope description")
    is_default: bool = Field(default=False, description="Whether this is a default scope")
    is_system: bool = Field(default=False, description="Whether this is a system scope")
    permissions: List[str] = Field(default_factory=list, description="Permissions included in this scope")

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class OAuth2Client(BaseModel):
    """OAuth2 client model."""

    client_id: str = Field(..., description="Unique client identifier")
    client_secret: str = Field(..., description="Client secret")
    client_name: str = Field(..., description="Human-readable client name")
    client_type: str = Field(default="confidential", description="Client type (confidential, public)")
    redirect_uris: List[str] = Field(default_factory=list, description="Allowed redirect URIs")
    grant_types: List[str] = Field(default_factory=list, description="Allowed grant types")
    response_types: List[str] = Field(default_factory=list, description="Allowed response types")
    scopes: List[str] = Field(default_factory=list, description="Allowed scopes")
    is_active: bool = Field(default=True, description="Whether client is active")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    expires_at: Optional[datetime] = Field(default=None, description="Client expiration timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional client metadata")

    @validator("client_type")
    def validate_client_type(cls, v: str) -> str:
        """Validate client type."""
        if v not in ["confidential", "public"]:
            raise ValueError("Client type must be 'confidential' or 'public'")
        return v

    @validator("redirect_uris")
    def validate_redirect_uris(cls, v: List[str]) -> List[str]:
        """Validate redirect URIs."""
        for uri in v:
            try:
                parsed = urlparse(uri)
                if not parsed.scheme or not parsed.netloc:
                    raise ValueError(f"Invalid redirect URI: {uri}")
            except Exception as e:
                raise ValueError(f"Invalid redirect URI: {uri}") from e
        return v

    @validator("grant_types")
    def validate_grant_types(cls, v: List[str]) -> List[str]:
        """Validate grant types."""
        valid_types = {
            "authorization_code",
            "client_credentials",
            "refresh_token",
            "device_code",
            "password",
            "implicit",
        }
        for grant_type in v:
            if grant_type not in valid_types:
                raise ValueError(f"Invalid grant type: {grant_type}")
        return v

    @validator("response_types")
    def validate_response_types(cls, v: List[str]) -> List[str]:
        """Validate response types."""
        valid_types = {
            "code",
            "token",
            "id_token",
            "code token",
            "code id_token",
            "token id_token",
            "code token id_token",
        }
        for response_type in v:
            if response_type not in valid_types:
                raise ValueError(f"Invalid response type: {response_type}")
        return v

    def is_redirect_uri_allowed(self, uri: str) -> bool:
        """Check if redirect URI is allowed for this client."""
        return uri in self.redirect_uris

    def is_grant_type_allowed(self, grant_type: str) -> bool:
        """Check if grant type is allowed for this client."""
        return grant_type in self.grant_types

    def is_response_type_allowed(self, response_type: str) -> bool:
        """Check if response type is allowed for this client."""
        return response_type in self.response_types

    def is_scope_allowed(self, scope: str) -> bool:
        """Check if scope is allowed for this client."""
        if not self.scopes:
            return True  # No scope restrictions
        requested_scopes = scope.split()
        return all(s in self.scopes for s in requested_scopes)

    def is_expired(self) -> bool:
        """Check if client has expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    def is_valid(self) -> bool:
        """Check if client is valid (active and not expired)."""
        return self.is_active and not self.is_expired()

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class OAuth2AuthorizationCode(BaseModel):
    """OAuth2 authorization code model."""

    code: str = Field(..., description="Authorization code")
    client_id: str = Field(..., description="Client identifier")
    user_id: str = Field(..., description="User identifier")
    redirect_uri: str = Field(..., description="Redirect URI used in authorization request")
    scopes: List[str] = Field(default_factory=list, description="Requested scopes")
    code_challenge: Optional[str] = Field(default=None, description="PKCE code challenge")
    code_challenge_method: Optional[str] = Field(default=None, description="PKCE code challenge method")
    nonce: Optional[str] = Field(default=None, description="Nonce for OpenID Connect")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    expires_at: datetime = Field(..., description="Expiration timestamp")
    is_used: bool = Field(default=False, description="Whether code has been used")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @validator("code_challenge_method")
    def validate_code_challenge_method(cls, v: Optional[str]) -> Optional[str]:
        """Validate code challenge method."""
        if v is not None and v not in ["S256", "plain"]:
            raise ValueError("Code challenge method must be 'S256' or 'plain'")
        return v

    def is_expired(self) -> bool:
        """Check if authorization code has expired."""
        return datetime.utcnow() > self.expires_at

    def is_valid(self) -> bool:
        """Check if authorization code is valid (not used and not expired)."""
        return not self.is_used and not self.is_expired()

    def mark_as_used(self) -> None:
        """Mark authorization code as used."""
        self.is_used = True

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class OAuth2AccessToken(BaseModel):
    """OAuth2 access token model."""

    token: str = Field(..., description="Access token")
    token_type: str = Field(default="Bearer", description="Token type")
    client_id: str = Field(..., description="Client identifier")
    user_id: Optional[str] = Field(default=None, description="User identifier")
    scopes: List[str] = Field(default_factory=list, description="Token scopes")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    expires_at: datetime = Field(..., description="Expiration timestamp")
    is_revoked: bool = Field(default=False, description="Whether token is revoked")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @validator("token_type")
    def validate_token_type(cls, v: str) -> str:
        """Validate token type."""
        if v.lower() not in ["bearer", "mac"]:
            raise ValueError("Token type must be 'Bearer' or 'MAC'")
        return v

    def is_expired(self) -> bool:
        """Check if access token has expired."""
        return datetime.utcnow() > self.expires_at

    def is_valid(self) -> bool:
        """Check if access token is valid (not revoked and not expired)."""
        return not self.is_revoked and not self.is_expired()

    def revoke(self) -> None:
        """Revoke access token."""
        self.is_revoked = True

    def has_scope(self, scope: str) -> bool:
        """Check if token has specific scope."""
        return scope in self.scopes

    def has_any_scope(self, scopes: List[str]) -> bool:
        """Check if token has any of the specified scopes."""
        return any(scope in self.scopes for scope in scopes)

    def has_all_scopes(self, scopes: List[str]) -> bool:
        """Check if token has all of the specified scopes."""
        return all(scope in self.scopes for scope in scopes)

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class OAuth2RefreshToken(BaseModel):
    """OAuth2 refresh token model."""

    token: str = Field(..., description="Refresh token")
    client_id: str = Field(..., description="Client identifier")
    user_id: str = Field(..., description="User identifier")
    scopes: List[str] = Field(default_factory=list, description="Token scopes")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    expires_at: datetime = Field(..., description="Expiration timestamp")
    is_revoked: bool = Field(default=False, description="Whether token is revoked")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    def is_expired(self) -> bool:
        """Check if refresh token has expired."""
        return datetime.utcnow() > self.expires_at

    def is_valid(self) -> bool:
        """Check if refresh token is valid (not revoked and not expired)."""
        return not self.is_revoked and not self.is_expired()

    def revoke(self) -> None:
        """Revoke refresh token."""
        self.is_revoked = True

    def has_scope(self, scope: str) -> bool:
        """Check if token has specific scope."""
        return scope in self.scopes

    def has_any_scope(self, scopes: List[str]) -> bool:
        """Check if token has any of the specified scopes."""
        return any(scope in self.scopes for scope in scopes)

    def has_all_scopes(self, scopes: List[str]) -> bool:
        """Check if token has all of the specified scopes."""
        return all(scope in self.scopes for scope in scopes)

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class OAuth2Grant(BaseModel):
    """OAuth2 grant model for tracking grants."""

    grant_id: str = Field(..., description="Unique grant identifier")
    client_id: str = Field(..., description="Client identifier")
    user_id: str = Field(..., description="User identifier")
    grant_type: str = Field(..., description="Grant type")
    scopes: List[str] = Field(default_factory=list, description="Granted scopes")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    expires_at: Optional[datetime] = Field(default=None, description="Grant expiration timestamp")
    is_active: bool = Field(default=True, description="Whether grant is active")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @validator("grant_type")
    def validate_grant_type(cls, v: str) -> str:
        """Validate grant type."""
        valid_types = {
            "authorization_code",
            "client_credentials",
            "refresh_token",
            "device_code",
            "password",
            "implicit",
        }
        if v not in valid_types:
            raise ValueError(f"Invalid grant type: {v}")
        return v

    def is_expired(self) -> bool:
        """Check if grant has expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    def is_valid(self) -> bool:
        """Check if grant is valid (active and not expired)."""
        return self.is_active and not self.is_expired()

    def revoke(self) -> None:
        """Revoke grant."""
        self.is_active = False

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class OAuth2DeviceCode(BaseModel):
    """OAuth2 device code model for device flow."""

    device_code: str = Field(..., description="Device code")
    user_code: str = Field(..., description="User code")
    client_id: str = Field(..., description="Client identifier")
    scopes: List[str] = Field(default_factory=list, description="Requested scopes")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    expires_at: datetime = Field(..., description="Expiration timestamp")
    interval: int = Field(default=5, description="Polling interval in seconds")
    user_id: Optional[str] = Field(default=None, description="User identifier after authorization")
    is_authorized: bool = Field(default=False, description="Whether device is authorized")
    is_expired: bool = Field(default=False, description="Whether device code is expired")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    def is_expired(self) -> bool:
        """Check if device code has expired."""
        return datetime.utcnow() > self.expires_at or self.is_expired

    def is_valid(self) -> bool:
        """Check if device code is valid (not expired and not authorized yet)."""
        return not self.is_expired() and not self.is_authorized

    def authorize(self, user_id: str) -> None:
        """Authorize device code for user."""
        self.user_id = user_id
        self.is_authorized = True

    def expire(self) -> None:
        """Mark device code as expired."""
        self.is_expired = True

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


def generate_client_id() -> str:
    """Generate a random client ID."""
    return secrets.token_urlsafe(32)


def generate_client_secret() -> str:
    """Generate a random client secret."""
    return secrets.token_urlsafe(48)


def generate_authorization_code() -> str:
    """Generate a random authorization code."""
    return secrets.token_urlsafe(32)


def generate_access_token() -> str:
    """Generate a random access token."""
    return secrets.token_urlsafe(64)


def generate_refresh_token() -> str:
    """Generate a random refresh token."""
    return secrets.token_urlsafe(64)


def generate_device_code() -> str:
    """Generate a random device code."""
    return secrets.token_urlsafe(32)


def generate_user_code() -> str:
    """Generate a user-friendly user code."""
    return secrets.token_urlsafe(8).upper()


def generate_grant_id() -> str:
    """Generate a random grant ID."""
    return secrets.token_urlsafe(32)

"""
OAuth2 server configuration.

Defines configuration options for the OAuth2 authorization server.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, validator


class OAuth2Config(BaseModel):
    """OAuth2 server configuration."""

    # Server settings
    server_name: str = Field(default="Zephyr OAuth2 Server", description="OAuth2 server name")
    server_url: str = Field(default="http://localhost:8000", description="OAuth2 server base URL")
    issuer: str = Field(default="http://localhost:8000", description="OAuth2 server issuer URL")

    # Token settings
    access_token_lifetime: int = Field(default=3600, description="Access token lifetime in seconds")
    refresh_token_lifetime: int = Field(default=86400 * 7, description="Refresh token lifetime in seconds")
    authorization_code_lifetime: int = Field(default=600, description="Authorization code lifetime in seconds")
    device_code_lifetime: int = Field(default=1800, description="Device code lifetime in seconds")
    device_code_interval: int = Field(default=5, description="Device code polling interval in seconds")

    # Token types
    access_token_type: str = Field(default="Bearer", description="Access token type")
    supported_token_types: List[str] = Field(default=["Bearer"], description="Supported token types")

    # Grant types
    supported_grant_types: List[str] = Field(
        default=["authorization_code", "client_credentials", "refresh_token", "device_code"],
        description="Supported grant types",
    )

    # Response types
    supported_response_types: List[str] = Field(
        default=["code", "token", "id_token", "code token", "code id_token", "token id_token", "code token id_token"],
        description="Supported response types",
    )

    # Scopes
    default_scopes: List[str] = Field(default=["read"], description="Default scopes")
    supported_scopes: List[str] = Field(
        default=["read", "write", "admin", "openid", "profile", "email"], description="Supported scopes"
    )

    # PKCE settings
    require_pkce: bool = Field(default=True, description="Require PKCE for public clients")
    supported_code_challenge_methods: List[str] = Field(
        default=["S256", "plain"], description="Supported PKCE code challenge methods"
    )

    # Security settings
    require_client_authentication: bool = Field(default=True, description="Require client authentication")
    allow_implicit_grant: bool = Field(default=False, description="Allow implicit grant flow")
    allow_public_clients: bool = Field(default=True, description="Allow public clients")

    # Rate limiting
    rate_limit_requests: int = Field(default=100, description="Rate limit requests per minute")
    rate_limit_window: int = Field(default=60, description="Rate limit window in seconds")

    # CORS settings
    allowed_origins: List[str] = Field(default_factory=list, description="Allowed CORS origins")
    allowed_methods: List[str] = Field(default=["GET", "POST", "OPTIONS"], description="Allowed CORS methods")
    allowed_headers: List[str] = Field(
        default=["Content-Type", "Authorization", "X-Requested-With"], description="Allowed CORS headers"
    )

    # Database settings
    token_storage_backend: str = Field(default="memory", description="Token storage backend")
    client_storage_backend: str = Field(default="memory", description="Client storage backend")

    # Endpoint settings
    authorization_endpoint: str = Field(default="/oauth/authorize", description="Authorization endpoint path")
    token_endpoint: str = Field(default="/oauth/token", description="Token endpoint path")
    revocation_endpoint: str = Field(default="/oauth/revoke", description="Token revocation endpoint path")
    introspection_endpoint: str = Field(default="/oauth/introspect", description="Token introspection endpoint path")
    device_authorization_endpoint: str = Field(
        default="/oauth/device", description="Device authorization endpoint path"
    )
    jwks_endpoint: str = Field(default="/oauth/jwks", description="JWKS endpoint path")
    userinfo_endpoint: str = Field(default="/oauth/userinfo", description="User info endpoint path")

    # OpenID Connect settings
    openid_connect_enabled: bool = Field(default=False, description="Enable OpenID Connect")
    supported_claims: List[str] = Field(
        default=["sub", "iss", "aud", "exp", "iat", "auth_time", "nonce", "acr", "amr", "azp"],
        description="Supported OpenID Connect claims",
    )
    supported_id_token_signing_alg_values: List[str] = Field(
        default=["RS256", "HS256"], description="Supported ID token signing algorithms"
    )

    # Logging and monitoring
    enable_request_logging: bool = Field(default=True, description="Enable request logging")
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")
    log_level: str = Field(default="INFO", description="Log level")

    # Custom settings
    custom_settings: Dict[str, Any] = Field(default_factory=dict, description="Custom settings")

    @validator("access_token_type")
    def validate_access_token_type(cls, v: str) -> str:
        """Validate access token type."""
        if v.lower() not in ["bearer", "mac"]:
            raise ValueError("Access token type must be 'Bearer' or 'MAC'")
        return v

    @validator("supported_grant_types")
    def validate_supported_grant_types(cls, v: List[str]) -> List[str]:
        """Validate supported grant types."""
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

    @validator("supported_response_types")
    def validate_supported_response_types(cls, v: List[str]) -> List[str]:
        """Validate supported response types."""
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

    @validator("supported_code_challenge_methods")
    def validate_code_challenge_methods(cls, v: List[str]) -> List[str]:
        """Validate code challenge methods."""
        valid_methods = {"S256", "plain"}
        for method in v:
            if method not in valid_methods:
                raise ValueError(f"Invalid code challenge method: {method}")
        return v

    @validator("log_level")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {v}")
        return v.upper()

    def is_grant_type_supported(self, grant_type: str) -> bool:
        """Check if grant type is supported."""
        return grant_type in self.supported_grant_types

    def is_response_type_supported(self, response_type: str) -> bool:
        """Check if response type is supported."""
        return response_type in self.supported_response_types

    def is_scope_supported(self, scope: str) -> bool:
        """Check if scope is supported."""
        if not self.supported_scopes:
            return True
        requested_scopes = scope.split()
        return all(s in self.supported_scopes for s in requested_scopes)

    def is_code_challenge_method_supported(self, method: str) -> bool:
        """Check if code challenge method is supported."""
        return method in self.supported_code_challenge_methods

    def get_token_lifetime(self, token_type: str) -> int:
        """Get token lifetime for specific token type."""
        if token_type == "access_token":
            return self.access_token_lifetime
        elif token_type == "refresh_token":
            return self.refresh_token_lifetime
        elif token_type == "authorization_code":
            return self.authorization_code_lifetime
        elif token_type == "device_code":
            return self.device_code_lifetime
        else:
            return self.access_token_lifetime

    def get_endpoint_url(self, endpoint: str) -> str:
        """Get full URL for endpoint."""
        if endpoint == "authorization":
            return f"{self.server_url}{self.authorization_endpoint}"
        elif endpoint == "token":
            return f"{self.server_url}{self.token_endpoint}"
        elif endpoint == "revocation":
            return f"{self.server_url}{self.revocation_endpoint}"
        elif endpoint == "introspection":
            return f"{self.server_url}{self.introspection_endpoint}"
        elif endpoint == "device_authorization":
            return f"{self.server_url}{self.device_authorization_endpoint}"
        elif endpoint == "jwks":
            return f"{self.server_url}{self.jwks_endpoint}"
        elif endpoint == "userinfo":
            return f"{self.server_url}{self.userinfo_endpoint}"
        else:
            raise ValueError(f"Unknown endpoint: {endpoint}")

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            # Add custom encoders if needed
        }

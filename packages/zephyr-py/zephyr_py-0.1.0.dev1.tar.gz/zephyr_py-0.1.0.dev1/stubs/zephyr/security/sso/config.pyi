from _typeshed import Incomplete
from pydantic import BaseModel
from typing import Any

class SSOConfig(BaseModel):
    enabled: bool
    default_provider: str | None
    auto_register: bool
    auto_activate: bool
    require_email_verification: bool
    state_lifetime: int
    token_lifetime: int
    max_login_attempts: int
    lockout_duration: int
    session_lifetime: int
    session_secure: bool
    session_httponly: bool
    session_samesite: str
    providers: dict[str, dict[str, Any]]
    enabled_providers: list[str]
    default_user_mapping: dict[str, str]
    success_redirect_url: str
    error_redirect_url: str
    logout_redirect_url: str
    enable_logging: bool
    log_level: str
    enable_metrics: bool
    rate_limit_requests: int
    rate_limit_window: int
    allowed_origins: list[str]
    allowed_methods: list[str]
    allowed_headers: list[str]
    custom_settings: dict[str, Any]
    def validate_session_samesite(cls, v: str) -> str: ...
    def validate_log_level(cls, v: str) -> str: ...
    def validate_enabled_providers(cls, v: list[str]) -> list[str]: ...
    def is_provider_enabled(self, provider: str) -> bool: ...
    def get_provider_config(self, provider: str) -> dict[str, Any] | None: ...
    def set_provider_config(self, provider: str, config: dict[str, Any]) -> None: ...
    def enable_provider(self, provider: str) -> None: ...
    def disable_provider(self, provider: str) -> None: ...
    def get_user_mapping(self, provider: str) -> dict[str, str]: ...
    def get_redirect_url(self, url_type: str) -> str: ...
    def is_secure_session(self) -> bool: ...
    def get_session_config(self) -> dict[str, Any]: ...
    def get_rate_limit_config(self) -> dict[str, int]: ...
    def get_cors_config(self) -> dict[str, list[str]]: ...
    class Config:
        json_encoders: Incomplete

class GoogleSSOConfig(BaseModel):
    client_id: str
    client_secret: str
    redirect_uri: str
    scopes: list[str]
    hosted_domain: str | None
    access_type: str
    prompt: str
    include_granted_scopes: bool
    user_mapping: dict[str, str]

class GitHubSSOConfig(BaseModel):
    client_id: str
    client_secret: str
    redirect_uri: str
    scopes: list[str]
    allow_signup: bool
    user_mapping: dict[str, str]

class MicrosoftSSOConfig(BaseModel):
    client_id: str
    client_secret: str
    redirect_uri: str
    tenant: str
    scopes: list[str]
    response_mode: str
    response_type: str
    user_mapping: dict[str, str]

class AppleSSOConfig(BaseModel):
    client_id: str
    client_secret: str
    redirect_uri: str
    team_id: str
    key_id: str
    private_key: str
    scopes: list[str]
    response_mode: str
    user_mapping: dict[str, str]

class SAMLSSOConfig(BaseModel):
    entity_id: str
    sso_url: str
    slo_url: str | None
    x509_cert: str
    private_key: str | None
    name_id_format: str
    attribute_mapping: dict[str, str]
    sign_requests: bool
    encrypt_assertions: bool
    want_assertions_signed: bool
    want_response_signed: bool

class GenericOAuth2SSOConfig(BaseModel):
    client_id: str
    client_secret: str
    redirect_uri: str
    authorization_url: str
    token_url: str
    user_info_url: str
    jwks_url: str | None
    issuer: str | None
    audience: str | None
    scopes: list[str]
    response_type: str
    response_mode: str
    user_mapping: dict[str, str]

from _typeshed import Incomplete
from datetime import datetime
from pydantic import BaseModel
from typing import Any

class SSOUser(BaseModel):
    id: str
    provider: str
    provider_user_id: str
    email: str
    username: str | None
    first_name: str | None
    last_name: str | None
    display_name: str | None
    avatar_url: str | None
    locale: str | None
    timezone: str | None
    is_verified: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: datetime | None
    metadata: dict[str, Any]
    provider_data: dict[str, Any]
    def validate_email(cls, v: str) -> str: ...
    def validate_provider(cls, v: str) -> str: ...
    def get_full_name(self) -> str: ...
    def get_avatar_url(self, size: int = 64) -> str | None: ...
    def to_dict(self) -> dict[str, Any]: ...
    class Config:
        json_encoders: Incomplete

class SSOProviderInfo(BaseModel):
    name: str
    display_name: str
    description: str
    icon_url: str | None
    color: str | None
    website_url: str | None
    documentation_url: str | None
    supported_scopes: list[str]
    supported_claims: list[str]
    is_enabled: bool
    is_configured: bool
    metadata: dict[str, Any]
    class Config:
        json_encoders: Incomplete

class SSOProviderConfig(BaseModel):
    provider: str
    client_id: str
    client_secret: str
    redirect_uri: str
    scopes: list[str]
    authorization_url: str
    token_url: str
    user_info_url: str
    jwks_url: str | None
    issuer: str | None
    audience: str | None
    is_enabled: bool
    auto_register: bool
    auto_activate: bool
    require_email_verification: bool
    user_mapping: dict[str, str]
    metadata: dict[str, Any]
    def validate_provider(cls, v: str) -> str: ...
    def validate_redirect_uri(cls, v: str) -> str: ...
    def get_authorization_url(self, state: str, additional_params: dict[str, str] | None = None) -> str: ...
    def to_dict(self) -> dict[str, Any]: ...
    class Config:
        json_encoders: Incomplete

class SSOAuthState(BaseModel):
    state: str
    provider: str
    redirect_url: str | None
    user_id: str | None
    created_at: datetime
    expires_at: datetime
    is_used: bool
    metadata: dict[str, Any]
    def is_expired(self) -> bool: ...
    def is_valid(self) -> bool: ...
    def mark_as_used(self) -> None: ...
    class Config:
        json_encoders: Incomplete

class SSOAuthResult(BaseModel):
    success: bool
    user: SSOUser | None
    provider: str
    state: str | None
    error: str | None
    error_code: str | None
    redirect_url: str | None
    metadata: dict[str, Any]
    @classmethod
    def success_result(cls, user: SSOUser, provider: str, state: str | None = None, redirect_url: str | None = None, **kwargs: Any) -> SSOAuthResult: ...
    @classmethod
    def error_result(cls, provider: str, error: str, error_code: str | None = None, state: str | None = None, **kwargs: Any) -> SSOAuthResult: ...
    def to_dict(self) -> dict[str, Any]: ...
    class Config:
        json_encoders: Incomplete

class SSOToken(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str | None
    scope: str | None
    id_token: str | None
    created_at: datetime
    expires_at: datetime
    provider: str
    user_id: str | None
    metadata: dict[str, Any]
    def is_expired(self) -> bool: ...
    def is_valid(self) -> bool: ...
    def get_remaining_time(self) -> int: ...
    class Config:
        json_encoders: Incomplete

def generate_state() -> str: ...
def generate_nonce() -> str: ...
def create_auth_state(provider: str, expires_in: int = 600, redirect_url: str | None = None, user_id: str | None = None, **kwargs: Any) -> SSOAuthState: ...

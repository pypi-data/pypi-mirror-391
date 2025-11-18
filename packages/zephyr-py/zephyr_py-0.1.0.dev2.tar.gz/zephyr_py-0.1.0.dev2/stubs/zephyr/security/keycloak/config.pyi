from _typeshed import Incomplete
from pydantic import BaseModel
from typing import Any

class KeycloakConfig(BaseModel):
    server_url: str
    realm: str
    public_client: bool
    client_id: str
    client_secret: str | None
    authorization_endpoint: str | None
    token_endpoint: str | None
    userinfo_endpoint: str | None
    jwks_uri: str | None
    end_session_endpoint: str | None
    introspection_endpoint: str | None
    verify_token_signature: bool
    verify_token_audience: bool
    verify_token_expiry: bool
    token_leeway: int
    default_scopes: list[str]
    admin_username: str | None
    admin_password: str | None
    admin_client_id: str
    admin_realm: str
    timeout: int
    verify_ssl: bool
    user_mapping: dict[str, str]
    auto_register: bool
    auto_activate: bool
    custom_settings: dict[str, Any]
    def validate_server_url(cls, v: str) -> str: ...
    def validate_client_secret(cls, v: str | None, values: dict[str, Any]) -> str | None: ...
    def get_realm_url(self) -> str: ...
    def get_authorization_endpoint(self) -> str: ...
    def get_token_endpoint(self) -> str: ...
    def get_userinfo_endpoint(self) -> str: ...
    def get_jwks_uri(self) -> str: ...
    def get_end_session_endpoint(self) -> str: ...
    def get_introspection_endpoint(self) -> str: ...
    def get_admin_url(self) -> str: ...
    def get_admin_token_endpoint(self) -> str: ...
    def get_well_known_url(self) -> str: ...
    class Config:
        json_encoders: Incomplete

class KeycloakRealmConfig(BaseModel):
    realm: str
    display_name: str | None
    enabled: bool
    registration_allowed: bool
    registration_email_as_username: bool
    login_with_email_allowed: bool
    duplicate_emails_allowed: bool
    password_policy: str | None
    access_token_lifespan: int
    refresh_token_lifespan: int
    ssl_required: str
    class Config:
        json_encoders: Incomplete

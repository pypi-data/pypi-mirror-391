from _typeshed import Incomplete
from datetime import datetime
from pydantic import BaseModel
from typing import Any

class KeycloakToken(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str | None
    refresh_expires_in: int | None
    id_token: str | None
    scope: str | None
    session_state: str | None
    issued_at: datetime
    class Config:
        json_encoders: Incomplete
    def is_expired(self) -> bool: ...
    def is_refresh_expired(self) -> bool: ...

class KeycloakUser(BaseModel):
    id: str | None
    username: str
    email: str | None
    email_verified: bool
    first_name: str | None
    last_name: str | None
    enabled: bool
    created_timestamp: int | None
    attributes: dict[str, list[str]]
    groups: list[str]
    realm_roles: list[str]
    client_roles: dict[str, list[str]]
    credentials: list[dict[str, Any]]
    required_actions: list[str]
    class Config:
        json_encoders: Incomplete
    def get_full_name(self) -> str: ...
    def has_role(self, role: str) -> bool: ...
    def has_client_role(self, client: str, role: str) -> bool: ...

class KeycloakRole(BaseModel):
    id: str | None
    name: str
    description: str | None
    composite: bool
    client_role: bool
    container_id: str | None
    composites: dict[str, list[str]]
    attributes: dict[str, list[str]]
    class Config:
        json_encoders: Incomplete

class KeycloakGroup(BaseModel):
    id: str | None
    name: str
    path: str | None
    sub_groups: list['KeycloakGroup']
    attributes: dict[str, list[str]]
    realm_roles: list[str]
    client_roles: dict[str, list[str]]
    class Config:
        json_encoders: Incomplete

class KeycloakClient(BaseModel):
    id: str | None
    client_id: str
    name: str | None
    description: str | None
    enabled: bool
    public_client: bool
    bearer_only: bool
    root_url: str | None
    base_url: str | None
    redirect_uris: list[str]
    web_origins: list[str]
    protocol: str
    standard_flow_enabled: bool
    implicit_flow_enabled: bool
    direct_access_grants_enabled: bool
    service_accounts_enabled: bool
    attributes: dict[str, str]
    class Config:
        json_encoders: Incomplete

class KeycloakRealm(BaseModel):
    id: str | None
    realm: str
    display_name: str | None
    display_name_html: str | None
    enabled: bool
    ssl_required: str
    registration_allowed: bool
    registration_email_as_username: bool
    login_with_email_allowed: bool
    duplicate_emails_allowed: bool
    access_token_lifespan: int
    refresh_token_lifespan: int
    class Config:
        json_encoders: Incomplete

class KeycloakUserInfo(BaseModel):
    sub: str
    email: str | None
    email_verified: bool
    preferred_username: str | None
    given_name: str | None
    family_name: str | None
    name: str | None
    locale: str | None
    zoneinfo: str | None
    attributes: dict[str, Any]
    class Config:
        extra: str
        json_encoders: Incomplete

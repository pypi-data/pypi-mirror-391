from _typeshed import Incomplete
from pydantic import BaseModel
from typing import Any

class OAuth2Config(BaseModel):
    server_name: str
    server_url: str
    issuer: str
    access_token_lifetime: int
    refresh_token_lifetime: int
    authorization_code_lifetime: int
    device_code_lifetime: int
    device_code_interval: int
    access_token_type: str
    supported_token_types: list[str]
    supported_grant_types: list[str]
    supported_response_types: list[str]
    default_scopes: list[str]
    supported_scopes: list[str]
    require_pkce: bool
    supported_code_challenge_methods: list[str]
    require_client_authentication: bool
    allow_implicit_grant: bool
    allow_public_clients: bool
    rate_limit_requests: int
    rate_limit_window: int
    allowed_origins: list[str]
    allowed_methods: list[str]
    allowed_headers: list[str]
    token_storage_backend: str
    client_storage_backend: str
    authorization_endpoint: str
    token_endpoint: str
    revocation_endpoint: str
    introspection_endpoint: str
    device_authorization_endpoint: str
    jwks_endpoint: str
    userinfo_endpoint: str
    openid_connect_enabled: bool
    supported_claims: list[str]
    supported_id_token_signing_alg_values: list[str]
    enable_request_logging: bool
    enable_metrics: bool
    log_level: str
    custom_settings: dict[str, Any]
    def validate_access_token_type(cls, v: str) -> str: ...
    def validate_supported_grant_types(cls, v: list[str]) -> list[str]: ...
    def validate_supported_response_types(cls, v: list[str]) -> list[str]: ...
    def validate_code_challenge_methods(cls, v: list[str]) -> list[str]: ...
    def validate_log_level(cls, v: str) -> str: ...
    def is_grant_type_supported(self, grant_type: str) -> bool: ...
    def is_response_type_supported(self, response_type: str) -> bool: ...
    def is_scope_supported(self, scope: str) -> bool: ...
    def is_code_challenge_method_supported(self, method: str) -> bool: ...
    def get_token_lifetime(self, token_type: str) -> int: ...
    def get_endpoint_url(self, endpoint: str) -> str: ...
    class Config:
        json_encoders: Incomplete

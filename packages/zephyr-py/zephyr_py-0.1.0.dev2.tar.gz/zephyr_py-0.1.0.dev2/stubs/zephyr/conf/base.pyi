from pydantic_settings import BaseSettings as PydanticBaseSettings

class BaseSettings(PydanticBaseSettings):
    DEBUG: bool
    SECRET_KEY: str
    HOST: str
    PORT: int
    WORKERS: int
    APP_NAME: str
    VERSION: str
    DESCRIPTION: str | None
    ENABLE_HEALTH_CHECKS: bool
    ENABLE_METRICS: bool
    ENABLE_TRACING: bool
    ENABLE_COMPRESSION: bool
    ENABLE_CACHING: bool
    ENABLE_CORS: bool
    ENABLE_RATE_LIMITING: bool
    ENABLE_AUTO_DOCS: bool
    ENABLE_REQUEST_ID: bool
    ENABLE_ERROR_DETAILS: bool
    CORS_ORIGINS: list[str]
    CORS_ALLOW_CREDENTIALS: bool
    CORS_ALLOW_METHODS: list[str]
    CORS_ALLOW_HEADERS: list[str]
    CORS_MAX_AGE: int
    RATE_LIMIT_REQUESTS: int
    RATE_LIMIT_WINDOW: int
    RATE_LIMIT_STORAGE: str
    DATABASE_URL: str | None
    DATABASE_POOL_SIZE: int
    DATABASE_MAX_OVERFLOW: int
    REDIS_URL: str | None
    REDIS_POOL_SIZE: int
    LOG_LEVEL: str
    LOG_FORMAT: str
    CACHE_BACKEND: str
    CACHE_DEFAULT_TTL: int
    AUTH_BACKEND: str
    AUTH_USER_MODEL: str | None
    AUTH_LOGIN_URL: str
    AUTH_LOGOUT_URL: str
    AUTH_RATE_LIMIT: int
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int
    JWT_ISSUER: str | None
    JWT_AUDIENCE: str | None
    OAUTH2_ENABLED: bool
    OAUTH2_AUTHORIZATION_CODE_EXPIRE_MINUTES: int
    OAUTH2_PKCE_REQUIRED: bool
    KEYCLOAK_ENABLED: bool
    KEYCLOAK_SERVER_URL: str | None
    KEYCLOAK_REALM: str | None
    KEYCLOAK_CLIENT_ID: str | None
    KEYCLOAK_CLIENT_SECRET: str | None
    SSO_GOOGLE_CLIENT_ID: str | None
    SSO_GOOGLE_CLIENT_SECRET: str | None
    SSO_GITHUB_CLIENT_ID: str | None
    SSO_GITHUB_CLIENT_SECRET: str | None
    WEBAUTHN_ENABLED: bool
    WEBAUTHN_RP_ID: str | None
    WEBAUTHN_RP_NAME: str
    WEBAUTHN_ORIGIN: str | None
    MFA_ENABLED: bool
    MFA_REQUIRED_FOR_ADMIN: bool
    MFA_TOTP_ISSUER: str
    MFA_BACKUP_CODES_COUNT: int
    LDAP_ENABLED: bool
    LDAP_SERVER_URI: str | None
    LDAP_BIND_DN: str | None
    LDAP_BIND_PASSWORD: str | None
    LDAP_USER_SEARCH_BASE: str | None
    RBAC_ENABLED: bool
    RBAC_DEFAULT_ROLE: str
    SESSION_BACKEND: str
    SESSION_COOKIE_NAME: str
    SESSION_COOKIE_SECURE: bool
    SESSION_COOKIE_HTTPONLY: bool
    SESSION_COOKIE_SAMESITE: str
    SESSION_EXPIRE_SECONDS: int
    PASSWORD_BCRYPT_ROUNDS: int
    TOKEN_BLACKLIST_MAX_SIZE: int
    OAUTH2_AUTHORIZATION_ENDPOINT: str
    OAUTH2_TOKEN_ENDPOINT: str
    OAUTH2_REVOKE_ENDPOINT: str
    SSO_AZURE_TENANT_ID: str | None
    SSO_AZURE_CLIENT_ID: str | None
    SSO_AZURE_CLIENT_SECRET: str | None
    KEYCLOAK_ADMIN_USERNAME: str | None
    KEYCLOAK_ADMIN_PASSWORD: str | None
    MFA_SMS_PROVIDER: str | None
    MFA_EMAIL_PROVIDER: str | None
    FEDERATION_ENABLED: bool
    LDAP_SERVER: str | None
    LDAP_PORT: int
    LDAP_USE_SSL: bool
    LDAP_USER_SEARCH_FILTER: str
    LDAP_GROUP_SEARCH_BASE: str | None
    LDAP_GROUP_SEARCH_FILTER: str
    UMA_ENABLED: bool
    UMA_RESOURCE_SERVER: str | None
    UMA_AUTHORIZATION_SERVER: str | None
    class Config:
        env_file: str
        env_file_encoding: str
        case_sensitive: bool

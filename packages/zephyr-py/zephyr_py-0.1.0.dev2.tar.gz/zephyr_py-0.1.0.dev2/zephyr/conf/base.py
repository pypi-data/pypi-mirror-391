"""Base settings class for Zephyr applications."""

from pydantic import Field
from pydantic_settings import BaseSettings as PydanticBaseSettings


class BaseSettings(PydanticBaseSettings):
    """
    Base settings for Zephyr applications.

    Users inherit from this in their settings.py file (Django-style).

    Example:
        # myproject/settings.py
        from zephyr.conf import BaseSettings

        class Settings(BaseSettings):
            DEBUG = True
            SECRET_KEY = "my-secret"
            ENABLE_CORS = True
    """

    # Core Application
    DEBUG: bool = False
    SECRET_KEY: str = Field(default="change-me-in-production")

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1

    # Application Metadata
    APP_NAME: str = "Zephyr"
    VERSION: str = "1.0.0"
    DESCRIPTION: str | None = None

    # Feature Flags
    ENABLE_HEALTH_CHECKS: bool = True
    ENABLE_METRICS: bool = True
    ENABLE_TRACING: bool = True
    ENABLE_COMPRESSION: bool = True
    ENABLE_CACHING: bool = True
    ENABLE_CORS: bool = True
    ENABLE_RATE_LIMITING: bool = True
    ENABLE_AUTO_DOCS: bool = True
    ENABLE_REQUEST_ID: bool = True
    ENABLE_ERROR_DETAILS: bool = True

    # CORS Configuration
    CORS_ORIGINS: list[str] = []
    CORS_ALLOW_CREDENTIALS: bool = False
    CORS_ALLOW_METHODS: list[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]
    CORS_MAX_AGE: int = 600

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 1000
    RATE_LIMIT_WINDOW: int = 60
    RATE_LIMIT_STORAGE: str = "memory"

    # Database
    DATABASE_URL: str | None = None
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str | None = None
    REDIS_POOL_SIZE: int = 10

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # Caching
    CACHE_BACKEND: str = "memory"
    CACHE_DEFAULT_TTL: int = 300

    # Authentication
    AUTH_BACKEND: str = "zephyr.security.backends.JWTAuthenticationBackend"
    AUTH_USER_MODEL: str | None = None
    AUTH_LOGIN_URL: str = "/auth/login"
    AUTH_LOGOUT_URL: str = "/auth/logout"
    AUTH_RATE_LIMIT: int = 5  # attempts per minute

    # JWT
    JWT_SECRET_KEY: str = Field(default="change-me-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_ISSUER: str | None = None
    JWT_AUDIENCE: str | None = None

    # OAuth2
    OAUTH2_ENABLED: bool = False
    OAUTH2_AUTHORIZATION_CODE_EXPIRE_MINUTES: int = 10
    OAUTH2_PKCE_REQUIRED: bool = True

    # Keycloak
    KEYCLOAK_ENABLED: bool = False
    KEYCLOAK_SERVER_URL: str | None = None
    KEYCLOAK_REALM: str | None = None
    KEYCLOAK_CLIENT_ID: str | None = None
    KEYCLOAK_CLIENT_SECRET: str | None = None

    # SSO
    SSO_GOOGLE_CLIENT_ID: str | None = None
    SSO_GOOGLE_CLIENT_SECRET: str | None = None
    SSO_GITHUB_CLIENT_ID: str | None = None
    SSO_GITHUB_CLIENT_SECRET: str | None = None

    # WebAuthn
    WEBAUTHN_ENABLED: bool = False
    WEBAUTHN_RP_ID: str | None = None
    WEBAUTHN_RP_NAME: str = "Zephyr App"
    WEBAUTHN_ORIGIN: str | None = None

    # MFA
    MFA_ENABLED: bool = False
    MFA_REQUIRED_FOR_ADMIN: bool = True
    MFA_TOTP_ISSUER: str = "Zephyr"
    MFA_BACKUP_CODES_COUNT: int = 10

    # LDAP
    LDAP_ENABLED: bool = False
    LDAP_SERVER_URI: str | None = None
    LDAP_BIND_DN: str | None = None
    LDAP_BIND_PASSWORD: str | None = None
    LDAP_USER_SEARCH_BASE: str | None = None

    # RBAC
    RBAC_ENABLED: bool = True
    RBAC_DEFAULT_ROLE: str = "user"

    # Sessions
    SESSION_BACKEND: str = "memory"
    SESSION_COOKIE_NAME: str = "sessionid"
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "lax"
    SESSION_EXPIRE_SECONDS: int = 1209600  # 2 weeks

    # Password Hashing
    PASSWORD_BCRYPT_ROUNDS: int = 12

    # Token Management
    TOKEN_BLACKLIST_MAX_SIZE: int = 10000

    # OAuth2
    OAUTH2_ENABLED: bool = False
    OAUTH2_AUTHORIZATION_ENDPOINT: str = "/oauth2/authorize"
    OAUTH2_TOKEN_ENDPOINT: str = "/oauth2/token"
    OAUTH2_REVOKE_ENDPOINT: str = "/oauth2/revoke"

    # SSO Providers
    SSO_GOOGLE_CLIENT_ID: str | None = None
    SSO_GOOGLE_CLIENT_SECRET: str | None = None
    SSO_GITHUB_CLIENT_ID: str | None = None
    SSO_GITHUB_CLIENT_SECRET: str | None = None
    SSO_AZURE_TENANT_ID: str | None = None
    SSO_AZURE_CLIENT_ID: str | None = None
    SSO_AZURE_CLIENT_SECRET: str | None = None

    # Keycloak
    KEYCLOAK_ENABLED: bool = False
    KEYCLOAK_SERVER_URL: str | None = None
    KEYCLOAK_REALM: str | None = None
    KEYCLOAK_CLIENT_ID: str | None = None
    KEYCLOAK_CLIENT_SECRET: str | None = None
    KEYCLOAK_ADMIN_USERNAME: str | None = None
    KEYCLOAK_ADMIN_PASSWORD: str | None = None

    # WebAuthn
    WEBAUTHN_ENABLED: bool = False
    WEBAUTHN_RP_NAME: str = "Zephyr"
    WEBAUTHN_RP_ID: str | None = None
    WEBAUTHN_ORIGIN: str | None = None

    # MFA
    MFA_ENABLED: bool = False
    MFA_TOTP_ISSUER: str = "Zephyr"
    MFA_SMS_PROVIDER: str | None = None
    MFA_EMAIL_PROVIDER: str | None = None

    # User Federation
    FEDERATION_ENABLED: bool = False
    LDAP_SERVER: str | None = None
    LDAP_PORT: int = 389
    LDAP_USE_SSL: bool = False
    LDAP_BIND_DN: str | None = None
    LDAP_BIND_PASSWORD: str | None = None
    LDAP_USER_SEARCH_BASE: str | None = None
    LDAP_USER_SEARCH_FILTER: str = "(uid={username})"
    LDAP_GROUP_SEARCH_BASE: str | None = None
    LDAP_GROUP_SEARCH_FILTER: str = "(member={user_dn})"

    # RBAC
    RBAC_ENABLED: bool = True
    RBAC_DEFAULT_ROLE: str = "user"

    # UMA
    UMA_ENABLED: bool = False
    UMA_RESOURCE_SERVER: str | None = None
    UMA_AUTHORIZATION_SERVER: str | None = None

    # Sessions
    SESSION_BACKEND: str = "memory"
    SESSION_COOKIE_NAME: str = "sessionid"
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "lax"
    SESSION_EXPIRE_SECONDS: int = 1209600  # 2 weeks

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

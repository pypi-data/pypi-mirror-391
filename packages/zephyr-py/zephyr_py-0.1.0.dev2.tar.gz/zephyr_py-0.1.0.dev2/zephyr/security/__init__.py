"""
Zephyr Security Module

Comprehensive authentication and authorization system for Zephyr applications.
"""

from .jwt import JWTManager, JWTConfig, JWTPayload
from .password import PasswordHasher
from .tokens import TokenManager, TokenBlacklist
from .user import User, AnonymousUser
from .backends import AuthenticationBackend, JWTAuthenticationBackend
from .middleware import BearerAuthMiddleware
from .oauth2 import OAuth2Server, OAuth2Config
from .sso import SSOManager, SSOConfig
from .rbac import RBACManager, RBACConfig

__all__ = [
    # JWT
    "JWTManager",
    "JWTConfig",
    "JWTPayload",
    # Password
    "PasswordHasher",
    # Tokens
    "TokenManager",
    "TokenBlacklist",
    # User
    "User",
    "AnonymousUser",
    # Backends
    "AuthenticationBackend",
    "JWTAuthenticationBackend",
    # Middleware
    "BearerAuthMiddleware",
    # OAuth2
    "OAuth2Server",
    "OAuth2Config",
    # SSO
    "SSOManager",
    "SSOConfig",
    # RBAC
    "RBACManager",
    "RBACConfig",
]

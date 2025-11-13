"""
Role-Based Access Control (RBAC) system for Zephyr.

Provides comprehensive RBAC functionality including roles, permissions,
policy engine, and access control mechanisms.
"""

from .models import Role, Permission, Policy, Resource, Action, Effect, PolicyRule, AccessDecision, AccessContext
from .engine import PolicyEngine, RBACEngine, AccessControlEngine
from .exceptions import (
    RBACError,
    RoleNotFoundError,
    PermissionNotFoundError,
    PolicyNotFoundError,
    AccessDeniedError,
    InvalidPolicyError,
    InvalidRoleError,
    InvalidPermissionError,
    PolicyEvaluationError,
    AccessControlError,
)
from .manager import RBACManager
from .config import RBACConfig

__all__ = [
    # Models
    "Role",
    "Permission",
    "Policy",
    "Resource",
    "Action",
    "Effect",
    "PolicyRule",
    "AccessDecision",
    "AccessContext",
    # Engines
    "PolicyEngine",
    "RBACEngine",
    "AccessControlEngine",
    # Exceptions
    "RBACError",
    "RoleNotFoundError",
    "PermissionNotFoundError",
    "PolicyNotFoundError",
    "AccessDeniedError",
    "InvalidPolicyError",
    "InvalidRoleError",
    "InvalidPermissionError",
    "PolicyEvaluationError",
    "AccessControlError",
    # Manager
    "RBACManager",
    # Config
    "RBACConfig",
]

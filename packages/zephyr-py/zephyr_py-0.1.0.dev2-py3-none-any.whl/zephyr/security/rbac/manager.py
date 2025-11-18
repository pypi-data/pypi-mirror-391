"""
RBAC manager for centralized access control.

Provides high-level RBAC management including role assignment, permission checking, and policy management.
"""

import logging
from typing import Any, Dict, List, Optional, Set

from .engine import AccessControlEngine
from .exceptions import (
    AccessDeniedError,
    RoleNotFoundError,
    PolicyNotFoundError,
    RBACError,
)
from .models import (
    AccessContext,
    AccessDecision,
    Effect,
    Policy,
    PolicyRule,
    Role,
)


class RBACManager:
    """
    RBAC manager for centralized access control.

    Provides high-level RBAC management including role assignment,
    permission checking, and policy management.
    """

    def __init__(self) -> None:
        """Initialize RBAC manager."""
        self.engine = AccessControlEngine()
        self.logger = logging.getLogger(__name__)

        # Initialize with default system roles and policies
        self._initialize_defaults()

    def _initialize_defaults(self) -> None:
        """Initialize default system roles and policies."""
        # Create default roles
        admin_role = Role(
            name="admin", description="Administrator role with full access", permissions=["*"], is_system=True
        )

        user_role = Role(
            name="user",
            description="Standard user role",
            permissions=["read:profile", "update:profile"],
            is_system=True,
        )

        self.add_role(admin_role)
        self.add_role(user_role)

        # Create default policies
        default_policy = Policy(name="default", description="Default access policy", is_system=True)

        # Allow all for admin role
        admin_rule = PolicyRule(effect=Effect.ALLOW, subjects=["admin"], resources=["*"], actions=["*"], priority=100)
        default_policy.add_rule(admin_rule)

        # Allow read for user role
        user_rule = PolicyRule(
            effect=Effect.ALLOW, subjects=["user"], resources=["profile", "public/*"], actions=["read"], priority=50
        )
        default_policy.add_rule(user_rule)

        # Deny all other access
        deny_rule = PolicyRule(effect=Effect.DENY, subjects=["*"], resources=["*"], actions=["*"], priority=0)
        default_policy.add_rule(deny_rule)

        self.add_policy(default_policy)

    # Role Management

    def add_role(self, role: Role) -> None:
        """Add role to RBAC system."""
        self.engine.add_role(role)
        self.logger.info(f"Added role: {role.name}")

    def remove_role(self, role_name: str) -> bool:
        """Remove role from RBAC system."""
        success = self.engine.rbac_engine.remove_role(role_name)
        if success:
            self.logger.info(f"Removed role: {role_name}")
        return success

    def get_role(self, role_name: str) -> Optional[Role]:
        """Get role by name."""
        return self.engine.rbac_engine.get_role(role_name)

    def list_roles(self) -> List[Role]:
        """List all roles."""
        return list(self.engine.rbac_engine.roles.values())

    def assign_role(self, user_id: str, role_name: str) -> None:
        """Assign role to user."""
        if not self.engine.rbac_engine.get_role(role_name):
            raise RoleNotFoundError(role_name)

        self.engine.assign_role(user_id, role_name)
        self.logger.info(f"Assigned role '{role_name}' to user '{user_id}'")

    def revoke_role(self, user_id: str, role_name: str) -> None:
        """Revoke role from user."""
        self.engine.revoke_role(user_id, role_name)
        self.logger.info(f"Revoked role '{role_name}' from user '{user_id}'")

    def get_user_roles(self, user_id: str) -> Set[str]:
        """Get user roles."""
        return self.engine.get_user_roles(user_id)

    def has_role(self, user_id: str, role_name: str) -> bool:
        """Check if user has role."""
        return self.engine.rbac_engine.has_role(user_id, role_name)

    # Permission Management

    def has_permission(self, user_id: str, permission: str) -> bool:
        """Check if user has permission."""
        return self.engine.rbac_engine.has_permission(user_id, permission)

    def get_user_permissions(self, user_id: str) -> Set[str]:
        """Get user permissions."""
        return self.engine.get_user_permissions(user_id)

    def check_permission(self, user_id: str, resource: str, action: str) -> bool:
        """Check if user can perform action on resource."""
        return self.engine.is_allowed(user_id, resource, action)

    # Policy Management

    def add_policy(self, policy: Policy) -> None:
        """Add policy to RBAC system."""
        self.engine.add_policy(policy)
        self.logger.info(f"Added policy: {policy.name}")

    def remove_policy(self, policy_name: str) -> bool:
        """Remove policy from RBAC system."""
        success = self.engine.policy_engine.remove_policy(policy_name)
        if success:
            self.logger.info(f"Removed policy: {policy_name}")
        return success

    def get_policy(self, policy_name: str) -> Optional[Policy]:
        """Get policy by name."""
        return self.engine.policy_engine.get_policy(policy_name)

    def list_policies(self) -> List[Policy]:
        """List all policies."""
        return list(self.engine.policy_engine.policies.values())

    def add_policy_rule(self, policy_name: str, rule: PolicyRule) -> None:
        """Add rule to policy."""
        policy = self.get_policy(policy_name)
        if not policy:
            raise PolicyNotFoundError(policy_name)

        policy.add_rule(rule)
        self.logger.info(f"Added rule to policy '{policy_name}': {rule.id}")

    def remove_policy_rule(self, policy_name: str, rule_id: str) -> bool:
        """Remove rule from policy."""
        policy = self.get_policy(policy_name)
        if not policy:
            raise PolicyNotFoundError(policy_name)

        success = policy.remove_rule(rule_id)
        if success:
            self.logger.info(f"Removed rule '{rule_id}' from policy '{policy_name}'")
        return success

    # Access Control

    def check_access(self, context: AccessContext) -> AccessDecision:
        """Check access for given context."""
        return self.engine.check_access(context)

    def is_allowed(self, user_id: str, resource: str, action: str, **kwargs: Any) -> bool:
        """Check if user is allowed to perform action on resource."""
        return self.engine.is_allowed(user_id, resource, action, **kwargs)

    def require_access(self, user_id: str, resource: str, action: str, **kwargs: Any) -> None:
        """Require access, raise exception if denied."""
        if not self.is_allowed(user_id, resource, action, **kwargs):
            raise AccessDeniedError(
                f"Access denied for user '{user_id}' to '{resource}:{action}'",
                resource=resource,
                action=action,
                user_id=user_id,
            )

    # Utility Methods

    def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user information."""
        roles = self.get_user_roles(user_id)
        permissions = self.get_user_permissions(user_id)

        return {
            "user_id": user_id,
            "roles": list(roles),
            "permissions": list(permissions),
            "role_count": len(roles),
            "permission_count": len(permissions),
        }

    def get_role_info(self, role_name: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive role information."""
        role = self.get_role(role_name)
        if not role:
            return None

        # Count users with this role
        user_count = sum(1 for roles in self.engine.rbac_engine.user_roles.values() if role_name in roles)

        return {
            "name": role.name,
            "description": role.description,
            "permissions": role.permissions,
            "parent_roles": role.parent_roles,
            "child_roles": role.child_roles,
            "is_system": role.is_system,
            "is_active": role.is_active,
            "max_users": role.max_users,
            "user_count": user_count,
            "created_at": role.created_at.isoformat(),
            "updated_at": role.updated_at.isoformat(),
        }

    def get_policy_info(self, policy_name: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive policy information."""
        policy = self.get_policy(policy_name)
        if not policy:
            return None

        active_rules = policy.get_active_rules()

        return {
            "name": policy.name,
            "description": policy.description,
            "version": policy.version,
            "rule_count": len(policy.rules),
            "active_rule_count": len(active_rules),
            "is_system": policy.is_system,
            "is_active": policy.is_active,
            "created_at": policy.created_at.isoformat(),
            "updated_at": policy.updated_at.isoformat(),
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get RBAC system statistics."""
        return {
            "roles": {
                "total": len(self.engine.rbac_engine.roles),
                "system": sum(1 for role in self.engine.rbac_engine.roles.values() if role.is_system),
                "active": sum(1 for role in self.engine.rbac_engine.roles.values() if role.is_active),
            },
            "policies": {
                "total": len(self.engine.policy_engine.policies),
                "system": sum(1 for policy in self.engine.policy_engine.policies.values() if policy.is_system),
                "active": sum(1 for policy in self.engine.policy_engine.policies.values() if policy.is_active),
            },
            "users": {
                "total": len(self.engine.rbac_engine.user_roles),
                "with_roles": sum(1 for roles in self.engine.rbac_engine.user_roles.values() if roles),
            },
        }

    def validate_role_hierarchy(self, role_name: str) -> List[str]:
        """Validate role hierarchy for circular dependencies."""
        visited = set()
        path = []
        circular_deps = []

        def check_role(role: str) -> None:
            if role in path:
                circular_deps.append(" -> ".join(path[path.index(role) :] + [role]))
                return

            if role in visited:
                return

            visited.add(role)
            path.append(role)

            role_obj = self.get_role(role)
            if role_obj:
                for parent in role_obj.parent_roles:
                    check_role(parent)

            path.pop()

        check_role(role_name)
        return circular_deps

    def cleanup_inactive_roles(self) -> int:
        """Clean up inactive roles."""
        inactive_roles = [
            name for name, role in self.engine.rbac_engine.roles.items() if not role.is_active and not role.is_system
        ]

        for role_name in inactive_roles:
            self.remove_role(role_name)

        return len(inactive_roles)

    def cleanup_inactive_policies(self) -> int:
        """Clean up inactive policies."""
        inactive_policies = [
            name
            for name, policy in self.engine.policy_engine.policies.items()
            if not policy.is_active and not policy.is_system
        ]

        for policy_name in inactive_policies:
            self.remove_policy(policy_name)

        return len(inactive_policies)

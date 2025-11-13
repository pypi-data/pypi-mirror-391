"""
RBAC data models.

Defines all RBAC-related data models including roles, permissions, policies, and access decisions.
"""

import secrets
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field, validator


class Effect(str, Enum):
    """Access control effect."""

    ALLOW = "allow"
    DENY = "deny"


class Action(BaseModel):
    """Action model for RBAC."""

    name: str = Field(..., description="Action name")
    description: str = Field(default="", description="Action description")
    resource_type: str = Field(default="*", description="Resource type this action applies to")
    is_system: bool = Field(default=False, description="Whether this is a system action")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @validator("name")
    def validate_name(cls, v: str) -> str:
        """Validate action name."""
        if not v or not v.strip():
            raise ValueError("Action name cannot be empty")
        return v.strip().lower()

    def __str__(self) -> str:
        """String representation."""
        return self.name

    def __hash__(self) -> int:
        """Hash for use in sets."""
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        """Equality comparison."""
        if not isinstance(other, Action):
            return False
        return self.name == other.name


class Resource(BaseModel):
    """Resource model for RBAC."""

    name: str = Field(..., description="Resource name")
    resource_type: str = Field(..., description="Resource type")
    description: str = Field(default="", description="Resource description")
    owner_id: Optional[str] = Field(default=None, description="Resource owner ID")
    parent_resource: Optional[str] = Field(default=None, description="Parent resource name")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Resource attributes")
    is_system: bool = Field(default=False, description="Whether this is a system resource")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @validator("name")
    def validate_name(cls, v: str) -> str:
        """Validate resource name."""
        if not v or not v.strip():
            raise ValueError("Resource name cannot be empty")
        return v.strip()

    def get_resource_path(self) -> str:
        """Get full resource path including parent."""
        if self.parent_resource:
            return f"{self.parent_resource}/{self.name}"
        return self.name

    def __str__(self) -> str:
        """String representation."""
        return self.get_resource_path()

    def __hash__(self) -> int:
        """Hash for use in sets."""
        return hash(self.get_resource_path())

    def __eq__(self, other: object) -> bool:
        """Equality comparison."""
        if not isinstance(other, Resource):
            return False
        return self.get_resource_path() == other.get_resource_path()


class Permission(BaseModel):
    """Permission model for RBAC."""

    name: str = Field(..., description="Permission name")
    description: str = Field(default="", description="Permission description")
    resource: str = Field(..., description="Resource this permission applies to")
    actions: List[str] = Field(..., description="Actions this permission allows")
    conditions: List[str] = Field(default_factory=list, description="Permission conditions")
    is_system: bool = Field(default=False, description="Whether this is a system permission")
    is_active: bool = Field(default=True, description="Whether permission is active")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @validator("name")
    def validate_name(cls, v: str) -> str:
        """Validate permission name."""
        if not v or not v.strip():
            raise ValueError("Permission name cannot be empty")
        return v.strip().lower()

    @validator("actions")
    def validate_actions(cls, v: List[str]) -> List[str]:
        """Validate actions."""
        if not v:
            raise ValueError("At least one action must be specified")
        return [action.strip().lower() for action in v if action.strip()]

    def has_action(self, action: str) -> bool:
        """Check if permission includes specific action."""
        return action.lower() in self.actions

    def matches_resource(self, resource: str) -> bool:
        """Check if permission matches resource (supports wildcards)."""
        if self.resource == "*":
            return True
        if self.resource == resource:
            return True
        if self.resource.endswith("*"):
            prefix = self.resource[:-1]
            return resource.startswith(prefix)
        return False

    def __str__(self) -> str:
        """String representation."""
        return f"{self.name}({self.resource}:{','.join(self.actions)})"

    def __hash__(self) -> int:
        """Hash for use in sets."""
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        """Equality comparison."""
        if not isinstance(other, Permission):
            return False
        return self.name == other.name


class Role(BaseModel):
    """Role model for RBAC."""

    name: str = Field(..., description="Role name")
    description: str = Field(default="", description="Role description")
    permissions: List[str] = Field(default_factory=list, description="Role permissions")
    parent_roles: List[str] = Field(default_factory=list, description="Parent roles")
    child_roles: List[str] = Field(default_factory=list, description="Child roles")
    is_system: bool = Field(default=False, description="Whether this is a system role")
    is_active: bool = Field(default=True, description="Whether role is active")
    max_users: Optional[int] = Field(default=None, description="Maximum number of users")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @validator("name")
    def validate_name(cls, v: str) -> str:
        """Validate role name."""
        if not v or not v.strip():
            raise ValueError("Role name cannot be empty")
        return v.strip().lower()

    def has_permission(self, permission: str) -> bool:
        """Check if role has specific permission."""
        return permission.lower() in self.permissions

    def add_permission(self, permission: str) -> None:
        """Add permission to role."""
        perm = permission.strip().lower()
        if perm and perm not in self.permissions:
            self.permissions.append(perm)
            self.updated_at = datetime.utcnow()

    def remove_permission(self, permission: str) -> None:
        """Remove permission from role."""
        perm = permission.strip().lower()
        if perm in self.permissions:
            self.permissions.remove(perm)
            self.updated_at = datetime.utcnow()

    def get_all_permissions(self, role_registry: Dict[str, "Role"]) -> Set[str]:
        """Get all permissions including inherited ones."""
        permissions = set(self.permissions)

        for parent_name in self.parent_roles:
            if parent_name in role_registry:
                parent_permissions = role_registry[parent_name].get_all_permissions(role_registry)
                permissions.update(parent_permissions)

        return permissions

    def __str__(self) -> str:
        """String representation."""
        return self.name

    def __hash__(self) -> int:
        """Hash for use in sets."""
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        """Equality comparison."""
        if not isinstance(other, Role):
            return False
        return self.name == other.name


class PolicyRule(BaseModel):
    """Policy rule model."""

    id: str = Field(default_factory=lambda: secrets.token_urlsafe(16), description="Rule ID")
    effect: Effect = Field(..., description="Rule effect")
    subjects: List[str] = Field(..., description="Subjects this rule applies to")
    resources: List[str] = Field(..., description="Resources this rule applies to")
    actions: List[str] = Field(..., description="Actions this rule applies to")
    conditions: List[str] = Field(default_factory=list, description="Rule conditions")
    priority: int = Field(default=0, description="Rule priority (higher = more important)")
    is_active: bool = Field(default=True, description="Whether rule is active")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    def matches_subject(self, subject: str) -> bool:
        """Check if rule matches subject."""
        if "*" in self.subjects:
            return True
        return subject in self.subjects

    def matches_resource(self, resource: str) -> bool:
        """Check if rule matches resource."""
        for rule_resource in self.resources:
            if rule_resource == "*":
                return True
            if rule_resource == resource:
                return True
            if rule_resource.endswith("*"):
                prefix = rule_resource[:-1]
                if resource.startswith(prefix):
                    return True
        return False

    def matches_action(self, action: str) -> bool:
        """Check if rule matches action."""
        if "*" in self.actions:
            return True
        return action.lower() in self.actions

    def __str__(self) -> str:
        """String representation."""
        return f"{self.effect.value}: {','.join(self.subjects)} -> {','.join(self.resources)}:{','.join(self.actions)}"


class Policy(BaseModel):
    """Policy model for RBAC."""

    name: str = Field(..., description="Policy name")
    description: str = Field(default="", description="Policy description")
    version: str = Field(default="1.0", description="Policy version")
    rules: List[PolicyRule] = Field(default_factory=list, description="Policy rules")
    is_system: bool = Field(default=False, description="Whether this is a system policy")
    is_active: bool = Field(default=True, description="Whether policy is active")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    def add_rule(self, rule: PolicyRule) -> None:
        """Add rule to policy."""
        self.rules.append(rule)
        self.updated_at = datetime.utcnow()

    def get_active_rules(self) -> List[PolicyRule]:
        """Get active rules sorted by priority."""
        active_rules = [rule for rule in self.rules if rule.is_active]
        return sorted(active_rules, key=lambda r: r.priority, reverse=True)

    def __str__(self) -> str:
        """String representation."""
        return f"{self.name} v{self.version}"


class AccessContext(BaseModel):
    """Access context for policy evaluation."""

    user_id: str = Field(..., description="User ID")
    user_roles: List[str] = Field(default_factory=list, description="User roles")
    user_attributes: Dict[str, Any] = Field(default_factory=dict, description="User attributes")
    resource: str = Field(..., description="Resource being accessed")
    action: str = Field(..., description="Action being performed")
    resource_attributes: Dict[str, Any] = Field(default_factory=dict, description="Resource attributes")
    environment: Dict[str, Any] = Field(default_factory=dict, description="Environment context")
    request_time: datetime = Field(default_factory=datetime.utcnow, description="Request timestamp")
    ip_address: Optional[str] = Field(default=None, description="Client IP address")
    user_agent: Optional[str] = Field(default=None, description="Client user agent")
    session_id: Optional[str] = Field(default=None, description="Session ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    def get_context_value(self, key: str) -> Any:
        """Get context value by key with dot notation support."""
        keys = key.split(".")
        value = self.dict()

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None

        return value


class AccessDecision(BaseModel):
    """Access decision model."""

    decision: Effect = Field(..., description="Access decision")
    context: AccessContext = Field(..., description="Access context")
    matched_rules: List[str] = Field(default_factory=list, description="Matched rule IDs")
    matched_policies: List[str] = Field(default_factory=list, description="Matched policy names")
    reason: str = Field(default="", description="Decision reason")
    confidence: float = Field(default=1.0, description="Decision confidence (0.0-1.0)")
    evaluation_time: float = Field(default=0.0, description="Evaluation time in seconds")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Decision timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    def is_allowed(self) -> bool:
        """Check if access is allowed."""
        return self.decision == Effect.ALLOW

    def is_denied(self) -> bool:
        """Check if access is denied."""
        return self.decision == Effect.DENY

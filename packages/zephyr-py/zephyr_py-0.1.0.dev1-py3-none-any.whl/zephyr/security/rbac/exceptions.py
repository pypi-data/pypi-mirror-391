"""
RBAC exceptions and error handling.

Defines all RBAC-specific exceptions with proper error codes and descriptions.
"""

from typing import Any, Dict, Optional


class RBACError(Exception):
    """Base RBAC error class."""

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        resource: str | None = None,
        action: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize RBAC error.

        Args:
            message: Error message
            error_code: Error code
            resource: Resource name
            action: Action name
            **kwargs: Additional error parameters
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.resource = resource
        self.action = action
        self.extra = kwargs

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for JSON response."""
        result = {"error": "rbac_error", "message": self.message}

        if self.error_code:
            result["error_code"] = self.error_code
        if self.resource:
            result["resource"] = self.resource
        if self.action:
            result["action"] = self.action

        result.update(self.extra)
        return result


class RoleNotFoundError(RBACError):
    """Role not found error."""

    def __init__(self, role_name: str, **kwargs: Any) -> None:
        super().__init__(
            message=f"Role '{role_name}' not found", error_code="role_not_found", resource=role_name, **kwargs
        )


class PermissionNotFoundError(RBACError):
    """Permission not found error."""

    def __init__(self, permission_name: str, **kwargs: Any) -> None:
        super().__init__(
            message=f"Permission '{permission_name}' not found",
            error_code="permission_not_found",
            resource=permission_name,
            **kwargs,
        )


class PolicyNotFoundError(RBACError):
    """Policy not found error."""

    def __init__(self, policy_name: str, **kwargs: Any) -> None:
        super().__init__(
            message=f"Policy '{policy_name}' not found", error_code="policy_not_found", resource=policy_name, **kwargs
        )


class AccessDeniedError(RBACError):
    """Access denied error."""

    def __init__(
        self,
        message: str = "Access denied",
        resource: str | None = None,
        action: str | None = None,
        user_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            message=message, error_code="access_denied", resource=resource, action=action, user_id=user_id, **kwargs
        )


class InvalidPolicyError(RBACError):
    """Invalid policy error."""

    def __init__(self, message: str, policy_name: str | None = None, **kwargs: Any) -> None:
        super().__init__(message=message, error_code="invalid_policy", resource=policy_name, **kwargs)


class InvalidRoleError(RBACError):
    """Invalid role error."""

    def __init__(self, message: str, role_name: str | None = None, **kwargs: Any) -> None:
        super().__init__(message=message, error_code="invalid_role", resource=role_name, **kwargs)


class InvalidPermissionError(RBACError):
    """Invalid permission error."""

    def __init__(self, message: str, permission_name: str | None = None, **kwargs: Any) -> None:
        super().__init__(message=message, error_code="invalid_permission", resource=permission_name, **kwargs)


class PolicyEvaluationError(RBACError):
    """Policy evaluation error."""

    def __init__(
        self, message: str, policy_name: str | None = None, condition: str | None = None, **kwargs: Any
    ) -> None:
        super().__init__(message=message, error_code="policy_evaluation_error", resource=policy_name, **kwargs)


class AccessControlError(RBACError):
    """Access control error."""

    def __init__(self, message: str, resource: str | None = None, action: str | None = None, **kwargs: Any) -> None:
        super().__init__(message=message, error_code="access_control_error", resource=resource, action=action, **kwargs)


class CircularDependencyError(RBACError):
    """Circular dependency error."""

    def __init__(self, message: str, dependency_chain: list[str] | None = None, **kwargs: Any) -> None:
        super().__init__(message=message, error_code="circular_dependency", dependency_chain=dependency_chain, **kwargs)


class InvalidResourceError(RBACError):
    """Invalid resource error."""

    def __init__(self, message: str, resource_name: str | None = None, **kwargs: Any) -> None:
        super().__init__(message=message, error_code="invalid_resource", resource=resource_name, **kwargs)


class InvalidActionError(RBACError):
    """Invalid action error."""

    def __init__(self, message: str, action_name: str | None = None, **kwargs: Any) -> None:
        super().__init__(message=message, error_code="invalid_action", action=action_name, **kwargs)


class PolicyConflictError(RBACError):
    """Policy conflict error."""

    def __init__(self, message: str, conflicting_policies: list[str] | None = None, **kwargs: Any) -> None:
        super().__init__(
            message=message, error_code="policy_conflict", conflicting_policies=conflicting_policies, **kwargs
        )


class RoleHierarchyError(RBACError):
    """Role hierarchy error."""

    def __init__(
        self, message: str, parent_role: str | None = None, child_role: str | None = None, **kwargs: Any
    ) -> None:
        super().__init__(
            message=message, error_code="role_hierarchy_error", parent_role=parent_role, child_role=child_role, **kwargs
        )


class PermissionAssignmentError(RBACError):
    """Permission assignment error."""

    def __init__(
        self, message: str, role_name: str | None = None, permission_name: str | None = None, **kwargs: Any
    ) -> None:
        super().__init__(
            message=message,
            error_code="permission_assignment_error",
            resource=role_name,
            action=permission_name,
            **kwargs,
        )


class PolicyRuleError(RBACError):
    """Policy rule error."""

    def __init__(self, message: str, rule_id: str | None = None, **kwargs: Any) -> None:
        super().__init__(message=message, error_code="policy_rule_error", rule_id=rule_id, **kwargs)


class ConditionEvaluationError(RBACError):
    """Condition evaluation error."""

    def __init__(self, message: str, condition: str | None = None, **kwargs: Any) -> None:
        super().__init__(message=message, error_code="condition_evaluation_error", condition=condition, **kwargs)


class AccessDecisionError(RBACError):
    """Access decision error."""

    def __init__(self, message: str, decision: str | None = None, **kwargs: Any) -> None:
        super().__init__(message=message, error_code="access_decision_error", decision=decision, **kwargs)


class RBACConfigurationError(RBACError):
    """RBAC configuration error."""

    def __init__(self, message: str, config_key: str | None = None, **kwargs: Any) -> None:
        super().__init__(message=message, error_code="rbac_configuration_error", config_key=config_key, **kwargs)


class PolicyVersionError(RBACError):
    """Policy version error."""

    def __init__(self, message: str, policy_name: str | None = None, version: str | None = None, **kwargs: Any) -> None:
        super().__init__(
            message=message, error_code="policy_version_error", resource=policy_name, version=version, **kwargs
        )


class RoleAssignmentError(RBACError):
    """Role assignment error."""

    def __init__(self, message: str, user_id: str | None = None, role_name: str | None = None, **kwargs: Any) -> None:
        super().__init__(
            message=message, error_code="role_assignment_error", user_id=user_id, resource=role_name, **kwargs
        )


class PermissionInheritanceError(RBACError):
    """Permission inheritance error."""

    def __init__(
        self, message: str, parent_role: str | None = None, child_role: str | None = None, **kwargs: Any
    ) -> None:
        super().__init__(
            message=message,
            error_code="permission_inheritance_error",
            parent_role=parent_role,
            child_role=child_role,
            **kwargs,
        )


class PolicyCacheError(RBACError):
    """Policy cache error."""

    def __init__(self, message: str, cache_key: str | None = None, **kwargs: Any) -> None:
        super().__init__(message=message, error_code="policy_cache_error", cache_key=cache_key, **kwargs)


class AccessAuditError(RBACError):
    """Access audit error."""

    def __init__(self, message: str, audit_id: str | None = None, **kwargs: Any) -> None:
        super().__init__(message=message, error_code="access_audit_error", audit_id=audit_id, **kwargs)

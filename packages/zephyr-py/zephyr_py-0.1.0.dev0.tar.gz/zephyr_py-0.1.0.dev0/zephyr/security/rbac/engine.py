"""
RBAC policy engine implementation.

Provides policy evaluation, access control, and decision making functionality.
"""

import time
from typing import Any, Dict, List, Optional, Set

from .exceptions import (
    AccessControlError,
    PolicyEvaluationError,
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


class PolicyEngine:
    """Policy evaluation engine."""

    def __init__(self) -> None:
        """Initialize policy engine."""
        self.policies: Dict[str, Policy] = {}
        self.conditions: Dict[str, Any] = {}

    def add_policy(self, policy: Policy) -> None:
        """Add policy to engine."""
        self.policies[policy.name] = policy

    def remove_policy(self, policy_name: str) -> bool:
        """Remove policy from engine."""
        if policy_name in self.policies:
            del self.policies[policy_name]
            return True
        return False

    def get_policy(self, policy_name: str) -> Optional[Policy]:
        """Get policy by name."""
        return self.policies.get(policy_name)

    def evaluate_policy(self, policy: Policy, context: AccessContext) -> List[PolicyRule]:
        """Evaluate policy against context."""
        matched_rules = []

        for rule in policy.get_active_rules():
            if self._evaluate_rule(rule, context):
                matched_rules.append(rule)

        return matched_rules

    def _evaluate_rule(self, rule: PolicyRule, context: AccessContext) -> bool:
        """Evaluate individual rule against context."""
        # Check subject match
        if not self._matches_subject(rule, context):
            return False

        # Check resource match
        if not self._matches_resource(rule, context):
            return False

        # Check action match
        if not self._matches_action(rule, context):
            return False

        # Check conditions
        if not self._evaluate_conditions(rule, context):
            return False

        return True

    def _matches_subject(self, rule: PolicyRule, context: AccessContext) -> bool:
        """Check if rule matches subject."""
        # Check user ID
        if context.user_id in rule.subjects:
            return True

        # Check user roles
        for role in context.user_roles:
            if role in rule.subjects:
                return True

        # Check wildcard
        if "*" in rule.subjects:
            return True

        return False

    def _matches_resource(self, rule: PolicyRule, context: AccessContext) -> bool:
        """Check if rule matches resource."""
        return rule.matches_resource(context.resource)

    def _matches_action(self, rule: PolicyRule, context: AccessContext) -> bool:
        """Check if rule matches action."""
        return rule.matches_action(context.action)

    def _evaluate_conditions(self, rule: PolicyRule, context: AccessContext) -> bool:
        """Evaluate rule conditions."""
        if not rule.conditions:
            return True

        for condition_name in rule.conditions:
            if not self._evaluate_condition(condition_name, context):
                return False

        return True

    def _evaluate_condition(self, condition_name: str, context: AccessContext) -> bool:
        """Evaluate individual condition."""
        if condition_name not in self.conditions:
            return True  # Unknown conditions are treated as true

        condition = self.conditions[condition_name]

        try:
            # Simple condition evaluation
            # In a real implementation, this would use a proper expression evaluator
            if isinstance(condition, str):
                return self._evaluate_expression(condition, context)
            elif callable(condition):
                return condition(context)
            else:
                return bool(condition)
        except Exception as e:
            raise PolicyEvaluationError(
                f"Failed to evaluate condition '{condition_name}': {e}", condition=condition_name
            )

    def _evaluate_expression(self, expression: str, context: AccessContext) -> bool:
        """Evaluate condition expression."""
        # Simple expression evaluation
        # In a real implementation, this would use a proper expression parser

        # Replace context variables
        expr = expression
        for key, value in context.dict().items():
            if isinstance(value, (str, int, float, bool)):
                expr = expr.replace(f"${{{key}}}", str(value))

        # Simple boolean evaluation
        try:
            # This is a simplified evaluator - in production, use a proper expression parser
            return eval(expr, {"__builtins__": {}}, {})
        except Exception:
            return False


class RBACEngine:
    """Role-Based Access Control engine."""

    def __init__(self) -> None:
        """Initialize RBAC engine."""
        self.roles: Dict[str, Role] = {}
        self.permissions: Dict[str, Any] = {}
        self.user_roles: Dict[str, Set[str]] = {}

    def add_role(self, role: Role) -> None:
        """Add role to engine."""
        self.roles[role.name] = role

    def remove_role(self, role_name: str) -> bool:
        """Remove role from engine."""
        if role_name in self.roles:
            del self.roles[role_name]
            # Remove from user assignments
            for user_id, roles in self.user_roles.items():
                roles.discard(role_name)
            return True
        return False

    def get_role(self, role_name: str) -> Optional[Role]:
        """Get role by name."""
        return self.roles.get(role_name)

    def assign_role(self, user_id: str, role_name: str) -> None:
        """Assign role to user."""
        if role_name not in self.roles:
            raise RBACError(f"Role '{role_name}' not found")

        if user_id not in self.user_roles:
            self.user_roles[user_id] = set()

        self.user_roles[user_id].add(role_name)

    def revoke_role(self, user_id: str, role_name: str) -> None:
        """Revoke role from user."""
        if user_id in self.user_roles:
            self.user_roles[user_id].discard(role_name)

    def get_user_roles(self, user_id: str) -> Set[str]:
        """Get user roles."""
        return self.user_roles.get(user_id, set())

    def has_role(self, user_id: str, role_name: str) -> bool:
        """Check if user has role."""
        return role_name in self.get_user_roles(user_id)

    def has_permission(self, user_id: str, permission: str) -> bool:
        """Check if user has permission through roles."""
        user_roles = self.get_user_roles(user_id)

        for role_name in user_roles:
            if role_name in self.roles:
                role = self.roles[role_name]
                if role.has_permission(permission):
                    return True

        return False

    def get_user_permissions(self, user_id: str) -> Set[str]:
        """Get all user permissions through roles."""
        permissions = set()
        user_roles = self.get_user_roles(user_id)

        for role_name in user_roles:
            if role_name in self.roles:
                role = self.roles[role_name]
                permissions.update(role.get_all_permissions(self.roles))

        return permissions


class AccessControlEngine:
    """Main access control engine."""

    def __init__(self) -> None:
        """Initialize access control engine."""
        self.policy_engine = PolicyEngine()
        self.rbac_engine = RBACEngine()

    def add_policy(self, policy: Policy) -> None:
        """Add policy to engine."""
        self.policy_engine.add_policy(policy)

    def add_role(self, role: Role) -> None:
        """Add role to engine."""
        self.rbac_engine.add_role(role)

    def assign_role(self, user_id: str, role_name: str) -> None:
        """Assign role to user."""
        self.rbac_engine.assign_role(user_id, role_name)

    def revoke_role(self, user_id: str, role_name: str) -> None:
        """Revoke role from user."""
        self.rbac_engine.revoke_role(user_id, role_name)

    def check_access(self, context: AccessContext) -> AccessDecision:
        """Check access for given context."""
        start_time = time.time()

        try:
            # First check RBAC permissions
            if not self._check_rbac_access(context):
                return AccessDecision(
                    decision=Effect.DENY,
                    context=context,
                    reason="Insufficient permissions",
                    evaluation_time=time.time() - start_time,
                )

            # Then check policies
            policy_decision = self._check_policy_access(context)

            evaluation_time = time.time() - start_time

            return AccessDecision(
                decision=policy_decision.decision,
                context=context,
                matched_rules=policy_decision.matched_rules,
                matched_policies=policy_decision.matched_policies,
                reason=policy_decision.reason,
                confidence=policy_decision.confidence,
                evaluation_time=evaluation_time,
            )

        except Exception as e:
            return AccessDecision(
                decision=Effect.DENY,
                context=context,
                reason=f"Access control error: {e}",
                evaluation_time=time.time() - start_time,
            )

    def _check_rbac_access(self, context: AccessContext) -> bool:
        """Check RBAC access."""
        # Check if user has any of the required roles
        user_roles = self.rbac_engine.get_user_roles(context.user_id)

        # For now, allow access if user has any roles
        # In a real implementation, this would check specific permissions
        return len(user_roles) > 0

    def _check_policy_access(self, context: AccessContext) -> AccessDecision:
        """Check policy-based access."""
        matched_rules = []
        matched_policies = []

        # Evaluate all active policies
        for policy_name, policy in self.policy_engine.policies.items():
            if not policy.is_active:
                continue

            policy_rules = self.policy_engine.evaluate_policy(policy, context)
            if policy_rules:
                matched_rules.extend([rule.id for rule in policy_rules])
                matched_policies.append(policy_name)

        # Determine decision based on matched rules
        if not matched_rules:
            return AccessDecision(
                decision=Effect.DENY,
                context=context,
                matched_rules=matched_rules,
                matched_policies=matched_policies,
                reason="No matching policies found",
            )

        # Check if any rule denies access
        for policy_name in matched_policies:
            policy = self.policy_engine.get_policy(policy_name)
            if policy:
                for rule in policy.get_active_rules():
                    if rule.id in matched_rules and rule.effect == Effect.DENY:
                        return AccessDecision(
                            decision=Effect.DENY,
                            context=context,
                            matched_rules=matched_rules,
                            matched_policies=matched_policies,
                            reason=f"Denied by rule {rule.id}",
                        )

        # If no deny rules matched, allow access
        return AccessDecision(
            decision=Effect.ALLOW,
            context=context,
            matched_rules=matched_rules,
            matched_policies=matched_policies,
            reason="Access allowed by policy",
        )

    def is_allowed(self, user_id: str, resource: str, action: str, **kwargs: Any) -> bool:
        """Check if user is allowed to perform action on resource."""
        context = AccessContext(user_id=user_id, resource=resource, action=action, **kwargs)

        decision = self.check_access(context)
        return decision.is_allowed()

    def get_user_permissions(self, user_id: str) -> Set[str]:
        """Get user permissions."""
        return self.rbac_engine.get_user_permissions(user_id)

    def get_user_roles(self, user_id: str) -> Set[str]:
        """Get user roles."""
        return self.rbac_engine.get_user_roles(user_id)

# governance/services/policy_engine.py
import json
import hashlib
from typing import List

from governance.models import Policy
from governance.services.policy_types import PolicyContext, PolicyDecision


class PolicyEngine:
    """
    Deterministic, side-effect free policy evaluator
    """

    @staticmethod
    def evaluate(context: PolicyContext) -> PolicyDecision:
        """
        Evaluate policies for a given context.
        """

        policies = (
            Policy.objects
            .filter(is_active=True)
            .order_by("-version")
        )

        for policy in policies:
            for rule in policy.rules.all():
                if PolicyEngine._matches(rule.condition, context):
                    decision = rule.effect == "ALLOW"
                    decision_hash = PolicyEngine._hash_decision(
                        policy.code,
                        policy.version,
                        context,
                        decision
                    )

                    return PolicyDecision(
                        allowed=decision,
                        reason=f"Matched rule in policy {policy.code}",
                        policy_code=policy.code,
                        policy_version=policy.version,
                        decision_hash=decision_hash
                    )

        # Default deny
        decision_hash = PolicyEngine._hash_decision(
            "DEFAULT_DENY",
            0,
            context,
            False
        )

        return PolicyDecision(
            allowed=False,
            reason="No matching policy rule found",
            policy_code="DEFAULT_DENY",
            policy_version=0,
            decision_hash=decision_hash
        )

    @staticmethod
    def _matches(condition: dict, context: PolicyContext) -> bool:
        """
        Declarative matcher — no executable logic.
        """
        for key, expected in condition.items():
            actual = context.attributes.get(key)
            if actual != expected:
                return False
        return True

    @staticmethod
    def _hash_decision(
        policy_code: str,
        policy_version: int,
        context: PolicyContext,
        decision: bool
    ) -> str:
        payload = {
            "policy_code": policy_code,
            "policy_version": policy_version,
            "actor_id": context.actor_id,
            "action": context.action,
            "resource": context.resource,
            "attributes": context.attributes,
            "decision": decision,
        }

        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

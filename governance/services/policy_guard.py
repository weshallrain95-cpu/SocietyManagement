# governance/services/policy_guard.py

from governance.services.policy_engine import PolicyEngine
from governance.services.policy_types import PolicyContext
from governance.services.decision_recorder import PolicyDecisionRecorder


class PolicyDenied(Exception):
    """
    Raised when a policy denies an action.
    """
    pass


def enforce_policy(
    *,
    actor_id: str,
    action: str,
    resource: str,
    attributes: dict,
):
    """
    Enforce a governance policy.

    - Evaluates policy
    - Records decision
    - Raises PolicyDenied on DENY
    """

    context = PolicyContext(
        actor_id=actor_id,
        action=action,
        resource=resource,
        attributes=attributes,
    )

    decision = PolicyEngine.evaluate(context)

    # Always record the decision
    PolicyDecisionRecorder.record(decision, context)

    if not decision.allowed:
        raise PolicyDenied(
            f"Policy denied action={action} on resource={resource}: {decision.reason}"
        )

    return decision

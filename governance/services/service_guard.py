from governance.services.policy_guard import enforce_policy, PolicyDenied
from governance.services.control_plane import GovernanceControlService

class ServicePolicyDenied(Exception):
    """
    Raised when a service-level policy denies an operation.
    """
    pass


def enforce_service_policy(
    *,
    actor_id: str,
    action: str,
    resource: str,
    attributes: dict,
):
    """
    Enforce governance policy in internal services / async jobs.
    """

    try:
        return enforce_policy(
            actor_id=actor_id,
            action=action,
            resource=resource,
            attributes=attributes,
        )
    except PolicyDenied as e:
        raise ServicePolicyDenied(str(e))

# inside enforce_service_policy()

mode = GovernanceControlService.get_control().enforcement_mode

if final_effect == "DENY":
    if mode == "OBSERVE_ONLY":
        return  # log only
    elif mode == "PROGRESSIVE":
        raise ServicePolicyDenied(f"[SOFT] {explanation}")
    elif mode == "STRICT":
        raise ServicePolicyDenied(f"[HARD] {explanation}")
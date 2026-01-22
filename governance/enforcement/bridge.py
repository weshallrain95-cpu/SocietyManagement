from governance.simulation.context import SimulationContext
from governance.enforcement.enforcer import GovernanceEnforcer


def enforce_policy(
    *,
    actor,
    action,
    resource,
    role=None,
    attributes=None,
    observe_only=False,
):
    ctx = SimulationContext(
        actor=actor,
        action=action,
        resource=resource,
        role=role,
        attributes=attributes or {},
    )

    return GovernanceEnforcer.enforce(ctx, observe_only=observe_only)

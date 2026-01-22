from communications.domain.contracts.routing_rules import ROLE_ROUTING_MATRIX


class RoleRoutingEngine:
    """
    Platform-grade role communication routing engine
    """

    def is_allowed(self, sender_role, receiver_role, context=None):
        allowed_targets = ROLE_ROUTING_MATRIX.get(sender_role, [])
        return receiver_role in allowed_targets

    def filter_allowed(self, sender_role, participants, context=None):
        """
        Filters participant list based on role graph
        """
        allowed = []
        for p in participants:
            if self.is_allowed(sender_role, p.role, context):
                allowed.append(p)
        return allowed

from communications.domain.contracts.routing_rules import ROLE_ROUTING_MATRIX
from communications.domain.contracts.governance_overrides import GOVERNANCE_OVERRIDES


class RoleRoutingEngine:
    def is_allowed(self, sender_role, receiver_role, context=None):

        # Governance override
        override = GOVERNANCE_OVERRIDES.get((sender_role, receiver_role))
        if override == "allow":
            return True
        if override == "deny":
            return False
        if override == "allow_if_policy":
            # Policy Engine hook point
            return True

        allowed_targets = ROLE_ROUTING_MATRIX.get(sender_role, [])
        return receiver_role in allowed_targets

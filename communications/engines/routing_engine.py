class RoutingEngine:
    def resolve_recipients(self, sender, context):
        return []
class RoutingEngine:
    def resolve_recipients(self, sender, context):
        # Role-aware, policy-aware routing
        return []

from communications.engines.role_routing_engine import RoleRoutingEngine


class RoutingEngine:
    def __init__(self):
        self.role_router = RoleRoutingEngine()

    def resolve_recipients(self, sender, context):
        """
        Society-scoped + role-governed routing
        """
        participants = context.get("participants", [])

        allowed = self.role_router.filter_allowed(
            sender_role=sender.role,
            participants=participants,
            context=context
        )

        return allowed

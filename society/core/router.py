"""
SocietyOS Router System
Central execution routing layer (Governed)
"""

from typing import Callable, Dict, Any
from society.core.context import ExecutionContext
from society.core.events import EventBus, Event
from society.core.governance import GovernanceDecision


class Route:
    """
    Represents a routed execution target
    """

    def __init__(self, name: str, handler: Callable[..., Any], domain: str = "core"):
        self.name = name
        self.handler = handler
        self.domain = domain


class Router:
    """
    Central router for SocietyOS
    """

    def __init__(self, context: ExecutionContext, event_bus: EventBus):
        self.context = context
        self.event_bus = event_bus
        self.routes: Dict[str, Route] = {}

    # -------------------------
    # Registration
    # -------------------------

    def register(self, route_name: str, handler: Callable[..., Any], domain: str = "core"):
        self.routes[route_name] = Route(route_name, handler, domain)

        if self.context.debug:
            print(f"[ROUTER] Registered route: {route_name} ({domain})")

    # -------------------------
    # Route Execution (Governed)
    # -------------------------

    def route(self, route_name: str, payload: Dict[str, Any], source: str = "system") -> Any:
        route = self.routes.get(route_name)

        if not route:
            raise ValueError(f"Route not found: {route_name}")

        # Governance gate (entry)
        decision = self.context.system.governance.evaluate(
            self.context,
            f"route.execute:{route_name}",
            {
                "route": route_name,
                "domain": route.domain,
                "payload": payload,
            },
        )

        if not decision.allowed:
            raise PermissionError(
                f"Route '{route_name}' blocked by governance: {decision.reason}"
            )

        if self.context.debug:
            print(f"[ROUTER] Routing -> {route_name} ({route.domain})")

        # Execute handler (preserve **payload contract)
        result = route.handler(**payload)

        # Emit event after execution (preserved behavior)
        self.event_bus.publish(
            event_name=f"route.executed.{route_name}",
            payload={
                "route": route_name,
                "domain": route.domain,
                "payload": payload,
                "result": result,
            },
            source=source,
        )

        return result

    # -------------------------
    # Introspection
    # -------------------------

    def list_routes(self):
        return list(self.routes.keys())

"""
SocietyOS Router System
Central execution routing layer
"""

from typing import Callable, Dict, Any
from society.core.context import ExecutionContext
from society.core.events import EventBus, Event


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

    def register(self, route_name: str, handler: Callable[..., Any], domain: str = "core"):
        self.routes[route_name] = Route(route_name, handler, domain)

        if self.context.debug:
            print(f"[ROUTER] Registered route: {route_name} ({domain})")

    def route(self, route_name: str, payload: Dict[str, Any], source: str = "system") -> Any:
        route = self.routes.get(route_name)

        if not route:
            raise ValueError(f"Route not found: {route_name}")

        if self.context.debug:
            print(f"[ROUTER] Routing -> {route_name} ({route.domain})")

        # Governance / policy hooks (future)
        # Intelligence hooks (future)
        # Compliance hooks (future)

        result = route.handler(**payload)

        # Emit event after execution
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

    def list_routes(self):
        return list(self.routes.keys())


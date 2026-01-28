"""
SocietyOS Lifecycle Manager
Controls system startup, shutdown, reload, and health
"""

from typing import Dict, Any, List
from society.core.context import ExecutionContext
from society.core.runtime import RuntimeEngine
from society.core.events import EventBus
from society.core.state import StateEngine
from society.core.router import Router
from society.core.orchestrator import Orchestrator


class LifecycleManager:
    """
    System lifecycle controller
    """

    def __init__(
        self,
        context: ExecutionContext,
        runtime: RuntimeEngine,
        event_bus: EventBus,
        state_engine: StateEngine,
        router: Router,
        orchestrator: Orchestrator,
    ):
        self.context = context
        self.runtime = runtime
        self.event_bus = event_bus
        self.state_engine = state_engine
        self.router = router
        self.orchestrator = orchestrator

        self.components: List[str] = []
        self.health: Dict[str, bool] = {}
        self.started = False

    def register_component(self, name: str):
        self.components.append(name)
        self.health[name] = False

    def boot(self):
        if self.started:
            return

        print("[LIFECYCLE] Boot sequence started")

        # Initialize core context
        self.context.initialize()

        # Initialize runtime
        self.runtime.initialize()

        # Mark core components healthy
        self.health["context"] = True
        self.health["runtime"] = True
        self.health["event_bus"] = True
        self.health["state_engine"] = True
        self.health["router"] = True
        self.health["orchestrator"] = True

        self.event_bus.publish(
            "system.booted",
            {"environment": self.context.environment},
            source="lifecycle",
        )

        self.started = True
        print("[LIFECYCLE] System boot complete")

    def start(self):
        if not self.started:
            self.boot()

        print("[LIFECYCLE] System start")
        self.runtime.start()

    def shutdown(self):
        print("[LIFECYCLE] Shutdown initiated")

        self.runtime.stop()

        self.event_bus.publish(
            "system.shutdown",
            {"environment": self.context.environment},
            source="lifecycle",
        )

        print("[LIFECYCLE] System shutdown complete")

    def reload(self):
        print("[LIFECYCLE] Reload initiated")

        self.shutdown()
        self.boot()
        self.start()

    def status(self) -> Dict[str, Any]:
        return {
            "started": self.started,
            "environment": self.context.environment,
            "health": self.health,
            "runtime": self.runtime.status(),
        }


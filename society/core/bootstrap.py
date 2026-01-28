"""
SocietyOS System Bootstrap
Creates and wires the full runtime system
"""

from society.core.kernel import Kernel
from society.core.context import ExecutionContext
from society.core.runtime import RuntimeEngine
from society.core.events import EventBus
from society.core.state import StateEngine
from society.core.router import Router
from society.core.orchestrator import Orchestrator
from society.core.lifecycle import LifecycleManager


class SocietySystem:
    """
    Live SocietyOS system instance
    """

    def __init__(self):
        # Kernel
        self.kernel = Kernel()

        # Core context
        self.context: ExecutionContext = self.kernel.context

        # Core runtime
        self.runtime: RuntimeEngine = self.kernel.runtime

        # Subsystems
        self.event_bus = EventBus(self.context)
        self.state_engine = StateEngine(self.context)
        self.router = Router(self.context, self.event_bus)
        self.orchestrator = Orchestrator(self.context, self.state_engine, self.event_bus)

        # Lifecycle
        self.lifecycle = LifecycleManager(
            context=self.context,
            runtime=self.runtime,
            event_bus=self.event_bus,
            state_engine=self.state_engine,
            router=self.router,
            orchestrator=self.orchestrator,
        )

        self.initialized = False

    def boot(self):
        """
        Boot the full system
        """
        if self.initialized:
            return self

        # Boot kernel
        self.kernel.boot()

        # Boot lifecycle
        self.lifecycle.boot()

        self.initialized = True
        print("[SYSTEM] SocietyOS bootstrapped")

        return self

    def start(self):
        """
        Start runtime execution
        """
        if not self.initialized:
            self.boot()

        self.lifecycle.start()
        print("[SYSTEM] SocietyOS started")

    def shutdown(self):
        """
        Shutdown system
        """
        self.lifecycle.shutdown()
        print("[SYSTEM] SocietyOS shutdown")

    def status(self):
        """
        System status
        """
        return {
            "initialized": self.initialized,
            "lifecycle": self.lifecycle.status(),
            "runtime": self.runtime.status(),
            "environment": self.context.environment,
        }


def bootstrap_system() -> SocietySystem:
    """
    Factory function for SocietyOS system
    """
    system = SocietySystem()
    system.boot()
    return system


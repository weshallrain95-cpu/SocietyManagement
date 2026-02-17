"""
SocietyOS System Bootstrap
Creates and wires the full runtime system
"""

from society.core.kernel import Kernel
from society.core.context import ExecutionContext
from society.core.events import EventBus
from society.core.state import StateEngine
from society.core.router import Router
from society.core.orchestrator import Orchestrator
from society.core.lifecycle import LifecycleManager
from society.core.registry import SystemRegistry
from society.core.env import load_environment
from society.core.governance import GovernanceAuthority


class SocietySystem:
    """
    Live SocietyOS system instance
    """

    def __init__(self, kernel: Kernel, context: ExecutionContext):
        self.kernel = kernel
        self.context = context
        self.runtime = kernel.runtime

        # Registry
        self.registry = SystemRegistry()

        # Governance
        self.governance = GovernanceAuthority(mode="observe")

        # Core subsystems
        self.event_bus = EventBus(self.context)
        self.state_engine = StateEngine(self.context)
        self.router = Router(self.context, self.event_bus)
        self.orchestrator = Orchestrator(
            self.context, self.state_engine, self.event_bus
        )

        # Lifecycle
        self.lifecycle = LifecycleManager(
            context=self.context,
            runtime=self.runtime,
            event_bus=self.event_bus,
            state_engine=self.state_engine,
            router=self.router,
            orchestrator=self.orchestrator,
        )

        # Registry wiring
        self.registry.register("kernel", "core", self.kernel)
        self.registry.register("context", "core", self.context)
        self.registry.register("runtime", "core", self.runtime)
        self.registry.register("governance", "core", self.governance)
        self.registry.register("event_bus", "core", self.event_bus)
        self.registry.register("state_engine", "core", self.state_engine)
        self.registry.register("router", "core", self.router)
        self.registry.register("orchestrator", "core", self.orchestrator)
        self.registry.register("lifecycle", "core", self.lifecycle)

        self.initialized = False

    def boot(self):
        if self.initialized:
            return self

        self.kernel.boot()
        self.lifecycle.boot()

        self.initialized = True
        print("[SYSTEM] SocietyOS bootstrapped")
        return self

    def start(self):
        if not self.initialized:
            self.boot()

        self.lifecycle.start()
        print("[SYSTEM] SocietyOS started")

    def shutdown(self):
        self.lifecycle.shutdown()
        print("[SYSTEM] SocietyOS shutdown")

    def status(self):
        return {
            "initialized": self.initialized,
            "environment": self.context.environment,
            "lifecycle": self.lifecycle.status(),
            "runtime": self.runtime.status(),
            "registry": self.registry.stats(),
            "governance": self.governance.snapshot(),
        }


def bootstrap_system():
    """
    Bootstrap SocietyOS system
    """
    print("[SYSTEM] Bootstrapping SocietyOS")

    env = load_environment()

    context = ExecutionContext(environment=env.environment)
    kernel = Kernel(context)

    system = SocietySystem(kernel=kernel, context=context)

    # 🔑 Critical back-reference
    context.system = system
    system.env = env

    print("[SYSTEM] SocietyOS bootstrapped")
    return system

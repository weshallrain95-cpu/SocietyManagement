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
from society.core.registry import SystemRegistry
from society.core.env import load_environment


class SocietySystem:
    """
    Live SocietyOS system instance
    """

    def __init__(self, kernel: Kernel, context: ExecutionContext, runtime: RuntimeEngine):
        self.kernel = kernel
        self.context = context
        self.runtime = runtime

        # Kernel
        self.kernel = kernel

        # Core context
        self.context: ExecutionContext = self.kernel.context

        # Core runtime
        self.runtime: RuntimeEngine = self.kernel.runtime

                # Registry
        self.registry = SystemRegistry()

        # Subsystems
        self.event_bus = EventBus(self.context)
        self.state_engine = StateEngine(self.context)
        self.router = Router(self.context, self.event_bus)
        self.orchestrator = Orchestrator(self.context, self.state_engine, self.event_bus)

        # Register core components
        self.registry.register("kernel", "core", self.kernel)
        self.registry.register("context", "core", self.context)
        self.registry.register("runtime", "core", self.runtime)
        self.registry.register("event_bus", "core", self.event_bus)
        self.registry.register("state_engine", "core", self.state_engine)
        self.registry.register("router", "core", self.router)
        self.registry.register("orchestrator", "core", self.orchestrator)

        # Lifecycle
        self.lifecycle = LifecycleManager(
            context=self.context,
            runtime=self.runtime,
            event_bus=self.event_bus,
            state_engine=self.state_engine,
            router=self.router,
            orchestrator=self.orchestrator,
        )

        # Register lifecycle
        self.registry.register("lifecycle", "core", self.lifecycle)

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
            "environment": self.context.environment,
            "lifecycle": self.lifecycle.status(),
            "runtime": self.runtime.status(),
            "registry": self.registry.stats(),
        }

def bootstrap_system(environment: str = None):
    """
    Bootstrap SocietyOS system
    """
    print("[SYSTEM] Bootstrapping SocietyOS")

    # Load environment config
    env_config = load_environment()

    # Context
    context = ExecutionContext(environment=env_config.environment)

    # Kernel
    kernel = Kernel(context=context)

    # Runtime
    runtime = RuntimeEngine(context=context)

    # System
    system = SocietySystem(
        kernel=kernel,
        context=context,
        runtime=runtime,
    )

    # Bind environment config
    system.env = env_config

    print("[SYSTEM] SocietyOS bootstrapped")
    return system



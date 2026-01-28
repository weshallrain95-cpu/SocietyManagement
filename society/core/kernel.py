"""
SocietyOS Runtime Kernel
Core execution authority of the platform
"""

from typing import Dict, Any
from society.core.context import ExecutionContext
from society.core.runtime import RuntimeEngine


class Kernel:
    """
    Root execution kernel of SocietyOS
    """

    def __init__(self):
        self.context = ExecutionContext()
        self.runtime = RuntimeEngine(self.context)
        self.components: Dict[str, Any] = {}
        self.started = False

    def register_component(self, name: str, component: Any):
        self.components[name] = component

    def boot(self):
        if self.started:
            raise RuntimeError("Kernel already started")

        self.context.initialize()
        self.runtime.initialize()
        self.started = True
        print("[KERNEL] SocietyOS kernel booted")

    def shutdown(self):
        if not self.started:
            return
        self.runtime.shutdown()
        self.started = False
        print("[KERNEL] SocietyOS kernel shutdown")


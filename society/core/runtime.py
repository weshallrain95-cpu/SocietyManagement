"""
SocietyOS Runtime Engine
Controls execution loop, lifecycle, and system heartbeat (Governed)
"""

import time
from typing import Optional
from society.core.context import ExecutionContext
from society.core.governance import GovernanceDecision


class RuntimeEngine:
    """
    Core runtime engine of SocietyOS (Governed)
    """

    def __init__(self, context: ExecutionContext):
        self.context = context
        self.running = False
        self.start_time = None
        self.heartbeat_interval = 1.0  # seconds
        self.cycles = 0

    # -------------------------
    # Lifecycle
    # -------------------------

    def initialize(self):
        """
        Initialize runtime engine
        """
        self.start_time = time.time()
        self.context.set_flag("runtime_initialized", True)
        print("[RUNTIME] Runtime engine initialized")

    def start(self):
        """
        Start execution loop (Governed)
        """
        if self.running:
            return

        decision = self.context.system.governance.evaluate(
            self.context,
            "runtime.start",
            {
                "environment": self.context.environment,
                "heartbeat_interval": self.heartbeat_interval,
            },
        )

        if not decision.allowed:
            raise PermissionError(
                f"Runtime start blocked: {decision.reason}"
            )

        self.running = True
        self.context.set_flag("runtime_running", True)
        print("[RUNTIME] Runtime engine started")
        self._execution_loop()

    def stop(self):
        """
        Stop execution loop (Governed)
        """
        if not self.running:
            return

        decision = self.context.system.governance.evaluate(
            self.context,
            "runtime.stop",
            {
                "cycles": self.cycles,
                "uptime": self.uptime(),
            },
        )

        if not decision.allowed:
            raise PermissionError(
                f"Runtime stop blocked: {decision.reason}"
            )

        self.running = False
        self.context.set_flag("runtime_running", False)
        print("[RUNTIME] Runtime engine stopped")

    def shutdown(self):
        """
        Shutdown runtime engine
        """
        self.stop()
        print("[RUNTIME] Runtime engine shutdown complete")

    # -------------------------
    # Execution Loop
    # -------------------------

    def _execution_loop(self):
        """
        Core execution loop
        """
        while self.running:
            try:
                self.tick()
            except PermissionError as pe:
                print(f"[RUNTIME] Tick blocked by governance: {pe}")
                self.running = False
                self.context.set_flag("runtime_running", False)
                break

            time.sleep(self.heartbeat_interval)

    def tick(self):
        """
        Single runtime cycle (Governed)
        """
        decision = self.context.system.governance.evaluate(
            self.context,
            "runtime.tick",
            {
                "cycle": self.cycles + 1,
                "uptime": self.uptime(),
                "environment": self.context.environment,
            },
        )

        if not decision.allowed:
            raise PermissionError(decision.reason)

        self.cycles += 1
        self.context.set("last_tick", time.time())

        if self.context.debug:
            print(f"[RUNTIME] Tick {self.cycles}")

        # Future hooks:
        # - event bus tick
        # - orchestration tick
        # - workflow tick
        # - state engine tick
        # - intelligence cycle

    # -------------------------
    # Status
    # -------------------------

    def uptime(self) -> Optional[float]:
        if not self.start_time:
            return None
        return time.time() - self.start_time

    def status(self) -> dict:
        """
        Runtime status snapshot
        """
        return {
            "running": self.running,
            "cycles": self.cycles,
            "uptime": self.uptime(),
            "heartbeat_interval": self.heartbeat_interval,
            "environment": self.context.environment,
        }

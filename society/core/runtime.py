"""
SocietyOS Runtime Engine
Controls execution loop, lifecycle, and system heartbeat
"""

import time
from typing import Optional
from society.core.context import ExecutionContext


class RuntimeEngine:
    """
    Core runtime engine of SocietyOS
    """

    def __init__(self, context: ExecutionContext):
        self.context = context
        self.running = False
        self.start_time = None
        self.heartbeat_interval = 1.0  # seconds
        self.cycles = 0

    def initialize(self):
        """
        Initialize runtime engine
        """
        self.start_time = time.time()
        self.context.set_flag("runtime_initialized", True)
        print("[RUNTIME] Runtime engine initialized")

    def start(self):
        """
        Start execution loop
        """
        if self.running:
            return

        self.running = True
        self.context.set_flag("runtime_running", True)
        print("[RUNTIME] Runtime engine started")
        self._execution_loop()

    def _execution_loop(self):
        """
        Core execution loop
        """
        while self.running:
            self.tick()
            time.sleep(self.heartbeat_interval)

    def tick(self):
        """
        Single runtime cycle
        """
        self.cycles += 1
        self.context.set("last_tick", time.time())

        if self.context.debug:
            print(f"[RUNTIME] Tick {self.cycles}")

        # Future hooks:
        # - event bus tick
        # - orchestration tick
        # - workflow tick
        # - state engine tick
        # - governance checks
        # - intelligence cycle

    def stop(self):
        """
        Stop execution loop
        """
        if not self.running:
            return

        self.running = False
        self.context.set_flag("runtime_running", False)
        print("[RUNTIME] Runtime engine stopped")

    def shutdown(self):
        """
        Shutdown runtime engine
        """
        self.stop()
        print("[RUNTIME] Runtime engine shutdown complete")

    def status(self) -> dict:
        """
        Runtime status snapshot
        """
        return {
            "running": self.running,
            "cycles": self.cycles,
            "uptime": None if not self.start_time else time.time() - self.start_time,
            "heartbeat_interval": self.heartbeat_interval,
            "environment": self.context.environment,
        }


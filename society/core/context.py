"""
Execution Context System
Carries environment, governance, compliance, and execution metadata
"""

import uuid
import os
from datetime import datetime
from typing import Dict, Any

import uuid
from datetime import datetime

class ExecutionContext:
    """
    Global execution context for SocietyOS runtime
    """

    def __init__(self, environment: str = "local"):
        self.environment = environment
        self.context_id = str(uuid.uuid4())
        self.start_time = datetime.utcnow()

        # Debug / diagnostics
        self.debug = False
        # Lifecycle state
        self.initialized = False

        # Runtime flags
        self.flags = {}

        # Shared runtime state (used by RuntimeEngine)
        self.state = {}
        # Back-reference to running system (governance/control)
        self.system = None




    def initialize(self):
        # Keep this lightweight — lifecycle depends on it
        print("[CONTEXT] Execution context initialized")

        # Environment
        self.environment = os.getenv("ENVIRONMENT", "local")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")

        # Governance / Compliance
        self.governance_mode = os.getenv("GOVERNANCE_MODE", "observe")
        self.compliance_mode = os.getenv("COMPLIANCE_MODE", "standard")
        self.security_mode = os.getenv("SECURITY_MODE", "standard")

        # Intelligence
        self.intelligence_mode = os.getenv("INTELLIGENCE_MODE", "simulation")
        self.ai_enabled = os.getenv("AI_ENABLED", "false").lower() == "true"

        # Runtime state
        self.state: Dict[str, Any] = {}
        self.flags: Dict[str, bool] = {}

        # Execution metadata
        self.execution_id = None
        self.trace_id = None

        # System identity
        self.system_name = "SocietyOS"
        self.system_version = "0.0.1"

        self.initialized = False

    def initialize(self):
        if self.initialized:
            return

        self.execution_id = str(uuid.uuid4())
        self.trace_id = str(uuid.uuid4())
        self.flags["booted"] = True
        self.initialized = True

    def set(self, key: str, value: Any):
        self.state[key] = value

    def get(self, key: str, default=None):
        return self.state.get(key, default)

    def set_flag(self, flag: str, value: bool = True):
        self.flags[flag] = value

    def has_flag(self, flag: str) -> bool:
        return self.flags.get(flag, False)

    def snapshot(self) -> Dict[str, Any]:
        """
        Returns a safe snapshot of context for logging/tracing
        """
        return {
            "context_id": self.context_id,
            "execution_id": self.execution_id,
            "trace_id": self.trace_id,
            "environment": self.environment,
            "governance_mode": self.governance_mode,
            "compliance_mode": self.compliance_mode,
            "security_mode": self.security_mode,
            "intelligence_mode": self.intelligence_mode,
            "ai_enabled": self.ai_enabled,
            "system_version": self.system_version,
            "timestamp": datetime.utcnow().isoformat(),
        }


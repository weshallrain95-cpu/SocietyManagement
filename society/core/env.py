"""
SocietyOS Environment Binding Layer
Environment-driven system behavior
"""

import os
from dataclasses import dataclass
from typing import Dict


@dataclass
class EnvironmentConfig:
    environment: str
    debug: bool
    log_level: str
    security_mode: str
    governance_mode: str
    compliance_mode: str
    intelligence_mode: str
    ai_enabled: bool
    service_mesh: str


def _bool(val: str) -> bool:
    return str(val).lower() in ("1", "true", "yes", "on")


def load_environment() -> EnvironmentConfig:
    """
    Load environment configuration from OS env
    """

    return EnvironmentConfig(
        environment=os.getenv("ENVIRONMENT", "local"),
        debug=_bool(os.getenv("DEBUG", "false")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        security_mode=os.getenv("SECURITY_MODE", "standard"),
        governance_mode=os.getenv("GOVERNANCE_MODE", "observe"),
        compliance_mode=os.getenv("COMPLIANCE_MODE", "standard"),
        intelligence_mode=os.getenv("INTELLIGENCE_MODE", "simulation"),
        ai_enabled=_bool(os.getenv("AI_ENABLED", "false")),
        service_mesh=os.getenv("SERVICE_MESH", "disabled"),
    )


def snapshot(env: EnvironmentConfig) -> Dict:
    return {
        "environment": env.environment,
        "debug": env.debug,
        "log_level": env.log_level,
        "security_mode": env.security_mode,
        "governance_mode": env.governance_mode,
        "compliance_mode": env.compliance_mode,
        "intelligence_mode": env.intelligence_mode,
        "ai_enabled": env.ai_enabled,
        "service_mesh": env.service_mesh,
    }


# governance/services/policy_types.py
from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class PolicyContext:
    actor_id: str
    action: str
    resource: str
    attributes: Dict[str, Any]


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reason: str
    policy_code: str
    policy_version: int
    decision_hash: str

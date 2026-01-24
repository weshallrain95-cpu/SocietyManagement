# society/legal/compliance/state/violation_state.py

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict

from society.legal.constitution.ontology.normative import Norm


# ============================
# Violation State
# ============================

@dataclass
class ViolationState:
    """
    Represents a legal violation as a system object.
    """

    # Core Reference
    norm: Norm

    # Violation Metadata
    violation_type: str               # PROHIBITION_BREACH, OBLIGATION_FAILURE, etc
    severity: str                     # LOW, MEDIUM, HIGH
    detected_at: datetime

    # Context
    context: Dict = field(default_factory=dict)

    # Classification
    category: Optional[str] = None    # CRITICAL, MAJOR, MINOR
    enforcement_priority: Optional[int] = None

    # Lifecycle
    status: str = "DETECTED"           # DETECTED, UNDER_REVIEW, ENFORCED, RESOLVED, DISMISSED

    # Governance
    governance_binding: Optional[Dict] = None

    # Enforcement Tracking
    enforcement_actions: Optional[Dict] = None
    resolved_at: Optional[datetime] = None

    # ----------------------------
    # State Transitions
    # ----------------------------

    def mark_under_review(self):
        self.status = "UNDER_REVIEW"

    def mark_enforced(self, actions: Dict, time: datetime):
        self.status = "ENFORCED"
        self.enforcement_actions = actions
        self.resolved_at = time

    def mark_resolved(self, time: datetime):
        self.status = "RESOLVED"
        self.resolved_at = time

    def dismiss(self, time: datetime):
        self.status = "DISMISSED"
        self.resolved_at = time

    # ----------------------------
    # Inspection
    # ----------------------------

    def is_active(self) -> bool:
        return self.status in {"DETECTED", "UNDER_REVIEW"}

    def is_resolved(self) -> bool:
        return self.status in {"RESOLVED", "DISMISSED"}

    def summary(self) -> Dict:
        return {
            "violation_type": self.violation_type,
            "severity": self.severity,
            "category": self.category,
            "status": self.status,
            "detected_at": self.detected_at,
            "resolved_at": self.resolved_at,
        }

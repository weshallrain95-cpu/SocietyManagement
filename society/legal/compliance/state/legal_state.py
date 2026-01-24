# society/legal/compliance/state/legal_state.py

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict


# ============================
# Legal State
# ============================

@dataclass
class LegalState:
    """
    Represents the legal state of an entity.
    This is the core legal state machine object.
    """

    entity_id: str

    # Core State
    status: str  # COMPLIANT, NON_COMPLIANT, UNDER_REVIEW, ENFORCED, SUSPENDED

    # Timestamps
    last_evaluated: datetime
    last_violation_at: Optional[datetime] = None
    last_enforcement_at: Optional[datetime] = None

    # State Metadata
    compliance_score: Optional[float] = None
    risk_score: Optional[float] = None
    enforcement_priority: Optional[int] = None

    # Legal Metadata
    legal_basis: Optional[Dict] = None
    active_laws: Optional[Dict] = None

    # Governance Binding
    governance_state: Optional[Dict] = None

    # ----------------------------
    # State Transitions
    # ----------------------------

    def mark_compliant(self, evaluated_at: datetime):
        self.status = "COMPLIANT"
        self.last_evaluated = evaluated_at

    def mark_non_compliant(self, evaluated_at: datetime, violation_time: datetime):
        self.status = "NON_COMPLIANT"
        self.last_evaluated = evaluated_at
        self.last_violation_at = violation_time

    def mark_under_review(self, evaluated_at: datetime):
        self.status = "UNDER_REVIEW"
        self.last_evaluated = evaluated_at

    def mark_enforced(self, enforced_at: datetime):
        self.status = "ENFORCED"
        self.last_enforcement_at = enforced_at

    def mark_suspended(self, suspended_at: datetime):
        self.status = "SUSPENDED"
        self.last_enforcement_at = suspended_at

    # ----------------------------
    # State Inspection
    # ----------------------------

    def is_compliant(self) -> bool:
        return self.status == "COMPLIANT"

    def is_violation(self) -> bool:
        return self.status == "NON_COMPLIANT"

    def is_enforced(self) -> bool:
        return self.status == "ENFORCED"

    def is_suspended(self) -> bool:
        return self.status == "SUSPENDED"

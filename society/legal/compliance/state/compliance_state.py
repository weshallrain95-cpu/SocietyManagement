# society/legal/compliance/state/compliance_state.py

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime

from society.legal.constitution.ontology.normative import Norm


# ============================
# Compliance State
# ============================

@dataclass
class ComplianceState:
    """
    Represents the compliance condition of an entity.
    Stores obligations, permissions, violations, and legal context.
    """

    # Core Status
    compliant: bool

    # Normative Memory
    obligations: List[Norm] = field(default_factory=list)
    permissions: List[Norm] = field(default_factory=list)
    violations: List[Norm] = field(default_factory=list)

    # Context
    evaluated_at: Optional[datetime] = None
    context: Optional[Dict] = None

    # Legal Metadata
    applicable_laws: Optional[List[str]] = None
    canon_path: Optional[List[str]] = None

    # Governance Binding
    governance_context: Optional[Dict] = None

    # ----------------------------
    # State Inspection
    # ----------------------------

    def has_violations(self) -> bool:
        return len(self.violations) > 0

    def has_obligations(self) -> bool:
        return len(self.obligations) > 0

    def has_permissions(self) -> bool:
        return len(self.permissions) > 0

    # ----------------------------
    # Legal Semantics
    # ----------------------------

    def summary(self) -> Dict:
        return {
            "compliant": self.compliant,
            "violations": len(self.violations),
            "obligations": len(self.obligations),
            "permissions": len(self.permissions),
            "evaluated_at": self.evaluated_at,
        }

    def detailed_view(self) -> Dict:
        return {
            "compliant": self.compliant,
            "violations": [v.to_dict() for v in self.violations],
            "obligations": [o.to_dict() for o in self.obligations],
            "permissions": [p.to_dict() for p in self.permissions],
            "context": self.context,
            "applicable_laws": self.applicable_laws,
            "canon_path": self.canon_path,
            "governance_context": self.governance_context,
        }

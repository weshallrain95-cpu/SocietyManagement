# society/legal/compliance/engines/scoring_engine.py

from typing import List, Dict

from society.legal.compliance.state.violation_state import ViolationState
from society.legal.compliance.state.compliance_state import ComplianceState


# ============================
# Legal Scoring Engine
# ============================

class LegalScoringEngine:
    """
    Computes compliance, risk, and enforcement priority scores.
    Turns legality into metrics.
    """

    # ----------------------------
    # Compliance Scoring
    # ----------------------------

    def compute_compliance_score(self, compliance_state: ComplianceState) -> float:
        """
        Returns a score between 0.0 and 1.0
        1.0 = fully compliant
        0.0 = fully non-compliant
        """

        total_norms = (
            len(compliance_state.obligations) +
            len(compliance_state.permissions) +
            len(compliance_state.violations)
        )

        if total_norms == 0:
            return 1.0

        violation_weight = 1.0
        obligation_weight = 0.5

        penalty = (
            len(compliance_state.violations) * violation_weight +
            len(compliance_state.obligations) * obligation_weight
        )

        score = max(0.0, 1.0 - (penalty / total_norms))
        return round(score, 3)

    # ----------------------------
    # Risk Scoring
    # ----------------------------

    def compute_risk_score(self, violations: List[ViolationState]) -> float:
        """
        Returns a risk score between 0.0 and 1.0
        """

        if not violations:
            return 0.0

        severity_weights = {
            "CRITICAL": 1.0,
            "MAJOR": 0.7,
            "MINOR": 0.3,
        }

        total_weight = 0.0

        for v in violations:
            total_weight += severity_weights.get(v.category, 0.5)

        risk = min(1.0, total_weight / len(violations))
        return round(risk, 3)

    # ----------------------------
    # Enforcement Priority
    # ----------------------------

    def compute_enforcement_priority(self, violations: List[ViolationState]) -> int:
        """
        Lower number = higher priority
        """

        if not violations:
            return 999  # No enforcement needed

        priorities = [v.enforcement_priority for v in violations if v.enforcement_priority]

        if not priorities:
            return 500

        return min(priorities)

    # ----------------------------
    # Composite Legal Score
    # ----------------------------

    def compute_legal_score(
        self,
        compliance_state: ComplianceState,
        violations: List[ViolationState]
    ) -> Dict:

        compliance_score = self.compute_compliance_score(compliance_state)
        risk_score = self.compute_risk_score(violations)
        enforcement_priority = self.compute_enforcement_priority(violations)

        return {
            "compliance_score": compliance_score,
            "risk_score": risk_score,
            "enforcement_priority": enforcement_priority,
            "legal_status": self.derive_legal_status(compliance_score, risk_score),
        }

    # ----------------------------
    # Legal Status Derivation
    # ----------------------------

    def derive_legal_status(self, compliance_score: float, risk_score: float) -> str:
        """
        High-level legal classification.
        """

        if compliance_score == 1.0:
            return "FULLY_COMPLIANT"
        if risk_score > 0.8:
            return "CRITICAL_RISK"
        if risk_score > 0.5:
            return "HIGH_RISK"
        if risk_score > 0.2:
            return "MODERATE_RISK"
        return "LOW_RISK"

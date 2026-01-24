# society/legal/compliance/engines/violation_engine.py

from typing import List, Dict
from django.utils import timezone

from society.legal.constitution.ontology.normative import NormativeType, Norm
from society.legal.compliance.state.violation_state import ViolationState


# ============================
# Violation Detection Engine
# ============================

class ViolationEngine:
    """
    Detects, classifies, and structures legal violations.
    Turns illegality into system objects.
    """

    def __init__(self):
        self.now = timezone.now()

    # ----------------------------
    # Violation Detection
    # ----------------------------

    def detect_violations(self, norms: List[Norm], context: Dict) -> List[ViolationState]:
        """
        Detects violations based on norms and context.
        """

        violations = []

        for norm in norms:
            # Prohibition violated
            if norm.action == NormativeType.PROHIBITION.value:
                violation = ViolationState(
                    norm=norm,
                    violation_type="PROHIBITION_BREACH",
                    severity="HIGH",
                    detected_at=self.now,
                    context=context,
                )
                violations.append(violation)

            # Obligation not satisfied
            if norm.action == NormativeType.OBLIGATION.value:
                violation = ViolationState(
                    norm=norm,
                    violation_type="OBLIGATION_FAILURE",
                    severity="MEDIUM",
                    detected_at=self.now,
                    context=context,
                )
                violations.append(violation)

        return violations

    # ----------------------------
    # Classification
    # ----------------------------

    def classify_violation(self, violation: ViolationState) -> ViolationState:
        """
        Classifies violation severity and category.
        """

        # Basic classification logic (extensible)
        if violation.violation_type == "PROHIBITION_BREACH":
            violation.category = "CRITICAL"
            violation.enforcement_priority = 1
        elif violation.violation_type == "OBLIGATION_FAILURE":
            violation.category = "MAJOR"
            violation.enforcement_priority = 2
        else:
            violation.category = "MINOR"
            violation.enforcement_priority = 3

        return violation

    # ----------------------------
    # Processing Pipeline
    # ----------------------------

    def process(self, norms: List[Norm], context: Dict) -> List[ViolationState]:
        """
        Full violation processing pipeline.
        """

        raw_violations = self.detect_violations(norms, context)
        classified = []

        for v in raw_violations:
            classified_violation = self.classify_violation(v)
            classified.append(classified_violation)

        return classified

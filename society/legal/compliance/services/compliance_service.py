# society/legal/compliance/services/compliance_service.py

from django.utils import timezone

from society.legal.compliance.engines.compliance_engine import LegalComplianceEngine
from society.legal.compliance.engines.violation_engine import ViolationEngine
from society.legal.compliance.engines.scoring_engine import LegalScoringEngine

from society.legal.compliance.models.legal_state import LegalStateModel
from society.legal.compliance.models.violation import Violation
from society.legal.compliance.models.compliance_record import ComplianceRecord


# ============================
# Compliance Service
# ============================

class ComplianceService:
    """
    Orchestrates legal evaluation, persistence, and integration.
    """

    def __init__(self):
        self.compliance_engine = LegalComplianceEngine()
        self.violation_engine = ViolationEngine()
        self.scoring_engine = LegalScoringEngine()

    # ----------------------------
    # Full Legal Evaluation
    # ----------------------------

    def evaluate_entity(self, entity_id: str, context: dict) -> dict:
        """
        Full legal evaluation pipeline.
        """

        now = timezone.now()

        # 1. Evaluate compliance
        result = self.compliance_engine.evaluate(entity_id, context)

        compliance_state = result["compliance"]["compliance_state"]
        norms = result["compliance"]["norms"]

        # 2. Detect violations
        violations_state = self.violation_engine.process(norms, context)

        # 3. Score legality
        scores = self.scoring_engine.compute_legal_score(
            compliance_state=compliance_state,
            violations=violations_state
        )

        # 4. Persist Legal State
        legal_state_model = LegalStateModel.objects.update_or_create(
            entity_id=entity_id,
            defaults={
                "status": result["legal_state"].status,
                "last_evaluated": now,
                "compliance_score": scores["compliance_score"],
                "risk_score": scores["risk_score"],
                "enforcement_priority": scores["enforcement_priority"],
            }
        )[0]

        # 5. Persist Violations
        persisted_violations = []
        for v in violations_state:
            violation_model = Violation.objects.create(
                entity_id=entity_id,
                violation_type=v.violation_type,
                severity=v.severity,
                category=v.category,
                enforcement_priority=v.enforcement_priority,
                norm_payload=v.norm.to_dict(),
                context=v.context,
                status=v.status,
                detected_at=v.detected_at,
            )
            persisted_violations.append(violation_model)

        # 6. Persist Compliance Record
        compliance_record = ComplianceRecord.objects.create(
            entity_id=entity_id,
            compliant=compliance_state.compliant,
            compliance_score=scores["compliance_score"],
            risk_score=scores["risk_score"],
            enforcement_priority=scores["enforcement_priority"],
            context=context,
            applicable_laws=compliance_state.applicable_laws or [],
            canon_path=compliance_state.canon_path or [],
            governance_context=compliance_state.governance_context,
            evaluated_at=now,
        )

        return {
            "legal_state": legal_state_model,
            "violations": persisted_violations,
            "compliance_record": compliance_record,
            "scores": scores,
        }

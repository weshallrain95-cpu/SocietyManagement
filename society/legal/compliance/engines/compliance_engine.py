# society/legal/compliance/engines/compliance_engine.py

from typing import Dict, List
from django.utils import timezone

from society.legal.constitution.models.bylaw import Bylaw
from society.legal.constitution.models.document import LegalDocument
from society.legal.constitution.models.canon import LegalCanonNode
from society.legal.constitution.ontology.normative import NormativeType, Norm
from society.legal.compliance.state.legal_state import LegalState
from society.legal.compliance.state.compliance_state import ComplianceState
from society.legal.compliance.state.violation_state import ViolationState


# ============================
# Legal Compliance Engine
# ============================

class LegalComplianceEngine:
    """
    Core engine for continuous legal evaluation.
    The system is always under law.
    """

    def __init__(self):
        self.now = timezone.now()

    # ----------------------------
    # Context Resolution
    # ----------------------------

    def resolve_applicable_law(self, context: Dict) -> Dict[str, List]:
        """
        Resolves applicable canon nodes, documents, and bylaws
        for a given context.
        """

        # Placeholder resolution logic (will evolve into rule resolver)
        canon_nodes = LegalCanonNode.objects.filter(status="ACTIVE")
        documents = LegalDocument.objects.filter(status="ACTIVE")
        bylaws = Bylaw.objects.filter(status="ACTIVE")

        return {
            "canon": list(canon_nodes),
            "documents": list(documents),
            "bylaws": list(bylaws),
        }

    # ----------------------------
    # Normative Interpretation
    # ----------------------------

    def interpret_norms(self, bylaws: List[Bylaw]) -> List[Norm]:
        """
        Converts bylaws into semantic norms.
        """

        norms = []

        for bylaw in bylaws:
            payload = bylaw.get_normative_payload()

            norm = Norm(
                subject=payload.get("subject", "entity"),
                action=payload.get("normative_type", "UNKNOWN"),
                obj=payload.get("object"),
                condition=payload.get("conditions", {}),
                consequence={
                    "sanctions": payload.get("sanctions", []),
                    "enforcement": payload.get("enforcement_hooks", {}),
                },
            )

            norms.append(norm)

        return norms

    # ----------------------------
    # Compliance Evaluation
    # ----------------------------

    def evaluate_compliance(self, context: Dict) -> Dict:
        """
        Evaluates legality of a context.
        """

        applicable = self.resolve_applicable_law(context)
        bylaws = applicable["bylaws"]

        norms = self.interpret_norms(bylaws)

        violations = []
        obligations = []
        permissions = []

        for norm in norms:
            if norm.action == NormativeType.PROHIBITION.value:
                violations.append(norm)
            elif norm.action == NormativeType.OBLIGATION.value:
                obligations.append(norm)
            elif norm.action == NormativeType.PERMISSION.value:
                permissions.append(norm)

        compliance = ComplianceState(
            compliant=len(violations) == 0,
            obligations=obligations,
            permissions=permissions,
            violations=violations,
        )

        return {
            "compliance_state": compliance,
            "norms": norms,
            "context": context,
        }

    # ----------------------------
    # State Machine Integration
    # ----------------------------

    def update_legal_state(self, entity_id: str, result: Dict) -> LegalState:
        """
        Updates legal state of an entity.
        """

        compliance_state = result["compliance_state"]

        if compliance_state.compliant:
            state = LegalState(
                entity_id=entity_id,
                status="COMPLIANT",
                last_evaluated=self.now,
            )
        else:
            state = LegalState(
                entity_id=entity_id,
                status="NON_COMPLIANT",
                last_evaluated=self.now,
            )

        return state

    # ----------------------------
    # Continuous Evaluation Loop
    # ----------------------------

    def evaluate(self, entity_id: str, context: Dict) -> Dict:
        """
        Full compliance pipeline.
        """

        result = self.evaluate_compliance(context)
        legal_state = self.update_legal_state(entity_id, result)

        return {
            "entity_id": entity_id,
            "legal_state": legal_state,
            "compliance": result,
        }

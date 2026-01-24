# society/legal/disputes/cases/services/case_service.py

from django.utils import timezone
from society.legal.disputes.cases.models.case import LegalCase
import uuid


# ============================
# Case Service
# ============================

class CaseService:
    """
    Manages legal case lifecycle.
    """

    def create_case(
        self,
        title: str,
        jurisdiction: str,
        authority: str,
        case_type: str,
        legal_domain: str,
        legal_basis: dict,
        governance_context: dict = None,
    ) -> LegalCase:

        case_number = f"CASE-{uuid.uuid4().hex[:12].upper()}"

        case = LegalCase.objects.create(
            case_number=case_number,
            title=title,
            jurisdiction=jurisdiction,
            authority=authority,
            case_type=case_type,
            legal_domain=legal_domain,
            legal_basis=legal_basis,
            governance_context=governance_context or {},
            status="FILED",
        )

        return case

    # ----------------------------
    # Lifecycle Operations
    # ----------------------------

    def admit_case(self, case: LegalCase):
        case.admit(timezone.now())
        return case

    def move_to_review(self, case: LegalCase):
        case.move_to_review()
        return case

    def start_hearing(self, case: LegalCase):
        case.start_hearing()
        return case

    def start_arbitration(self, case: LegalCase):
        case.start_arbitration()
        return case

    def mark_judgement_pending(self, case: LegalCase):
        case.mark_judgement_pending()
        return case

    def decide(self, case: LegalCase):
        case.decide()
        return case

    def enforce(self, case: LegalCase):
        case.enforce()
        return case

    def appeal(self, case: LegalCase):
        case.appeal()
        return case

    def close_case(self, case: LegalCase):
        case.close(timezone.now())
        return case

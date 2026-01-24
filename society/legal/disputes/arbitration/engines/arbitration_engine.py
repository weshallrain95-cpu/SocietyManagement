# society/legal/disputes/arbitration/engines/arbitration_engine.py

from django.utils import timezone
from society.legal.disputes.cases.models.case import LegalCase
from society.legal.disputes.cases.models.judgement import LegalJudgement


# ============================
# Arbitration Engine
# ============================

class ArbitrationEngine:
    """
    Core arbitration orchestration engine.
    Governs arbitration lifecycle.
    """

    def initiate_arbitration(self, case: LegalCase):
        case.start_arbitration()
        return case

    def admit_case(self, case: LegalCase):
        case.admit(timezone.now())
        return case

    def move_to_hearing(self, case: LegalCase):
        case.start_hearing()
        return case

    def mark_judgement_pending(self, case: LegalCase):
        case.mark_judgement_pending()
        return case

    def deliver_judgement(
        self,
        case: LegalCase,
        verdict: str,
        reasoning: str,
        legal_basis: dict,
        orders: dict,
        final: bool = False,
        appealable: bool = True,
    ) -> LegalJudgement:

        judgement = LegalJudgement.objects.create(
            case=case,
            verdict=verdict,
            reasoning=reasoning,
            legal_basis=legal_basis,
            orders=orders,
            final=final,
            appealable=appealable,
        )

        case.decide()
        return judgement

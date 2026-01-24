# society/legal/disputes/arbitration/engines/ruling_engine.py

from django.utils import timezone
from society.legal.disputes.cases.models.case import LegalCase
from society.legal.disputes.cases.models.judgement import LegalJudgement


# ============================
# Ruling Engine
# ============================

class RulingEngine:
    """
    Generates legal rulings and decisions.
    """

    def issue_ruling(
        self,
        case: LegalCase,
        verdict: str,
        reasoning: str,
        legal_basis: dict,
        orders: dict,
        compliance_deadline=None,
        final: bool = False,
        appealable: bool = True,
    ) -> LegalJudgement:

        judgement = LegalJudgement.objects.create(
            case=case,
            verdict=verdict,
            reasoning=reasoning,
            legal_basis=legal_basis,
            orders=orders,
            compliance_deadline=compliance_deadline,
            final=final,
            appealable=appealable,
        )

        case.decide()
        return judgement

    def enforce_ruling(self, case: LegalCase):
        case.enforce()
        return case

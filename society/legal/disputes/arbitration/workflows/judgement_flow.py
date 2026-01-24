# society/legal/disputes/arbitration/workflows/judgement_flow.py

from society.legal.disputes.arbitration.engines.ruling_engine import RulingEngine
from society.legal.disputes.cases.models.case import LegalCase


# ============================
# Judgement Flow
# ============================

class JudgementFlow:
    """
    Controls judgement lifecycle.
    """

    def __init__(self):
        self.ruling_engine = RulingEngine()

    def deliver_judgement(
        self,
        case: LegalCase,
        verdict: str,
        reasoning: str,
        legal_basis: dict,
        orders: dict,
        compliance_deadline=None,
        final: bool = False,
        appealable: bool = True,
    ):
        judgement = self.ruling_engine.issue_ruling(
            case=case,
            verdict=verdict,
            reasoning=reasoning,
            legal_basis=legal_basis,
            orders=orders,
            compliance_deadline=compliance_deadline,
            final=final,
            appealable=appealable,
        )
        return judgement

    def enforce(self, case: LegalCase):
        return self.ruling_engine.enforce_ruling(case)

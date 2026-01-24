# society/legal/disputes/arbitration/workflows/appeal_flow.py

from society.legal.disputes.cases.models.case import LegalCase


# ============================
# Appeal Flow
# ============================

class AppealFlow:
    """
    Controls appeal lifecycle.
    """

    def initiate_appeal(self, case: LegalCase):
        case.appeal()
        return case

    def admit_appeal(self, case: LegalCase):
        case.move_to_review()
        return case

    def close_appeal(self, case: LegalCase):
        case.close(case.closed_at)
        return case

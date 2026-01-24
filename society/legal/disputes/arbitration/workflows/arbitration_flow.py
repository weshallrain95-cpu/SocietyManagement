# society/legal/disputes/arbitration/workflows/arbitration_flow.py

from society.legal.disputes.arbitration.engines.arbitration_engine import ArbitrationEngine
from society.legal.disputes.arbitration.engines.hearing_engine import ArbitrationHearingEngine
from society.legal.disputes.cases.models.case import LegalCase


# ============================
# Arbitration Flow
# ============================

class ArbitrationFlow:
    """
    Controls full arbitration lifecycle.
    """

    def __init__(self):
        self.arbitration_engine = ArbitrationEngine()
        self.hearing_engine = ArbitrationHearingEngine()

    def start(self, case: LegalCase):
        self.arbitration_engine.initiate_arbitration(case)
        self.arbitration_engine.admit_case(case)
        return case

    def conduct_hearing(self, case: LegalCase, hearing_type, schedule_time, **kwargs):
        self.arbitration_engine.move_to_hearing(case)
        hearing = self.hearing_engine.schedule(case, hearing_type, schedule_time, **kwargs)
        return hearing

    def conclude_hearing(self, hearing, outcome: str):
        self.hearing_engine.conclude(hearing, outcome)
        return hearing

# society/legal/disputes/arbitration/engines/hearing_engine.py

from django.utils import timezone
from society.legal.disputes.cases.models.hearing import LegalHearing
from society.legal.disputes.cases.models.case import LegalCase


# ============================
# Hearing Engine
# ============================

class ArbitrationHearingEngine:
    """
    Controls arbitration hearings.
    """

    def schedule(
        self,
        case: LegalCase,
        hearing_type: str,
        schedule_time,
        mode: str = "VIRTUAL",
        location: str = None,
        agenda: str = None,
    ) -> LegalHearing:

        hearing = LegalHearing.objects.create(
            case=case,
            hearing_type=hearing_type,
            schedule_time=schedule_time,
            mode=mode,
            location=location,
            agenda=agenda,
            status="SCHEDULED",
        )

        return hearing

    def start(self, hearing: LegalHearing):
        hearing.status = "ONGOING"
        hearing.save()
        return hearing

    def adjourn(self, hearing: LegalHearing, reason: str = None):
        hearing.status = "ADJOURNED"
        if reason:
            hearing.outcome = f"Adjourned: {reason}"
        hearing.save()
        return hearing

    def conclude(self, hearing: LegalHearing, outcome: str):
        hearing.status = "COMPLETED"
        hearing.outcome = outcome
        hearing.save()
        return hearing

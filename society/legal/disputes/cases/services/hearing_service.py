# society/legal/disputes/cases/services/hearing_service.py

from society.legal.disputes.cases.models.hearing import LegalHearing
from society.legal.disputes.cases.models.case import LegalCase
from django.utils import timezone


# ============================
# Hearing Service
# ============================

class HearingService:
    """
    Manages legal hearings.
    """

    def schedule_hearing(
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

    def start_hearing(self, hearing: LegalHearing):
        hearing.status = "ONGOING"
        hearing.save()
        return hearing

    def complete_hearing(self, hearing: LegalHearing, outcome: str = None):
        hearing.status = "COMPLETED"
        if outcome:
            hearing.outcome = outcome
        hearing.save()
        return hearing

    def adjourn_hearing(self, hearing: LegalHearing):
        hearing.status = "ADJOURNED"
        hearing.save()
        return hearing

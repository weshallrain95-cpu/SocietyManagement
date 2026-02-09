from django.utils import timezone

from statutory.models import SocietyObligationStatus, LegalObligation


COMPLETED_STATUS = "COMPLETED"


def complete_obligation(society, obligation_id: int):
    """
    Marks a legal obligation as completed for a society.

    Production-safe:
    - idempotent
    - audit-ready
    - multi-society safe
    """

    obligation = LegalObligation.objects.get(id=obligation_id)

    status, _ = SocietyObligationStatus.objects.get_or_create(
        society=society,
        legal_obligation=obligation,
        defaults={
            "status": COMPLETED_STATUS,
        }
    )

    # update if exists
    status.status = COMPLETED_STATUS
    status.overridden_on = timezone.now()
    status.save()

    return status

from statutory.preregistration.status import (
    preregistration_blockers,
    is_preregistration_complete,
)
from statutory.models import LegalChecklistItem, LegalStage
from society.models import Society


PRE_REGISTRATION_STAGE_CODE = "PRE_REGISTRATION"
SNAPSHOT_TITLE_MH = "Pre-Registration Readiness Checklist (Maharashtra)"


def preregistration_readiness_snapshot(society: Society) -> dict:
    """
    Read-only, registrar-facing snapshot of pre-registration readiness.
    """

    blockers = preregistration_blockers(society)
    registrar_ready = is_preregistration_complete(society)

    items = []
    total_mandatory = 0
    completed_mandatory = 0

    if society is None:
        return {
            "title": SNAPSHOT_TITLE_MH,
            "registrar_ready": False,
            "completed": False,
            "summary": {
                "total_mandatory": 0,
                "completed_mandatory": 0,
            },
            "items": [],
            "blockers": blockers,
        }

    try:
        stage = LegalStage.objects.get(
            code=PRE_REGISTRATION_STAGE_CODE,
            state=society.state,
        )
    except LegalStage.DoesNotExist:
        return {
            "title": SNAPSHOT_TITLE_MH,
            "registrar_ready": False,
            "completed": False,
            "summary": {
                "total_mandatory": 0,
                "completed_mandatory": 0,
            },
            "items": [],
            "blockers": blockers,
        }

    checklist_items = LegalChecklistItem.objects.filter(
        stage=stage
    ).order_by("id")

    for item in checklist_items:
        is_completed = True

        if item.mandatory:
            total_mandatory += 1

            # completion is inferred from blockers
            for blocker in blockers:
                if blocker.get("obligation_code") == item.code:
                    is_completed = False
                    break

            if is_completed:
                completed_mandatory += 1

        items.append({
            "code": item.code,
            "title": item.title,
            "mandatory": item.mandatory,
            "status": "COMPLETED" if is_completed else "PENDING",
            "evidence_required": item.requires_document,
        })

    return {
        "title": SNAPSHOT_TITLE_MH,
        "registrar_ready": registrar_ready,
        "completed": registrar_ready,
        "summary": {
            "total_mandatory": total_mandatory,
            "completed_mandatory": completed_mandatory,
        },
        "items": items,
        "blockers": blockers,
    }

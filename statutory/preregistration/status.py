from statutory.models import (
    LegalStage,
    LegalChecklistItem,
    SocietyObligationStatus,
    SocietyLegalDocument,
)


PRE_REGISTRATION_STAGE_CODE = "PRE_REGISTRATION"
COMPLETED_STATUS = "COMPLETED"
VALID_DOCUMENT_STATUSES = ("SIGNED", "VERIFIED")


def is_preregistration_complete(society) -> bool:
    """
    Returns True if and only if the society has completed
    all mandatory pre-registration obligations with evidence.
    """

    blockers = preregistration_blockers(society)
    return len(blockers) == 0


def preregistration_blockers(society) -> list[dict]:
    blockers = []

    if society is None:
        return [{
            "type": "NO_SOCIETY",
            "message": "No society record found. Pre-registration cannot be evaluated."
        }]

    try:
        stage = LegalStage.objects.get(
            code=PRE_REGISTRATION_STAGE_CODE,
            state=society.state
        )
    except LegalStage.DoesNotExist:
        return [{
            "type": "CONFIGURATION_ERROR",
            "message": "Pre-registration legal stage is not configured for this state."
        }]


    obligations = LegalChecklistItem.objects.filter(
        stage=stage,
        mandatory=True
    ).select_related("artifact_template")

    for obligation in obligations:
        obligation_status = SocietyObligationStatus.objects.filter(
            society=society,
            obligation=obligation
        ).first()

        if not obligation_status or obligation_status.status != COMPLETED_STATUS:
            blockers.append({
                "type": "OBLIGATION_INCOMPLETE",
                "obligation_code": obligation.code,
                "title": obligation.title,
                "message": "Mandatory legal obligation not completed."
            })
            continue

        if obligation.requires_document:
            has_signed_document = SocietyLegalDocument.objects.filter(
                society=society,
                artifact_template=obligation.artifact_template,
                status__in=VALID_DOCUMENT_STATUSES
            ).exists()

            if not has_signed_document:
                blockers.append({
                    "type": "DOCUMENT_MISSING",
                    "obligation_code": obligation.code,
                    "title": obligation.title,
                    "message": "Signed legal document not uploaded."
                })

    return blockers

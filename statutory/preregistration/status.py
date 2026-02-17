# statutory/preregistration/status.py
from typing import List, Dict

from statutory.models import (
    State,
    LegalStage,
    LegalObligation,
    SocietyObligationStatus,
    SocietyLegalDocument,
)

# IMPORTANT:
# We no longer rely on "PRE_REGISTRATION"
# because real seeded stages are named:
# "Society Formation & Registration (Pre-Registration)"
PRE_REGISTRATION_STAGE_KEYWORD = "Pre-Registration"

COMPLETED_STATUS = "COMPLETED"
VALID_DOCUMENT_STATUSES = ("SIGNED", "VERIFIED")


def _get_preregistration_stage(society):
    """
    Unified resolver used by BOTH:
    - snapshot.py
    - status.py

    Prevents mismatch bugs.
    """

    if society is None:
        return None

    state_obj = None
    state_code = getattr(society, "state_code", None)

    if state_code:
        state_obj = State.objects.filter(code__iexact=state_code).first()

    stage = None

    # Prefer state-scoped stage
    if state_obj:
        stage = LegalStage.objects.filter(
            state=state_obj,
            name__icontains=PRE_REGISTRATION_STAGE_KEYWORD
        ).first()

    # Fallback: global stage
    if stage is None:
        stage = LegalStage.objects.filter(
            name__icontains=PRE_REGISTRATION_STAGE_KEYWORD
        ).first()

    return stage


def is_preregistration_complete(society) -> bool:
    """
    Returns True only when ALL mandatory obligations
    and required evidence documents are complete.
    """
    blockers = preregistration_blockers(society)
    return len(blockers) == 0


def preregistration_blockers(society) -> List[Dict]:
    """
    Return a list of blocker dicts describing why preregistration is not complete.
    Fully defensive. Handles missing configuration gracefully.
    """

    if society is None:
        return [{
            "type": "NO_SOCIETY",
            "message": "No society record found. Pre-registration cannot be evaluated."
        }]

    stage = _get_preregistration_stage(society)

    if stage is None:
        return [{
            "type": "CONFIGURATION_ERROR",
            "message": "Pre-registration legal stage is not configured."
        }]

    blockers: List[Dict] = []

    obligations = LegalObligation.objects.filter(
        legal_stage=stage,
        mandatory=True
    )

    for obligation in obligations:

        # Check obligation completion
        obligation_status = SocietyObligationStatus.objects.filter(
            society=society,
            legal_obligation=obligation
        ).first()

        if not obligation_status or obligation_status.status != COMPLETED_STATUS:
            blockers.append({
                "type": "OBLIGATION_INCOMPLETE",
                "obligation_id": obligation.id,
                "obligation_title": obligation.title,
                "message": "Mandatory legal obligation not completed."
            })
            continue

        # Check evidence document requirement
        requires_document = obligation.artifact_templates.exists()

        if requires_document:
            has_signed_document = SocietyLegalDocument.objects.filter(
                society=society,
                template__in=obligation.artifact_templates.all(),
                status__in=VALID_DOCUMENT_STATUSES
            ).exists()

            if not has_signed_document:
                blockers.append({
                    "type": "DOCUMENT_MISSING",
                    "obligation_id": obligation.id,
                    "obligation_title": obligation.title,
                    "message": "Signed legal document not uploaded."
                })

    return blockers

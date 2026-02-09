# statutory/preregistration/status.py
from typing import List, Dict

from django.db.models import Q

from statutory.models import (
    State,
    LegalStage,
    LegalObligation,
    LegalChecklistItem,
    SocietyObligationStatus,
    SocietyLegalDocument,
)

PRE_REGISTRATION_STAGE_NAME = "PRE_REGISTRATION"
COMPLETED_STATUS = "COMPLETED"
VALID_DOCUMENT_STATUSES = ("SIGNED", "VERIFIED")


def is_preregistration_complete(society) -> bool:
    """
    Returns True if and only if the society has completed
    all mandatory pre-registration obligations with evidence.
    """
    blockers = preregistration_blockers(society)
    return len(blockers) == 0


def preregistration_blockers(society) -> List[Dict]:
    """
    Return a list of blocker dicts describing why preregistration is not complete.
    Defensive: works when some related rows are missing and provides helpful messages.
    """

    if society is None:
        return [{
            "type": "NO_SOCIETY",
            "message": "No society record found. Pre-registration cannot be evaluated."
        }]

    # Resolve State from society.state_code if possible
    state_obj = None
    state_code = getattr(society, "state_code", None)
    if state_code:
        state_obj = State.objects.filter(code__iexact=state_code).first()

    # Try to load the configured LegalStage for pre-registration for the resolved state.
    stage = None
    if state_obj:
        stage = LegalStage.objects.filter(state=state_obj, name__icontains=PRE_REGISTRATION_STAGE_NAME).first()

    if stage is None:
        # Fall back: try any stage with PRE_REGISTRATION in name (global)
        stage = LegalStage.objects.filter(name__icontains=PRE_REGISTRATION_STAGE_NAME).first()

    if stage is None:
        return [{
            "type": "CONFIGURATION_ERROR",
            "message": "Pre-registration legal stage is not configured."
        }]

    blockers = []

    # Use LegalObligation as the canonical obligation entity (it links to legal_stage).
    obligations = LegalObligation.objects.filter(legal_stage=stage, mandatory=True)

    for obligation in obligations:
        # Check SocietyObligationStatus for the obligation
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
            # This obligation is incomplete; no point checking documents for it.
            continue

        # If the obligation has associated artifact templates then signed/verified documents are required.
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

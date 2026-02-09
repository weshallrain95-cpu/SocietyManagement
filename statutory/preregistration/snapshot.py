# statutory/preregistration/snapshot.py
from typing import Dict, List

from statutory.preregistration.status import (
    preregistration_blockers,
    is_preregistration_complete,
)

from statutory.models import (
    State,
    LegalStage,
    LegalObligation,
    LegalArtifactTemplate,
    SocietyLegalDocument,
)

from society.models import Society


SNAPSHOT_TITLE_MH = "Pre-Registration Readiness Checklist (Maharashtra)"
PRE_REGISTRATION_STAGE_NAME = "PRE_REGISTRATION"


def preregistration_readiness_snapshot(society: Society) -> Dict:
    """
    Registrar-facing snapshot of pre-registration readiness.

    IMPORTANT SIGNALS:
    - evidence_required → template exists for obligation
    - completion → obligation not in blockers
    - document_uploaded → society uploaded signed document
    """

    blockers = preregistration_blockers(society)
    registrar_ready = is_preregistration_complete(society)

    items: List[Dict] = []
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

    # Resolve state from society.state_code -> State object
    state_obj = None
    state_code = getattr(society, "state_code", None)
    if state_code:
        state_obj = State.objects.filter(code__iexact=state_code).first()

    # Resolve PRE_REGISTRATION stage
    stage = None
    if state_obj:
        stage = LegalStage.objects.filter(
            state=state_obj,
            name__icontains=PRE_REGISTRATION_STAGE_NAME
        ).first()

    if stage is None:
        stage = LegalStage.objects.filter(
            name__icontains=PRE_REGISTRATION_STAGE_NAME
        ).first()

    if stage is None:
        return {
            "title": SNAPSHOT_TITLE_MH,
            "registrar_ready": False,
            "completed": False,
            "summary": {
                "total_mandatory": 0,
                "completed_mandatory": 0,
            },
            "items": [],
            "blockers": [
                {
                    "type": "CONFIGURATION_ERROR",
                    "message": "Pre-registration legal stage is not configured.",
                }
            ],
        }

    # Fetch obligations
    obligations = LegalObligation.objects.filter(
        legal_stage=stage
    ).order_by("id")

    # Build quick lookup for incomplete obligations
    incomplete_obligation_ids = {
        b.get("obligation_id")
        for b in blockers
        if b.get("obligation_id")
    }

    for obligation in obligations:

        # completion state
        is_completed = obligation.id not in incomplete_obligation_ids

        if obligation.mandatory:
            total_mandatory += 1
            if is_completed:
                completed_mandatory += 1

        # ----------------------------
        # EVIDENCE LAYER
        # ----------------------------

        # 1) does template exist?
        templates_exist = LegalArtifactTemplate.objects.filter(
            legal_obligation=obligation
        ).exists()

        # 2) has society uploaded signed document?
        documents_uploaded = SocietyLegalDocument.objects.filter(
            society=society,
            template__legal_obligation=obligation,
            status="SIGNED",
        ).exists()

        # ----------------------------
        # BUILD SNAPSHOT ITEM
        # ----------------------------
        
        uploaded_doc = SocietyLegalDocument.objects.filter(
            society=society,
            template__in=obligation.artifact_templates.all()
        ).order_by("-uploaded_at").first()

        items.append({
            "id": obligation.id,
            "code": f"OBL-{obligation.id}",
            "title": obligation.title,
            "mandatory": obligation.mandatory,
            "status": "COMPLETED" if is_completed else "PENDING",
            "evidence_required": templates_exist,
            "document_uploaded": uploaded_doc is not None,
            "document": {
                "template_id": uploaded_doc.template_id,
                "file": uploaded_doc.file.url if uploaded_doc else None,
                "uploaded_at": uploaded_doc.uploaded_at.isoformat() if uploaded_doc else None,
            } if uploaded_doc else None,
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

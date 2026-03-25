from typing import Dict, List

from statutory.models import (
    LegalStage,
    LegalObligation,
    LegalArtifactTemplate,
    SocietyLegalDocument,
    State,
)
from society.models import Society


PRE_REGISTRATION_STAGE_NAME = "PRE_REGISTRATION"


def generate_registrar_pack(society: Society) -> Dict:
    """
    Builds registrar submission bundle for a society.

    Includes:
    - Completed obligations
    - Uploaded legal documents
    - Editable templates (Word / Form / Drafts)
    """

    if not society:
        return {"error": "Society not found"}

    # resolve state
    state_obj = None
    if society.state_code:
        state_obj = State.objects.filter(code__iexact=society.state_code).first()

    # resolve pre-registration stage
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
        return {"error": "Pre-registration stage not configured"}

    obligations = LegalObligation.objects.filter(
        legal_stage=stage
    ).order_by("id")

    completed_obligations: List[Dict] = []
    uploaded_documents: List[Dict] = []
    editable_templates: List[Dict] = []

    for obligation in obligations:

        templates = LegalArtifactTemplate.objects.filter(
            legal_obligation=obligation
        )

        docs = SocietyLegalDocument.objects.filter(
            society=society,
            template__in=templates
        )

        # completed if document exists OR marked complete
        if docs.exists():
            completed_obligations.append({
                "obligation_id": obligation.id,
                "title": obligation.title,
                "mandatory": obligation.is_mandatory,
            })

        # attach uploaded files
        for d in docs:
            uploaded_documents.append({
                "template_id": d.template_id,
                "file": d.file.url if d.file else None,
                "status": d.status,
                "uploaded_at": d.uploaded_at,
            })

        # attach editable templates
        for t in templates:
            editable_templates.append({
                "template_id": t.id,
                "artifact_type": t.artifact_type,
                "artifact_code": t.artifact_code,
                "template_body": t.template_body,
            })

    return {
        "society": {
            "id": society.id,
            "name": society.name,
        },
        "pack": {
            "completed_obligations": completed_obligations,
            "documents": uploaded_documents,
            "templates": editable_templates,
        }
    }

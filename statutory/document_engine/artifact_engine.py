# statutory/document_engine/artifact_engine.py

from statutory.models import SocietyLegalDocument


# ✅ MUST BE ABOVE FUNCTION
ARTIFACTS = [
    "PROVISIONAL_COMMITTEE_RESOLUTION_MH",
    "FORM_A_MH",
    "PROMOTER_CONSENT_LETTER_MH",
    "BANK_ACCOUNT_LETTER_MH",
    "FIRST_GENERAL_MEETING_MINUTES_MH",
    "BUILDER_DOCUMENT_NOTICE_MH",
    "REGISTRAR_SUBMISSION_LETTER_MH",
    "BYLAW_DRAFT_MH",
]


def derive_artifact_status(society_id):

    docs = SocietyLegalDocument.objects.filter(
        society_id=society_id
    )

    doc_map = {
        d.template.artifact_code: d
        for d in docs
        if d.template and d.template.artifact_code
    }

    result = []

    for code in ARTIFACTS:

        # 🔥 BYLAWS
        if code == "BYLAW_DRAFT_MH":
            result.append({
                "artifact_code": code,
                "status": "GENERATED",
                "file": f"/api/society/bylaws/download/?society_id={society_id}",
            })
            continue

        doc = doc_map.get(code)

        if not doc:
            status = "NOT_STARTED"
            file = ""
        else:
            if doc.file:
                status = doc.status or "UPLOADED"
                file = doc.file.url
            else:
                status = doc.status or "GENERATED"
                file = ""

        result.append({
            "artifact_code": code,
            "status": status,
            "file": file,
        })

    return result
import io
import json
import zipfile
from datetime import datetime

from statutory.preregistration.snapshot import preregistration_readiness_snapshot
from statutory.models import SocietyLegalDocument, LegalArtifactTemplate
from society.models import Society


def build_registrar_pack(society: Society) -> bytes:
    """
    Builds registrar-ready ZIP package.
    Contains:
    - readiness snapshot
    - completed obligations
    - uploaded evidence
    - templates
    """

    snapshot = preregistration_readiness_snapshot(society)

    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z:

        # 1. Snapshot
        z.writestr(
            "snapshot.json",
            json.dumps(snapshot, indent=2)
        )

        # 2. Completed obligations
        completed = [
            item for item in snapshot["items"]
            if item["status"] == "COMPLETED"
        ]

        z.writestr(
            "completed_obligations.json",
            json.dumps(completed, indent=2)
        )

        # 3. Uploaded documents
        documents = SocietyLegalDocument.objects.filter(
            society=society
        )

        for doc in documents:
            if doc.file:
                z.write(
                    doc.file.path,
                    f"documents/{doc.file.name.split('/')[-1]}"
                )

        # 4. Templates
        templates = LegalArtifactTemplate.objects.all()

        for t in templates:
            if t.template_body:
                filename = f"templates/{t.artifact_type}_{t.id}.txt"
                z.writestr(filename, t.template_body)

        # 5. Metadata
        z.writestr(
            "meta.json",
            json.dumps({
                "generated_at": datetime.utcnow().isoformat(),
                "society_id": society.id,
                "society_name": society.name
            }, indent=2)
        )

    buffer.seek(0)
    return buffer.read()

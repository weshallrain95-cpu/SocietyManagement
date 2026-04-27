from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from statutory.models import SocietyLegalDocument, LegalArtifactTemplate
from society.models import Society


@api_view(["POST"])
def upload_artifact(request):
    society_id = request.POST.get("society_id")
    artifact_code = request.POST.get("artifact_code")
    uploaded_file = request.FILES.get("file")
    # ✅ Allow only PDF
    if uploaded_file:
        if not uploaded_file.name.lower().endswith(".pdf"):
            return Response(
                {"error": "Only PDF files allowed"},
                status=400
            )

    if not society_id or not artifact_code:
        return Response({"error": "Missing params"}, status=400)

    # ❌ Block bylaws upload
    if artifact_code == "BYLAW_DRAFT_MH":
        return Response({"error": "Bylaws cannot be uploaded"}, status=400)

    society = get_object_or_404(Society, id=society_id)

    template = LegalArtifactTemplate.objects.filter(
        artifact_code=artifact_code
    ).first()

    if not template:
        return Response({"error": "Invalid artifact"}, status=400)

    doc, _ = SocietyLegalDocument.objects.update_or_create(
        society=society,
        template=template,
        defaults={
            "file": uploaded_file,
            "status": "UPLOADED",
        },
    )

    return Response({
        "success": True,
        "artifact_code": artifact_code,
        "status": doc.status,
    })
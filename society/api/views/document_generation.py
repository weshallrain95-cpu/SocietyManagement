from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from society.models import Society
from statutory.document_engine.generator import DocumentGenerator
from statutory.preregistration.consent_engine import ConsentEngine


@api_view(["POST"])
def generate_document(request):

    society_id = request.data.get("society_id")
    artifact_code = request.data.get("artifact_code")
    data = request.data.get("data", {})

    if not society_id or not artifact_code:
        return Response(
            {"error": "society_id and artifact_code are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        society = Society.objects.get(id=society_id)
    except Society.DoesNotExist:
        return Response(
            {"error": "Society not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        # 🔥 SPECIAL CASE: PROMOTER CONSENT LETTERS
        from statutory.preregistration.consent_engine import ConsentEngine

        if artifact_code == "PROMOTER_CONSENT_LETTER_MH":
            ConsentEngine.initialize_requests(society)
            doc = DocumentGenerator.generate_consent_letters(society)

        else:
            doc = DocumentGenerator.generate_document(
                society,
                artifact_code,
                data
            )
    
    except Exception as e:
        print("🚨 GENERATION ERROR:", str(e))   # 👈 ADD THIS LINE

        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

    return Response({
        "message": "Document generated",
        "document_id": doc.id,
        "file": doc.file.url if doc.file else None
    })
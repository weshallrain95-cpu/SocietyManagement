from rest_framework.decorators import api_view
from rest_framework.response import Response

from statutory.document_engine.artifact_engine import derive_artifact_status


@api_view(["GET"])
def get_artifact_status(request):
    society_id = request.GET.get("society_id")

    if not society_id:
        return Response({"error": "society_id required"}, status=400)

    data = derive_artifact_status(society_id)

    return Response({
        "society_id": society_id,
        "documents": data
    })
from rest_framework.decorators import api_view
from rest_framework.response import Response
from society.models import Society

@api_view(["POST"])
def update_registration_docs(request):
    society_id = request.data.get("society_id")
    doc_type = request.data.get("doc_type")  # "REG_CERT" or "OC_CERT"
    file = request.FILES.get("file")

    if not society_id or not doc_type or not file:
        return Response({"error": "Missing fields"}, status=400)

    try:
        society = Society.objects.get(id=society_id)
    except Society.DoesNotExist:
        return Response({"error": "Society not found"}, status=404)

    if doc_type == "REG_CERT":
        society.registration_certificate = file

    elif doc_type == "OC_CERT":
        society.oc_certificate = file

    society.save()

    return Response({"message": "Saved"})
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from society.models import Society
from society.services_excel import generate_structure_excel


@api_view(["GET"])
def download_structure_excel(request):

    society_id = request.GET.get("society_id")

    if not society_id:
        return Response({"error": "society_id required"}, status=400)

    society = get_object_or_404(Society, id=society_id)

    # ✅ Generator already returns HttpResponse
    return generate_structure_excel(society)
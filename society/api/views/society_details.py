from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from society.models import Society


@api_view(["GET"])
def get_society_details(request):

    society_id = request.GET.get("society_id")

    if not society_id:
        return Response({"error": "society_id required"}, status=400)

    society = get_object_or_404(Society, id=society_id)

    return Response({
        "id": society.id,
        "name": society.name,

        # 🔥 LEGAL IDENTITY
        "registration_number": society.registration_number,
        "registration_date": society.registration_date,
        "district": society.district,
        "registrar_office": society.registrar_office,

        # 🔥 LEGAL STATUS
        "legal_status": society.legal_status,

        # 🔥 OPTIONAL FUTURE
        "state_code": society.state_code,
    })
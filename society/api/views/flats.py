from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from society.models import Society, Flat


@api_view(["GET"])
def get_flats(request):
    society_id = request.GET.get("society_id")

    if not society_id:
        return Response({"error": "society_id required"}, status=400)

    society = get_object_or_404(Society, id=society_id)

    flats = Flat.objects.filter(society=society).order_by("flat_number")

    data = [
        {
            "id": f.id,
            "flat_number": f.flat_number,
        }
        for f in flats
    ]

    return Response(data)
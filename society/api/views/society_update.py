from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from society.models import Society


@api_view(["POST"])
def update_society(request):
    society_id = request.data.get("society_id")
    capital = request.data.get("authorized_share_capital")

    if not society_id:
        return Response({"error": "society_id required"}, status=400)

    society = get_object_or_404(Society, id=society_id)

    # update ONLY what is passed (safe pattern)
    if capital is not None:
        society.authorized_share_capital = capital

    society.save(update_fields=["authorized_share_capital"])

    return Response({"status": "success"})
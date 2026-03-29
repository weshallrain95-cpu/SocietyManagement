from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from society.models import Society


@api_view(["POST"])
def complete_onboarding(request):
    society_id = request.data.get("society_id")

    if not society_id:
        return Response({"error": "society_id required"}, status=400)

    society = get_object_or_404(Society, id=society_id)

    # 🔒 LOCK ONBOARDING
    society.onboarding_stage = "ONBOARDING_COMPLETE"
    society.save()

    return Response({"status": "completed"})
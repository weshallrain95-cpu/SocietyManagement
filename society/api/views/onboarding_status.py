from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from society.models import Society, FlatOwnership


@api_view(["GET"])
def get_onboarding_status(request):

    society_id = request.GET.get("society_id")

    if not society_id:
        return Response({"error": "society_id required"}, status=400)

    society = get_object_or_404(Society, id=society_id)

    # ----------------------------
    # BASIC FLAGS
    # ----------------------------
    has_structure = society.flats.exists()

    has_ownership = FlatOwnership.objects.filter(
        flat__society=society,
        is_active=True
    ).exists()

    # ----------------------------
    # STAGE (SOURCE OF TRUTH)
    # ----------------------------
    stage = society.onboarding_stage

    # ----------------------------
    # RESPONSE
    # ----------------------------
    return Response({
        "society_id": society.id,
        "stage": stage,
        "has_structure": has_structure,
        "has_ownership": has_ownership,
        "allowed_actions": {
            "can_generate_structure": stage == "STRUCTURE_PENDING",

            # Upload only allowed BEFORE refinement
            "can_upload_ownership": stage in ["STRUCTURE_CREATED"],

            # 🔥 NEW
            "needs_refinement": stage == "OWNERSHIP_REFINEMENT_PENDING",

            "is_complete": stage == "ONBOARDING_COMPLETE",
        }
    })
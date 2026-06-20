from rest_framework.decorators import api_view
from rest_framework.response import Response


from society.onboarding_state_engine import (
    derive_onboarding_state,
    derive_allowed_actions,
)


@api_view(["GET"])
def get_onboarding_status(request):

    society_id = request.GET.get("society_id")

    if not society_id:
        return Response({"error": "society_id required"}, status=400)

    state = derive_onboarding_state(society_id)
    actions = derive_allowed_actions(society_id)

    return Response({
        "society_id": society_id,
        "stage": state,
        "allowed_actions": actions,
    })
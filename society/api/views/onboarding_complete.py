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

@api_view(["POST"])
def mark_governance_complete(request):
    society_id = request.data.get("society_id")

    if not society_id:
        return Response({"error": "society_id required"}, status=400)

    try:
        society = Society.objects.get(id=society_id)

        # move to operations stage
        society.onboarding_stage = "OPERATIONS_PENDING"
        society.save()

        return Response({
            "status": "governance_complete",
            "next_stage": society.onboarding_stage
        })

    except Society.DoesNotExist:
        return Response({"error": "Society not found"}, status=404)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
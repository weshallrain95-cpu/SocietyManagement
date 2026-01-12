from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from society.models import Society
from statutory.services import (
    get_next_legal_step,
    compute_risk,
    complete_current_step,
    finalize_society_if_allowed,
)


@api_view(["GET"])
def next_legal_step(request, society_id):
    try:
        society = Society.objects.get(id=society_id)
    except Society.DoesNotExist:
        return Response(
            {"detail": "No Society matches the given query."},
            status=status.HTTP_404_NOT_FOUND,
        )

    progress = get_next_legal_step(society)

    if progress is None:
        return Response(
            {
                "society": society.name,
                "message": "All legal stages completed",
                "status": "COMPLETED",
                "risk": "GREEN",
            },
            status=status.HTTP_200_OK,
        )

    risk = compute_risk(progress)

    return Response(
        {
            "society": society.name,
            "stage": progress.legal_stage.name,
            "status": progress.status,
            "risk": risk,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
def complete_legal_step(request, society_id):
    try:
        society = Society.objects.get(id=society_id)
    except Society.DoesNotExist:
        return Response(
            {"detail": "No Society matches the given query."},
            status=status.HTTP_404_NOT_FOUND,
        )

    completed, next_step = complete_current_step(society)

    if completed is None:
        return Response(
            {
                "society": society.name,
                "message": "All legal stages already completed",
            },
            status=status.HTTP_200_OK,
        )

    response = {
        "society": society.name,
        "completed_stage": completed.legal_stage.name,
    }

    if next_step:
        response["next_stage"] = next_step.legal_stage.name
        response["status"] = "IN_PROGRESS"
    else:
        response["status"] = "COMPLETED"

    return Response(response, status=status.HTTP_200_OK)


@api_view(["POST"])
def finalize_society_completion(request, society_id):
    try:
        society = Society.objects.get(id=society_id)
    except Society.DoesNotExist:
        return Response(
            {"detail": "No Society matches the given query."},
            status=status.HTTP_404_NOT_FOUND,
        )

    allowed, reason = finalize_society_if_allowed(society)

    if not allowed:
        return Response(
            {
                "society": society.name,
                "status": "NOT_FINALIZED",
                "reason": reason,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {
            "society": society.name,
            "status": "LEGALLY_COMPLETED",
            "message": "Society legally finalized with all mandatory documents",
        },
        status=status.HTTP_200_OK,
    )

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from society.models import Society

from society.finance.maintenance.preview_engine import (
    generate_scr31_preview,
)


@api_view(["POST"])
def scr31_preview(request):

    society_id = request.data.get("society_id")

    heads = request.data.get("heads", [])
    
    governance = request.data.get(
        "governance",
        {},
    )
    
    parking_allocations = request.data.get(
        "parking_allocations",
        []
    )

    if not society_id:

        return Response({
            "status": "failed",
            "message": "society_id required",
        }, status=400)

    society = get_object_or_404(
        Society,
        id=society_id,
    )

    preview = generate_scr31_preview(
        society=society,
        heads=heads,
        governance=governance,
        parking_allocations=parking_allocations,
    )

    return Response({

        "status": "success",

        "preview": preview,

    })
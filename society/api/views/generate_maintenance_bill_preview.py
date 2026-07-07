from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.shortcuts import get_object_or_404

from society.models import (
    Society,
    Flat,
)

from society.finance.kernel.scr33_simulation_engine import (
    simulate_scr33,
)

from society.finance.maintenance.maintenance_bill_artifact_generator import (
    MaintenanceBillArtifactGenerator,
)

import os

@api_view(["POST"])
def generate_maintenance_bill_preview(request):

    society_id = request.data.get(
        "society_id"
    )

    if not society_id:

        return Response({

            "status": "failed",

            "message":
                "society_id required",
        }, status=400)

    society = get_object_or_404(

        Society,

        id=society_id,
    )

    simulation = simulate_scr33(

        society=society,
    )

    preview_flat = (

        Flat.objects.filter(
            society=society
        )
        .order_by(
            "-carpet_area_sqft"
        )
        .first()
    )

    if not preview_flat:

        return Response({

            "status": "failed",

            "message":
                "No flats found",
        }, status=400)

    pdf_path = (

        MaintenanceBillArtifactGenerator.generate(

            society=society,

            simulation=simulation,

            preview_flat=preview_flat,
        )
    )

    return Response({

        "status": "success",

        "society_id":
            society.id,

        "preview_flat":
            preview_flat.flat_number,

        "preview_ready":
            True,

        "pdf_url":

            "/media/maintenance_preview_artifacts/"

            + os.path.basename(
                pdf_path
            ),
    })
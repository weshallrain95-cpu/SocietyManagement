from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from society.models import Society

from society.finance.kernel.scr33_simulation_engine import (
    simulate_scr33,
)


# =========================================================
# SCR33 CONTEXT
# =========================================================
#
# PURPOSE:
# Hydrate SCR33 financial simulation state.
#
# THIS API:
# ✔ NEVER persists
# ✔ NEVER posts accounting entries
# ✔ NEVER generates bills
# ✔ ONLY returns orchestration payload
#
# =========================================================


@api_view(["POST"])
def scr33_context(request):

    society_id = request.data.get(
        "society_id"
    )

    runtime_overrides = request.data.get(
        "runtime_overrides",
        {},
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

        runtime_overrides=runtime_overrides,
    )

    return Response({

        "status": "success",

        "effective_heads":
            simulation.get(
                "effective_heads",
                [],
            ),

        "preview":
            simulation.get(
                "preview",
                {},
            ),
    })
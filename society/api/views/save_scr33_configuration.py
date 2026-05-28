from decimal import Decimal

from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response

from society.models import (
    Society,
    MaintenanceCharge,
    ParkingRateConfiguration,
)

VALID_BASES = {

    "EQUAL",

    "AREA",

    "PER_SLOT",

    "PER_INLET",

    "MANUAL",

    "PERCENT_MAINT",
}


@api_view(["POST"])
@transaction.atomic
def save_scr33_configuration(request):

    society_id = request.data.get(
        "society_id"
    )

    maintenance_heads = request.data.get(
        "maintenance_heads",
        []
    )

    parking_children = request.data.get(
        "parking_children",
        []
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

    maintenance_saved = 0

    parking_saved = 0

    saved_codes = set()

    # ===================================================
    # SAVE MAINTENANCE HEADS
    # ===================================================

    for head in maintenance_heads:

        code = str(
            head.get("code", "")
        ).strip().upper()

        if not code:
            continue

        basis = str(
            head.get("basis", "")
        ).strip().upper()

        if basis not in VALID_BASES:
            continue

        try:

            rate = Decimal(
                str(
                    head.get("rate", 0)
                )
            )

        except Exception:

            rate = Decimal("0.00")

        MaintenanceCharge.objects.update_or_create(

            society=society,

            code=code,

            defaults={

                "name": head.get(
                    "name",
                    code,
                ),

                "basis": basis,

                "rate": rate,

                "is_active": bool(
                    head.get(
                        "is_active",
                        True,
                    )
                ),
            }
        )

        saved_codes.add(code)

        maintenance_saved += 1

    # ===================================================
    # DISABLE REMOVED HEADS
    # ===================================================

    MaintenanceCharge.objects.filter(
        society=society,
    ).exclude(
        code__in=saved_codes
    ).update(
        is_active=False
    )

    # ===================================================
    # SAVE PARKING GOVERNANCE
    # ===================================================

    for child in parking_children:

        parking_type = str(
            child.get(
                "parking_type",
                ""
            )
        ).strip().upper()

        if not parking_type:
            continue

        try:

            rate = Decimal(
                str(
                    child.get("rate", 0)
                )
            )

        except Exception:

            rate = Decimal("0.00")

        ParkingRateConfiguration.objects.update_or_create(

            society=society,

            parking_type=parking_type,

            defaults={

                "rate": rate,

                "is_active": bool(
                    child.get(
                        "is_active",
                        True,
                    )
                ),
            }
        )

        parking_saved += 1

    return Response({

        "status": "success",

        "maintenance_saved":
            maintenance_saved,

        "parking_saved":
            parking_saved,
    })
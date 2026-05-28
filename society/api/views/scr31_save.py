from decimal import Decimal
from django.utils import timezone

from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response

from society.models import (
    Society,
    Flat,
    FlatOccupancy,
    MaintenanceCharge,
    ParkingSlot,
    ParkingAllocation,
)


VALID_BASES = {
    "EQUAL",
    "AREA",
    "PER_SLOT",
    "PER_INLET",
    "MANUAL",
    "PERCENT_MAINT",
}

VALID_OCCUPANCY_TYPES = {
    "SELF",
    "RENTED",
}


@api_view(["POST"])
@transaction.atomic
def save_scr31_configuration(request):

    society_id = request.data.get("society_id")

    heads = request.data.get("heads", [])

    governance = request.data.get(
        "governance",
        {},
    )
    
    occupancy_updates = request.data.get(
        "occupancy_updates",
        []
    )

    parking_allocations = request.data.get(
        "parking_allocations",
        []
    )

    parking_matrix = request.data.get(
        "parking_matrix",
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

    billing_rule = getattr(
        society,
        "billing_rule",
        None,
    )
    saved_codes = set()

    maintenance_saved = 0

    occupancy_saved = 0

    parking_saved = 0

    # ===================================================
    # SAVE MAINTENANCE HEADS
    # ===================================================

    for head in heads:

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
                str(head.get("rate", 0))
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
    # DISABLE DESELECTED HEADS
    # ===================================================

    MaintenanceCharge.objects.filter(
        society=society,
    ).exclude(
        code__in=saved_codes
    ).update(
        is_active=False
    )

    # ===================================================
    # SAVE OCCUPANCY STATES
    # ===================================================

    for item in occupancy_updates:

        flat_id = item.get("flat_id")

        occupancy_type = str(
            item.get(
                "occupancy_type",
                "SELF",
            )
        ).strip().upper()

        if occupancy_type not in VALID_OCCUPANCY_TYPES:
            continue

        flat = Flat.objects.filter(
            society=society,
            id=flat_id,
        ).first()

        if not flat:
            continue

        FlatOccupancy.objects.update_or_create(

            flat=flat,

            defaults={
                "occupancy_type": occupancy_type,
            }
        )

        occupancy_saved += 1
    
    # ===================================================
    # SAVE PARKING MATRIX
    # ===================================================

    for row in parking_matrix:

        flat_id = row.get("flat_id")

        if not flat_id:
            continue

        flat = Flat.objects.filter(
            society=society,
            id=flat_id,
        ).first()

        if not flat:
            continue

        vehicle_map = [

            (
                "CAR",
                int(
                    row.get(
                        "four_wheeler",
                        0,
                    ) or 0
                ),
            ),

            (
                "BIKE",
                int(
                    row.get(
                        "two_wheeler",
                        0,
                    ) or 0
                ),
            ),

            (
                "EV",
                int(
                    row.get(
                        "ev_vehicle",
                        0,
                    ) or 0
                ),
            ),

            (
                "VISITOR",
                int(
                    row.get(
                        "visitor",
                        0,
                    ) or 0
                ),
            ),
        ]

        # -----------------------------------------------
        # REMOVE OLD ACTIVE AUTO ALLOCATIONS
        # -----------------------------------------------

        ParkingAllocation.objects.filter(

            flat=flat,

            parking_slot__society=society,

            parking_slot__slot_number__startswith="AUTO-",

        ).delete()

        # -----------------------------------------------
        # CREATE NEW SLOT + ALLOCATION STRUCTURE
        # -----------------------------------------------

        for parking_type, quantity in vehicle_map:

            if quantity <= 0:
                continue

            for index in range(quantity):

                slot_number = (

                    f"AUTO-"
                    f"{parking_type}-"
                    f"{flat.id}-"
                    f"{index + 1}"
                )

                parking_slot, created = (

                    ParkingSlot.objects.get_or_create(

                        society=society,

                        slot_number=slot_number,

                        defaults={

                            "parking_type":
                                parking_type,

                            "allocation_type":
                                "RESERVED",

                            "is_chargeable":
                                True,
                        }
                    )
                )

                ParkingAllocation.objects.update_or_create(

                    parking_slot=parking_slot,

                    defaults={

                        "flat": flat,

                        "allocated_on": (
                            timezone.now().date()
                        ),

                        "is_active": True,

                        "released_on": None,
                    }
                )

                parking_saved += 1

    # ===================================================
    # SAVE PARKING ALLOCATIONS
    # ===================================================

    active_parking_ids = []

    for item in parking_allocations:

        parking_slot_id = item.get(
            "parking_slot_id"
        )

        flat_id = item.get(
            "flat_id"
        )

        if not parking_slot_id:
            continue

        if not flat_id:
            continue

        parking_slot = (
            ParkingSlot.objects.filter(
                society=society,
                id=parking_slot_id,
            ).first()
        )

        if not parking_slot:
            continue

        flat = Flat.objects.filter(
            society=society,
            id=flat_id,
        ).first()

        if not flat:
            continue

        allocation, created = (
            ParkingAllocation.objects.update_or_create(

                parking_slot=parking_slot,

                defaults={

                    "flat": flat,

                    "allocated_on": (
                        timezone.now().date()
                    ),

                    "is_active": True,

                    "released_on": None,
                }
            )
        )

        active_parking_ids.append(
            allocation.id
        )

        parking_saved += 1

    # ===================================================
    # DEACTIVATE REMOVED PARKING ALLOCATIONS
    # ===================================================

    if parking_allocations:

        ParkingAllocation.objects.filter(
            parking_slot__society=society,
        ).exclude(
            id__in=active_parking_ids
        ).update(
            is_active=False
        )

    # ===================================================
    # BILLING GOVERNANCE
    # ===================================================

    if billing_rule:

        billing_rule.billing_cycle = governance.get(
            "billing_cycle",
            billing_rule.billing_cycle,
        )

        start_date = governance.get(
            "billing_start_date"
        )

        if start_date:
            billing_rule.billing_start_date = (
                start_date
            )

        billing_rule.due_day = governance.get(
            "due_day",
            billing_rule.due_day,
        )

        billing_rule.grace_days = governance.get(
            "grace_days",
            billing_rule.grace_days,
        )

        billing_rule.interest_rules = (
            governance.get(
                "interest_rules",
                {},
            )
        )

        billing_rule.penalty_rules = (
            governance.get(
                "penalty_rules",
                {},
            )
        )

        billing_rule.save()

    

    return Response({

        "status": "success",

        "maintenance_saved": maintenance_saved,

        "occupancy_saved": occupancy_saved,

        "governance_saved": True,

        "parking_saved": parking_saved,

    })
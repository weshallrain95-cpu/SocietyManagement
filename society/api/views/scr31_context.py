from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from society.models import (
    Society,
    Flat,
    ParkingSlot,
    ParkingAllocation,
)

from society.finance.maintenance.registry.hydration import (
    get_hydrated_maintenance_heads,
)


@api_view(["GET"])
def scr31_context(request):

    society_id = request.GET.get("society_id")

    if not society_id:

        return Response({
            "status": "failed",
            "message": "society_id required",
        }, status=400)

    society = get_object_or_404(
        Society,
        id=society_id,
    )

    maintenance_heads = (
        get_hydrated_maintenance_heads(society)
    )

    occupancy_selection = []
    
    parking_slots = []

    parking_allocations = []

    flats = Flat.objects.filter(
        society=society
    ).select_related(
        "wing_ref",
        "occupancy",
    )

    for flat in flats:

        occupancy = getattr(
            flat,
            "occupancy",
            None,
        )

        occupancy_type = getattr(
            occupancy,
            "occupancy_type",
            "SELF",
        )

        occupancy_selection.append({

            "flat_id": flat.id,

            "flat_number": flat.flat_number,

            "wing": (
                flat.wing_ref.name
                if flat.wing_ref
                else ""
            ),

            "occupancy_type": occupancy_type,
        })
        
        # =====================================
    # PARKING SLOT HYDRATION
    # =====================================

    slots = ParkingSlot.objects.filter(
        society=society
    )

    for slot in slots:

        parking_slots.append({

            "parking_slot_id": slot.id,

            "slot_number": slot.slot_number,

            "parking_type": (
                slot.parking_type
            ),

            "allocation_type": (
                slot.allocation_type
            ),

            "is_chargeable": (
                slot.is_chargeable
            ),
        })

    # =====================================
    # PARKING ALLOCATION HYDRATION
    # =====================================

    allocations = (
        ParkingAllocation.objects.filter(
            parking_slot__society=society,
            is_active=True,
        ).select_related(
            "flat",
            "parking_slot",
        )
    )

    for allocation in allocations:

        parking_allocations.append({

            "parking_slot_id": (
                allocation.parking_slot.id
            ),

            "slot_number": (
                allocation.parking_slot.slot_number
            ),

            "flat_id": (
                allocation.flat.id
            ),

            "flat_number": (
                allocation.flat.flat_number
            ),
        })

    billing_rule = getattr(
        society,
        "billing_rule",
        None,
    )
    
    default_interest_rules = {

        "enabled": True,

        "rate": 21,

        "after_days": 0,
    }

    default_penalty_rules = {

        "enabled": False,

        "type": "FLAT",

        "value": 500,

        "after_days": 15,
    }

    default_reminder_rules = {

        "enabled": True,

        "before_due_days": 3,

        "on_due_date": True,

        "after_due_days": 5,
    }

    default_automation_rules = {

        "auto_generate_bills": True,

        "auto_apply_interest": True,

        "auto_apply_penalty": True,

        "auto_send_reminders": True,
    }

    default_parking_rules = {

        "enabled": False,

        "parking_mode": "FREE",

        "billing_basis": "PER_SLOT",

        "allocation_based": False,

        "rate": 0,
    }

    governance = {

    # =====================================
    # BILLING CYCLE GOVERNANCE
    # =====================================

    "billing_cycle": (

        billing_rule.billing_cycle

        if billing_rule
        else "MONTHLY"
    ),

    "billing_start_date": (

        str(
            billing_rule.billing_start_date
        )

        if (
            billing_rule
            and billing_rule.billing_start_date
        )

        else None
    ),

    "due_day": (

        billing_rule.due_day

        if billing_rule
        else 10
    ),

    "grace_days": (

        billing_rule.grace_days

        if billing_rule
        else 5
    ),
    
    # =====================================
    # NON OCCUPANCY GOVERNANCE
    # =====================================

    "non_occupancy": {

        "enabled": True,

        "rate": 10,

        "apply_interest": True,

        "apply_penalty": True,
    },
    # =====================================
    # PARKING GOVERNANCE
    # =====================================

    "parking": (
        default_parking_rules
    ),

    # =====================================
    # INTEREST GOVERNANCE
    # =====================================

    "interest_rules": (

        {

            **default_interest_rules,

            **(
                billing_rule.interest_rules

                if (
                    billing_rule
                    and billing_rule.interest_rules
                )

                else {}
            )
        }
    ),

    # =====================================
    # PENALTY GOVERNANCE
    # =====================================

    "penalty_rules": (

        {

            **default_penalty_rules,

            **(
                billing_rule.penalty_rules

                if (
                    billing_rule
                    and billing_rule.penalty_rules
                )

                else {}
            )
        }
    ),

    # =====================================
    # REMINDER GOVERNANCE
    # =====================================

    "reminder_rules": (
        default_reminder_rules
    ),

    # =====================================
    # AUTOMATION GOVERNANCE
    # =====================================

    "automation": (
        default_automation_rules
    )
}
    return Response({

        "status": "success",

        "maintenance_heads": maintenance_heads,
        "occupancy_selection": occupancy_selection,
        "governance": governance,
        "parking_slots": parking_slots,

        "parking_allocations":
            parking_allocations,

    })
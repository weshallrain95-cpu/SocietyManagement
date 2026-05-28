from copy import deepcopy

from society.finance.maintenance.registry.hydration import (
    get_hydrated_maintenance_heads,
)

from society.finance.maintenance.preview_engine import (
    generate_scr31_preview,
)

from society.models import (
    ParkingAllocation,
    ParkingRateConfiguration,
)

# =========================================================
# SCR33 SIMULATION ENGINE
# =========================================================
#
# PURPOSE:
# Hydrate persisted governance truth and apply
# runtime UI mutations WITHOUT persistence.
#
# THIS ENGINE:
# ✔ NEVER writes to DB
# ✔ NEVER posts accounting entries
# ✔ NEVER generates artifacts
# ✔ ONLY simulates runtime financial state
#
# =========================================================


def simulate_scr33(
    society,
    runtime_overrides=None,
):

    runtime_overrides = (
        runtime_overrides or {}
    )

    # =====================================================
    # LOAD PERSISTED MAINTENANCE HEADS
    # =====================================================

    persisted_heads = (
        get_hydrated_maintenance_heads(
            society
        )
    )

    effective_heads = deepcopy(
        persisted_heads
    )

    # =====================================================
    # HYDRATE PARKING CHILD ROWS
    # =====================================================

    parking_summary = {

        "CAR": 0,

        "BIKE": 0,

        "EV": 0,

        "VISITOR": 0,
    }

    parking_allocations = (
        ParkingAllocation.objects.filter(
            parking_slot__society=society,
            is_active=True,
        ).select_related(
            "parking_slot"
        )
    )

    for allocation in parking_allocations:

        parking_type = (
            allocation
            .parking_slot
            .parking_type
        )

        if (
            parking_type
            in parking_summary
        ):

            parking_summary[
                parking_type
            ] += 1

    default_parking_rates = {

        "CAR": 250,

        "BIKE": 100,

        "EV": 500,

        "VISITOR": 0,
    }

    for parking_type, default_rate in (
        default_parking_rates.items()
    ):

        ParkingRateConfiguration.objects.get_or_create(

            society=society,

            parking_type=parking_type,

            defaults={

                "rate": default_rate,

                "is_active": True,
            }
        )

    parking_rate_configs = (
        ParkingRateConfiguration.objects.filter(
            society=society
        )
    )

    parking_rate_map = {

        config.parking_type: {

            "rate": float(config.rate),

            "is_active": config.is_active,
        }

        for config in parking_rate_configs
    }

    for head in effective_heads:

        if (
            head.get("code")
            != "PARKING_CHARGES"
        ):
            continue

        head["children"] = [

            {
                "code":
                    "FOUR_WHEELER",

                "label":
                    "Four Wheeler",

                "basis":
                    "PER_SLOT",

                "rate":
                    parking_rate_map.get(
                        "CAR",
                        {}
                    ).get(
                        "rate",
                        250,
                    ),

                "count":
                    parking_summary["CAR"],
                
                "is_active":
                    parking_rate_map.get(
                        "CAR",
                        {}
                    ).get(
                        "is_active",
                        True,
                    ),
            },

            {
                "code":
                    "TWO_WHEELER",

                "label":
                    "Two Wheeler",

                "basis":
                    "PER_SLOT",

                "rate":
                    parking_rate_map.get(
                        "BIKE",
                        {}
                    ).get(
                        "rate",
                        100,
                    ),

                "count":
                    parking_summary["BIKE"],
                
                "is_active":
                    parking_rate_map.get(
                        "BIKE",
                        {}
                    ).get(
                        "is_active",
                        True,
                    ),
            },

            {
                "code":
                    "EV",

                "label":
                    "EV Vehicle",

                "basis":
                    "PER_SLOT",

                "rate":
                    parking_rate_map.get(
                        "EV",
                        {}
                    ).get(
                        "rate",
                        500,
                    ),

                "count":
                    parking_summary["EV"],
                
                "is_active":
                    parking_rate_map.get(
                        "EV",
                        {}
                    ).get(
                        "is_active",
                        True,
                    ),
            },

            {
                "code":
                    "VISITOR",

                "label":
                    "Visitor Parking",

                "basis":
                    "PER_SLOT",

                "rate":
                    parking_rate_map.get(
                        "VISITOR",
                        {}
                    ).get(
                        "rate",
                        0,
                    ),

                "count":
                    parking_summary[
                        "VISITOR"
                    ],
                
                "is_active":
                    parking_rate_map.get(
                        "VISITOR",
                        {}
                    ).get(
                        "is_active",
                        True,
                    ),
            },
        ]
    # =====================================================
    # APPLY RUNTIME EDITS
    # =====================================================

    edited_heads = (
        runtime_overrides.get(
            "edited_heads",
            []
        )
    )

    for edited in edited_heads:

        code = edited.get("code")

        if not code:
            continue

        for head in effective_heads:

            if head["code"] != code:
                continue

            if "basis" in edited:

                head["basis"] = (
                    edited["basis"]
                )

            if "rate" in edited:

                head["rate"] = (
                    edited["rate"]
                )

            if "is_active" in edited:

                head["is_active"] = (
                    edited["is_active"]
                )

    # =====================================================
    # APPLY DISABLED HEADS
    # =====================================================

    disabled_heads = set(

        runtime_overrides.get(
            "disabled_heads",
            []
        )
    )

    for head in effective_heads:

        if head["code"] in disabled_heads:

            head["is_active"] = False

    # =====================================================
    # APPLY NEW RUNTIME HEADS
    # =====================================================

    new_heads = (
        runtime_overrides.get(
            "new_heads",
            []
        )
    )

    for new_head in new_heads:

        effective_heads.append({

            "code": (
                new_head.get("code")
                or "CUSTOM"
            ),

            "name": (
                new_head.get("name")
                or "Custom Head"
            ),

            "basis": (
                new_head.get("basis")
                or "EQUAL"
            ),

            "rate": (
                new_head.get("rate")
                or 0
            ),

            "is_active": True,
        })

    # =====================================================
    # PREVIEW ENGINE
    # =====================================================

    simulation_heads = [

        head

        for head in effective_heads

        if head.get("is_active")
    ]

    preview_heads = []

    for head in simulation_heads:

        preview_heads.append({

            "code":
                head.get("code"),

            "name":
                head.get("name"),

            "basis":
                head.get("basis"),

            "rate":
                head.get("rate"),

            "is_active":
                head.get("is_active", True),

            "applicability":
                head.get(
                    "applicability",
                    "ALL_FLATS",
                ),
        })

    preview = generate_scr31_preview(

        society=society,

        heads=preview_heads,
    )

    # =====================================================
    # RETURN SCR33 ORCHESTRATION PAYLOAD
    # =====================================================

    return {

        "effective_heads":
            effective_heads,

        "preview":
            preview,
    }
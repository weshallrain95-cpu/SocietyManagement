from society.models import MaintenanceCharge

from society.finance.maintenance.registry.maintenance_heads import (
    DEFAULT_MAINTENANCE_HEADS,
)

EXCLUDED_CODES = {

    # -----------------------------------------
    # EVENT / TRANSACTIONAL CHARGES
    # -----------------------------------------

    "TRANSFER_FEES",
    "TRANSFER_PREMIUM",
    "MOVE_IN_OUT",
    "CHEQUE_BOUNCE",
    "INTEREST_ON_DUES",
    "LATE_PAYMENT",
    "FESTIVAL_CONTRIBUTIONS",


    # -----------------------------------------
    # SOCIETY INCOME / NON-MEMBER BILLING
    # -----------------------------------------

    "BANK_INTEREST",
    "TOWER_RENT",
    "VISITOR_PARKING",

}

def get_hydrated_maintenance_heads(society):

    existing_charges = MaintenanceCharge.objects.filter(
        society=society
    )

    existing_by_code = {
        charge.code: charge
        for charge in existing_charges
    }

    hydrated = []

    registry_codes = set()

    # =====================================================
    # HYDRATE DEFAULT REGISTRY HEADS
    # =====================================================

    for item in DEFAULT_MAINTENANCE_HEADS:

        code = item["code"]

        registry_codes.add(code)

        existing = existing_by_code.get(code)

        hydrated.append({

            "code": code,

            "name": (
                existing.name
                if existing else item["name"]
            ),

            "description": item["description"],

            "category": item["category"],

            "basis": (

            item["default_basis"]

            if not item["editable_basis"]

            else (

                "PER_INLET"

                if existing
                and existing.basis == "PER_UNIT"

                else (

                    "MANUAL"

                    if existing
                    and (
                        existing.basis is None
                        or str(existing.basis).strip() == ""
                    )

                    else (

                        existing.basis
                        if existing
                        else item["default_basis"]
                    )
                )
            )
        ),
            
            "rate": (
                str(existing.rate)
                if existing else item["suggested_rate"]
            ),

            "is_active": (
                existing.is_active
                if existing else item["enabled_by_default"]
            ),

            "editable_basis": item["editable_basis"],

            "editable_rate": item["editable_rate"],

            "recommended": item["recommended"],

            "applicability": item["applicability"],

            "configured": bool(existing),

            "custom": False,
        })

    # =====================================================
    # INCLUDE CUSTOM USER-DEFINED CHARGES
    # =====================================================

    for charge in existing_charges:

        if charge.code in EXCLUDED_CODES:
            continue
        if charge.code in registry_codes:
            continue

        hydrated.append({

            "code": charge.code,

            "name": charge.name,

            "description": "",

            "category": "CUSTOM",

            "basis": (

                "PER_INLET"

                if charge.basis == "PER_UNIT"

                else (

                    "MANUAL"

                    if (
                        charge.basis is None
                        or str(charge.basis).strip() == ""
                    )

                    else charge.basis
                )
            ),

            "rate": str(charge.rate),

            "is_active": charge.is_active,

            "editable_basis": True,

            "editable_rate": True,

            "recommended": False,

            "applicability": "ALL_FLATS",

            "configured": True,

            "custom": True,
        })

    return hydrated
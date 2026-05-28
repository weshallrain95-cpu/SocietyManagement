from decimal import Decimal

from society.models import (
    Flat,
    ParkingAllocation,
)

def money(value):

    return Decimal(value).quantize(
        Decimal("0.01")
    )

SUPPORTED_BASES = {
    "EQUAL",
    "AREA",
    "PER_SLOT",
    "PER_INLET",
    "MANUAL",
    "PERCENT_MAINT",
}


def calculate_preview_amount(
    flat,
    head,
    parking_slot_map,
):

    basis = head.get("basis")

    rate = Decimal(
        str(
            head.get("rate") or 0
        )
    )

    applicability = head.get(
        "applicability",
        "ALL_FLATS",
    )



    # ---------------------------------------------------
    # RENTED ONLY
    # ---------------------------------------------------

    if applicability == "RENTED_ONLY":

        occupancy = getattr(
            flat,
            "occupancy",
            None,
        )

        occupancy_type = getattr(
            occupancy,
            "occupancy_type",
            None,
        )

        if occupancy_type != "RENTED":
            return Decimal("0.00")

    # ---------------------------------------------------
    # PARKING ONLY
    # ---------------------------------------------------

    if applicability == "PARKING_ONLY":

        slots = parking_slot_map.get(
            flat.id,
            0,
        )

        if slots <= 0:
            return Decimal("0.00")

    # ---------------------------------------------------
    # EQUAL DISTRIBUTION
    # ---------------------------------------------------

    if basis == "EQUAL":
        return money(rate)

    # ---------------------------------------------------
    # AREA BASED
    # ---------------------------------------------------

    if basis == "AREA":

        area = (
            getattr(flat, "carpet_area_sqft", None)
            or 0
        )

        return money(
            Decimal(str(area)) * rate
        )

    # ---------------------------------------------------
    # PARKING SLOT BASED
    # ---------------------------------------------------

    if basis == "PER_SLOT":

        slots = parking_slot_map.get(
            flat.id,
            0,
        )

        return money(
            Decimal(str(slots)) * rate
        )

    # ---------------------------------------------------
    # WATER INLET BASED
    # ---------------------------------------------------

    if basis == "PER_INLET":

        inlets = (
            getattr(flat, "water_inlets", None)
            or 1
        )

        return money(
            Decimal(str(inlets)) * rate
        )

    # ---------------------------------------------------
    # MANUAL
    # ---------------------------------------------------

    if basis == "MANUAL":
        return money(rate)

    # ---------------------------------------------------
    # PERCENT OF MAINTENANCE
    # ---------------------------------------------------

    # handled after base computation

    return Decimal("0.00")


def generate_scr31_preview(
    society,
    heads,
    governance=None,
    parking_allocations=None,
):

    flats = Flat.objects.filter(
        society=society
    ).select_related(
        "wing_ref"
    )

    flat_results = []

    society_total = Decimal("0.00")

    highest_bill = Decimal("0.00")

    lowest_bill = None

    wing_totals = {}

    # ===================================================
    # PARKING SLOT MAP
    # ===================================================

    parking_slot_map = {}

    allocations = (
        ParkingAllocation.objects.filter(
            parking_slot__society=society,
            is_active=True,
        )
    )

    for allocation in allocations:

        flat_id = allocation.flat_id

        parking_slot_map.setdefault(
            flat_id,
            0,
        )

        parking_slot_map[flat_id] += 1

    # ===================================================
    # FLAT-WISE SIMULATION
    # ===================================================

    for flat in flats:

        flat_total = Decimal("0.00")

        breakdown = []

        base_maintenance = Decimal("0.00")

        # -----------------------------------------------
        # FIRST PASS
        # -----------------------------------------------

        for head in heads:

            if not head.get("is_active"):
                continue

            amount = calculate_preview_amount(
                flat,
                head,
                parking_slot_map,
            )

            breakdown.append({
                "code": head.get("code"),
                "name": head.get("name"),
                "amount": str(amount),
            })

            flat_total += amount

            if head.get("basis") != "PERCENT_MAINT":
                base_maintenance += amount

        # -----------------------------------------------
        # SECOND PASS
        # PERCENT_MAINT
        # -----------------------------------------------

        for row in breakdown:

            matching = next(
                (
                    h for h in heads
                    if h.get("code") == row["code"]
                ),
                None
            )

            if not matching:
                continue

            if matching.get("basis") != "PERCENT_MAINT":
                continue

            applicability = matching.get(
                "applicability",
                "ALL_FLATS",
            )

            # -----------------------------------
            # RENTED ONLY
            # -----------------------------------

            if applicability == "RENTED_ONLY":

                occupancy = getattr(
                    flat,
                    "occupancy",
                    None,
                )

                occupancy_type = getattr(
                    occupancy,
                    "occupancy_type",
                    None,
                )

                if occupancy_type != "RENTED":

                    row["amount"] = "0.00"

                    continue

            percent = Decimal(
                str(matching.get("rate", 0))
            )

            amount = money(
                base_maintenance
                * percent
                / Decimal("100")
            )

            row["amount"] = str(amount)

            flat_total += amount

        # -----------------------------------------------
        # WING TOTALS
        # -----------------------------------------------

        wing_name = (
            flat.wing_ref.name
            if flat.wing_ref
            else "UNKNOWN"
        )

        wing_totals.setdefault(
            wing_name,
            Decimal("0.00")
        )

        wing_totals[wing_name] += flat_total

        # -----------------------------------------------
        # SOCIETY TOTALS
        # -----------------------------------------------

        society_total += flat_total

        if flat_total > highest_bill:
            highest_bill = flat_total

        if (
            lowest_bill is None
            or flat_total < lowest_bill
        ):
            lowest_bill = flat_total

        flat_results.append({

            "flat_id": flat.id,

            "flat_number": flat.flat_number,

            "wing": wing_name,

            "total": str(money(flat_total)),

            "breakdown": breakdown,
        })

    # ===================================================
    # HEADWISE FINANCIAL IMPACT
    # ===================================================

    headwise_summary_map = {}

    for flat_data in flat_results:

        wing = flat_data.get(
            "wing"
        )

        breakdown = flat_data.get(
            "breakdown",
            []
        )

        for row in breakdown:

            code = row.get("code")

            if not code:
                continue

            amount = Decimal(
                str(
                    row.get(
                        "amount",
                        0
                    )
                )
            )

            

            if code not in headwise_summary_map:

                headwise_summary_map[
                    code
                ] = {

                    "code": code,

                    "name":
                        row.get("name"),

                    "basis": "",

                    "rate": "",

                    "per_flat":
                        str(amount),

                    "wing_totals": {},

                    "total":
                        Decimal("0.00"),
                }

                matching_head = next(

                    (
                        h for h in heads

                        if h.get("code")
                        == code
                    ),

                    None,
                )

                if matching_head:

                    headwise_summary_map[
                        code
                    ]["basis"] = (

                        matching_head.get(
                            "basis",
                            "",
                        )
                    )

                    headwise_summary_map[
                        code
                    ]["rate"] = str(

                        matching_head.get(
                            "rate",
                            "",
                        )
                    )

            headwise_summary_map[
                code
            ]["total"] += amount

            
            wing_totals_map = (

                headwise_summary_map[
                    code
                ]["wing_totals"]
            )

            wing_totals_map.setdefault(

                wing,
                Decimal("0.00")
            )

            wing_totals_map[
                wing
            ] += amount

    headwise_summary = []

    for _, summary in (
        headwise_summary_map.items()
    ):

        summary["total"] = str(

            money(
                summary["total"]
            )
        )

        summary["wing_totals"] = {

            wing: str(
                money(total)
            )

            for wing, total in

            summary[
                "wing_totals"
            ].items()
        }

        headwise_summary.append(
            summary
        )

    # ===================================================
    # SUMMARY
    # ===================================================

    flat_count = len(flat_results)

    average_bill = (
        society_total / flat_count
        if flat_count > 0
        else Decimal("0.00")
    )

    governance_preview = {}

    if governance:

        governance_preview = {

            # =================================
            # BILLING CYCLE
            # =================================

            "billing_cycle": governance.get(
                "billing_cycle"
            ),

            "billing_start_date": governance.get(
                "billing_start_date"
            ),

            "due_day": governance.get(
                "due_day"
            ),

            "grace_days": governance.get(
                "grace_days"
            ),

            # =================================
            # NON OCCUPANCY
            # =================================

            "non_occupancy": governance.get(
                "non_occupancy",
                {},
            ),

            # =================================
            # PARKING
            # =================================

            "parking": governance.get(
                "parking",
                {},
            ),

            # =================================
            # INTEREST
            # =================================

            "interest_rules": governance.get(
                "interest_rules",
                {},
            ),

            # =================================
            # PENALTY
            # =================================

            "penalty_rules": governance.get(
                "penalty_rules",
                {},
            ),

            # =================================
            # REMINDERS
            # =================================

            "reminder_rules": governance.get(
                "reminder_rules",
                {},
            ),

            # =================================
            # AUTOMATION
            # =================================

            "automation": governance.get(
                "automation",
                {},
            ),
        }

    return {

        "society_total": str(
            money(society_total)
        ),

        "average_bill": str(
            money(average_bill)
        ),

        "highest_bill": str(
            money(highest_bill)
        ),

        "lowest_bill": str(
            money(lowest_bill)
            if lowest_bill is not None
            else Decimal("0.00")
        ),

        "wing_totals": [
            {
                "wing": wing,
                "total": str(
                    money(total)
                ),
            }
            for wing, total in wing_totals.items()
        ],

        "sample_flats": flat_results[:10],
        "headwise_summary":
            headwise_summary,
        "governance_preview": governance_preview,
    }
from decimal import Decimal
from calendar import monthrange

from society.models import (
    BankAccount,
    FlatOccupancy,
    FlatOwnership,
    FlatOwner,
    ParkingAllocation,
    ParkingRateConfiguration,
    MemberReceivable,
)


def build_maintenance_bill_payload(flat_bill):

    society = flat_bill.bill.society
    flat = flat_bill.flat

    # =====================================================
    # MEMBER HYDRATION
    # =====================================================

    member_name = "-"

    ownership = (
        FlatOwnership.objects.filter(
            flat=flat,
            is_active=True,
        )
        .order_by("-id")
        .first()
    )

    if ownership:

        owner = (
            FlatOwner.objects.filter(
                ownership=ownership
            )
            .select_related("person")
            .first()
        )

        if owner and owner.person:

            member_name = (
                owner.person.full_name
            )

    # =====================================================
    # OCCUPANCY
    # =====================================================

    occupancy_status = "UNKNOWN"

    occupancy = (
        FlatOccupancy.objects.filter(
            flat=flat
        )
        .order_by("-declared_on")
        .first()
    )

    if occupancy:

        occupancy_status = (
            occupancy.occupancy_type
        )
    
    
    # =====================================================
    # BANKING
    # =====================================================

    active_bank_account = (
        BankAccount.objects.filter(
            society=society,
            is_active=True,
        )
        .order_by(
            "treasury_role",
            "name",
        )
        .first()
    )

    bank_name = "-"

    account_number = "-"

    ifsc = "-"

    upi_id = "-"

    if active_bank_account:

        bank_name = (
            active_bank_account.bank_name
        )

        account_number = (
            active_bank_account.account_number
        )

        ifsc = (
            active_bank_account.ifsc
        )

        upi_id = (
            active_bank_account.upi_id
        )
    
    # =====================================================
    # CHARGE LINES
    # =====================================================

    charges = []

    core_total = Decimal("0.00")

    active_heads = {

        c.code: c

        for c in
        society.maintenance_charges.filter(
            is_active=True,
        )
    }

    for index, line in enumerate(
        flat_bill.lines.all(),
        start=1,
    ):

        amount = Decimal(
            str(line.amount)
        )

        core_total += amount

        config = active_heads.get(
            line.charge_code
        )
        
        excluded_codes = {

            "NON_OCCUPANCY",

            "PARKING_CHARGES",

            "INTEREST_ON_DUES",

            "LATE_PAYMENT",
        }

        if (
            line.charge_code in excluded_codes
            or
            line.charge_code.startswith("PARKING_")
        ):
            continue
        
        charges.append({

            "sr_no": index,

            "name":
                line.charge_name,

            "basis":

                config.basis

                if config
                else "-",

            "rate":

                str(config.rate)

                if config
                else "-",

            "amount":
                str(amount),
        })

    # =====================================================
    # NON OCCUPANCY
    # =====================================================

    non_occupancy_amount = Decimal("0.00")

    non_occupancy_line = (
        flat_bill.lines.filter(
            charge_code="NON_OCCUPANCY"
        )
        .first()
    )

    if non_occupancy_line:

        non_occupancy_amount = Decimal(
            str(
                non_occupancy_line.amount
            )
        )

    # =====================================================
    # PARKING
    # =====================================================

    parking_rows = []

    parking_total = Decimal("0.00")

    allocations = (
        ParkingAllocation.objects.filter(
            flat=flat,
            is_active=True,
        ).select_related(
            "parking_slot",
        )
    )

    for allocation in allocations:

        parking_type = (
            allocation.parking_slot.parking_type
        )

        config = (
            ParkingRateConfiguration.objects.filter(
                society=society,
                parking_type=parking_type,
                is_active=True,
            )
            .first()
        )

        rate = (
            config.rate
            if config
            else Decimal("0.00")
        )

        amount = rate

        parking_rows.append({

            "vehicle_type":

                {
                    "CAR": "Four Wheeler",
                    "BIKE": "Two Wheeler",
                    "EV": "EV Vehicle",
                    "VISITOR": "Visitor Parking",
                }.get(
                    parking_type,
                    parking_type,
                ),

            "rate":
                str(rate),

            "quantity":
                1,

            "amount":
                str(amount),
        })

        parking_total += amount

    # =====================================================
    # SPECIAL RECOVERY
    # =====================================================

    special_total = (
        non_occupancy_amount
        +
        parking_total
    )

    gross_bill_amount = (
        core_total
        +
        special_total
    )

    # =====================================================
    # ACCOUNT POSITION
    # =====================================================

    receivables = (
        MemberReceivable.objects.filter(
            society=society,
            flat=flat,
            status__in=[
                "OPEN",
                "PARTIAL",
            ],
        )
    )

    previous_outstanding = Decimal("0.00")

    advance_balance = Decimal("0.00")

    interest_levied = Decimal("0.00")

    penalty_levied = Decimal("0.00")

    recovery_charges = Decimal("0.00")

    for receivable in receivables:

        source_type = str(
            receivable.source_type
        ).upper()

        amount = Decimal(
            str(
                receivable.outstanding_amount
            )
        )

        if "ADVANCE" in source_type:

            advance_balance += amount

        elif "INTEREST" in source_type:

            interest_levied += amount

        elif "PENALTY" in source_type:

            penalty_levied += amount

        previous_outstanding += amount

    net_adjustment = (

        previous_outstanding

        +

        interest_levied

        +

        penalty_levied

        +

        recovery_charges

        -

        advance_balance
    )

    net_payable = (
        gross_bill_amount
        +
        net_adjustment
    )

    # =====================================================
    # BILL METADATA
    # =====================================================

    maintenance_bill = flat_bill.bill

    billing_month = (
        maintenance_bill.billing_month
    )

    days_in_month = monthrange(
        billing_month.year,
        billing_month.month,
    )[1]

    billing_period = (

        f"{billing_month}"

        f" to "

        f"{billing_month.replace(day=days_in_month)}"
    )

    bill_number = (
        maintenance_bill.bill_number
    )

    bill_date = (
        str(maintenance_bill.bill_date)
        if maintenance_bill.bill_date
        else ""
    )

    due_date = (
        str(maintenance_bill.due_date)
        if maintenance_bill.due_date
        else ""
    )
    
    # =====================================================
    # PAYLOAD
    # =====================================================

    payload = {

        "society": {

            "id": society.id,

            "name": society.name,

            "address": getattr(
                society,
                "address",
                "",
            ),
        },

        "member": {

            "member_name": member_name,

            "flat_number": getattr(
                flat,
                "flat_number",
                "-",
            ),

            "wing": getattr(
                flat,
                "wing",
                "-",
            ),

            "floor": getattr(
                flat,
                "floor",
                "-",
            ),

            "area": getattr(
                flat,
                "carpet_area_sqft",
                "-",
            ),

            "occupancy_status":
                occupancy_status,
                },

        "bill": {

            "bill_number":
                bill_number,

            "billing_month_label":

                billing_month.strftime(
                    "%B %Y"
                ),

            "bill_date":
                bill_date,

            "due_date":
                due_date,

            "billing_period":
                billing_period,

            "bill_category":
                "Monthly Maintenance",

            "days_in_period":
                str(days_in_month),
        },

        "special_recoveries": {

            "non_occupancy_amount":
                str(non_occupancy_amount),

            "parking_total":
                str(parking_total),

            "parking_rows":
                parking_rows,

            "total_special_recovery":
                str(special_total),
        },

        "charges":
            charges,

        "summary": {

            "core_maintenance_total":
                str(core_total),

            "special_recovery_total":
                str(special_total),

            "gross_bill_amount":
                str(gross_bill_amount),
        },

        "account_position": {

            "previous_outstanding":
                str(previous_outstanding),

            "advance_balance":
                str(advance_balance),

            "interest_levied":
                str(interest_levied),

            "penalty_levied":
                str(penalty_levied),

            "recovery_charges":
                str(recovery_charges),

            "net_adjustment":
                str(net_adjustment),

            "net_payable":
                str(net_payable),
        },

        "payment": {

            "bank_name":
                bank_name,

            "account_number":
                account_number,

            "ifsc":
                ifsc,

            "upi_id":
                upi_id,
        },

        "notes": [

            "Generated by SocietyOS",

        ],
    }

    return payload
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

from society.models import (
    FlatOccupancy,
    ParkingAllocation,
    ParkingRateConfiguration,
    MemberReceivable,
    MaintenanceCharge,
    FlatOwnership,
    FlatOwner,
    BankAccount,
)

from society.finance.maintenance.maintenance_engine import (
    calculate_flat_maintenance,
)

# =====================================================
# SCR35 MAINTENANCE BILL HYDRATION CONTRACT
# =====================================================
#
# PRINCIPLE:
#
# SCR35 hydrates directly from DB truth.
#
# SCR35 may use historical code for discovery,
# but never as a source of truth.
#
# Every field rendered in the artifact must map
# to an authoritative persisted model.
#
# -----------------------------------------------------
# SECTION: SOCIETY
# -----------------------------------------------------
#
# Source:
#   Society
#
# Fields:
#   society_id
#   society_name
#   society_address
#
# -----------------------------------------------------
# SECTION: MEMBER
# -----------------------------------------------------
#
# Sources:
#   Flat
#   FlatOwnership
#   FlatOwner
#   Person
#
# Fields:
#   member_name
#   flat_number
#   wing
#   floor
#   area
#
# -----------------------------------------------------
# SECTION: OCCUPANCY
# -----------------------------------------------------
#
# Source:
#   FlatOccupancy
#
# Rule:
#   Latest declared occupancy record wins.
#
# Fields:
#   occupancy_status
#
# -----------------------------------------------------
# SECTION: BILL CHARGES
# -----------------------------------------------------
#
# Sources:
#   MaintenanceCharge
#   calculate_flat_maintenance()
#
# Include:
#   Operational maintenance heads only.
#
# Exclude:
#   NON_OCCUPANCY
#   PARKING_CHARGES
#   INTEREST_ON_DUES
#   LATE_PAYMENT
#
# These belong to other sections.
#
# -----------------------------------------------------
# SECTION: SPECIAL RECOVERIES
# -----------------------------------------------------
#
# NON OCCUPANCY
#
# Sources:
#   FlatOccupancy
#
# Rule:
#   Apply only when occupancy_type == RENTED
#
# PARKING
#
# Sources:
#   ParkingAllocation
#   ParkingRateConfiguration
#
# Rule:
#   Allocation truth from ParkingAllocation.
#   Rate truth from ParkingRateConfiguration.
#
# -----------------------------------------------------
# SECTION: ACCOUNT POSITION
# -----------------------------------------------------
#
# Source:
#   MemberReceivable
#
# Fields:
#   previous_outstanding
#   advance_balance
#   interest_levied
#   penalty_levied
#   recovery_charges
#   net_adjustment
#
# -----------------------------------------------------
# SECTION: BANKING
# -----------------------------------------------------
#
# Source:
#   BankAccount
#
# Hydration:
#   All active accounts.
#
# Selection:
#   Deferred to SCR35 UX.
#
# -----------------------------------------------------
# SECTION: BILL METADATA
# -----------------------------------------------------
#
# Fields:
#   bill_number
#   bill_date
#   due_date
#   billing_period
#   days_in_period
#
# Source:
#   SCR35 generation context.
#
# =====================================================

def build_preview_bill_payload(
    society,
    simulation,
    preview_flat,
):

    # =====================================================
    # MEMBER NAME
    # =====================================================

    member_name = "-"

    ownership = (
        FlatOwnership.objects.filter(
            flat=preview_flat,
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
            flat=preview_flat
        )
        .order_by("-declared_on")
        .first()
    )

    if occupancy:

        occupancy_status = (
            occupancy.occupancy_type
        )

    # =====================================================
    # MEMBER BLOCK
    # =====================================================

    member_block = {

        "member_name":
            member_name,

        "flat_number":
            preview_flat.flat_number,

        "wing":

            preview_flat.wing_ref.name

            if getattr(
                preview_flat,
                "wing_ref",
                None,
            )

            else "-",

        "floor":
            preview_flat.floor,

        "area":
            getattr(
                preview_flat,
                "carpet_area_sqft",
                0,
            ),

        "occupancy_status":
            occupancy_status,
    }

    # =====================================================
    # SOCIETY
    # =====================================================

    society_block = {

        "id":
            society.id,

        "name":
            society.name,

        "address":
            getattr(
                society,
                "address",
                "",
            ),
    }

    # =====================================================
    # BILL GOVERNANCE
    # =====================================================
    
    # =====================================================
    # PREVIEW BILL METADATA
    # =====================================================

    today = timezone.now().date()

    due_date = (
        today
        + timedelta(days=15)
    )

    society_code = (
        society.name.strip()
        .split()[0]
        .upper()[:4]
    )

    preview_bill_number = (
        f"{society_code}"
        f"-MAIN-001-"
        f"{today.strftime('%m%y')}"
    )

    month_start = (
        today.replace(day=1)
    )

    if today.month == 12:

        next_month = (
            today.replace(
                year=today.year + 1,
                month=1,
                day=1,
            )
        )

    else:

        next_month = (
            today.replace(
                month=today.month + 1,
                day=1,
            )
        )

    month_end = (
        next_month
        - timedelta(days=1)
    )
    
    bill_block = {

        "bill_number":
            preview_bill_number,

        "billing_month_label":
            today.strftime(
                "%B %Y"
            ),

        "bill_date":
            str(today),

        "due_date":
            str(due_date),

        "billing_period":

            f"{month_start}"
            f" to "
            f"{month_end}",

        "bill_category":
            "Monthly Maintenance",

        "days_in_period":

            str(
                (
                    month_end
                    - month_start
                ).days
                + 1
            ),
    }

    # =====================================================
    # ACCOUNT POSITION
    # =====================================================
    print(
        "\nPREVIEW FLAT:",
        preview_flat.id,
        preview_flat.flat_number,
    )
    receivables = (
        MemberReceivable.objects.filter(
            society=society,
            flat=preview_flat,
            status__in=[
                "OPEN",
                "PARTIAL",
            ],
        )
    )

    total_outstanding = Decimal("0.00")

    advance_balance = Decimal("0.00")

    interest_outstanding = Decimal("0.00")

    penalty_outstanding = Decimal("0.00")

    for receivable in receivables:

        print(
            receivable.flat_id,
            receivable.source_type,
            receivable.outstanding_amount,
        )

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

            interest_outstanding += amount

        elif "PENALTY" in source_type:

            penalty_outstanding += amount

        total_outstanding += amount
    
    print(
        "\nACCOUNT TOTAL =",
        total_outstanding,
    )
    account_position = {

        "previous_outstanding":
            str(total_outstanding),

        "advance_balance":
            str(advance_balance),

        "interest_levied":
            str(interest_outstanding),

        "penalty_levied":
            str(penalty_outstanding),

        "recovery_charges":
            "0.00",

        "net_adjustment":
            str(total_outstanding),

        "net_payable":
            "0.00",
    }

    # =====================================================
    # BILLING ENGINE
    # =====================================================

    rows, base_amount = (
        calculate_flat_maintenance(
            preview_flat
        )
    )

    charges = []

    core_total = Decimal(
        str(base_amount)
    )

    active_heads = {

        c.code: c

        for c in
        MaintenanceCharge.objects.filter(
            society=society,
            is_active=True,
        )
    }

    for index, row in enumerate(
        rows,
        start=1,
    ):

        code = row.get(
            "charge_code",
            ""
        )

        config = active_heads.get(
            code
        )

        excluded_codes = {
            "NON_OCCUPANCY",
            "PARKING_CHARGES",
            "INTEREST_ON_DUES",
            "LATE_PAYMENT",
        }

        if code in excluded_codes:
            continue

        charges.append({

            "sr_no": index,

            "name":
                row.get(
                    "charge_name",
                    "",
                ),

            "basis":

                config.basis

                if config
                else "-",

            "rate":

                str(
                    config.rate
                )

                if config
                else "-",

            "amount":

                str(
                    row.get(
                        "amount",
                        0,
                    )
                ),
        })

    # =====================================================
    # NON OCCUPANCY
    # =====================================================

    non_occupancy_amount = (
        Decimal("0.00")
    )

    if occupancy:

        if (
            occupancy.occupancy_type
            == "RENTED"
        ):

            non_occupancy_amount = (

                base_amount

                *

                Decimal("0.10")

            ).quantize(
                Decimal("0.01")
            )

    # =====================================================
    # PARKING
    # =====================================================

    parking_rows = []

    parking_total = Decimal("0.00")

    allocations = (
        ParkingAllocation.objects.filter(
            flat=preview_flat,
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

    special_total = (

        non_occupancy_amount

        +

        parking_total
    )

    special_recoveries = {

        "non_occupancy_amount":
            str(
                non_occupancy_amount
            ),

        "parking_total":
            str(
                parking_total
            ),

        "parking_rows":
            parking_rows,

        "total_special_recovery":
            str(
                special_total
            ),
    }

    # =====================================================
    # BANKING
    # =====================================================

    active_bank_accounts = (
        BankAccount.objects.filter(
            society=society,
            is_active=True,
        )
        .order_by(
            "treasury_role",
            "name",
        )
    )

    payment = {

        "available_accounts": [

            {

                "name":
                    account.name,

                "bank_name":
                    account.bank_name,

                "account_number":
                    account.account_number,

                "ifsc":
                    account.ifsc,

                "upi_id":
                    account.upi_id,

                "treasury_role":
                    account.treasury_role,

                "banking_phone":
                    account.banking_phone,

                "banking_email":
                    account.banking_email,
            }

            for account in active_bank_accounts
        ],

        # Preview-only default account.
        # SCR35 user selection comes later.

        "bank_name":

            active_bank_accounts.first().bank_name

            if active_bank_accounts.exists()

            else "-",

        "account_number":

            active_bank_accounts.first().account_number

            if active_bank_accounts.exists()

            else "-",

        "ifsc":

            active_bank_accounts.first().ifsc

            if active_bank_accounts.exists()

            else "-",

        "upi_id":

            active_bank_accounts.first().upi_id

            if active_bank_accounts.exists()

            else "-",

        "selected_account":
            None,

        "selection_required":
            True,
    }

    
    # =====================================================
    # SUMMARY
    # =====================================================

    gross_bill_amount = (

        Decimal(
            str(base_amount)
        )

        +

        non_occupancy_amount

        +

        parking_total
    )

    net_payable = (

        gross_bill_amount

        +

        Decimal(
            account_position[
                "net_adjustment"
            ]
        )
    )

    summary = {

        "core_maintenance_total":
            str(base_amount),

        "special_recovery_total":
            str(special_total),

        "gross_bill_amount":
            str(gross_bill_amount),
    }

    account_position[
        "net_payable"
    ] = str(
        net_payable
    )

    
    return {

        "society":
            society_block,

        "member":
            member_block,

        "bill":
            bill_block,

        "special_recoveries":
            special_recoveries,

        "charges":
            charges,

        "summary":
            summary,

        "account_position":
            account_position,

        "payment":
            payment,

        "notes": [],
    }
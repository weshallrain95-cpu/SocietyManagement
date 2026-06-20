from django.db import transaction
from django.utils import timezone
from society.models import MaintenanceBill
from decimal import Decimal
from society.models import SocietyRule, LedgerEntry
from society.constants import TransactionType

from society.models import (
    Flat,
    MaintenanceBill,
    FlatMaintenanceBill,
    FlatMaintenanceBillLine,
    MemberReceivable,
    ParkingAllocation,
    ParkingRateConfiguration,
)

CATEGORY_PRIORITY = {
    # Core monthly operations
    "SERVICE_CHARGE": 1,
    "WATER": 1,
    "COMMON_ELECTRICITY": 1,

    # Statutory / unavoidable
    "PROPERTY_TAX": 2,
    "INSURANCE": 2,

    # Conditional charges
    "PARKING": 3,
    "NON_OCCUPANCY": 3,
    "AMENITY": 3,

    # Penalties
    "INTEREST": 4,

    # Reserves
    "REPAIR_FUND": 5,
    "SINKING_FUND": 5,

    # Other statutory
    "EDUCATION_FUND": 6,
    "ELECTION_FUND": 6,

    # Catch-all
    "OTHER": 7,

    # Advance (always last)
    "ADVANCE": 99,
}
def get_category_priority(category: str) -> int:
    return CATEGORY_PRIORITY.get(category, 50)

@transaction.atomic
def transfer_flat_ownership(*, flat, new_owners):
    """
    Transfers flat ownership.
    - One active ownership per flat
    - Supports multiple owners
    - Preserves history
    """

    from society.models import FlatOwnership, FlatOwner

    # Close existing active ownership
    active = FlatOwnership.objects.filter(
        flat=flat,
        is_active=True,
    ).first()

    if active:
        active.is_active = False
        active.relinquished_on = timezone.now().date()
        active.save()

    # Create new ownership record
    ownership = FlatOwnership.objects.create(
        flat=flat,
        acquired_on=timezone.now().date(),
        is_active=True,
    )

    total = sum(o["ownership_percentage"] for o in new_owners)
    if total != 100:
        raise ValueError("Ownership percentages must total 100")

    for o in new_owners:
        FlatOwner.objects.create(
            ownership=ownership,
            user=o.get("user"),
            legal_entity_name=o.get("legal_entity_name"),
            ownership_percentage=o["ownership_percentage"],
        )
    return ownership
# 🚗 Transfer parking automatically
    transfer_parking_on_flat_transfer(flat=flat)

from django.utils import timezone
from society.models import ParkingAllocation


def transfer_parking_on_flat_transfer(*, flat):
    """
    When a flat changes ownership, move all active parking allocations
    to the new active owners of the flat.
    """

    # 🔍 Active parking allocations for this flat
    active_allocations = ParkingAllocation.objects.filter(
        flat=flat,
        is_active=True,
    )

    if not active_allocations.exists():
        return  # No parking to transfer

    # 🔍 New owners
    ownership = flat.ownerships.filter(is_active=True).first()
    if not ownership:
        return

    new_owners = ownership.owners.all()

    # 🔒 Deactivate existing allocations
    for alloc in active_allocations:
        alloc.is_active = False
        alloc.released_on = timezone.now().date()
        alloc.save()

    # 🆕 Create new allocations (one per owner)
    for owner in new_owners:
        ParkingAllocation.objects.create(
            parking_slot=alloc.parking_slot,
            flat=flat,
            user=owner.user,
            allocated_on=timezone.now().date(),
            is_active=True,
        )

from decimal import Decimal
from datetime import timedelta
from datetime import date

from django.db import transaction

from society.models import (
    MaintenanceBill,
    FlatMaintenanceBill,
    FlatMaintenanceBillLine,
    Flat,
    MemberReceivable,
    NotificationEvent,
)

from society.finance.maintenance.maintenance_engine import (
    calculate_flat_maintenance,
)


@transaction.atomic
def generate_monthly_maintenance_bill(*, society, billing_month):

# ==========================================================
# 🧠 MONTHLY MAINTENANCE BILLING ENGINE (V2 — CANONICAL)
# ==========================================================
# Date: 2026-05-09
#
# Purpose:
# This is the SINGLE canonical implementation for generating
# society-wide monthly maintenance billing.
#
# What this creates:
# ✔ MaintenanceBill (master batch)
# ✔ FlatMaintenanceBill (per flat snapshot)
# ✔ FlatMaintenanceBillLine (charge line items)
# ✔ MemberReceivable records
# ✔ Transaction records (V2)
# ✔ LedgerEntryV2 records via record_charge()
# ✔ NotificationEvent records
#
# Financial Architecture:
# - Fully aligned to Transaction + LedgerEntryV2 system
# - Uses double-entry accounting via post_transaction()
# - Legacy LedgerEntry system is NOT used
#
# Critical Guarantees:
# ✔ Duplicate billing prevention
# ✔ Atomic transaction safety
# ✔ Immutable billing snapshot generation
# ✔ Society-wide receivable creation
# ✔ Standardized maintenance charge execution
#
# Billing Logic:
# - Charges are derived from MaintenanceCharge
# - Basis rules executed via maintenance_engine
# - Supports AREA / EQUAL / PER_SLOT / PER_INLET /
#   PERCENT_MAINT billing strategies
#
# Current Operational Flow:
# SCR31
#   ↓
# maintenance_setup API
#   ↓
# generate_monthly_maintenance_bill()
#   ↓
# V2 financial posting
#
# Important Notes:
# - This is onboarding operationalization infrastructure
# - PDFs are generated separately via bill_generator.py
# - Financial realism depends on configured rates/basis
#
# ⚠️ STRICT RULES
# - DO NOT create maintenance bills manually
# - DO NOT bypass this function for recurring billing
# - DO NOT directly create LedgerEntryV2 rows
#
# Future Enhancements:
# - Bill PDF orchestration
# - Auto-scheduled monthly billing
# - Billing preview simulation
# - WhatsApp/email bill dispatch
# - Partial billing support
# ==========================================================

    # ==========================================================
    # PREVENT DUPLICATE BILLING
    # ==========================================================
    if MaintenanceBill.objects.filter(
        society=society,
        billing_month=billing_month
    ).exists():

        raise ValueError(
            f"Maintenance bill already generated for {billing_month}"
        )

    # ==========================================================
    # CREATE MASTER BILL
    # ==========================================================
    
    # ==========================================================
    # BILL METADATA
    # ==========================================================

    society_code = (
        society.name.strip()
        .split()[0]
        .upper()[:4]
    )

    serial = (
        MaintenanceBill.objects.filter(
            society=society
        ).count()
        + 1
    )

    bill_number = (
        f"{society_code}"
        f"-MAIN-"
        f"{serial:03d}-"
        f"{billing_month.strftime('%m%y')}"
    )

    bill_date = timezone.now().date()

    due_date = (
        bill_date
        + timedelta(days=15)
    )
    
    bill = MaintenanceBill.objects.create(
        society=society,
        billing_month=billing_month,

        bill_number=bill_number,

        bill_date=bill_date,

        due_date=due_date,

        generated_on=date.today(),

        total_amount=Decimal("0.00"),
    )

    total_society_amount = Decimal("0.00")

    flats = Flat.objects.filter(
        society=society
    )

    # ==========================================================
    # GENERATE FLAT BILLS
    # ==========================================================
    for flat in flats:

        rows, base_amount = calculate_flat_maintenance(flat)

        # ------------------------------------------------------
        # PARKING RECOVERY
        # ------------------------------------------------------
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
                ).first()
            )

            if not config:
                continue

            amount = config.rate

            rows.append({
                "charge_code":
                    f"PARKING_{parking_type}",

                "charge_name":
                    {
                        "CAR":
                            "Parking - Four Wheeler",

                        "BIKE":
                            "Parking - Two Wheeler",

                        "EV":
                            "Parking - EV Vehicle",

                        "VISITOR":
                            "Parking - Visitor",
                    }.get(
                        parking_type,
                        "Parking",
                    ),

                "amount":
                    str(amount),
            })

            parking_total += amount

        
        
        # ------------------------------------------------------
        # NON OCCUPANCY CALCULATION
        # ------------------------------------------------------
        non_occ = Decimal("0.00")

        occupancy = getattr(
            flat,
            "occupancy",
            None,
        )

        if occupancy and occupancy.occupancy_type == "RENTED":

            non_occ = Decimal("0.00")

        total = (
            base_amount
            + parking_total
            + non_occ
        )

        # ------------------------------------------------------
        # CREATE FLAT BILL
        # ------------------------------------------------------
        flat_bill = FlatMaintenanceBill.objects.create(
            bill=bill,
            flat=flat,
            base_amount=base_amount,
            non_occupancy_charge=non_occ,
            total_payable=total,
        )

        # ------------------------------------------------------
        # CREATE LINE ITEMS
        # ------------------------------------------------------
        for r in rows:

            FlatMaintenanceBillLine.objects.create(
                bill=flat_bill,
                charge_code=r["charge_code"],
                charge_name=r["charge_name"],
                amount=r["amount"],
            )

        # ------------------------------------------------------
        # CREATE RECEIVABLE ENTRIES
        # ------------------------------------------------------
        from society.services import record_charge

        record_charge(
            flat=flat,
            amount=total,
            category="MAINTENANCE",
            description=f"Maintenance bill {billing_month}",
        )

        # ------------------------------------------------------
        # MEMBER RECEIVABLE
        # ------------------------------------------------------
        MemberReceivable.objects.create(
            society=society,
            flat=flat,
            bill=flat_bill,
            amount=total,
            outstanding_amount=total,
        )

        # ------------------------------------------------------
        # NOTIFICATION EVENT
        # ------------------------------------------------------
        NotificationEvent.objects.create(
            society=society,
            flat=flat,
            event_type="MAINTENANCE_BILL",
            reference_id=str(flat_bill.id),
            payload={
                "flat": str(flat),
                "amount": str(total),
                "billing_month": str(billing_month),
            },
        )

        total_society_amount += total

    # ==========================================================
    # UPDATE MASTER TOTAL
    # ==========================================================
    bill.total_amount = total_society_amount

    bill.save(update_fields=["total_amount"])

    return bill


# ==========================================================
# ⚠️ LEGACY PAYMENT FUNCTION (SOFT BLOCK)
# Date: 2026-05-03
#
# This function is deprecated but still operational.
# It now routes through V2 engine and raises a warning.
#
# ⚠️ DO NOT USE FOR NEW DEVELOPMENT
# Use: record_member_payment()
# ==========================================================

import warnings
from decimal import Decimal
from django.db import transaction
from django.utils import timezone

from society.models import Payment, ChartOfAccount
from society.finance.kernel.posting_engine import post_transaction


def record_payment(
    *,
    society,
    flat,
    amount,
    payment_mode,
    bill=None,
    reference_number=None,
):
    warnings.warn(
        "⚠️ record_payment() is deprecated. Use record_member_payment()",
        DeprecationWarning,
        stacklevel=2
    )

    with transaction.atomic():

        # 1️⃣ Create payment record (keep existing behavior)
        payment = Payment.objects.create(
            society=society,
            flat=flat,
            bill=bill,
            amount=amount,
            payment_mode=payment_mode,
            reference_number=reference_number,
            status="RECEIVED",
        )

        # 2️⃣ Resolve accounts
        bank_account = ChartOfAccount.objects.filter(
            society=society,
            account_type="ASSET"
        ).first()

        receivable_account = ChartOfAccount.objects.get(
            society=society,
            code="MEMBER_RECEIVABLE"
        )

        if not bank_account:
            raise Exception("❌ No ASSET account found")

        # 3️⃣ Post via V2 engine
        post_transaction(
            society=society,
            transaction_type="PAYMENT",
            reference_type="PAYMENT",
            reference_id=str(payment.id),
            description=f"Payment received ({payment_mode})",
            entries=[
                {"account": bank_account, "type": "DEBIT", "amount": Decimal(amount), "flat": flat},
                {"account": receivable_account, "type": "CREDIT", "amount": Decimal(amount), "flat": flat},
            ],
        )

    return payment

def get_flat_outstanding_balance(flat):
    """
    Returns net outstanding = total debits - total credits
    """

    debits = flat.ledger_entries.filter(
        entry_type="DEBIT"
    ).aggregate(total=models.Sum("amount"))["total"] or Decimal("0.00")

    credits = flat.ledger_entries.filter(
        entry_type="CREDIT"
    ).aggregate(total=models.Sum("amount"))["total"] or Decimal("0.00")

    return debits - credits

# society/services.py
# ==========================================================
# 🧠 FLAT BALANCE CALCULATION (V2 — TEMPORARY IMPLEMENTATION)
# ==========================================================
# Date: 2026-05-02
#
# Context:
# This function was migrated from legacy LedgerEntry-based
# calculation to the new Transaction + LedgerEntryV2 system.
#
# Why change was required:
# - Legacy LedgerEntry is now DEPRECATED and blocked
# - Old logic depended on debit_account / credit_account fields
# - New system uses normalized double-entry rows (DEBIT/CREDIT)
#
# Current Behavior (IMPORTANT):
# ⚠️ This implementation calculates balance at SOCIETY level,
# not per-flat level.
#
# Reason:
# - LedgerEntryV2 currently does NOT store flat reference
# - Hence filtering is done only by society
#
# Impact:
# - All flats will temporarily show SAME balance
# - This is expected during migration phase
#
# Future Fix (MANDATORY):
# - Add `flat` field to LedgerEntryV2
# - Backfill historical data
# - Update this function to filter by flat
#
# ⚠️ DO NOT USE for final financial reporting until fixed
# ==========================================================

from society.models import LedgerEntryV2
from django.db.models import Sum
from decimal import Decimal

def get_flat_balance(flat) -> Decimal:
    entries = LedgerEntryV2.objects.filter(
        flat=flat,
        account__code="MEMBER_RECEIVABLE"
    )

    debits = (
        entries.filter(entry_type="DEBIT")
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    credits = (
        entries.filter(entry_type="CREDIT")
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    return debits - credits



# ==========================================================
# ⚠️ LEGACY PAYMENT FUNCTION (SOFT BLOCK - V2 REDIRECT)
# Date: 2026-05-03
#
# This function previously wrote directly to LedgerEntry.
# It is now redirected to V2 transaction engine.
#
# ⚠️ DO NOT USE FOR NEW DEVELOPMENT
# Use: record_member_payment()
# ==========================================================

import warnings
from decimal import Decimal
from django.db import transaction

from society.models import ChartOfAccount
from society.finance.kernel.posting_engine import post_transaction


@transaction.atomic
def record_payment(
    *,
    flat,
    amount: Decimal,
    description: str = "Payment received",
    category: str = "PAYMENT",
):
    warnings.warn(
        "⚠️ record_payment() is deprecated. Use record_member_payment()",
        DeprecationWarning,
        stacklevel=2
    )

    if amount <= 0:
        raise ValueError("Payment amount must be positive")

    # 🔍 Resolve accounts
    bank_account = ChartOfAccount.objects.filter(
        society=flat.society,
        account_type="ASSET"
    ).first()

    receivable_account = ChartOfAccount.objects.get(
        society=flat.society,
        code="MEMBER_RECEIVABLE"
    )

    if not bank_account:
        raise Exception("❌ No ASSET account found")

    # 🧾 Post via V2 engine
    post_transaction(
        society=flat.society,
        transaction_type="PAYMENT",
        reference_type="LEGACY_PAYMENT",
        reference_id=f"LEGACY-PAY-{flat.id}-{amount}",
        description=description,
        entries=[
            {"account": bank_account, "type": "DEBIT", "amount": amount, "flat": flat},
            {"account": receivable_account, "type": "CREDIT", "amount": amount, "flat": flat},
        ],
    )

# ==========================================================
# ⚠️ DEPRECATED GENERIC PAYMENT FUNCTION
# Date: 2026-05-03
#
# This function is unsafe because:
# - Uses legacy LedgerEntry
# - Bypasses posting engine
# - Does not enforce double-entry
#
# Replacement:
# - record_member_payment()
# - record_vendor_payment() (future)
# - record_transfer() (future)
# ==========================================================

def record_payment(*args, **kwargs):
    raise Exception("❌ Deprecated. Use specific payment flows.")
    
    return LedgerEntry.objects.create(
        society=flat.society,
        flat=flat,
        entry_type="CREDIT",
        category="ADVANCE",
        debit_amount=Decimal("0.00"),
        credit_amount=amount,
        description=description,
        entry_date=timezone.now().date(),
    )
def record_charge(
    *,
    flat,
    amount: Decimal,
    category: str,
    description: str,
):
    """
    Records a charge as a DEBIT entry.
    """

    if amount <= 0:
        raise ValueError("Charge amount must be positive")

    LedgerEntry.objects.create(
        flat=flat,
        society=flat.society,
        entry_type="CHARGE",
        category=category,
        debit_amount=amount,
        credit_amount=Decimal("0.00"),
        description=description,
    )

from society.finance.kernel.posting_engine import post_transaction
from society.models import ChartOfAccount
from decimal import Decimal
from django.db import transaction
from django.utils import timezone

# ==========================================================
# 🧠 CHARGE FUNCTION (V2 — DOUBLE ENTRY ENGINE)
# Date: 2026-05-02
#
# This replaces legacy LedgerEntry-based charge logic
# as part of accounting system migration.
#
# Replacement:
# → Use post_transaction() based charge flow
# ==========================================================

def record_charge(
    *,
    flat,
    amount: Decimal,
    category: str,
    description: str,
):
    """
    Records a maintenance charge using double-entry accounting (V2).
    """

    if amount <= 0:
        raise ValueError("Charge amount must be positive")

    with transaction.atomic():

        receivable_account = ChartOfAccount.objects.get(
            society=flat.society,
            code="MEMBER_RECEIVABLE"
        )

        income_account = ChartOfAccount.objects.get(
            society=flat.society,
            code="MAINTENANCE_INCOME"
        )

        post_transaction(
            society=flat.society,
            transaction_type="BILL",
            reference_type="CHARGE",
            reference_id=f"CHARGE-{flat.id}-{timezone.now().timestamp()}",
            description=description,
            entries=[
                {"account": receivable_account, "type": "DEBIT", "amount": amount, "flat": flat},
                {"account": income_account, "type": "CREDIT", "amount": amount, "flat": flat},
            ],
        )

# ==========================================================
# 🧠 MEMBER PAYMENT FUNCTION (V2 — DOUBLE ENTRY ENGINE)
# Date: 2026-05-03
#
# Purpose:
# Handles ONLY member payments (reducing receivable)
#
# Why separate:
# - Payments are multi-type (member, vendor, transfer)
# - Each flow has different accounting logic
#
# Accounting:
# DEBIT  → Bank/Cash (asset increases)
# CREDIT → Member Receivable (liability reduces)
#
# Engine:
# Uses post_transaction() → V2 system
# ==========================================================

from django.utils import timezone
from society.models import BankAccount
from django.db import transaction
from society.models import ChartOfAccount
from society.finance.kernel.posting_engine import post_transaction

def record_member_payment(
    *,
    flat,
    amount,
    bank_account_id,  # NEW (MANDATORY)
    description="Payment received",
):
    if amount <= 0:
        raise ValueError("Payment amount must be positive")

    with transaction.atomic():

        # 🔍 Fetch accounts (scoped to society)
        try:
            bank_account = BankAccount.objects.get(
                id=bank_account_id,
                society=flat.society
            )
        except BankAccount.DoesNotExist:
            raise Exception("❌ Invalid bank_account_id for this society")

        bank_account_coa = bank_account.chart_account

        try:
            receivable_account = ChartOfAccount.objects.get(
                society=flat.society,
                code="MEMBER_RECEIVABLE"
            )
        except ChartOfAccount.DoesNotExist:
            raise Exception("❌ MEMBER_RECEIVABLE account not found")


        # 🧾 Post transaction via V2 engine
        post_transaction(
            society=flat.society,
            transaction_type="PAYMENT",
            reference_type="MEMBER_PAYMENT",
            reference_id=f"PAY-{flat.id}-{timezone.now().timestamp()}",
            description=description,
            entries=[
                {"account": bank_account_coa, "type": "DEBIT", "amount": amount, "flat": flat},
                {"account": receivable_account, "type": "CREDIT", "amount": amount, "flat": flat},
            ],
        )


from datetime import date
from decimal import Decimal
from django.db.models import Sum
from society.models import LedgerEntry


def get_flat_ageing(flat, as_of: date | None = None):
    """
    Returns ageing buckets for outstanding dues.
    READ-ONLY function.
    """
    if as_of is None:
        as_of = date.today()

    buckets = {
        "0_30": Decimal("0.00"),
        "31_60": Decimal("0.00"),
        "61_90": Decimal("0.00"),
        "90_plus": Decimal("0.00"),
    }

    debits = LedgerEntry.objects.filter(
        flat=flat,
        entry_type="DEBIT",
    )

    for d in debits:
        age_days = (as_of - d.entry_date).days
        amount = d.debit_amount

        if age_days <= 30:
            buckets["0_30"] += amount
        elif age_days <= 60:
            buckets["31_60"] += amount
        elif age_days <= 90:
            buckets["61_90"] += amount
        else:
            buckets["90_plus"] += amount

    return buckets
def get_flat_statement(flat):
    """
    Full chronological ledger for a flat.
    """
    return LedgerEntry.objects.filter(
        flat=flat
    ).order_by("entry_date", "id")
from datetime import date

def calculate_interest(*, principal, rate, days):
    """
    Simple interest, daily basis
    """
    return (principal * rate * days) / Decimal("36500")
from django.utils.timezone import now
from decimal import Decimal
from datetime import date
from django.db import transaction
from society.models import SocietyRule, LedgerEntry
def apply_interest_to_flat(*, flat):
    today = now().date()
    rule = (
        SocietyRule.objects
        .filter(
            society=flat.society,
            rule_type="INTEREST",
            is_active=True,
        )
        .order_by("-effective_from")
        .first()
    )

    if not rule:
        return None
    interest = (
        balance
        * (rule.rate / Decimal("100"))
        / Decimal("365")
    ).quantize(Decimal("0.01"))

    if interest <= 0:
        return None

    LedgerEntry.objects.create(
        society=flat.society,
        flat=flat,
        entry_type="INTEREST",
        debit_amount=interest,
        credit_amount=Decimal("0.00"),
        description=f"Interest @ {rule.rate}%",
        entry_date=today,
    )

    return interest
    dues = LedgerEntry.objects.filter(
        flat=flat,
        debit_amount__gt=0,
        is_settled=False,
    )

    total_interest = Decimal("0.00")

    for due in dues:
        days_overdue = (today - due.entry_date).days
        if days_overdue <= rule.applies_after_days:
            continue

        interest = calculate_interest(
            principal=due.outstanding_amount,
            rate=rule.rate,
            days=days_overdue,
        )

        total_interest += interest

    if total_interest > 0:
        LedgerEntry.objects.create(
            society=flat.society,
            flat=flat,
            entry_type="DEBIT",
            debit_amount=total_interest,
            credit_amount=Decimal("0.00"),
            description="Interest on overdue maintenance",
            entry_date=today,
        )

    return total_interest
    from decimal import Decimal
from society.models import NoticeLog


def generate_notice(
    *,
    flat,
    notice_type,
    reference_period,
    notes="",
):
    principal, interest, total = get_interest_snapshot_for_flat(flat)

    if total <= Decimal("0.00"):
        return None

    return NoticeLog.objects.create(
        society=flat.society,
        flat=flat,
        notice_type=notice_type,
        outstanding_amount=principal,
        interest_amount=interest,
        total_payable=total,
        reference_period=reference_period,
        notes=notes,
    )

def calculate_non_occupancy_charge(*, service_charges, rule):
    max_allowed = (service_charges * rule.cap_percentage) / Decimal("100")
    calculated = (service_charges * rule.rate) / Decimal("100")
    return min(calculated, max_allowed)
# society/services.py

from decimal import Decimal
from society.models import LedgerEntry


def get_flat_statement(flat, *, from_date=None, to_date=None):
    """
    Returns a chronological ledger statement with running balance
    """

    qs = LedgerEntry.objects.filter(flat=flat)

    if from_date:
        qs = qs.filter(entry_date__gte=from_date)

    if to_date:
        qs = qs.filter(entry_date__lte=to_date)

    qs = qs.order_by("entry_date", "id")

    running_balance = Decimal("0.00")
    statement = []

    for entry in qs:
        running_balance += entry.debit_amount
        running_balance -= entry.credit_amount

        statement.append({
            "date": entry.entry_date,
            "description": entry.description,
            "debit": entry.debit_amount,
            "credit": entry.credit_amount,
            "balance": running_balance,
        })

    return statement
def get_flat_statement_report(
    *,
    flat,
    from_date=None,
    to_date=None,
):
    entries = get_flat_statement(
        flat,
        from_date=from_date,
        to_date=to_date,
    )

    opening_balance = (
        entries[0]["balance"] - entries[0]["debit"] + entries[0]["credit"]
        if entries else Decimal("0.00")
    )

    closing_balance = entries[-1]["balance"] if entries else Decimal("0.00")

    return {
        "flat": str(flat),
        "period": {
            "from": from_date,
            "to": to_date,
        },
        "opening_balance": opening_balance,
        "closing_balance": closing_balance,
        "entries": entries,
    }

from decimal import Decimal

from society.models import NoticeLog
from decimal import Decimal

def generate_notice(
    *,
    flat,
    notice_type,
    reference_period,
    notes="",
):
    principal, interest, total = get_interest_snapshot_for_flat(flat)

    if total <= Decimal("0.00"):
        return None

    return NoticeLog.objects.create(
        society=flat.society,
        flat=flat,
        notice_type=notice_type,
        outstanding_amount=principal,
        interest_amount=interest,
        reference_period=reference_period,
        notes=notes,
    )


from decimal import Decimal

from decimal import Decimal
from datetime import date
from django.db.models import Sum
from society.models import LedgerEntry, SocietyRule


def calculate_interest_snapshot(*, flat) -> Decimal:
    """
    Calculates interest on outstanding balance for a flat
    based on active INTEREST rules.
    """

    # Outstanding principal
    principal = (
        LedgerEntry.objects
        .filter(flat=flat)
        .aggregate(
            debit=Sum("debit_amount"),
            credit=Sum("credit_amount"),
        )
    )

    outstanding = (principal["debit"] or Decimal("0.00")) - (
        principal["credit"] or Decimal("0.00")
    )

    if outstanding <= Decimal("0.00"):
        return Decimal("0.00")

    # Active interest rule
    rule = (
        SocietyRule.objects
        .filter(
            society=flat.society,
            rule_type="INTEREST",
            is_active=True,
        )
        .order_by("-effective_from")
        .first()
    )

    if not rule:
        return Decimal("0.00")

    # Days overdue
    oldest_due = (
        LedgerEntry.objects
        .filter(
            flat=flat,
            debit_amount__gt=0,
        )
        .order_by("entry_date")
        .first()
    )

    if not oldest_due:
        return Decimal("0.00")

    days_overdue = (date.today() - oldest_due.entry_date).days

    if days_overdue <= rule.applies_after_days:
        return Decimal("0.00")

    # Simple interest calculation
    interest = (
        outstanding
        * rule.rate
        / Decimal("100.00")
        * Decimal(days_overdue)
        / Decimal("365")
    )

    return interest.quantize(Decimal("0.01"))

def get_interest_snapshot_for_flat(flat):
    """
    Returns (principal, interest, total)
    """
    principal = get_flat_balance(flat)
    interest = calculate_interest_snapshot(flat=flat)

    principal = principal or Decimal("0.00")
    interest = interest or Decimal("0.00")

    return principal, interest, principal + interest
# society/services.py

from society.models import (
    FlatRecoveryStatus,
    RecoveryActionLog,
    RecoveryStage,
)
from decimal import Decimal

def advance_recovery_stage(
    *,
    flat,
    next_stage,
    reference="",
    notes="",
):
    status, _ = FlatRecoveryStatus.objects.get_or_create(
        flat=flat
    )

    allowed_flow = [
        RecoveryStage.NONE,
        RecoveryStage.REMINDER,
        RecoveryStage.DEMAND,
        RecoveryStage.FINAL,
        RecoveryStage.REGISTRAR,
        RecoveryStage.LEGAL,
        RecoveryStage.CLOSED,
    ]

    current_index = allowed_flow.index(status.stage)
    next_index = allowed_flow.index(next_stage)

    if next_index != current_index + 1:
        raise ValueError(
            f"Invalid recovery transition: {status.stage} → {next_stage}"
        )

    outstanding = get_flat_balance(flat)

    status.stage = next_stage
    status.outstanding_amount = outstanding
    status.notes = notes
    status.save()

    RecoveryActionLog.objects.create(
        flat=flat,
        stage=next_stage,
        reference=reference,
        notes=notes,
    )

    return status
from django.db.models import Sum
from decimal import Decimal
from society.models import LedgerEntry


def get_society_income_expenditure(
    *,
    society,
    from_date=None,
    to_date=None,
):
    qs = LedgerEntry.objects.filter(society=society)

    if from_date:
        qs = qs.filter(entry_date__gte=from_date)

    if to_date:
        qs = qs.filter(entry_date__lte=to_date)

    totals = qs.aggregate(
        total_income=Sum("credit_amount"),
        total_expense=Sum("debit_amount"),
    )

    income = totals["total_income"] or Decimal("0.00")
    expense = totals["total_expense"] or Decimal("0.00")

    return {
        "income": income,
        "expense": expense,
        "surplus": income - expense,
    }

from society.models import Flat

def get_flat_balances_for_society(society):
    report = []

    for flat in Flat.objects.filter(society=society):
        balance = get_flat_balance(flat)

        report.append({
            "flat": str(flat),
            "balance": balance,
            "status": (
                "DUE" if balance > 0
                else "ADVANCE" if balance < 0
                else "CLEAR"
            ),
        })

    return report


from society.models import VendorPayable
def create_vendor_payable(vendor_bill):

    return VendorPayable.objects.create(
        society=vendor_bill.society,
        vendor_bill=vendor_bill,
        amount=vendor_bill.amount,
        outstanding_amount=vendor_bill.amount,
    )


from decimal import Decimal
from django.utils import timezone

from society.models import VendorPayment, LedgerEntry
from society.models import ChartOfAccount
from society.models import BankAccount

def record_vendor_payment(
    *,
    payable,
    amount,
    payment_method,
    bank_account_id,   # NEW (MANDATORY)
    reference_number=None,
):

    if amount <= 0:
        raise ValueError("Payment amount must be positive")

    if payable.status == "PAID":
        raise ValueError("This payable is already fully paid")

    if amount > payable.outstanding_amount:
        raise ValueError("Payment exceeds outstanding payable")

    # Create payment record
    payment = VendorPayment.objects.create(
        society=payable.society,
        vendor_payable=payable,
        amount=amount,
        payment_method=payment_method,
        reference_number=reference_number,
        payment_date=timezone.now(),
    )

    # Update outstanding amount
    payable.outstanding_amount -= Decimal(amount)

    if payable.outstanding_amount == Decimal("0.00"):
        payable.status = "PAID"
    else:
        payable.status = "PARTIALLY_PAID"

    payable.save()

    from society.finance.kernel.posting_engine import post_transaction

    try:
        bank_account = BankAccount.objects.get(
            id=bank_account_id,
            society=payable.society
        )
    except BankAccount.DoesNotExist:
        raise Exception("❌ Invalid bank_account_id for this society")

    bank_account_coa = bank_account.chart_account

    expense_account = ChartOfAccount.objects.get(
        society=payable.society,
        code="GENERAL_EXPENSE"
    )

    post_transaction(
        society=payable.society,
        transaction_type="VENDOR_PAYMENT",
        reference_type="VENDOR_PAYMENT",
        reference_id=str(payment.id),
        description=f"Vendor payment - {payable.vendor_bill.vendor.name}",
        entries=[
            {"account": expense_account, "type": "DEBIT", "amount": Decimal(amount)},
            {"account": bank_account_coa, "type": "CREDIT", "amount": Decimal(amount)},
        ],
    )


    # ❌ LEGACY LEDGER BLOCK (DISABLED - 2026-05-03)
    """
    from society.models import LedgerEntry, ChartOfAccount

    bank_account = ChartOfAccount.objects.get(code="BANK")
    vendor_payable_account = ChartOfAccount.objects.get(code="VENDOR_PAYABLE")

    LedgerEntry.objects.create(
        society=payable.society,
        debit_account=vendor_payable_account,
        credit_account=bank_account,
        amount=amount,
        description=f"Vendor payment - {payable.vendor_bill.vendor.name}",
        source_type="VENDOR_PAYMENT",
        source_ref=str(payment.id),
    )

    LedgerEntry.objects.create(
        society=payable.society,
        flat=None,
        debit_account_id=PAYABLE_ACCOUNT_ID,
        credit_account_id=BANK_ACCOUNT_ID,
        amount=Decimal(amount),
        description=f"Vendor payment: {payable.vendor_bill.vendor.name}",
        entry_date=timezone.now().date(),
    )
    """


    return payment


from datetime import date
from calendar import monthrange

def get_monthly_society_snapshot(*, society, year, month):
    start = date(year, month, 1)
    end = date(year, month, monthrange(year, month)[1])

    pnl = get_society_income_expenditure(
        society=society,
        from_date=start,
        to_date=end,
    )

    balances = get_flat_balances_for_society(society)

    total_receivable = sum(
        f["balance"] for f in balances if f["balance"] > 0
    )

    return {
        "period": f"{start:%b %Y}",
        "income": pnl["income"],
        "expense": pnl["expense"],
        "surplus": pnl["surplus"],
        "receivable": total_receivable,
        "flat_balances": balances,
    }
def export_agm_income_expenditure(
    *,
    society,
    from_date,
    to_date,
):
    pnl = get_society_income_expenditure(
        society=society,
        from_date=from_date,
        to_date=to_date,
    )

    return {
        "society": str(society),
        "period": f"{from_date} to {to_date}",
        "income": pnl["income"],
        "expenditure": pnl["expense"],
        "surplus_or_deficit": pnl["surplus"],
        "generated_on": date.today(),
    }
def export_registrar_arrears_list(*, society):
    rows = []

    for item in get_flat_balances_for_society(society):
        if item["balance"] > 0:
            rows.append({
                "flat": item["flat"],
                "outstanding_amount": item["balance"],
                "status": "ARREARS",
            })

    return {
        "society": str(society),
        "total_defaulters": len(rows),
        "generated_on": date.today(),
        "arrears": rows,
    }
def export_flat_account_statement(
    *,
    flat,
    from_date=None,
    to_date=None,
):
    statement = get_flat_statement(
        flat,
        from_date=from_date,
        to_date=to_date,
    )

    closing_balance = (
        statement[-1]["balance"]
        if statement
        else Decimal("0.00")
    )

    return {
        "flat": str(flat),
        "society": str(flat.society),
        "period": f"{from_date or 'START'} to {to_date or 'TODAY'}",
        "entries": statement,
        "closing_balance": closing_balance,
        "generated_on": date.today(),
    }
# society/services.py

DEFAULT_COA_TEMPLATE = [
    # ASSETS
    {"code": "BANK", "name": "Bank Account", "type": "ASSET"},
    {"code": "CASH", "name": "Cash in Hand", "type": "ASSET"},
    {"code": "FD", "name": "Fixed Deposits", "type": "ASSET"},

    # LIABILITIES
    {"code": "PAYABLE", "name": "Maintenance Payable", "type": "LIABILITY"},
    {"code": "ADVANCE", "name": "Advance from Members", "type": "LIABILITY"},

    # INCOME
    {"code": "MAINT", "name": "Maintenance Charges", "type": "INCOME"},
    {"code": "PARK", "name": "Parking Charges", "type": "INCOME"},
    {"code": "NOC", "name": "Non-Occupancy Charges", "type": "INCOME"},
    {"code": "INTEREST_INC", "name": "Interest Earned", "type": "INCOME"},

    # EXPENSES
    {"code": "SAL", "name": "Staff Salaries", "type": "EXPENSE"},
    {"code": "ELEC", "name": "Electricity Charges", "type": "EXPENSE"},
    {"code": "REPAIR", "name": "Repairs & Maintenance", "type": "EXPENSE"},
    {"code": "ADMIN", "name": "Administrative Expenses", "type": "EXPENSE"},

    # RESERVES
    {"code": "SINK", "name": "Sinking Fund", "type": "RESERVE"},
    {"code": "REPAIR_FUND", "name": "Repair Fund", "type": "RESERVE"},
]
from society.models import ChartOfAccount
from django.db import transaction

@transaction.atomic
def seed_default_coa_for_society(*, society):
    created = []
    skipped = []

    for item in DEFAULT_COA_TEMPLATE:
        coa, is_created = ChartOfAccount.objects.get_or_create(
            society=society,
            code=item["code"],
            defaults={
                "name": item["name"],
                "account_type": item["type"],
                "is_system": True,
            }
        )
        (created if is_created else skipped).append(coa.code)

    return {
        "created": created,
        "skipped": skipped,
    }

from decimal import Decimal
from django.db import transaction
from django.utils import timezone

from society.models import LedgerEntry, ChartOfAccount
from society.models import BankAccount


@transaction.atomic
def post_double_entry(
    *,
    society,
    flat=None,
    debit_account_code,
    credit_account_code,
    amount,
    description,
    entry_date,
    created_by=None,
    source_type=None,
    source_ref=None,
    bank_account_id=None,   # 🔥 NEW
):
    bank_account = None

    # Resolve bank once if needed
    if debit_account_code == "BANK" or credit_account_code == "BANK":
        if not bank_account_id:
            raise Exception("❌ bank_account_id required for BANK transactions")

        try:
            bank_account = BankAccount.objects.get(
                id=bank_account_id,
                society=society
            )
        except BankAccount.DoesNotExist:
            raise Exception("❌ Invalid bank_account_id")

    # Resolve debit account
    if debit_account_code == "BANK":
        debit_account = bank_account.chart_account
    else:
        try:
            debit_account = ChartOfAccount.objects.get(
                society=society,
                code=debit_account_code,
            )
        except ChartOfAccount.DoesNotExist:
            raise Exception(f"❌ Invalid debit account: {debit_account_code}")

    # Resolve credit account
    if credit_account_code == "BANK":
        credit_account = bank_account.chart_account
    else:
        try:
            credit_account = ChartOfAccount.objects.get(
                society=society,
                code=credit_account_code,
            )
        except ChartOfAccount.DoesNotExist:
            raise Exception(f"❌ Invalid credit account: {credit_account_code}")

    return LedgerEntry.objects.create(
        society=society,
        flat=flat,
        debit_account=debit_account,
        credit_account=credit_account,
        amount=amount,
        description=description,
        entry_date=entry_date,
        created_by=created_by,
        source_type=source_type,
        source_ref=source_ref,
    )

# imports
from decimal import Decimal
from django.db import transaction

from society.constants import TransactionType
from society.models import ChartOfAccount, LedgerEntry

TRANSACTION_POSTING_RULES = {
    TransactionType.MAINTENANCE_RECEIPT: {
        "debit": "BANK",
        "credit": "MAINT",
    },
    TransactionType.SALARY_PAYMENT: {
        "debit": "SAL",
        "credit": "BANK",
    },
}


from django.core.exceptions import MultipleObjectsReturned

def resolve_transaction_rule(*, society, transaction_type):
    try:
        return TransactionRule.objects.get(
            society=society,
            transaction_type=transaction_type.value,
            is_active=True,
        )
    except TransactionRule.DoesNotExist:
        raise ValueError(
            f"No active TransactionRule for {transaction_type.value} in {society}"
        )
    except MultipleObjectsReturned:
        raise ValueError(
            f"Multiple active TransactionRules found for {transaction_type.value} in {society}. "
            "Please deactivate duplicates."
        )

from society.constants import TransactionType
from society.models import TransactionRule

DEFAULT_TRANSACTION_RULES = {

    # Billing
    TransactionType.MAINTENANCE_BILL: ("PAYABLE", "MAINT"),

    # Member payment
    TransactionType.MAINTENANCE_RECEIPT: ("BANK", "PAYABLE"),

    # Expenses
    TransactionType.ELECTRICITY_BILL_PAYMENT: ("ELEC", "BANK"),
    TransactionType.SALARY_PAYMENT: ("SAL", "BANK"),

    # Cash movement
    TransactionType.BANK_DEPOSIT: ("BANK", "CASH"),
    TransactionType.BANK_WITHDRAWAL: ("CASH", "BANK"),

    # Investments
    TransactionType.FD_CREATION: ("FD", "BANK"),
    TransactionType.FD_INTEREST_RECEIVED: ("BANK", "INTEREST_INC"),

    # Penalty
    TransactionType.PENALTY_CHARGED: ("PAYABLE", "PENALTY"),
}

from decimal import Decimal
from django.db import transaction

from society.models import LedgerEntry, ChartOfAccount
from society.constants import TransactionType


@transaction.atomic
def record_transaction(
    *,
    society,
    flat=None,
    transaction_type,
    amount,
    description,
    entry_date=None,
    source_type=None,
    source_ref=None,
    created_by=None,
    bank_account_id=None,   # 🔥 NEW
):
    """
    User-facing transaction entry point.
    Accounting-agnostic.
    Supports audit & maker-checker metadata.
    """

    from django.utils import timezone

    if entry_date is None:
        entry_date = timezone.now().date()

    rule = resolve_transaction_rule(
        society=society,
        transaction_type=transaction_type,
    )

    # Ensure bank_account_id is provided when BANK is involved
    if (
        rule.debit_account_code == "BANK"
        or rule.credit_account_code == "BANK"
    ):
        if not bank_account_id:
            raise Exception("❌ bank_account_id required for BANK transactions")

    # SAFEGUARD: Ensure rule accounts exist in Chart of Accounts
    # (Skip BANK — handled via BankAccount)

    if rule.debit_account_code != "BANK":
        if not ChartOfAccount.objects.filter(
            society=society,
            code=rule.debit_account_code
        ).exists():
            raise ValueError(
                f"Invalid debit account '{rule.debit_account_code}' "
                f"for transaction rule {transaction_type}"
            )

    if rule.credit_account_code != "BANK":
        if not ChartOfAccount.objects.filter(
            society=society,
            code=rule.credit_account_code
        ).exists():
            raise ValueError(
                f"Invalid credit account '{rule.credit_account_code}' "
                f"for transaction rule {transaction_type}"
            )

    # Ensure accounting period is open
    assert_open_accounting_period(
        society=society,
        entry_date=entry_date,
    )

    entry = post_double_entry(
        society=society,
        flat=flat,
        debit_account_code=rule.debit_account_code,
        credit_account_code=rule.credit_account_code,
        amount=amount,
        description=description,
        entry_date=entry_date,
        source_type=source_type,
        source_ref=source_ref,
        created_by=created_by,
        bank_account_id=bank_account_id,   # 🔥 NEW
    )

    return entry

    
    # Ledger integrity check
    from society.finance.ledger_integrity import verify_ledger_integrity
    verify_ledger_integrity(society)

    return entry


from django.utils import timezone
from django.db import transaction as db_transaction
from society.models import PendingTransaction, LedgerEntry


@db_transaction.atomic
def approve_pending_transaction(*, pending_txn, approved_by):
    """
    Checker action.
    Posts to ledger exactly once.
    """
    
    if pending_txn.status != "SUBMITTED":
        raise ValueError("Only SUBMITTED transactions can be approved")

    if pending_txn.created_by_id == approved_by.id:
        raise ValueError(
            "Maker and Checker must be different users"
        )

    # Safety: prevent double posting
    already_posted = LedgerEntry.objects.filter(
        source_type="PENDING_TXN",
        source_ref=str(pending_txn.id),
    ).exists()

    if already_posted:
        raise ValueError("This transaction has already been posted to ledger")

    # Post to ledger (uses your hardened engine)
    record_transaction(
        society=pending_txn.society,
        transaction_type=TransactionType(pending_txn.transaction_type),
        amount=pending_txn.amount,
        description=pending_txn.description,
        entry_date=pending_txn.entry_date,
        source_type="PENDING_TXN",
        source_ref=str(pending_txn.id),
        created_by=approved_by,
    )

    # Mark approved
    pending_txn.status = "APPROVED"
    pending_txn.approved_by = approved_by
    pending_txn.approved_at = timezone.now()
    pending_txn.save(update_fields=[
        "status",
        "approved_by",
        "approved_at",
    ])


from society.models import AccountingPeriod

def assert_open_period(*, society, entry_date):
    if not AccountingPeriod.objects.filter(
        society=society,
        start_date__lte=entry_date,
        end_date__gte=entry_date,
        is_closed=False,
    ).exists():
        raise ValueError("Accounting period is closed for this date")


from society.models import TransactionRule
from society.constants import TransactionType

def seed_transaction_rules_for_society(*, society):
    created = []
    skipped = []

    for tx_type, (debit, credit) in DEFAULT_TRANSACTION_RULES.items():
        rule, is_created = TransactionRule.objects.get_or_create(
            society=society,
            transaction_type=tx_type.value,
            defaults={
                "debit_account_code": debit,
                "credit_account_code": credit,
                "is_active": True,
            },
        )

        if is_created:
            created.append(tx_type.value)
        else:
            skipped.append(tx_type.value)

    return {"created": created, "skipped": skipped}

from society.models import AccountingPeriod

def assert_open_accounting_period(*, society, entry_date):
    try:
        period = AccountingPeriod.objects.get(
            society=society,
            start_date__lte=entry_date,
            end_date__gte=entry_date,
            is_closed=False,
        )
    except AccountingPeriod.DoesNotExist:
        raise ValueError(
            f"No open accounting period for {entry_date}"
        )

    return period

from datetime import date
from django.db import transaction
from society.models import AccountingPeriod


@transaction.atomic
def create_opening_accounting_period_for_society(*, society):
    """
    Creates the first open financial year for the society.
    Idempotent.
    """

    if AccountingPeriod.objects.filter(society=society).exists():
        return None  # Already initialized

    today = date.today()

    # Determine financial year (April–March)
    if today.month < 4:
        start_year = today.year - 1
    else:
        start_year = today.year

    start_date = date(start_year, 4, 1)
    end_date = date(start_year + 1, 3, 31)

    return AccountingPeriod.objects.create(
        society=society,
        start_date=start_date,
        end_date=end_date,
        is_closed=False,
    )

# ==========================================================
# SOCIETY STRUCTURE GENERATOR
# ==========================================================

from django.db import transaction
from society.models import Wing, Floor, Flat

WING_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def generate_wing_name(index: int) -> str:
    """
    Converts index → A,B,C...Z
    """
    if index < len(WING_ALPHABET):
        return WING_ALPHABET[index]

    return f"W{index + 1}"


def generate_flat_number(
    wing_name,
    floor_number,
    flat_index,
    style="A-101",
):

    if style == "A-101":
        return f"{wing_name}-{floor_number}{flat_index:02d}"

    if style == "A101":
        return f"{wing_name}{floor_number}{flat_index:02d}"

    if style == "101":
        return f"{floor_number}{flat_index:02d}"

    raise ValueError(f"Unsupported flat numbering style: {style}")

def generate_structure_dispatcher(*, society, mode, **kwargs):

    if mode == "STANDARD":
        return generate_society_structure(
            society=society,
            total_wings=kwargs["total_wings"],
            floors_per_wing=kwargs["floors_per_wing"],
            floor_layout=kwargs["floor_layout"],
            flat_numbering_style=kwargs.get("style", "A-101"),
        )

    elif mode == "GROUP":
        from society.services_group_engine import generate_grouped_structure

        return generate_grouped_structure(
            society=society,
            total_wings=kwargs["total_wings"],
            floors_per_wing=kwargs["floors_per_wing"],
            groups=kwargs["groups"],
            flat_numbering_style=kwargs.get("style", "A-101"),
        )

    else:
        raise ValueError("Invalid structure mode")

        
@transaction.atomic
def generate_society_structure(
    *,
    society,
    total_wings,
    floors_per_wing,
    floor_layout,
    flat_numbering_style="A-101",
):

    # Prevent duplicate structure
    if society.flats.exists():
        return {
            "status": "SKIPPED",
            "message": "Society structure already exists",
            "wings": society.wings.count(),
            "floors": Floor.objects.filter(wing__society=society).count(),
            "flats": society.flats.count(),
        }

    created_wings = 0
    created_floors = 0
    created_flats = 0

    for wing_index in range(total_wings):

        wing_name = generate_wing_name(wing_index)

        wing = Wing.objects.create(
            society=society,
            name=wing_name,
        )

        created_wings += 1

        for floor_number in range(1, floors_per_wing + 1):

            floor = Floor.objects.create(
                wing=wing,
                number=floor_number,
            )

            created_floors += 1

            for flat_index, layout in enumerate(floor_layout, start=1):

                flat_number = generate_flat_number(
                    wing_name,
                    floor_number,
                    flat_index,
                    flat_numbering_style,
                )

                Flat.objects.create(
                    society=society,

                    # legacy fields
                    wing=wing_name,
                    floor=floor_number,

                    # canonical relations
                    wing_ref=wing,
                    floor_ref=floor,

                    flat_number=flat_number,
                    flat_type=layout.get("type"),
                    carpet_area_sqft=layout.get("area"),
                )

                created_flats += 1

    return {
        "status": "CREATED",
        "wings": created_wings,
        "floors": created_floors,
        "flats": created_flats,
        "flats_per_floor": len(floor_layout),
    }


from collections import defaultdict
from django.utils import timezone
from society.models import Flat, Person, FlatOwnership, FlatOwner


def import_flat_owners(*, society, rows):

    grouped = defaultdict(list)

    for r in rows:
        grouped[r["flat"]].append(r)

    flats_processed = 0

    for flat_number, owners in grouped.items():

        flat = Flat.objects.filter(
            society=society,
            flat_number=flat_number,
        ).first()

        if not flat:
            raise ValueError(f"Flat not found: {flat_number}")

        # --------------------------------
        # Find existing ownership
        # --------------------------------
        ownership = FlatOwnership.objects.filter(
            flat=flat,
            is_active=True,
        ).first()

        if not ownership:
            ownership = FlatOwnership.objects.create(
                flat=flat,
                acquired_on=timezone.now().date(),
                is_active=True,
            )

        # --------------------------------
        # Add owners
        # --------------------------------
        total_percent = 0

        for o in owners:

            person, _ = Person.objects.get_or_create(
                phone=o["phone"],
                defaults={"full_name": o["name"]},
            )

            FlatOwner.objects.get_or_create(
                ownership=ownership,
                person=person,
                defaults={
                    "ownership_percentage": o["percent"]
                }
            )

            total_percent += o["percent"]

        if total_percent != 100:
            raise ValueError(
                f"Ownership for flat {flat_number} must equal 100%"
            )

        flats_processed += 1

    return {
        "flats_processed": flats_processed
    }

import openpyxl
from collections import defaultdict
from decimal import Decimal
from django.db import transaction
from django.utils import timezone

from society.models import (
    Person,
    Flat,
    FlatOwnership,
    FlatOwner,
)


@transaction.atomic
def import_flat_owners_from_excel(*, society, file_path):
    """
    Bulk import flat owners from Excel.
    """

    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active

    rows = []
    for r in sheet.iter_rows(min_row=2, values_only=True):

        rows.append({
            "flat": r[0],
            "name": r[1],
            "phone": str(r[2]) if r[2] else None,
            "percent": r[3],
            "entity": r[4],
        })

    return import_flat_owners(society=society, rows=rows)


@transaction.atomic
def import_flat_owners(*, society, rows):
    """
    Core import engine (Excel / CSV / API compatible).
    """

    flats = {
        f.flat_number: f
        for f in Flat.objects.filter(society=society)
    }

    grouped = defaultdict(list)

    for r in rows:
        grouped[r["flat"]].append(r)

    created_people = 0
    ownership_records = 0
    owner_links = 0

    for flat_number, owners in grouped.items():

        flat = flats.get(flat_number)

        if not flat:
            raise ValueError(f"Flat not found: {flat_number}")

        percent_total = sum(
            Decimal(str(o["percent"])) for o in owners
        )

        if percent_total != Decimal("100"):
            raise ValueError(
                f"Ownership must total 100 for flat {flat_number}"
            )

        ownership, created = FlatOwnership.objects.get_or_create(
            flat=flat,
            is_active=True,
            defaults={
                "acquired_on": timezone.now().date()
            },
        )

        if created:
            ownership_records += 1

        for o in owners:

            person = None

            if o["name"]:
                person, p_created = Person.objects.get_or_create(
                    phone=o["phone"],
                    defaults={
                        "full_name": o["name"],
                    }
                )

                if p_created:
                    created_people += 1

            FlatOwner.objects.get_or_create(
                ownership=ownership,
                person=person,
                legal_entity_name=o["entity"],
                defaults={
                    "ownership_percentage": o["percent"]
                }
            )

            owner_links += 1

    return {
        "people_created": created_people,
        "ownership_records": ownership_records,
        "owners_linked": owner_links,
    }
    

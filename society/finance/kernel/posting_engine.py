from decimal import Decimal
from django.db import transaction as db_transaction
from django.utils import timezone
from society.models import Transaction, LedgerEntryV2


class PostingError(Exception):
    pass


# ==========================================================
# 🧠 POSTING ENGINE (V2 — SINGLE SOURCE OF FINANCIAL TRUTH)
# ==========================================================
# Date: 2026-05-01
#
# Purpose:
# This function is the ONLY allowed entry point for creating
# financial transactions in the system.
#
# Why this exists:
# - Legacy system allowed direct LedgerEntry writes from
#   multiple places (services, utils, APIs)
# - No guarantee of debit = credit
# - No idempotency → duplicate postings possible
# - No transaction grouping → poor auditability
#
# What this enforces:
# ✔ Double-entry accounting (total debit == total credit)
# ✔ Minimum 2 entries per transaction
# ✔ Atomicity (all-or-nothing database write)
# ✔ Idempotency via (society, reference_type, reference_id)
# ✔ Centralized control of all financial postings
#
# How it works:
# - Validates entries (amount, type)
# - Checks debit vs credit balance
# - Prevents duplicate transactions
# - Creates Transaction (parent record)
# - Creates multiple LedgerEntryV2 (child entries)
#
# ⚠️ STRICT RULE:
# - DO NOT create LedgerEntryV2 directly
# - DO NOT bypass this function in services/APIs
#
# Future Integration:
# - Billing engine → calls post_transaction()
# - Payment engine → calls post_transaction()
# - Adjustments → calls post_transaction()
#
# ==========================================================


@db_transaction.atomic
def post_transaction(
    *,
    society,
    entries,
    transaction_type,
    reference_type,
    reference_id,
    description="",
    transaction_date=None,
    idempotency_key=None,   # 🔥 ADD THIS
):
    """
    Core financial posting engine (V2).

    entries = [
        {"account": account_obj, "type": "DEBIT", "amount": Decimal("100")},
        {"account": account_obj, "type": "CREDIT", "amount": Decimal("100")},
    ]
    """
    # 🔥 IDEMPOTENCY (SINGLE SOURCE OF TRUTH)
    existing = None

    if idempotency_key:
        existing = Transaction.objects.filter(
            society=society,
            idempotency_key=idempotency_key
        ).first()
    else:
        existing = Transaction.objects.filter(
            society=society,
            reference_type=reference_type,
            reference_id=reference_id,
        ).first()

    if existing:
        return existing

    if not entries or len(entries) < 2:
        raise PostingError("At least 2 entries required")

    total_debit = Decimal("0")
    total_credit = Decimal("0")

    for entry in entries:
        if entry["amount"] <= 0:
            raise PostingError("Amount must be positive")

        if entry["type"] == "DEBIT":
            total_debit += entry["amount"]
        elif entry["type"] == "CREDIT":
            total_credit += entry["amount"]
        else:
            raise PostingError("Invalid entry type")

    if total_debit != total_credit:
        raise PostingError("Debit and Credit must match")

    txn = Transaction.objects.create(
        society=society,
        transaction_type=transaction_type,
        reference_type=reference_type,
        reference_id=reference_id,
        description=description,
        transaction_date=transaction_date or timezone.now().date(),
        idempotency_key=idempotency_key,  # 🔥 ADD THIS
    )

    ledger_entries = []

    for entry in entries:
        ledger_entries.append(
            LedgerEntryV2(
                transaction=txn,
                flat=entry.get("flat"),   # ✅ ADD THIS LINE
                account=entry["account"],
                entry_type=entry["type"],
                amount=entry["amount"],
            )
        )

    LedgerEntryV2.objects.bulk_create(ledger_entries)

    return txn


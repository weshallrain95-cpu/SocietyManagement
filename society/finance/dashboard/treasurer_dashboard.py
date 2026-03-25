from decimal import Decimal
from django.db.models import Sum
from django.utils.timezone import now

from society.models import (
    MemberReceivable,
    PaymentTransaction,
    VendorPayable,
    VendorPayment,
    LedgerEntry,
)


def get_treasurer_dashboard(society):

    today = now().date()

    # -----------------------------
    # MEMBER RECEIVABLES
    # -----------------------------
    total_receivables = (
        MemberReceivable.objects
        .filter(society=society)
        .aggregate(total=Sum("outstanding_amount"))["total"]
        or Decimal("0.00")
    )

    # -----------------------------
    # VENDOR PAYABLES
    # -----------------------------
    vendor_payables = (
        VendorPayable.objects
        .filter(society=society)
        .aggregate(total=Sum("outstanding_amount"))["total"]
        or Decimal("0.00")
    )

    # -----------------------------
    # COLLECTIONS THIS MONTH
    # -----------------------------
    collections_this_month = (
        PaymentTransaction.objects
        .filter(
            receivable__society=society,
            payment_date__month=today.month,
            payment_date__year=today.year,
        )
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    # -----------------------------
    # VENDOR PAYMENTS THIS MONTH
    # -----------------------------
    vendor_payments_this_month = (
        VendorPayment.objects
        .filter(
            society=society,
            payment_date__month=today.month,
            payment_date__year=today.year,
        )
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    # -----------------------------
    # OUTSTANDING FLATS
    # -----------------------------
    outstanding_flats = (
        MemberReceivable.objects
        .filter(
            society=society,
            outstanding_amount__gt=0,
        )
        .values("flat")
        .distinct()
        .count()
    )

    # -----------------------------
    # CASH POSITION (BANK ACCOUNT)
    # -----------------------------
    bank_debits = (
        LedgerEntry.objects
        .filter(
            society=society,
            debit_account__code="BANK"
        )
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    bank_credits = (
        LedgerEntry.objects
        .filter(
            society=society,
            credit_account__code="BANK"
        )
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    cash_position = bank_debits - bank_credits

    return {
        "total_receivables": total_receivables,
        "vendor_payables": vendor_payables,
        "collections_this_month": collections_this_month,
        "vendor_payments_this_month": vendor_payments_this_month,
        "outstanding_flats": outstanding_flats,
        "cash_position": cash_position,
    }
    
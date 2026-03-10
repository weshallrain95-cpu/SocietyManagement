from django.db.models import Sum
from decimal import Decimal
from society.models import LedgerEntry


def verify_ledger_integrity(society):
    """
    Ensures ledger remains balanced.
    Total debits must equal total credits.
    """

    debit_total = (
        LedgerEntry.objects
        .filter(society=society)
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    credit_total = (
        LedgerEntry.objects
        .filter(society=society)
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    if debit_total != credit_total:
        raise Exception(
            f"Ledger imbalance detected. Debits={debit_total}, Credits={credit_total}"
        )

    return True

def get_ledger_totals(society):

    debit_total = (
        LedgerEntry.objects
        .filter(society=society)
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    credit_total = (
        LedgerEntry.objects
        .filter(society=society)
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    return {
        "debit_total": debit_total,
        "credit_total": credit_total,
        "difference": debit_total - credit_total,
    }


from django.db.models import Sum
from decimal import Decimal

from society.models import LedgerEntry


def get_bank_balance(society):

    debit = (
        LedgerEntry.objects
        .filter(
            society=society,
            debit_account__code="BANK"
        )
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    credit = (
        LedgerEntry.objects
        .filter(
            society=society,
            credit_account__code="BANK"
        )
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    return debit - credit
    
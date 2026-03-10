from django.db.models import Sum
from decimal import Decimal

from society.models import LedgerEntry, ChartOfAccount


def generate_trial_balance(society):

    accounts = ChartOfAccount.objects.filter(society=society)

    rows = []

    total_debit = Decimal("0.00")
    total_credit = Decimal("0.00")

    for account in accounts:

        debit = (
            LedgerEntry.objects
            .filter(
                society=society,
                debit_account=account
            )
            .aggregate(total=Sum("amount"))["total"]
            or Decimal("0.00")
        )

        credit = (
            LedgerEntry.objects
            .filter(
                society=society,
                credit_account=account
            )
            .aggregate(total=Sum("amount"))["total"]
            or Decimal("0.00")
        )

        if debit == 0 and credit == 0:
            continue

        rows.append({
            "account_code": account.code,
            "account_name": account.name,
            "debit": debit,
            "credit": credit,
        })

        total_debit += debit
        total_credit += credit

    return {
        "rows": rows,
        "totals": {
            "debit": total_debit,
            "credit": total_credit,
        },
        "is_balanced": total_debit == total_credit,
    }
    
from django.db.models import Sum
from decimal import Decimal

from society.models import LedgerEntry, ChartOfAccount


def generate_balance_sheet(society):

    accounts = ChartOfAccount.objects.filter(society=society)

    assets = []
    liabilities = []
    reserves = []

    for account in accounts:

        debit = (
            LedgerEntry.objects
            .filter(society=society, debit_account=account)
            .aggregate(total=Sum("amount"))["total"]
            or Decimal("0.00")
        )

        credit = (
            LedgerEntry.objects
            .filter(society=society, credit_account=account)
            .aggregate(total=Sum("amount"))["total"]
            or Decimal("0.00")
        )

        balance = debit - credit

        if balance == 0:
            continue

        if account.account_type == "ASSET":

            assets.append({
                "account": account.name,
                "amount": balance
            })

        elif account.account_type == "LIABILITY":

            liabilities.append({
                "account": account.name,
                "amount": credit - debit
            })

        elif account.account_type == "RESERVE":

            reserves.append({
                "account": account.name,
                "amount": credit - debit
            })

    return {
        "assets": assets,
        "liabilities": liabilities,
        "reserves": reserves
    }
    
from django.db.models import Sum
from decimal import Decimal

from society.models import LedgerEntry, ChartOfAccount


def generate_income_expenditure(society):

    accounts = ChartOfAccount.objects.filter(society=society)

    income_rows = []
    expense_rows = []

    total_income = Decimal("0.00")
    total_expense = Decimal("0.00")

    for account in accounts:

        if account.account_type not in ["INCOME", "EXPENSE"]:
            continue

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

        if account.account_type == "INCOME":

            amount = credit - debit

            if amount > 0:
                income_rows.append({
                    "account": account.name,
                    "amount": amount
                })

                total_income += amount

        elif account.account_type == "EXPENSE":

            amount = debit - credit

            if amount > 0:
                expense_rows.append({
                    "account": account.name,
                    "amount": amount
                })

                total_expense += amount

    return {
        "income": income_rows,
        "expenses": expense_rows,
        "totals": {
            "income": total_income,
            "expense": total_expense,
            "surplus": total_income - total_expense
        }
    }
    
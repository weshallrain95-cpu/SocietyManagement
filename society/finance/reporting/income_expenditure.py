"""
===============================================================================

SocietyOS Financial Reporting Platform

Income & Expenditure Statement

Consumes the canonical balances produced by the
Account Balance Engine.

Contains NO ledger calculations.

===============================================================================
"""

from decimal import Decimal

from django.utils import timezone

from society.finance.reporting.account_balance_engine import (
    AccountBalanceEngine,
)


class IncomeExpenditureEngine:

    @staticmethod
    def generate_income_expenditure(society):

        report = (
            AccountBalanceEngine
            .generate_account_balances(society)
        )

        balances = report["accounts"]

        income = []

        for balance in balances.values():

            if not balance["has_activity"]:
                continue

            if balance["account_type"] != "INCOME":
                continue

            income.append({

                "account": balance["account"],

                "code": balance["code"],

                "name": balance["name"],

                "amount": balance["closing_balance"],

            })

        expenses = []

        for balance in balances.values():

            if not balance["has_activity"]:
                continue

            if balance["account_type"] != "EXPENSE":
                continue

            expenses.append({

                "account": balance["account"],

                "code": balance["code"],

                "name": balance["name"],

                "amount": balance["closing_balance"],

            })

        total_income = Decimal("0.00")
        total_expenses = Decimal("0.00")

        for row in income:
            total_income += row["amount"]

        for row in expenses:
            total_expenses += row["amount"]

        net_result = total_income - total_expenses

        surplus = Decimal("0.00")
        deficit = Decimal("0.00")

        if net_result >= Decimal("0.00"):
            surplus = net_result
        else:
            deficit = abs(net_result)

        totals = {

            "income": total_income,

            "expenses": total_expenses,

            "surplus": surplus,

            "deficit": deficit,

            "net_result": net_result,

        }

        return {

            "society": society,

            "generated_at": timezone.now(),

            "income": income,

            "expenses": expenses,

            "totals": totals,

        }
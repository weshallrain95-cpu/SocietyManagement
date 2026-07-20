"""
===============================================================================

SocietyOS Financial Reporting Platform

Balance Sheet Engine

Consumes the canonical balances produced by the
Account Balance Engine and the Income & Expenditure Engine.

Contains NO ledger calculations.

===============================================================================
"""

from decimal import Decimal

from django.utils import timezone

from society.finance.reporting.account_balance_engine import (
    AccountBalanceEngine,
)

from society.finance.reporting.income_expenditure import (
    IncomeExpenditureEngine,
)


class BalanceSheetEngine:

    @staticmethod
    def generate_balance_sheet(society):

        balances = (
            AccountBalanceEngine
            .generate_account_balances(society)
        )

        income_statement = (
            IncomeExpenditureEngine
            .generate_income_expenditure(society)
        )

        balances = balances["accounts"]

        assets = []

        for balance in balances.values():

            if not balance["has_activity"]:
                continue

            if balance["account_type"] != "ASSET":
                continue

            assets.append({

                "account": balance["account"],

                "code": balance["code"],

                "name": balance["name"],

                "amount": balance["closing_balance"],

            })

        liabilities = []

        for balance in balances.values():

            if not balance["has_activity"]:
                continue

            if balance["account_type"] != "LIABILITY":
                continue

            liabilities.append({

                "account": balance["account"],

                "code": balance["code"],

                "name": balance["name"],

                "amount": balance["closing_balance"],

            })
        
        equity = []

        for balance in balances.values():

            if not balance["has_activity"]:
                continue

            if balance["account_type"] != "EQUITY":
                continue

            equity.append({

                "account": balance["account"],

                "code": balance["code"],

                "name": balance["name"],

                "amount": balance["closing_balance"],

            })

        current_year_result = {

            "income": (
                income_statement["totals"]["income"]
            ),

            "expenses": (
                income_statement["totals"]["expenses"]
            ),

            "surplus": (
                income_statement["totals"]["surplus"]
            ),

            "deficit": (
                income_statement["totals"]["deficit"]
            ),

            "net_result": (
                income_statement["totals"]["net_result"]
            ),

        }

        total_assets = sum(
            row["amount"]
            for row in assets
        )

        total_liabilities = sum(
            row["amount"]
            for row in liabilities
        )

        total_equity = sum(
            row["amount"]
            for row in equity
        )

        net_worth = (
            total_liabilities
            + total_equity
            + current_year_result["surplus"]
            - current_year_result["deficit"]
        )

        difference = (
            total_assets
            - net_worth
        )

        totals = {

            "assets": total_assets,

            "liabilities": total_liabilities,

            "equity": total_equity,

            "net_worth": net_worth,

            "difference": difference,

            "is_balanced": (
                difference == Decimal("0.00")
            ),

        }

        return {

            "society": society,

            "generated_at": timezone.now(),

            "assets": assets,

            "liabilities": liabilities,

            "equity": equity,

            "current_year_result": current_year_result,

            "totals": totals,

        }
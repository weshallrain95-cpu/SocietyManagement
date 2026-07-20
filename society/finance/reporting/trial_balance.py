"""
===============================================================================

SocietyOS Financial Reporting Platform

Trial Balance Engine

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


class TrialBalanceEngine:

    @staticmethod
    def generate_trial_balance(society):

        report = (
            AccountBalanceEngine
            .generate_account_balances(society)
        )

        balances = report["accounts"]

        rows = []

        for balance in balances.values():
            if not balance["has_activity"]:
                continue
            debit = Decimal("0.00")
            credit = Decimal("0.00")

            if balance["closing_side"] == "DEBIT":
                debit = balance["closing_balance"]
            else:
                credit = balance["closing_balance"]

            rows.append({

                "account": balance["account"],

                "code": balance["code"],

                "name": balance["name"],

                "account_type": balance["account_type"],

                "debit": debit,

                "credit": credit,

            })

            total_debit = Decimal("0.00")
            total_credit = Decimal("0.00")

            for row in rows:

                total_debit += row["debit"]

                total_credit += row["credit"]

            difference = total_debit - total_credit

            totals = {

                "debit": total_debit,

                "credit": total_credit,

                "difference": difference,

                "is_balanced": (
                    total_debit == total_credit
                ),

            }

        return {
            "society": society,
            "generated_at": timezone.now(),
            "rows": rows,
            "totals": totals,
        }

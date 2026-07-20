"""
===============================================================================

SocietyOS Financial Reporting Platform

Account Balance Engine
----------------------

The Account Balance Engine is the single source of financial truth.

Its responsibility is to calculate the closing balance of every
Chart of Account from the General Ledger (LedgerEntryV2).

No report should ever calculate balances independently.

Consumers:

    • Trial Balance
    • Income & Expenditure Statement
    • Balance Sheet
    • General Ledger
    • Ledger Integrity
    • Audit Reports

===============================================================================
"""

from decimal import Decimal

from django.utils import timezone

from society.models import (
    ChartOfAccount,
    LedgerEntryV2,
)


class AccountBalanceEngine:
    """
    Generates account balances from the production ledger.
    """

    @staticmethod
    def generate_account_balances(society):

        #
        # ------------------------------------------------------------------
        # STEP 1
        # Load every Chart of Account.
        # ------------------------------------------------------------------
        #

        balances = {}

        accounts = (
            ChartOfAccount.objects
            .filter(society=society)
            .order_by("code")
        )

        for account in accounts:

            balances[account.id] = {

                "account": account,

                "account_id": account.id,

                "code": account.code,

                "name": account.name,

                "account_type": account.account_type,

                "subtype": getattr(account, "subtype", None),

                "debit_total": Decimal("0.00"),

                "credit_total": Decimal("0.00"),

                "has_activity": False,

                "entry_count": 0,

                "first_activity": None,

                "last_activity": None,

                "closing_side": None,

                "closing_balance": Decimal("0.00"),

                "net_movement": Decimal("0.00"),
            }

        #
        # ------------------------------------------------------------------
        # STEP 2
        # Load every ledger line belonging to this society.
        # ------------------------------------------------------------------
        #

        ledger_entries = (
            LedgerEntryV2.objects
            .select_related(
                "transaction",
                "account",
            )
            .filter(
                transaction__society=society,
            )
            .order_by(
                "id",
            )
        )

        #
        # ------------------------------------------------------------------
        # STEP 3
        # Walk the ledger exactly once.
        # ------------------------------------------------------------------
        #

        for entry in ledger_entries:

            balance = balances.get(entry.account_id)

            if balance is None:
                continue

            balance["entry_count"] += 1

            activity_date = entry.transaction.transaction_date

            if balance["first_activity"] is None:
                balance["first_activity"] = activity_date

            balance["last_activity"] = activity_date

            if entry.entry_type == "DEBIT":

                balance["debit_total"] += entry.amount

            elif entry.entry_type == "CREDIT":

                balance["credit_total"] += entry.amount

        #
        # ------------------------------------------------------------------
        # STEP 4
        # Compute closing balances.
        # ------------------------------------------------------------------
        #

        for balance in balances.values():

            balance["has_activity"] = (
                balance["debit_total"] != Decimal("0.00")
                or
                balance["credit_total"] != Decimal("0.00")
            )
            
            debit = balance["debit_total"]

            credit = balance["credit_total"]

            balance["net_movement"] = debit - credit

            if debit >= credit:

                balance["closing_side"] = "DEBIT"

                balance["closing_balance"] = debit - credit

            else:

                balance["closing_side"] = "CREDIT"

                balance["closing_balance"] = credit - debit

        
        summary = {

            "total_accounts": len(balances),

            "active_accounts": sum(
                1
                for balance in balances.values()
                if balance["has_activity"]
            ),

            "debit_accounts": sum(
                1
                for balance in balances.values()
                if balance["closing_side"] == "DEBIT"
            ),

            "credit_accounts": sum(
                1
                for balance in balances.values()
                if balance["closing_side"] == "CREDIT"
            ),
        }
        
        return {
            "society": society,
            "generated_at": timezone.now(),
            "accounts": balances,
            "summary": summary,
        }
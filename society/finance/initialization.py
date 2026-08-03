from datetime import date
from decimal import Decimal

from django.db import transaction

from society.models import (
    ChartOfAccount,
    AccountGroup,
    AccountingPeriod,
)

from society.services import post_double_entry
from society.finance.ledger_integrity import verify_ledger_integrity
from society.finance.trial_balance import generate_trial_balance
from society.finance.kernel.coa_seed import seed_core_coa
from society.finance.kernel.asset_coa_seed import (
    seed_asset_coa,
)

"""
===============================================================================
 SocietyOS Financial Onboarding Orchestrator
===============================================================================

File:
    society/finance/initialization.py

Status:
    ACTIVE
    Canonical Financial Initialization / Onboarding Orchestrator

Architecture Version:
    Finance Platform V2

Refined On:
    2026-07-21

-------------------------------------------------------------------------------
PURPOSE
-------------------------------------------------------------------------------

This module is the single orchestration entry point responsible for preparing
the financial foundation of a society.

It does NOT perform accounting itself.

Instead, it coordinates the various specialized financial initialization
services required before the society can begin financial operations.

This module intentionally contains orchestration logic only.

Business Rule:

    "Users onboard a financial system.
     Services provision the accounting foundation."

-------------------------------------------------------------------------------
WHY THIS FILE EXISTS
-------------------------------------------------------------------------------

During the evolution of the Finance Platform, multiple initialization
mechanisms emerged.

Earlier implementations embedded Chart of Accounts creation directly inside
this file.

Later iterations introduced dedicated provisioning services such as:

    seed_core_coa()

This file has now been repurposed to become the orchestration layer rather
than owning individual initialization responsibilities.

It coordinates specialized services instead of duplicating them.

-------------------------------------------------------------------------------
DESIGN PRINCIPLES
-------------------------------------------------------------------------------

Every initialization step must be:

✓ Idempotent
✓ Safe to execute repeatedly
✓ Independently testable
✓ Independently replaceable
✓ Business driven
✓ Atomic

This allows financial onboarding to be resumed safely from any point.

-------------------------------------------------------------------------------
THIS MODULE SHOULD NEVER
-------------------------------------------------------------------------------

This module should never contain:

• Chart of Account definitions
• Posting logic
• Ledger logic
• Trial Balance calculations
• Validation algorithms
• Domain-specific accounting rules

Those belong in their respective services.

-------------------------------------------------------------------------------
THIS MODULE SHOULD ONLY
-------------------------------------------------------------------------------

Coordinate the financial onboarding workflow:

    Ensure Account Groups

        ↓

    Ensure Core Chart of Accounts

        ↓

    Ensure Financial Period

        ↓

    Ensure Opening Balances

        ↓

    Verify Ledger Integrity

        ↓

    Verify Trial Balance

        ↓

    Return Initialization Status

-------------------------------------------------------------------------------
LEGACY NOTE
-------------------------------------------------------------------------------

The original implementation embedded:

    seed_chart_of_accounts()

directly inside this module.

That implementation has been superseded by:

    society.finance.kernel.coa_seed.seed_core_coa()

which represents the Finance Platform V2 accounting model.

The legacy COA implementation is retained only for historical reference until
its complete removal.

-------------------------------------------------------------------------------
WORKING PROTOCOL
-------------------------------------------------------------------------------

When extending financial onboarding:

DO

✓ Add new orchestration steps here.
✓ Keep orchestration linear.
✓ Delegate business logic to specialized modules.
✓ Keep every step idempotent.

DO NOT

✗ Embed accounting rules.
✗ Duplicate domain services.
✗ Create alternative initialization paths.
✗ Couple orchestration to UI screens.

There must always be one canonical initialization pipeline.

===============================================================================
"""
# -------------------------------------------------------------------
# 1. ACCOUNT GROUPS
# -------------------------------------------------------------------

ACCOUNT_GROUPS = [

    {"code": "ASSET", "name": "Assets", "category": "ASSET"},
    {"code": "LIABILITY", "name": "Liabilities", "category": "LIABILITY"},
    {"code": "EQUITY", "name": "Equity", "category": "EQUITY"},
    {"code": "INCOME", "name": "Income", "category": "INCOME"},
    {"code": "EXPENSE", "name": "Expenses", "category": "EXPENSE"},

    {"code": "RECEIVABLE", "name": "Receivables", "category": "ASSET"},
    {"code": "PAYABLE", "name": "Payables", "category": "LIABILITY"},
    {"code": "FUND", "name": "Society Funds", "category": "LIABILITY"},

    {"code": "SYSTEM", "name": "System Accounts", "category": "LIABILITY"},
]


def seed_account_groups():

    for g in ACCOUNT_GROUPS:

        AccountGroup.objects.get_or_create(
            code=g["code"],
            defaults={
                "name": g["name"],
                "category": g["category"],
            },
        )


# -------------------------------------------------------------------
# 3. CREATE FINANCIAL YEAR
# -------------------------------------------------------------------

def create_financial_year(society, year_start):

    start = date(year_start, 4, 1)
    end = date(year_start + 1, 3, 31)

    AccountingPeriod.objects.get_or_create(
        society=society,
        start_date=start,
        end_date=end,
        defaults={"is_open": True},
    )


# -------------------------------------------------------------------
# 4. OPENING BALANCES
# -------------------------------------------------------------------

def create_opening_balances(society, opening_data):

    adjustment_account = ChartOfAccount.objects.get(
        society=society,
        code="9998",
    )

    for account_code, amount in opening_data.items():

        amount = Decimal(amount)

        if amount == 0:
            continue

        account = ChartOfAccount.objects.get(
            society=society,
            code=account_code,
        )

        if account.group.category == "ASSET":

            post_double_entry(
                society=society,
                debit_account_code=account.code,
                credit_account_code=adjustment_account.code,
                amount=abs(amount),
                description="Opening Balance",
                source_type="FIN_INIT",
                source_ref="OPENING_BALANCE",
            )

        else:

            post_double_entry(
                society=society,
                debit_account_code=adjustment_account.code,
                credit_account_code=account.code,
                amount=abs(amount),
                description="Opening Balance",
                source_type="FIN_INIT",
                source_ref="OPENING_BALANCE",
            )


# -------------------------------------------------------------------
# 5. FINANCIAL ONBOARDING ORCHESTRATION
# -------------------------------------------------------------------

from society.finance.balance_sanity import validate_opening_balances

@transaction.atomic
def initialize_finance(
    society,
    financial_year,
    opening_data=None,
):

    #
    # Financial initialization is intentionally idempotent.
    #
    # This orchestrator may be executed multiple times throughout
    # Financial Onboarding.
    #
    # Each downstream service is responsible for ensuring its own
    # state and must therefore be safe to execute repeatedly.
    #
    # Never short-circuit this orchestration solely because
    # finance_initialized=True.
    #
    # Idempotency is a contractual requirement of every
    # initialization service.
    #

    seed_account_groups()

    seed_core_coa(society)

    seed_asset_coa(society)

    create_financial_year(society, financial_year)

    if opening_data:
        validate_opening_balances(society, opening_data)
        create_opening_balances(society, opening_data)

    verify_ledger_integrity(society)

    tb = generate_trial_balance(society)

    if not tb["is_balanced"]:
        raise Exception("Opening Trial Balance failed")


    return tb

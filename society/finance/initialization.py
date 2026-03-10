from datetime import date
from django.db import transaction

from society.models import (
    AccountGroup,
    ChartOfAccount,
    AccountingPeriod,
)

# -------------------------------------------------------------------
# 1. ACCOUNT GROUP SEEDING
# -------------------------------------------------------------------

ACCOUNT_GROUPS = [

    {"code": "ASSET", "name": "Assets", "category": "ASSET"},
    {"code": "LIABILITY", "name": "Liabilities", "category": "LIABILITY"},
    {"code": "INCOME", "name": "Income", "category": "INCOME"},
    {"code": "EXPENSE", "name": "Expenses", "category": "EXPENSE"},
    {"code": "FUND", "name": "Society Funds", "category": "LIABILITY"},
    {"code": "RECEIVABLE", "name": "Receivables", "category": "ASSET"},
    {"code": "PAYABLE", "name": "Payables", "category": "LIABILITY"},
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
# 2. MASTER CHART OF ACCOUNTS
# (Derived from the reference society financial statement)
# -------------------------------------------------------------------

MASTER_COA = [

    # ---- ASSETS ----

    {"code": "BANK", "name": "Bank Account", "group": "ASSET"},
    {"code": "CASH", "name": "Cash In Hand", "group": "ASSET"},
    {"code": "FIXED_DEPOSIT", "name": "Fixed Deposits", "group": "ASSET"},

    # ---- RECEIVABLES ----

    {"code": "MAINT_RECEIVABLE", "name": "Maintenance Receivable", "group": "RECEIVABLE"},
    {"code": "INTEREST_RECEIVABLE", "name": "Interest Receivable", "group": "RECEIVABLE"},

    # ---- FUNDS ----

    {"code": "SINKING_FUND", "name": "Sinking Fund", "group": "FUND"},
    {"code": "REPAIR_FUND", "name": "Repair Fund", "group": "FUND"},
    {"code": "BUILDING_FUND", "name": "Building Fund", "group": "FUND"},
    {"code": "SECURITY_DEPOSIT", "name": "Security Deposits", "group": "LIABILITY"},
    {"code": "SHARE_CAPITAL", "name": "Share Capital", "group": "LIABILITY"},

    # ---- INCOME ----

    {"code": "MAINT_INCOME", "name": "Maintenance Charges", "group": "INCOME"},
    {"code": "INTEREST_INCOME", "name": "Interest Income", "group": "INCOME"},
    {"code": "PARKING_INCOME", "name": "Parking Charges", "group": "INCOME"},
    {"code": "TRANSFER_FEES", "name": "Transfer Fees", "group": "INCOME"},

    # ---- EXPENSES (from the PDF structure) ----

    {"code": "ELECTRICITY_EXPENSE", "name": "Electricity Expenses", "group": "EXPENSE"},
    {"code": "SECURITY_EXPENSE", "name": "Security Expenses", "group": "EXPENSE"},
    {"code": "HOUSEKEEPING_EXPENSE", "name": "Housekeeping Expenses", "group": "EXPENSE"},
    {"code": "GARDEN_EXPENSE", "name": "Garden Expenses", "group": "EXPENSE"},
    {"code": "REPAIR_EXPENSE", "name": "Repair & Maintenance", "group": "EXPENSE"},
    {"code": "AUDIT_FEES", "name": "Audit Fees", "group": "EXPENSE"},
    {"code": "SALARY_EXPENSE", "name": "Salary & Staff Expenses", "group": "EXPENSE"},
    {"code": "LEGAL_EXPENSE", "name": "Legal / Professional Fees", "group": "EXPENSE"},
    {"code": "SOFTWARE_EXPENSE", "name": "Software Expenses", "group": "EXPENSE"},
    {"code": "WEBSITE_EXPENSE", "name": "Website Expenses", "group": "EXPENSE"},

    # ---- SYSTEM ----

    {"code": "OPENING_BALANCE_ADJUSTMENT", "name": "Opening Balance Adjustment", "group": "SYSTEM"},
    {"code": "SUSPENSE_ACCOUNT", "name": "Suspense Account", "group": "SYSTEM"},
]


def seed_chart_of_accounts(society):

    for account in MASTER_COA:

        group = AccountGroup.objects.get(code=account["group"])

        ChartOfAccount.objects.get_or_create(
            society=society,
            code=account["code"],
            defaults={
                "name": account["name"],
                "group": group,
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
# 4. MASTER INITIALIZATION ENTRY POINT
# -------------------------------------------------------------------

@transaction.atomic
def initialize_finance(society, financial_year):

    """
    Bootstraps full finance structure for a society.
    """

    seed_account_groups()

    seed_chart_of_accounts(society)

    create_financial_year(society, financial_year)

    society.finance_initialized = True
    society.save(update_fields=["finance_initialized"])


from decimal import Decimal

from society.services import post_double_entry


def create_opening_balances(society, opening_data):

    """
    Converts opening balances into ledger entries.
    """

    adjustment_account = ChartOfAccount.objects.get(
        society=society,
        code="OPENING_BALANCE_ADJUSTMENT",
    )

    for account_code, amount in opening_data.items():

        amount = Decimal(amount)

        if amount == 0:
            continue

        account = ChartOfAccount.objects.get(
            society=society,
            code=account_code,
        )

        # Asset accounts → Debit
        if amount > 0:

            post_double_entry(
                society=society,
                debit_account_code=account.code,
                credit_account_code=adjustment_account.code,
                amount=abs(amount),
                description="Opening Balance",
                source_type="FIN_INIT",
                source_ref="OPENING_BALANCE",
            )

        # Liability accounts → Credit
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

@transaction.atomic
def initialize_finance(society, financial_year, opening_data=None):

    seed_account_groups()

    seed_chart_of_accounts(society)

    create_financial_year(society, financial_year)

    if opening_data:
        create_opening_balances(society, opening_data)

    society.finance_initialized = True
    society.save(update_fields=["finance_initialized"])

@transaction.atomic
def initialize_finance(
    society,
    financial_year,
    opening_data=None
):

    seed_account_groups()

    seed_chart_of_accounts(society)

    create_financial_year(society, financial_year)

    if opening_data:
        create_opening_balances(society, opening_data)

    from society.finance.ledger_integrity import verify_ledger_integrity

    verify_ledger_integrity(society)

    opening_tb = generate_opening_trial_balance(society)

    society.finance_initialized = True
    society.save(update_fields=["finance_initialized"])

    return opening_tb


from society.finance.trial_balance import generate_trial_balance

def generate_opening_trial_balance(society):

    """
    Generates a trial balance immediately after initialization
    to verify opening ledger correctness.
    """

    tb = generate_trial_balance(society)

    if not tb["is_balanced"]:

        raise Exception(
            "Opening Trial Balance failed. Ledger is not balanced."
        )

    return tb


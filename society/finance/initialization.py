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


# -------------------------------------------------------------------
# 1. ACCOUNT GROUPS
# -------------------------------------------------------------------

ACCOUNT_GROUPS = [

    {"code": "ASSET", "name": "Assets", "category": "ASSET"},
    {"code": "LIABILITY", "name": "Liabilities", "category": "LIABILITY"},
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
# 2. MASTER CHART OF ACCOUNTS (PHASE-1)
# -------------------------------------------------------------------

MASTER_COA = [

    # ---------- ASSETS ----------

    {"code": "1000", "name": "Bank Account", "group": "ASSET"},
    {"code": "1010", "name": "Cash", "group": "ASSET"},
    {"code": "1020", "name": "Fixed Deposits", "group": "ASSET"},

    {"code": "1100", "name": "Maintenance Receivable", "group": "RECEIVABLE"},
    {"code": "1110", "name": "Interest Receivable", "group": "RECEIVABLE"},
    {"code": "1120", "name": "Other Receivable", "group": "RECEIVABLE"},

    {"code": "1200", "name": "Member Advances", "group": "ASSET"},

    {"code": "1300", "name": "Building Asset", "group": "ASSET"},
    {"code": "1310", "name": "Lift Asset", "group": "ASSET"},
    {"code": "1320", "name": "Electrical Asset", "group": "ASSET"},
    {"code": "1330", "name": "CCTV Asset", "group": "ASSET"},
    {"code": "1340", "name": "Computer Asset", "group": "ASSET"},
    {"code": "1350", "name": "Fire System Asset", "group": "ASSET"},

    # ---------- LIABILITIES ----------

    {"code": "2000", "name": "Maintenance Payable", "group": "PAYABLE"},

    {"code": "2100", "name": "Share Capital", "group": "FUND"},
    {"code": "2110", "name": "Building Fund", "group": "FUND"},
    {"code": "2120", "name": "Sinking Fund", "group": "FUND"},
    {"code": "2130", "name": "Repair Fund", "group": "FUND"},
    {"code": "2140", "name": "Education Fund", "group": "FUND"},
    {"code": "2150", "name": "Election Fund", "group": "FUND"},

    {"code": "2200", "name": "Member Security Deposits", "group": "LIABILITY"},
    {"code": "2210", "name": "Vendor Payables", "group": "PAYABLE"},
    {"code": "2220", "name": "Audit Fees Payable", "group": "PAYABLE"},

    # ---------- INCOME ----------

    {"code": "3000", "name": "Maintenance Income", "group": "INCOME"},
    {"code": "3010", "name": "Parking Income", "group": "INCOME"},
    {"code": "3020", "name": "Interest Income", "group": "INCOME"},
    {"code": "3030", "name": "Transfer Fees", "group": "INCOME"},
    {"code": "3040", "name": "Late Fees", "group": "INCOME"},
    {"code": "3050", "name": "Hall Booking Income", "group": "INCOME"},
    {"code": "3060", "name": "Water Charges Recovery", "group": "INCOME"},
    {"code": "3070", "name": "Electricity Charges Recovery", "group": "INCOME"},
    {"code": "3080", "name": "Misc Income", "group": "INCOME"},

    # ---------- EXPENSES ----------

    {"code": "4000", "name": "Salary Expense", "group": "EXPENSE"},
    {"code": "4010", "name": "Security Expense", "group": "EXPENSE"},
    {"code": "4020", "name": "Electricity Expense", "group": "EXPENSE"},
    {"code": "4030", "name": "Water Expense", "group": "EXPENSE"},
    {"code": "4040", "name": "Repair Expense", "group": "EXPENSE"},
    {"code": "4050", "name": "Lift Maintenance", "group": "EXPENSE"},
    {"code": "4060", "name": "Garden Expense", "group": "EXPENSE"},
    {"code": "4070", "name": "Insurance Expense", "group": "EXPENSE"},
    {"code": "4080", "name": "Bank Charges", "group": "EXPENSE"},
    {"code": "4090", "name": "Legal & Professional", "group": "EXPENSE"},
    {"code": "4100", "name": "Software Expense", "group": "EXPENSE"},
    {"code": "4110", "name": "Printing & Stationery", "group": "EXPENSE"},
    {"code": "4120", "name": "Office Expense", "group": "EXPENSE"},
    {"code": "4130", "name": "Telephone Expense", "group": "EXPENSE"},
    {"code": "4140", "name": "Diesel Expense", "group": "EXPENSE"},
    {"code": "4150", "name": "Postage & Courier", "group": "EXPENSE"},

    # ---------- PAYABLES ----------

    {
        "code": "2230",
        "name": "TDS Payable",
        "group": "PAYABLE",
    },

    {
        "code": "2240",
        "name": "Vendor Security Deposit",
        "group": "PAYABLE",
    },

    {
        "code": "2250",
        "name": "Vendor Retention Payable",
        "group": "PAYABLE",
    },

    {
        "code": "1210",
        "name": "Vendor Advances",
        "group": "ASSET",
    },

    {
        "code": "1220",
        "name": "GST Input Credit",
        "group": "ASSET",
    },
    
    # ---------- SYSTEM ----------

    {"code": "9998", "name": "Opening Balance Adjustment", "group": "SYSTEM"},
    {"code": "9999", "name": "Suspense Account", "group": "SYSTEM"},

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
                "is_system": True,
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
# 5. MASTER INITIALIZATION
# -------------------------------------------------------------------

from society.finance.balance_sanity import validate_opening_balances

@transaction.atomic
def initialize_finance(
    society,
    financial_year,
    opening_data=None,
):

    if society.finance_initialized:
        raise Exception("Finance already initialized for this society")

    seed_account_groups()

    seed_chart_of_accounts(society)

    create_financial_year(society, financial_year)

    if opening_data:
        validate_opening_balances(society, opening_data)
        create_opening_balances(society, opening_data)

    verify_ledger_integrity(society)

    tb = generate_trial_balance(society)

    if not tb["is_balanced"]:
        raise Exception("Opening Trial Balance failed")

    society.finance_initialized = True
    society.save(update_fields=["finance_initialized"])

    return tb

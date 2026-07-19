from decimal import Decimal
from django.utils import timezone

from society.finance.kernel.posting_engine import post_transaction
from society.finance.kernel.expense_account_factory import get_expense_account
from society.models import BankAccount


def record_expense_payment(
    *,
    society,
    amount,
    subtype,
    bank_account_id,
    reference_id,
    description="",
):

    """
    ==========================================================
    SocietyOS
    Direct Expense Payment Engine
    ==========================================================

    Purpose
    -------

    Records immediate Expense Payments made
    directly by the Society.

    This engine is intended for expenses that
    do NOT pass through the Vendor Procurement
    lifecycle.

    Examples

    • Petty Cash
    • Courier Charges
    • Refreshments
    • Office Supplies
    • Staff Reimbursements
    • Cash Purchases
    • Immediate Utility Payments
    • Miscellaneous Administrative Expenses

    Accounting

        Dr Expense

        Cr Bank

    This is an immediate cash / bank
    disbursement.

    ----------------------------------------------------------

    This engine does NOT create:

    • Expense Authorization
    • Vendor Bill
    • Vendor Payable
    • Vendor Payment

    ----------------------------------------------------------

    Vendor Procurement follows a completely
    different workflow.

    Expense Authorization

            ↓

    Vendor Bill

            ↓

    Vendor Payable

            ↓

    Vendor Payment

            ↓

    Bank Payment

    ----------------------------------------------------------

    Single Responsibility

    Record immediate expense payments that do
    not generate Vendor Payables.

    The Payables subsystem owns all vendor
    procurement workflows.
    ==========================================================
    """

    # 🔥 Get expense account
    expense_account = get_expense_account(
        society=society,
        subtype=subtype,
    )

    # 🔥 Get bank account
    bank = BankAccount.objects.get(
        id=bank_account_id,
        society=society
    )

    bank_account = bank.chart_account
    
    if amount <= 0:
        raise ValueError("Amount must be positive")

    if not reference_id:
        raise ValueError("reference_id is required")
    
    return post_transaction(
        society=society,
        transaction_type="PAYMENT",
        reference_type="EXPENSE_PAYMENT",
        reference_id=reference_id,
        description=description or f"{subtype} expense",

        transaction_date=timezone.now().date(),

        entries=[
            {
                "account": expense_account,
                "type": "DEBIT",
                "amount": Decimal(amount),
            },
            {
                "account": bank_account,
                "type": "CREDIT",
                "amount": Decimal(amount),
            },
        ],
    )
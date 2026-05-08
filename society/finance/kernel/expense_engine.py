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
    Records an expense payment from society.
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
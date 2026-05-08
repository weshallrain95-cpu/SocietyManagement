from decimal import Decimal
from django.utils import timezone

from society.finance.kernel.posting_engine import post_transaction
from society.models import ChartOfAccount, BankAccount


def record_member_payment(
    *,
    society,
    flat,
    amount,
    bank_account_id,
    reference_id,
):
    """
    Records payment received from member.
    """

    # 🔥 Get bank account
    bank = BankAccount.objects.get(
        id=bank_account_id,
        society=society
    )

    bank_account = bank.chart_account

    # 🔥 Get receivable account
    receivable_account = ChartOfAccount.objects.get(
        society=society,
        code="MEMBER_RECEIVABLES"
    )

    if amount <= 0:
        raise ValueError("Amount must be positive")

    if not reference_id:
        raise ValueError("reference_id is required")
        
    return post_transaction(
        society=society,
        transaction_type="PAYMENT",
        reference_type="MEMBER_PAYMENT",
        reference_id=reference_id,
        description=f"Payment received from flat {flat.id}",
        transaction_date=timezone.now().date(),

        entries=[
            {
                "account": bank_account,
                "type": "DEBIT",
                "amount": Decimal(amount),
                "flat": flat,
            },
            {
                "account": receivable_account,
                "type": "CREDIT",
                "amount": Decimal(amount),
                "flat": flat,
            },
        ],
    )
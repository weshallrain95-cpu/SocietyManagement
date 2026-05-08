from decimal import Decimal
from django.utils import timezone

from society.finance.kernel.posting_engine import post_transaction
from society.finance.kernel.income_account_factory import get_income_account
from society.models import ChartOfAccount


def generate_member_bill(
    *,
    society,
    flat,
    amount,
    subtype,
    reference_id,
):
    """
    Creates a billing transaction for a member.
    """

    # 🔥 Get accounts
    income_account = get_income_account(
        society=society,
        subtype=subtype,
    )

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
        transaction_type="BILL",
        reference_type="MEMBER_BILL",
        reference_id=reference_id,
        description=f"{subtype} bill for flat {flat.id}",
        transaction_date=timezone.now().date(),

        entries=[
            {
                "account": receivable_account,
                "type": "DEBIT",
                "amount": Decimal(amount),
                "flat": flat,
            },
            {
                "account": income_account,
                "type": "CREDIT",
                "amount": Decimal(amount),
                "flat": flat,
            },
        ],
    )
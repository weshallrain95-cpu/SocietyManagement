from decimal import Decimal
from django.db import transaction
from society.models import LedgerEntry


@transaction.atomic
def post_journal(
    *,
    society,
    flat=None,
    debit_account,
    credit_account,
    amount: Decimal,
    description,
    reference_type=None,
    reference_id=None,
):
    """
    Core financial posting engine.
    All financial transactions must pass through here.
    """

    if amount <= 0:
        raise ValueError("Journal amount must be positive")

    LedgerEntry.objects.create(
        society=society,
        flat=flat,
        debit_account=debit_account,
        credit_account=credit_account,
        amount=amount,
        description=description,
        reference_type=reference_type,
        reference_id=reference_id,
    )

    
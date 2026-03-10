from decimal import Decimal

from society.models import LedgerEntry


def get_flat_statement(flat):
    """
    Returns a UI-ready ledger statement for a flat.

    Each row contains:
    date
    description
    signed amount (+ve bill, -ve payment)
    running balance
    """

    entries = (
        LedgerEntry.objects
        .filter(flat=flat)
        .select_related("debit_account", "credit_account")
        .order_by("entry_date", "id")
    )

    statement = []
    balance = Decimal("0.00")

    for entry in entries:

        debit = entry.debit_account.code
        credit = entry.credit_account.code
        amount = entry.amount

        signed_amount = Decimal("0.00")

        # Bill raised → receivable increases
        if credit == "PAYABLE":
            signed_amount = amount
            balance += amount

        # Payment received → receivable decreases
        elif debit == "PAYABLE":
            signed_amount = -amount
            balance -= amount

        statement.append({
            "date": entry.entry_date,
            "description": entry.description,
            "amount": signed_amount,
            "balance": balance,
        })

    return statement
    
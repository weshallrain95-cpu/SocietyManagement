from decimal import Decimal
from django.db.models import Sum

from society.models import Flat, LedgerEntry


def get_society_receivable_snapshot(society):
    """
    Optimized receivable snapshot.
    Avoids N+1 queries.
    """

    flats = Flat.objects.filter(society=society)

    # PAYABLE credits = payments
    payable_credits = (
        LedgerEntry.objects
        .filter(
            society=society,
            credit_account__code="PAYABLE"
        )
        .values("flat")
        .annotate(total=Sum("amount"))
    )

    # PAYABLE debits = bills
    payable_debits = (
        LedgerEntry.objects
        .filter(
            society=society,
            debit_account__code="PAYABLE"
        )
        .values("flat")
        .annotate(total=Sum("amount"))
    )

    credit_map = {r["flat"]: r["total"] for r in payable_credits}
    debit_map = {r["flat"]: r["total"] for r in payable_debits}

    balances = []

    for flat in flats:
        credits = credit_map.get(flat.id, Decimal("0.00"))
        debits = debit_map.get(flat.id, Decimal("0.00"))

        # Correct formula
        balance = debits - credits

        balances.append({
            "flat_id": flat.id,
            "flat_number": flat.flat_number,
            "balance": balance,
        })

    total_receivable = sum(b["balance"] for b in balances)

    defaulters = [
        b for b in balances
        if b["balance"] > Decimal("0.00")
    ]

    return {
        "total_flats": flats.count(),
        "total_receivable": total_receivable,
        "defaulter_count": len(defaulters),
        "defaulters": sorted(
            defaulters,
            key=lambda x: x["balance"],
            reverse=True
        ),
    }

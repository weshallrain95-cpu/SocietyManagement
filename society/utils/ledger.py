def get_flat_statement(flat):
    entries = (
        LedgerEntry.objects
        .filter(flat=flat)
        .order_by("created_at", "id")
    )

    running_balance = Decimal("0.00")
    statement = []

    for e in entries:
        running_balance += e.amount
        statement.append({
            "date": e.created_at.date(),
            "category": e.category,
            "description": e.description,
            "amount": e.amount,
            "balance": running_balance,
        })

    return statement
def get_flat_outstanding(flat):
    return (
        LedgerEntry.objects
        .filter(
            flat=flat,
            amount__gt=0,
            is_settled=False,
        )
        .aggregate(total=models.Sum("amount") - models.Sum("settled_amount"))
        ["total"] or Decimal("0.00")
    )
from datetime import date

def get_flat_ageing(flat, as_of=None):
    as_of = as_of or date.today()

    buckets = {
        "0_30": Decimal("0.00"),
        "31_60": Decimal("0.00"),
        "61_90": Decimal("0.00"),
        "90_plus": Decimal("0.00"),
    }

    dues = LedgerEntry.objects.filter(
        flat=flat,
        amount__gt=0,
        is_settled=False,
    )

    for d in dues:
        days = (as_of - d.created_at.date()).days
        outstanding = d.amount - d.settled_amount

        if days <= 30:
            buckets["0_30"] += outstanding
        elif days <= 60:
            buckets["31_60"] += outstanding
        elif days <= 90:
            buckets["61_90"] += outstanding
        else:
            buckets["90_plus"] += outstanding

    return buckets
def get_society_receivables(society):
    flats = Flat.objects.filter(society=society)

    total = Decimal("0.00")
    ageing_totals = {
        "0_30": Decimal("0.00"),
        "31_60": Decimal("0.00"),
        "61_90": Decimal("0.00"),
        "90_plus": Decimal("0.00"),
    }

    for flat in flats:
        ageing = get_flat_ageing(flat)
        for k in ageing_totals:
            ageing_totals[k] += ageing[k]
        total += sum(ageing.values())

    return {
        "total_receivable": total,
        "ageing": ageing_totals,
    }

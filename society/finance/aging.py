from datetime import date
from decimal import Decimal
from django.db.models import Sum

from society.models import FlatMaintenanceBill, LedgerEntry


def get_maintenance_aging_report(society):

    today = date.today()

    bills = (
        FlatMaintenanceBill.objects
        .filter(bill__society=society)
        .select_related("flat", "bill")
        .order_by("bill__billing_month")
    )

    payments = (
        LedgerEntry.objects
        .filter(
            society=society,
            credit_account__code="PAYABLE"
        )
        .values("flat")
        .annotate(total=Sum("amount"))
    )

    payment_map = {p["flat"]: p["total"] for p in payments}

    rows = []

    total_0_30 = Decimal("0.00")
    total_30_60 = Decimal("0.00")
    total_60_90 = Decimal("0.00")
    total_90_plus = Decimal("0.00")

    # Track remaining payment per flat
    flat_remaining_payment = payment_map.copy()

    for b in bills:

        remaining_payment = flat_remaining_payment.get(b.flat.id, Decimal("0.00"))

        bill_amount = b.total_payable

        applied = min(bill_amount, remaining_payment)

        outstanding = bill_amount - applied

        flat_remaining_payment[b.flat.id] = remaining_payment - applied

        if outstanding <= 0:
            continue

        days = (today - b.bill.billing_month).days

        bucket_0_30 = bucket_30_60 = bucket_60_90 = bucket_90_plus = Decimal("0.00")

        if days <= 30:
            bucket_0_30 = outstanding
            total_0_30 += outstanding

        elif days <= 60:
            bucket_30_60 = outstanding
            total_30_60 += outstanding

        elif days <= 90:
            bucket_60_90 = outstanding
            total_60_90 += outstanding

        else:
            bucket_90_plus = outstanding
            total_90_plus += outstanding

        rows.append({
            "flat_number": b.flat.flat_number,
            "0_30": bucket_0_30,
            "30_60": bucket_30_60,
            "60_90": bucket_60_90,
            "90_plus": bucket_90_plus,
            "total": outstanding,
        })

    return {
        "rows": rows,
        "totals": {
            "0_30": total_0_30,
            "30_60": total_30_60,
            "60_90": total_60_90,
            "90_plus": total_90_plus,
            "grand_total": total_0_30 + total_30_60 + total_60_90 + total_90_plus,
        }
    }
    
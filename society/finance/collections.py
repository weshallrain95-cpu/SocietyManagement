from decimal import Decimal
from django.db.models import Sum

from society.models import FlatMaintenanceBill, LedgerEntry


def get_maintenance_collection_tracker(society, billing_month):
    """
    Returns billing vs collection snapshot for a given month.
    """

    # Total billed
    billed = (
        FlatMaintenanceBill.objects
        .filter(
            bill__society=society,
            bill__billing_month=billing_month
        )
        .aggregate(total=Sum("total_payable"))["total"]
        or Decimal("0.00")
    )

    # Total collected
    collected = (
        LedgerEntry.objects
        .filter(
            society=society,
            debit_account__code="PAYABLE",
            source_type="PAYMENT"
        )
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    outstanding = billed - collected

    collection_rate = Decimal("0.00")

    if billed > 0:
        collection_rate = (collected / billed) * Decimal("100.00")

    return {
        "billing_month": billing_month,
        "billed": billed,
        "collected": collected,
        "outstanding": outstanding,
        "collection_rate_percent": round(collection_rate, 2),
    }
    
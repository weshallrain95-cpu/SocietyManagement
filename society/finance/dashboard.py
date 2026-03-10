from decimal import Decimal

from society.finance.receivables import get_society_receivable_snapshot
from society.finance.aging import get_maintenance_aging_report
from society.finance.bank import get_bank_balance
from society.finance.income_expenditure import generate_income_expenditure


def get_finance_dashboard(society):
    """
    Aggregates all financial KPIs for the society dashboard.
    """

    receivable_snapshot = get_society_receivable_snapshot(society)
    aging_report = get_maintenance_aging_report(society)

    bank_balance = get_bank_balance(society)
    pnl = generate_income_expenditure(society)

    total_flats = receivable_snapshot["total_flats"]
    total_receivable = receivable_snapshot["total_receivable"]
    defaulter_count = receivable_snapshot["defaulter_count"]

    paid_flats = total_flats - defaulter_count

    collection_rate = Decimal("0.00")

    if total_flats > 0:
        collection_rate = (
            Decimal(paid_flats) / Decimal(total_flats)
        ) * Decimal("100.00")

    aging_totals = aging_report["totals"]

    return {

        "society_finance": {
            "total_flats": total_flats,
            "paid_flats": paid_flats,
            "defaulter_flats": defaulter_count,
        },

        "receivables": {
            "total_receivable": total_receivable,
            "collection_rate_percent": round(collection_rate, 2),
        },

        "bank": {
            "balance": bank_balance
        },

        "income_expenditure": pnl["totals"],

        "aging_summary": aging_totals,

        "top_defaulters": receivable_snapshot["defaulters"][:10],
    }
    
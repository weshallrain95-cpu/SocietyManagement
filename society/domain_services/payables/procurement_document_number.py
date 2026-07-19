from datetime import date

from society.models import ExpenseAuthorization


def generate_procurement_document_number():
    """
    Generates the next Procurement Order number.

    Format:

        PDOC-YYYY-000001
    """

    year = date.today().year

    prefix = f"PDOC-{year}-"

    latest = (
        ExpenseAuthorization.objects
        .filter(
            procurement_document_number__startswith=prefix,
        )
        .order_by(
            "-procurement_document_number",
        )
        .first()
    )

    if latest is None:

        sequence = 1

    else:

        sequence = (
            int(
                latest.procurement_document_number
                .split("-")[-1]
            )
            + 1
        )

    return (
        f"{prefix}{sequence:06d}"
    )
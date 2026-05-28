from io import BytesIO

from django.http import HttpResponse

from openpyxl import Workbook
from openpyxl.styles import Font

from society.models import Flat, FlatOwnership, FlatOwner
from datetime import date

def generate_opening_balance_excel(society):
    """
    Generates pre-filled opening balance Excel template
    using active ownership records.
    """

    wb = Workbook()

    ws = wb.active
    ws.title = "Opening Balances"

    headers = [
        "Society ID",
        "Wing",
        "Flat No",
        "Owner Name",
        "Phone",
        "Maintenance Outstanding",
        "Interest Outstanding",
        "Penalty Outstanding",
        "Advance Balance",
    ]

    ws.append(headers)

    # Bold header row
    for col in range(1, len(headers) + 1):
        ws.cell(row=1, column=col).font = Font(bold=True)

    flats = (
        Flat.objects.filter(society=society)
        .select_related("wing_ref")
        .order_by("wing_ref__name", "flat_number")
    )

    for flat in flats:

        ownership = (
            FlatOwnership.objects.filter(
                flat=flat,
                is_active=True,
            )
            .prefetch_related("owners__person")
            .first()
        )

        if not ownership:
            continue

        owner = (
            FlatOwner.objects.filter(
                ownership=ownership
            )
            .select_related("person")
            .first()
        )

        owner_name = ""
        phone = ""

        if owner:

            if owner.person:
                owner_name = owner.person.full_name
                phone = owner.person.phone

            elif owner.legal_entity_name:
                owner_name = owner.legal_entity_name

        ws.append([
            society.id,
            flat.wing_ref.name if flat.wing_ref else "",
            flat.flat_number,
            owner_name,
            phone,
            "",
            "",
            "",
            "",
        ])
    
    buffer = BytesIO()

    wb.save(buffer)

    buffer.seek(0)

    today = date.today().strftime("%Y%m%d")

    filename = (
        f"{society.name.replace(' ', '')}"
        f"_SID{society.id}"
        f"_OpeningBalanceTemplate"
        f"_{today}.xlsx"
    )

    response = HttpResponse(
        buffer.getvalue(),
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )

    response["Content-Disposition"] = (
        f'attachment; filename="{filename}"'
    )

    return response
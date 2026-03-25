from openpyxl import Workbook
from openpyxl.styles import Font
from django.http import HttpResponse
from io import BytesIO

from society.models import Flat


def generate_structure_excel(society):
    """
    Generates ownership Excel template based on existing society structure.
    """

    wb = Workbook()
    ws = wb.active
    ws.title = "Ownership Template"

    headers = [
        "Society ID",
        "Wing",
        "Floor",
        "Flat No",
        "Flat Type",
        "Area (sqft)",  # ✅ ADDED
        "Owner Name",
        "Phone",
        "%",
        "Entity",
    ]

    ws.append(headers)

    # Bold header
    for col in range(1, len(headers) + 1):
        ws.cell(row=1, column=col).font = Font(bold=True)

    flats = (
        Flat.objects.filter(society=society)
        .select_related("wing_ref", "floor_ref")
        .order_by("wing_ref__name", "floor", "id")
    )

    for flat in flats:
        ws.append([
            society.id,
            flat.wing_ref.name if flat.wing_ref else flat.wing,
            flat.floor,
            flat.flat_number,
            flat.flat_type or "",
            flat.carpet_area_sqft or "",  # ✅ ADDED
            "",
            "",
            "",
            "",
        ])

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    filename = f"{society.name.replace(' ', '')}_uploadtemplate_structureonboarding.xlsx"

    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    return response
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response

from society.models import Society

from society.excel.maintenance_bill_balance_upload import (
    parse_maintenance_bill_balance_excel,
    persist_maintenance_bill_opening_balances,
)


@api_view(["POST"])
def upload_maintenance_bill_opening_balance_excel(request):

    society_id = request.data.get("society_id")
    file_obj = request.FILES.get("file")

    if not society_id:
        return Response(
            {
                "status": "failed",
                "message": "society_id required",
            },
            status=400,
        )

    if not file_obj:
        return Response(
            {
                "status": "failed",
                "message": "Excel file required",
            },
            status=400,
        )

    if not file_obj.name.endswith(".xlsx"):
        return Response(
            {
                "status": "failed",
                "message": "Only .xlsx files supported",
            },
            status=400,
        )

    society = get_object_or_404(
        Society,
        id=society_id,
    )

    try:

        parsed = parse_maintenance_bill_balance_excel(
            file_obj=file_obj,
            society=society,
        )

    except Exception as e:

        return Response(
            {
                "status": "failed",
                "message": "Excel parsing failed",
                "error": str(e),
            },
            status=500,
        )

    if parsed.get("status") == "failed":

        return Response(
            {
                "status": "failed",
                "errors": parsed.get("errors", []),
                "warnings": parsed.get("warnings", []),
                "rows_detected": len(
                    parsed.get("rows", [])
                ),
            },
            status=400,
        )

    try:

        persisted = (
            persist_maintenance_bill_opening_balances(
                society=society,
                parsed_rows=parsed.get("rows", []),
            )
        )

    except Exception as e:

        return Response(
            {
                "status": "failed",
                "message": "Opening balance persistence failed",
                "error": str(e),
            },
            status=500,
        )

    return Response(
        {
            "status": "success",

            "message": (
                "Opening balances imported successfully"
            ),

            "flats_processed": len(
                parsed.get("rows", [])
            ),

            "receivables_created": (
                persisted.get(
                    "receivables_created",
                    0,
                )
            ),

            "initialization_rows": (
                persisted.get(
                    "initialization_rows",
                    0,
                )
            ),

            "total_outstanding": str(
                persisted.get(
                    "total_outstanding",
                    0,
                )
            ),

            "total_advance": str(
                persisted.get(
                    "total_advance",
                    0,
                )
            ),

            "warnings": parsed.get(
                "warnings",
                [],
            ),

            "warning_count": len(
                parsed.get(
                    "warnings",
                    [],
                )
            ),
        }
    )
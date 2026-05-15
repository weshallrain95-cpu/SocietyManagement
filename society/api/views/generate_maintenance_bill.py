from datetime import date

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from society.models import Society

from society.services import (
    generate_monthly_maintenance_bill,
)


@api_view(["POST"])
def generate_maintenance_bill(request):

    society_id = request.data.get("society_id")
    billing_month = request.data.get("billing_month")

    if not society_id:
        return Response(
            {"error": "society_id required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not billing_month:
        return Response(
            {"error": "billing_month required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        society = Society.objects.get(id=society_id)

    except Society.DoesNotExist:
        return Response(
            {"error": "Society not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    try:

        bill = generate_monthly_maintenance_bill(
            society=society,
            billing_month=billing_month,
        )

    except Exception as e:

        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

    return Response({
        "message": "Maintenance bill generated successfully",
        "bill_id": bill.id,
        "billing_month": str(bill.billing_month),
        "total_amount": str(bill.total_amount),
    })
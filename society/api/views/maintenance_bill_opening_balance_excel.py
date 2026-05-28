from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response

from society.models import Society

from society.excel.opening_balance_template import (
    generate_opening_balance_excel,
)


@api_view(["GET"])
def download_maintenance_bill_opening_balance_excel(request):

    society_id = request.GET.get("society_id")

    if not society_id:
        return Response(
            {"error": "society_id required"},
            status=400,
        )

    society = get_object_or_404(
        Society,
        id=society_id,
    )

    return generate_opening_balance_excel(society)
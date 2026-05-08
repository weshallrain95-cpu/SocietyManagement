from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from society.models import Society, Flat
from society.finance.kernel.billing_engine import generate_member_bill


@api_view(["POST"])
def generate_bill(request):
    """
    Creates a member bill (single line for now).
    """

    society = Society.objects.first()  # temp pattern

    flat_id = request.data.get("flat_id")
    amount = request.data.get("amount")
    subtype = request.data.get("subtype")
    reference_id = request.data.get("reference_id")

    # 🔒 minimal validation
    if not all([flat_id, amount, subtype, reference_id]):
        return Response(
            {"error": "flat_id, amount, subtype, reference_id required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        flat = Flat.objects.get(id=flat_id, society=society)
    except Flat.DoesNotExist:
        return Response({"error": "Invalid flat_id"}, status=400)

    try:
        txn = generate_member_bill(
            society=society,
            flat=flat,
            amount=amount,
            subtype=subtype,
            reference_id=reference_id,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=400)

    return Response({
        "message": "Bill generated",
        "transaction_id": txn.id,
        "reference_id": txn.reference_id,
    })
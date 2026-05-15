from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from society.models import (
    Society,
    MaintenanceCharge,
)

from society.api.serializers.maintenance_charge_serializer import (
    MaintenanceChargeSerializer,
)

from society.finance.maintenance.maintenance_template import (
    seed_maintenance_template,
)


@api_view(["GET", "POST"])
def maintenance_setup(request):

    # ==========================================================
    # GET → LOAD MAINTENANCE CONFIGURATION
    # ==========================================================
    if request.method == "GET":

        society_id = request.GET.get("society_id")

        if not society_id:
            return Response(
                {"error": "society_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            society = Society.objects.get(id=society_id)

        except Society.DoesNotExist:
            return Response(
                {"error": "Society not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # ------------------------------------------------------
        # AUTO SEED TEMPLATE IF EMPTY
        # ------------------------------------------------------
        existing = MaintenanceCharge.objects.filter(
            society=society
        ).exists()

        if not existing:
            seed_maintenance_template(society)

        queryset = MaintenanceCharge.objects.filter(
            society=society
        ).order_by("name")

        serializer = MaintenanceChargeSerializer(
            queryset,
            many=True
        )

        return Response(serializer.data)

    # ==========================================================
    # POST → SAVE MAINTENANCE CONFIGURATION
    # ==========================================================
    society_id = request.data.get("society_id")
    charges = request.data.get("charges", [])

    if not society_id:
        return Response(
            {"error": "society_id required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        society = Society.objects.get(id=society_id)

    except Society.DoesNotExist:
        return Response(
            {"error": "Society not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    updated = []

    for item in charges:

        charge_id = item.get("id")

        try:
            charge = MaintenanceCharge.objects.get(
                id=charge_id,
                society=society
            )

        except MaintenanceCharge.DoesNotExist:
            continue

        serializer = MaintenanceChargeSerializer(
            instance=charge,
            data=item,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            updated.append(serializer.data)

    return Response({
        "message": "Maintenance configuration saved",
        "charges": updated,
    })
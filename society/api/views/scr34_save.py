from django.shortcuts import get_object_or_404
from django.db import transaction

from rest_framework.decorators import api_view
from rest_framework.response import Response

from society.models import (
    Society,
    BankAccount,
)


@api_view(["POST"])
def save_scr34_configuration(request):

    society_id = request.data.get(
        "society_id"
    )

    selected_bank_id = request.data.get(
        "bank_account_id"
    )

    official_email = (
        request.data.get(
            "official_email",
            "",
        ).strip()
    )

    society = get_object_or_404(
        Society,
        id=society_id,
    )

    active_banks = (
        BankAccount.objects.filter(
            society=society,
            is_active=True,
        )
        .order_by("id")
    )

    if not active_banks.exists():

        return Response(
            {
                "status": "failed",
                "message":
                    "No active bank accounts available.",
            },
            status=400,
        )

    # =====================================================
    # SINGLE ACTIVE BANK
    # =====================================================

    active_bank_count = active_banks.count()

    if active_bank_count == 1:

        bank = active_banks.first()

        with transaction.atomic():

            if bank.treasury_role != "OPERATIONS":

                bank.treasury_role = "OPERATIONS"

                bank.save(
                    update_fields=[
                        "treasury_role",
                    ]
                )

            if official_email:

                society.official_email = official_email

            society.communications_enabled = True

            society.save(
                update_fields=[
                    "official_email",
                    "communications_enabled",
                ]
            )

        return Response(
            {
                "status": "success",
                "message":
                    "Maintenance Billing successfully activated.",
                "operations_bank": bank.id,
            }
        )

    # =====================================================
    # MULTIPLE ACTIVE BANKS
    # =====================================================

    if not selected_bank_id:

        return Response(
            {
                "status": "failed",
                "message":
                    "Please select the Maintenance Collection Bank Account.",
            },
            status=400,
        )

    selected_bank = get_object_or_404(
        BankAccount,
        id=selected_bank_id,
        society=society,
        is_active=True,
    )

    with transaction.atomic():

        if selected_bank.treasury_role != "OPERATIONS":

            active_banks.filter(
                treasury_role="OPERATIONS",
            ).exclude(
                id=selected_bank.id,
            ).update(
                treasury_role="RESERVE",
            )

            selected_bank.treasury_role = "OPERATIONS"

            selected_bank.save(
                update_fields=[
                    "treasury_role",
                ]
            )

        if official_email:

            society.official_email = official_email

        society.communications_enabled = True

        society.save(
            update_fields=[
                "official_email",
                "communications_enabled",
            ]
        )

    return Response(
        {
            "status": "success",
            "message":
                "Maintenance Billing successfully activated.",
            "operations_bank":
                selected_bank.id,
        }
    )   
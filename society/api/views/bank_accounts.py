from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from society.models import Society, BankAccount
from society.api.serializers.bank_account_serializer import (
    BankAccountSerializer,
)


@api_view(["GET", "POST", "PATCH"])
def bank_accounts(request):

    # ==========================================================
    # GET → LIST BANK ACCOUNTS
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

        queryset = BankAccount.objects.filter(
            society=society
        ).order_by("-created_at")

        serializer = BankAccountSerializer(
            queryset,
            many=True
        )

        return Response(serializer.data)

    # ==========================================================
    # PATCH → UPDATE BANK ACCOUNT
    # ==========================================================
    if request.method == "PATCH":

        bank_id = request.data.get("id")

        if not bank_id:
            return Response(
                {"error": "Bank account id required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            bank = BankAccount.objects.get(id=bank_id)

        except BankAccount.DoesNotExist:
            return Response(
                {"error": "Bank account not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = BankAccountSerializer(
            instance=bank,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():

            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    # ==========================================================
    # POST → CREATE BANK ACCOUNT
    # ==========================================================
    serializer = BankAccountSerializer(data=request.data)

    if serializer.is_valid():

        bank = serializer.save()

        return Response(
            BankAccountSerializer(bank).data,
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )
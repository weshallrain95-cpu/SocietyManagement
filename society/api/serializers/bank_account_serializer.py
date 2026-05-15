from rest_framework import serializers

from society.models import BankAccount


class BankAccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = BankAccount

        fields = [
            "id",
            "society",
            "name",
            "bank_name",
            "account_number",
            "ifsc",
            "treasury_role",
            "bank_address",
            "chart_account",
            "is_active",
            "created_at",
            "upi_id",
            "banking_phone",
            "banking_email",
        ]

        read_only_fields = [
            "chart_account",
            "created_at",
        ]
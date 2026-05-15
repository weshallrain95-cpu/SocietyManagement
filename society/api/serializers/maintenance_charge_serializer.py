from rest_framework import serializers

from society.models import MaintenanceCharge


class MaintenanceChargeSerializer(serializers.ModelSerializer):

    class Meta:
        model = MaintenanceCharge

        fields = [
            "id",
            "society",
            "code",
            "name",
            "basis",
            "rate",
            "effective_from",
            "is_active",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
        ]
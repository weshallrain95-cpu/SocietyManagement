from rest_framework import serializers
from society.models import AuditEvent


class AuditEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditEvent
        fields = [
            "id",
            "created_at",
            "event_type",
            "domain",
            "object_type",
            "object_id",
            "actor_id",
            "payload",
            "event_hash",
        ]
        read_only_fields = fields

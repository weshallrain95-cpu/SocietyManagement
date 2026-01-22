from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAdminUser
from society.models import AuditEvent
from society.api.serializers.audit import AuditEventSerializer


class AuditEventViewSet(ReadOnlyModelViewSet):
    """
    Read-only access to audit events.
    """
    serializer_class = AuditEventSerializer
    permission_classes = [IsAdminUser]

    queryset = AuditEvent.objects.all().order_by("-created_at")

    filterset_fields = [
        "event_type",
        "domain",
        "object_type",
        "object_id",
        "actor_id",
    ]

    ordering_fields = [
        "created_at",
        "event_type",
        "domain",
    ]

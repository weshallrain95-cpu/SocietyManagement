from django.db import models
import uuid


class LegalState(models.Model):
    """
    Canonical legal state object.
    Represents current legal truth of any entity.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    entity_id = models.CharField(max_length=255, db_index=True)
    entity_type = models.CharField(max_length=100)

    jurisdiction = models.CharField(max_length=100)
    legal_domain = models.CharField(max_length=100)

    legal_status = models.CharField(max_length=50)

    authority_state = models.JSONField(default=dict)
    canon_state = models.JSONField(default=dict)
    compliance_state = models.JSONField(default=dict)
    dispute_state = models.JSONField(default=dict)
    enforcement_state = models.JSONField(default=dict)
    evidence_state = models.JSONField(default=dict)
    audit_state = models.JSONField(default=dict)

    lifecycle = models.JSONField(default=dict)

    last_event_id = models.CharField(max_length=255, null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("entity_id", "entity_type")
        indexes = [
            models.Index(fields=["entity_id"]),
            models.Index(fields=["legal_status"]),
            models.Index(fields=["legal_domain"]),
        ]

    def __str__(self):
        return f"{self.entity_type}:{self.entity_id} [{self.legal_status}]"

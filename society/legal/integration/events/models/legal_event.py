from django.db import models
import uuid


# ============================
# Legal Event Model
# ============================

class LegalEvent(models.Model):
    """
    Canonical legal event object.
    Represents a legally relevant act.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Identity
    event_id = models.CharField(max_length=100, unique=True, db_index=True)
    event_type = models.CharField(max_length=100)

    # Semantics
    intent = models.CharField(max_length=100)
    source_platform = models.CharField(max_length=100)

    # Jurisdiction & Authority
    jurisdiction = models.CharField(max_length=100)
    authority_id = models.CharField(max_length=255)
    authority_type = models.CharField(max_length=100)
    supremacy_rank = models.IntegerField()

    # Legal Binding
    legal_domain = models.CharField(max_length=100)
    canon_ref = models.CharField(max_length=255)

    # Entity
    entity_id = models.CharField(max_length=255)
    entity_type = models.CharField(max_length=100)

    # State
    state_from = models.CharField(max_length=100, null=True, blank=True)
    state_to = models.CharField(max_length=100, null=True, blank=True)

    # Contexts
    governance_context = models.JSONField(default=dict)
    compliance_context = models.JSONField(default=dict)
    enforcement_context = models.JSONField(default=dict)

    # Evidence
    evidence_refs = models.JSONField(default=list)

    # Payload
    payload = models.JSONField(default=dict)

    # Integrity
    hash = models.CharField(max_length=128)
    signature = models.TextField(null=True, blank=True)

    # Audit
    created_by = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Legal Event"
        verbose_name_plural = "Legal Events"
        indexes = [
            models.Index(fields=["event_id"]),
            models.Index(fields=["intent"]),
            models.Index(fields=["entity_id"]),
            models.Index(fields=["legal_domain"]),
        ]

    def __str__(self):
        return f"{self.intent} | {self.event_id}"

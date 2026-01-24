# society/legal/compliance/models/legal_state.py

from django.db import models
import uuid


# ============================
# Persistent Legal State Model
# ============================

class LegalStateModel(models.Model):
    """
    Persistent legal state of an entity.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Identity
    entity_id = models.CharField(max_length=255, db_index=True)

    # Core State
    status = models.CharField(
        max_length=50,
        choices=[
            ("COMPLIANT", "Compliant"),
            ("NON_COMPLIANT", "Non Compliant"),
            ("UNDER_REVIEW", "Under Review"),
            ("ENFORCED", "Enforced"),
            ("SUSPENDED", "Suspended"),
        ],
    )

    # Timestamps
    last_evaluated = models.DateTimeField()
    last_violation_at = models.DateTimeField(null=True, blank=True)
    last_enforcement_at = models.DateTimeField(null=True, blank=True)

    # Scores
    compliance_score = models.FloatField(null=True, blank=True)
    risk_score = models.FloatField(null=True, blank=True)
    enforcement_priority = models.IntegerField(null=True, blank=True)

    # Legal Metadata
    legal_basis = models.JSONField(null=True, blank=True)
    active_laws = models.JSONField(null=True, blank=True)

    # Governance Binding
    governance_state = models.JSONField(null=True, blank=True)

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Legal State"
        verbose_name_plural = "Legal States"
        indexes = [
            models.Index(fields=["entity_id"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.entity_id} [{self.status}]"

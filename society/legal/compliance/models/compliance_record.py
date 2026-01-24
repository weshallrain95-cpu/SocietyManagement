# society/legal/compliance/models/compliance_record.py

from django.db import models
import uuid


# ============================
# Compliance Record
# ============================

class ComplianceRecord(models.Model):
    """
    Persistent compliance evaluation history.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Identity
    entity_id = models.CharField(max_length=255, db_index=True)

    # Evaluation Data
    compliant = models.BooleanField()
    compliance_score = models.FloatField()
    risk_score = models.FloatField()
    enforcement_priority = models.IntegerField()

    # Context
    context = models.JSONField(default=dict)

    # Law Context
    applicable_laws = models.JSONField(default=list)
    canon_path = models.JSONField(default=list)

    # Governance
    governance_context = models.JSONField(null=True, blank=True)

    # Evaluation Timestamp
    evaluated_at = models.DateTimeField()

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Compliance Record"
        verbose_name_plural = "Compliance Records"
        indexes = [
            models.Index(fields=["entity_id"]),
            models.Index(fields=["evaluated_at"]),
            models.Index(fields=["compliant"]),
        ]

    def __str__(self):
        return f"{self.entity_id} @ {self.evaluated_at}"

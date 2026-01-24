# society/legal/compliance/models/violation.py

from django.db import models
import uuid


# ============================
# Persistent Violation Model
# ============================

class Violation(models.Model):
    """
    Persistent legal violation record.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Identity
    entity_id = models.CharField(max_length=255, db_index=True)

    # Violation Core
    violation_type = models.CharField(max_length=100)
    severity = models.CharField(max_length=50)
    category = models.CharField(max_length=50, null=True, blank=True)
    enforcement_priority = models.IntegerField(null=True, blank=True)

    # Normative Reference
    norm_payload = models.JSONField()

    # Context
    context = models.JSONField(default=dict)

    # Lifecycle
    status = models.CharField(
        max_length=50,
        default="DETECTED",
        choices=[
            ("DETECTED", "Detected"),
            ("UNDER_REVIEW", "Under Review"),
            ("ENFORCED", "Enforced"),
            ("RESOLVED", "Resolved"),
            ("DISMISSED", "Dismissed"),
        ]
    )

    detected_at = models.DateTimeField()
    resolved_at = models.DateTimeField(null=True, blank=True)

    # Enforcement
    enforcement_actions = models.JSONField(null=True, blank=True)

    # Governance
    governance_binding = models.JSONField(null=True, blank=True)

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Violation"
        verbose_name_plural = "Violations"
        indexes = [
            models.Index(fields=["entity_id"]),
            models.Index(fields=["status"]),
            models.Index(fields=["severity"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self):
        return f"{self.entity_id} - {self.violation_type}"

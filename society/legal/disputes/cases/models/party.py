# society/legal/disputes/cases/models/party.py

from django.db import models
import uuid


# ============================
# Legal Party Model
# ============================

class LegalParty(models.Model):
    """
    Represents a legal participant in a case.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Identity
    name = models.CharField(max_length=255)
    party_type = models.CharField(
        max_length=50,
        choices=[
            ("COMPLAINANT", "Complainant"),
            ("RESPONDENT", "Respondent"),
            ("REPRESENTATIVE", "Representative"),
            ("AUTHORITY", "Authority"),
            ("ARBITRATOR", "Arbitrator"),
            ("PANEL", "Panel"),
            ("INSTITUTION", "Institution"),
        ]
    )

    # Contact / Identity
    entity_ref = models.CharField(max_length=255, null=True, blank=True)
    contact_info = models.JSONField(default=dict, blank=True)

    # Legal Capacity
    legal_capacity = models.CharField(
        max_length=50,
        default="FULL",
        choices=[
            ("FULL", "Full Capacity"),
            ("LIMITED", "Limited Capacity"),
            ("REPRESENTED", "Represented"),
        ]
    )

    # Authority Binding
    authority_role = models.CharField(max_length=100, null=True, blank=True)

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Legal Party"
        verbose_name_plural = "Legal Parties"

    def __str__(self):
        return f"{self.name} ({self.party_type})"

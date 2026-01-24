# society/legal/disputes/cases/models/judgement.py

from django.db import models
import uuid
from .case import LegalCase


# ============================
# Legal Judgement Model
# ============================

class LegalJudgement(models.Model):
    """
    Represents a legal judgement / ruling.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Relations
    case = models.OneToOneField(LegalCase, on_delete=models.CASCADE, related_name="judgement")

    # Decision
    verdict = models.CharField(
        max_length=50,
        choices=[
            ("ALLOWED", "Allowed"),
            ("DISMISSED", "Dismissed"),
            ("PARTIALLY_ALLOWED", "Partially Allowed"),
            ("SETTLED", "Settled"),
            ("REMANDED", "Remanded"),
        ]
    )

    reasoning = models.TextField()
    legal_basis = models.JSONField(default=dict)

    # Orders
    orders = models.JSONField(default=dict)   # enforcement orders, sanctions, remedies

    # Compliance
    compliance_deadline = models.DateTimeField(null=True, blank=True)

    # Finality
    final = models.BooleanField(default=False)
    appealable = models.BooleanField(default=True)

    # Audit
    delivered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Legal Judgement"
        verbose_name_plural = "Legal Judgements"

    def __str__(self):
        return f"Judgement - {self.case.case_number}"

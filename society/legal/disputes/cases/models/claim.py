# society/legal/disputes/cases/models/claim.py

from django.db import models
import uuid
from .case import LegalCase
from .party import LegalParty


# ============================
# Legal Claim Model
# ============================

class LegalClaim(models.Model):
    """
    Represents a legal claim within a case.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Relations
    case = models.ForeignKey(LegalCase, on_delete=models.CASCADE, related_name="claims")
    claimant = models.ForeignKey(LegalParty, on_delete=models.CASCADE, related_name="claims_made")
    respondent = models.ForeignKey(LegalParty, on_delete=models.CASCADE, related_name="claims_received")

    # Claim Content
    title = models.CharField(max_length=255)
    description = models.TextField()

    # Legal Basis
    legal_basis = models.JSONField(default=dict)
    relief_sought = models.TextField()

    # Status
    status = models.CharField(
        max_length=50,
        choices=[
            ("FILED", "Filed"),
            ("UNDER_REVIEW", "Under Review"),
            ("ACCEPTED", "Accepted"),
            ("REJECTED", "Rejected"),
            ("MERGED", "Merged"),
            ("RESOLVED", "Resolved"),
        ],
        default="FILED"
    )

    # Audit
    filed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Legal Claim"
        verbose_name_plural = "Legal Claims"

    def __str__(self):
        return f"{self.title} ({self.case.case_number})"

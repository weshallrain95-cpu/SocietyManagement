# society/legal/disputes/cases/models/hearing.py

from django.db import models
import uuid
from .case import LegalCase


# ============================
# Legal Hearing Model
# ============================

class LegalHearing(models.Model):
    """
    Represents a hearing session in a legal case.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Relations
    case = models.ForeignKey(LegalCase, on_delete=models.CASCADE, related_name="hearings")

    # Hearing Info
    hearing_type = models.CharField(
        max_length=50,
        choices=[
            ("PRELIMINARY", "Preliminary"),
            ("EVIDENCE", "Evidence"),
            ("ARGUMENT", "Argument"),
            ("ARBITRATION", "Arbitration"),
            ("FINAL", "Final"),
        ]
    )

    mode = models.CharField(
        max_length=50,
        choices=[
            ("PHYSICAL", "Physical"),
            ("VIRTUAL", "Virtual"),
            ("HYBRID", "Hybrid"),
        ],
        default="VIRTUAL"
    )

    schedule_time = models.DateTimeField()
    location = models.CharField(max_length=255, null=True, blank=True)

    # Proceedings
    agenda = models.TextField(null=True, blank=True)
    proceedings_record = models.JSONField(default=dict, blank=True)

    # Outcome
    outcome = models.TextField(null=True, blank=True)

    # Status
    status = models.CharField(
        max_length=50,
        choices=[
            ("SCHEDULED", "Scheduled"),
            ("ONGOING", "Ongoing"),
            ("COMPLETED", "Completed"),
            ("ADJOURNED", "Adjourned"),
            ("CANCELLED", "Cancelled"),
        ],
        default="SCHEDULED"
    )

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Legal Hearing"
        verbose_name_plural = "Legal Hearings"

    def __str__(self):
        return f"Hearing - {self.case.case_number} @ {self.schedule_time}"

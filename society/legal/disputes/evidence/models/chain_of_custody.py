# society/legal/disputes/evidence/models/chain_of_custody.py

from django.db import models
import uuid
from .evidence import Evidence


# ============================
# Chain of Custody
# ============================

class ChainOfCustody(models.Model):
    """
    Tracks custody and handling of evidence.
    Legal-grade traceability.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Evidence Binding
    evidence = models.ForeignKey(Evidence, on_delete=models.CASCADE, related_name="custody_chain")

    # Custody Info
    handler = models.CharField(max_length=255)  # person/system handling
    action = models.CharField(max_length=100)   # COLLECTED, TRANSFERRED, VERIFIED, STORED, ACCESSED, ARCHIVED

    # Integrity Snapshot
    hash_snapshot = models.CharField(max_length=128)

    # Context
    location = models.CharField(max_length=255, null=True, blank=True)
    purpose = models.TextField(null=True, blank=True)

    # Timestamp
    timestamp = models.DateTimeField()

    # Audit
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Chain of Custody"
        verbose_name_plural = "Chain of Custody"
        indexes = [
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self):
        return f"{self.evidence.reference_id} - {self.action} @ {self.timestamp}"

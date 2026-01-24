# society/legal/disputes/evidence/models/evidence_version.py

from django.db import models
import uuid
from .evidence import Evidence


# ============================
# Evidence Version Model
# ============================

class EvidenceVersion(models.Model):
    """
    Tracks versions of evidence.
    Ensures immutability + history.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Evidence Binding
    evidence = models.ForeignKey(Evidence, on_delete=models.CASCADE, related_name="versions")

    # Versioning
    version_number = models.IntegerField()
    storage_uri = models.TextField()

    # Integrity
    hash_sha256 = models.CharField(max_length=128)
    hash_sha512 = models.CharField(max_length=256, null=True, blank=True)

    # Change Metadata
    change_reason = models.TextField(null=True, blank=True)
    changed_by = models.CharField(max_length=255)
    changed_at = models.DateTimeField()

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Evidence Version"
        verbose_name_plural = "Evidence Versions"
        unique_together = ("evidence", "version_number")
        indexes = [
            models.Index(fields=["version_number"]),
        ]

    def __str__(self):
        return f"{self.evidence.reference_id} v{self.version_number}"

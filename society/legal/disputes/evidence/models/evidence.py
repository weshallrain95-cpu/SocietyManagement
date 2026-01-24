# society/legal/disputes/evidence/models/evidence.py

from django.db import models
import uuid


# ============================
# Evidence Model
# ============================

class Evidence(models.Model):
    """
    Represents a piece of legal evidence.
    Court-grade digital evidence object.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Identity
    reference_id = models.CharField(max_length=100, unique=True, db_index=True)

    # Case Binding
    case_id = models.CharField(max_length=255, db_index=True)

    # Evidence Type
    evidence_type = models.CharField(
        max_length=50,
        choices=[
            ("DOCUMENT", "Document"),
            ("IMAGE", "Image"),
            ("VIDEO", "Video"),
            ("AUDIO", "Audio"),
            ("COMMUNICATION", "Communication"),
            ("LOG", "Log"),
            ("AUDIT", "Audit"),
            ("SYSTEM_RECORD", "System Record"),
            ("SIGNATURE", "Signature"),
            ("OTHER", "Other"),
        ]
    )

    # Content Reference
    storage_uri = models.TextField()  # location in storage system
    mime_type = models.CharField(max_length=100)

    # Integrity
    hash_sha256 = models.CharField(max_length=128)
    hash_sha512 = models.CharField(max_length=256, null=True, blank=True)

    # Authenticity
    signed = models.BooleanField(default=False)
    signature_ref = models.TextField(null=True, blank=True)
    signer_identity = models.CharField(max_length=255, null=True, blank=True)

    # Legal Metadata
    source = models.CharField(max_length=255)  # who/what produced it
    collected_by = models.CharField(max_length=255)
    collected_at = models.DateTimeField()

    # Context
    context = models.JSONField(default=dict)

    # Status
    status = models.CharField(
        max_length=50,
        choices=[
            ("COLLECTED", "Collected"),
            ("VERIFIED", "Verified"),
            ("DISPUTED", "Disputed"),
            ("INVALIDATED", "Invalidated"),
            ("ARCHIVED", "Archived"),
        ],
        default="COLLECTED"
    )

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Evidence"
        verbose_name_plural = "Evidence"
        indexes = [
            models.Index(fields=["case_id"]),
            models.Index(fields=["evidence_type"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Evidence {self.reference_id} ({self.evidence_type})"

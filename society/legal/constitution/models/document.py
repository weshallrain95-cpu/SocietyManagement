# society/legal/constitution/models/document.py

from django.db import models
import uuid

from society.legal.constitution.models.canon import LegalCanonNode
from society.legal.constitution.models.authority import LegalAuthority


# ============================
# Document Types
# ============================

class DocumentType(models.TextChoices):
    CONSTITUTION = "CONSTITUTION", "Constitution"
    LAW = "LAW", "Law"
    BYLAW = "BYLAW", "Bylaw"
    REGULATION = "REGULATION", "Regulation"
    POLICY = "POLICY", "Policy"
    PROCEDURE = "PROCEDURE", "Procedure"
    DIRECTIVE = "DIRECTIVE", "Directive"
    NOTICE = "NOTICE", "Notice"
    ORDER = "ORDER", "Order"
    INTERPRETATION = "INTERPRETATION", "Interpretation"


# ============================
# Legal Document (Machine-Law)
# ============================

class LegalDocument(models.Model):
    """
    Machine-legible legal document.
    This is the unified schema for all digital law.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Identity
    title = models.CharField(max_length=255)
    code = models.CharField(max_length=100, unique=True)
    doc_type = models.CharField(max_length=50, choices=DocumentType.choices)

    # Canon Binding
    canon_node = models.ForeignKey(
        LegalCanonNode,
        on_delete=models.PROTECT,
        related_name="documents"
    )

    # Authority Source
    authority_source = models.ForeignKey(
        LegalAuthority,
        on_delete=models.PROTECT,
        related_name="documents"
    )

    # Legal Context
    jurisdiction = models.CharField(max_length=100)
    legal_domain = models.CharField(max_length=100)
    hierarchy_level = models.PositiveIntegerField()

    # Normative Structure
    normative_type = models.CharField(max_length=50)  # obligation / prohibition / permission / etc
    scope = models.JSONField(default=dict)
    conditions = models.JSONField(default=dict)

    # Legal Logic
    rules = models.JSONField(default=list)
    obligations = models.JSONField(default=list)
    prohibitions = models.JSONField(default=list)
    permissions = models.JSONField(default=list)
    exceptions = models.JSONField(default=list)
    sanctions = models.JSONField(default=list)

    # Enforcement
    enforcement_bindings = models.JSONField(default=dict)

    # Versioning
    version = models.CharField(max_length=50, default="1.0.0")

    # Validity
    effective_from = models.DateTimeField()
    effective_until = models.DateTimeField(null=True, blank=True)

    # Governance Binding
    governance_binding = models.JSONField(default=dict)

    # Audit
    created_by = models.CharField(max_length=255)
    approved_by = models.CharField(max_length=255, null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    # Lifecycle
    status = models.CharField(
        max_length=50,
        default="DRAFT",
        choices=[
            ("DRAFT", "Draft"),
            ("ACTIVE", "Active"),
            ("SUSPENDED", "Suspended"),
            ("REPEALED", "Repealed"),
            ("ARCHIVED", "Archived"),
        ]
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Legal Document"
        verbose_name_plural = "Legal Documents"
        ordering = ["hierarchy_level", "title"]

    def __str__(self):
        return f"{self.title} [{self.code}]"

    # ============================
    # Domain Logic
    # ============================

    def is_active(self, at_time=None):
        from django.utils import timezone
        now = at_time or timezone.now()
        if self.effective_until:
            return self.effective_from <= now <= self.effective_until
        return self.effective_from <= now

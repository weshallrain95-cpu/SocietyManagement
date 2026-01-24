# society/legal/constitution/models/bylaw.py

from django.db import models
import uuid

from society.legal.constitution.models.canon import LegalCanonNode
from society.legal.constitution.models.document import LegalDocument
from society.legal.constitution.models.authority import LegalAuthority


# ============================
# Bylaw (Atomic Law Unit)
# ============================

class Bylaw(models.Model):
    """
    Atomic unit of law.
    This is the smallest enforceable legal object in the system.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Identity
    code = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Canon Binding
    canon_node = models.ForeignKey(
        LegalCanonNode,
        on_delete=models.PROTECT,
        related_name="bylaws"
    )

    # Document Binding
    legal_document = models.ForeignKey(
        LegalDocument,
        on_delete=models.PROTECT,
        related_name="bylaws"
    )

    # Authority Source
    authority_source = models.ForeignKey(
        LegalAuthority,
        on_delete=models.PROTECT,
        related_name="bylaws"
    )

    # Legal Context
    legal_domain = models.CharField(max_length=100)
    jurisdiction = models.CharField(max_length=100)
    scope = models.JSONField(default=dict)

    # Normative Structure
    normative_type = models.CharField(max_length=50)  # obligation / prohibition / permission / right / duty
    conditions = models.JSONField(default=dict)

    # Legal Logic
    obligations = models.JSONField(default=list)
    prohibitions = models.JSONField(default=list)
    permissions = models.JSONField(default=list)
    exceptions = models.JSONField(default=list)
    sanctions = models.JSONField(default=list)

    # Enforcement Hooks
    enforcement_hooks = models.JSONField(default=dict)

    # Versioning
    version = models.CharField(max_length=50, default="1.0.0")

    # Validity
    effective_from = models.DateTimeField()
    effective_until = models.DateTimeField(null=True, blank=True)

    # Governance Binding
    governance_binding = models.JSONField(default=dict)

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

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Bylaw"
        verbose_name_plural = "Bylaws"
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.title}"

    # ============================
    # Domain Logic
    # ============================

    def is_active(self, at_time=None):
        from django.utils import timezone
        now = at_time or timezone.now()
        if self.effective_until:
            return self.effective_from <= now <= self.effective_until
        return self.effective_from <= now

    def is_enforceable(self, at_time=None):
        return self.status == "ACTIVE" and self.is_active(at_time)

    def get_normative_payload(self):
        """
        Returns machine-usable legal logic bundle.
        """
        return {
            "normative_type": self.normative_type,
            "conditions": self.conditions,
            "obligations": self.obligations,
            "prohibitions": self.prohibitions,
            "permissions": self.permissions,
            "exceptions": self.exceptions,
            "sanctions": self.sanctions,
            "enforcement_hooks": self.enforcement_hooks,
        }

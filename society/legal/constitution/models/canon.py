# society/legal/constitution/models/canon.py

from django.db import models
import uuid

from society.legal.constitution.models.authority import LegalAuthority


# ============================
# Canon Types (Hierarchy of Law)
# ============================

class CanonType(models.TextChoices):
    CONSTITUTION = "CONSTITUTION", "Constitution"
    PRIMARY_LAW = "PRIMARY_LAW", "Primary Law"
    SECONDARY_LAW = "SECONDARY_LAW", "Secondary Law"
    PROCEDURAL_LAW = "PROCEDURAL_LAW", "Procedural Law"
    REGULATORY_LAW = "REGULATORY_LAW", "Regulatory Law"
    DISCIPLINARY_LAW = "DISCIPLINARY_LAW", "Disciplinary Law"
    FINANCIAL_LAW = "FINANCIAL_LAW", "Financial Law"
    INTERPRETATIVE_LAW = "INTERPRETATIVE_LAW", "Interpretative Law"


# ============================
# Legal Canon Node
# ============================

class LegalCanonNode(models.Model):
    """
    Represents a node in the legal canon hierarchy.
    This defines the structure of law itself.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Identity
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Hierarchy
    canon_type = models.CharField(max_length=50, choices=CanonType.choices)
    hierarchy_level = models.PositiveIntegerField()
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children"
    )

    # Authority Source
    authority_source = models.ForeignKey(
        LegalAuthority,
        on_delete=models.PROTECT,
        related_name="canon_nodes"
    )

    # Legal Context
    jurisdiction = models.CharField(max_length=100)
    scope = models.JSONField(default=dict)
    legal_domain = models.CharField(max_length=100)

    # Governance Binding
    governance_binding = models.JSONField(default=dict)

    # Versioning
    version = models.CharField(max_length=50, default="1.0.0")

    # Lifecycle
    status = models.CharField(
        max_length=50,
        default="ACTIVE",
        choices=[
            ("DRAFT", "Draft"),
            ("ACTIVE", "Active"),
            ("SUSPENDED", "Suspended"),
            ("REPEALED", "Repealed"),
            ("ARCHIVED", "Archived"),
        ]
    )

    # Validity
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField(null=True, blank=True)

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Legal Canon Node"
        verbose_name_plural = "Legal Canon Nodes"
        ordering = ["hierarchy_level", "name"]

    def __str__(self):
        return f"{self.name} ({self.canon_type})"

    # ============================
    # Domain Logic
    # ============================

    def is_active(self, at_time=None):
        from django.utils import timezone
        now = at_time or timezone.now()
        if self.valid_until:
            return self.valid_from <= now <= self.valid_until
        return self.valid_from <= now

    def is_root(self):
        return self.parent is None

    def get_ancestors(self):
        ancestors = []
        node = self.parent
        while node:
            ancestors.append(node)
            node = node.parent
        return ancestors

    def get_descendants(self):
        descendants = []

        def traverse(node):
            for child in node.children.all():
                descendants.append(child)
                traverse(child)

        traverse(self)
        return descendants

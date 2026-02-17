from django.db import models
from society.models import Case

class BylawDecision(models.Model):
    """
    Canonical decision entity that drives by-law generation.
    India-generic, state-aware, legally structured.
    """

    CATEGORY_CHOICES = [
        ("IDENTITY", "Identity"),
        ("MEMBERSHIP", "Membership"),
        ("SHARE_CAPITAL", "Share Capital"),
        ("COMMITTEE", "Committee Structure"),
        ("FINANCE", "Finance"),
        ("USAGE", "Usage"),
        ("TENANCY", "Tenancy"),
        ("TRANSFER", "Transfer"),
        ("COMPLIANCE", "Compliance"),
        ("DISCIPLINE", "Discipline"),
    ]

    decision_code = models.CharField(max_length=120, unique=True)

    category = models.CharField(max_length=40, choices=CATEGORY_CHOICES)

    question = models.TextField()

    description = models.TextField(blank=True)

    legal_reference = models.TextField(blank=True)

    allowed_values = models.JSONField(default=dict, blank=True)

    default_value = models.JSONField(default=dict, blank=True)

    risk_rules = models.JSONField(default=dict, blank=True)

    registrar_notes = models.TextField(blank=True)

    clause_template_code = models.CharField(max_length=120, blank=True)

    sequence_order = models.IntegerField(default=0)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.decision_code} ({self.category})"

# statutory/bylaws/models.py

from django.db import models
import uuid


# ============================================================
# VERSION REGISTRY
# ============================================================

class BylawVersion(models.Model):
    """
    Represents a legally published version of model bye-laws.
    Example:
        MH-2014
        MH-2021
    """

    code = models.CharField(max_length=50, unique=True)   # MH-2014
    title = models.CharField(max_length=255)
    effective_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code


# ============================================================
# CHAPTER
# ============================================================

class BylawChapter(models.Model):
    """
    Top legal container.

    Example:
        CHAPTER I — PRELIMINARY
        CHAPTER II — MEMBERSHIP
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    version = models.ForeignKey(
        BylawVersion,
        on_delete=models.CASCADE,
        related_name="chapters"
    )

    chapter_number = models.PositiveIntegerField()
    title = models.CharField(max_length=500)

    description = models.TextField(blank=True)

    sequence_order = models.PositiveIntegerField()

    class Meta:
        ordering = ["sequence_order"]
        unique_together = ("version", "chapter_number")

    def __str__(self):
        return f"Chapter {self.chapter_number}: {self.title}"


# ============================================================
# CLAUSE
# ============================================================

class BylawClause(models.Model):
    """
    Legally authoritative clause.

    Fidelity requirement:
        text MUST match legal document word-to-word.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    chapter = models.ForeignKey(
        BylawChapter,
        on_delete=models.CASCADE,
        related_name="clauses"
    )

    clause_number = models.CharField(max_length=20)  # 1, 2, 3, etc.

    title = models.CharField(max_length=500)

    legal_text = models.TextField()  # RAW LAW TEXT (immutable)

    explanation = models.TextField(blank=True)  # human-friendly

    machine_tags = models.JSONField(default=dict, blank=True)

    sequence_order = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sequence_order"]
        unique_together = ("chapter", "clause_number")

    def __str__(self):
        return f"Clause {self.clause_number} — {self.title}"


# ============================================================
# SUB-CLAUSE
# ============================================================

class BylawSubClause(models.Model):
    """
    Nested clause.

    Example:
        3(a)
        3(b)
        3(c)
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    clause = models.ForeignKey(
        BylawClause,
        on_delete=models.CASCADE,
        related_name="sub_clauses"
    )

    sub_clause_number = models.CharField(max_length=10)  # a, b, c

    legal_text = models.TextField()

    explanation = models.TextField(blank=True)

    sequence_order = models.PositiveIntegerField()

    class Meta:
        ordering = ["sequence_order"]
        unique_together = ("clause", "sub_clause_number")

    def __str__(self):
        return f"{self.clause.clause_number}({self.sub_clause_number})"

class BylawDraft(models.Model):
    """
    Working editable draft of by-laws for a specific case.
    """

    case = models.OneToOneField(Case, on_delete=models.CASCADE)

    version_code = models.CharField(max_length=20, default="MH-2014")

    is_locked = models.BooleanField(default=False)
    approved_by_committee = models.BooleanField(default=False)
    registrar_ready = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bylaw Draft for Case {self.case.id}"

# ============================================================
# DECISION HOOK
# ============================================================

class BylawDecisionHook(models.Model):
    """
    Connects legal clause → decision engine.

    Example:
        Clause: Non-occupancy charges
        Decision: NON_OCCUPANCY_CHARGES
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    clause = models.ForeignKey(
        BylawClause,
        on_delete=models.CASCADE,
        related_name="decision_hooks"
    )

    decision_code = models.CharField(max_length=100)

    enforcement_level = models.CharField(
        max_length=20,
        choices=[
            ("INFO", "Informational"),
            ("ADVISORY", "Advisory"),
            ("SOFT_BLOCK", "Soft Block"),
            ("HARD_BLOCK", "Hard Block"),
        ],
        default="ADVISORY",
    )

    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.clause} → {self.decision_code}"

class BylawDecision(models.Model):
    """
    Structured society decisions that influence by-law drafting.
    """

    draft = models.ForeignKey(BylawDraft, on_delete=models.CASCADE)

    decision_key = models.CharField(max_length=100)
    decision_value = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

from society.models import Case



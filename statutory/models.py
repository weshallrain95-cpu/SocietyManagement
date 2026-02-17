from django.db import models
from django.contrib.auth.models import User
from society.models import Society

class State(models.Model):
    code = models.CharField(max_length=10, unique=True)  # MH, KA, DL, etc.
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class LegalStage(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    sequence_order = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    is_mandatory = models.BooleanField(default=True)
    expected_duration_days = models.PositiveIntegerField(default=30)
    amber_after_days = models.PositiveIntegerField(default=45)
    red_after_days = models.PositiveIntegerField(default=60)


    class Meta:
        ordering = ['sequence_order']

    def __str__(self):
        return f"{self.state.code} - {self.name}"


class LegalObligation(models.Model):
    legal_stage = models.ForeignKey(LegalStage, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    mandatory = models.BooleanField(default=True)
    reference_law = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.title


class LegalChecklistItem(models.Model):
    legal_obligation = models.ForeignKey(LegalObligation, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    mandatory = models.BooleanField(default=True)

    def __str__(self):
        return self.description


class LegalArtifactTemplate(models.Model):
    """
    Template for statutory legal artifacts (forms, letters, resolutions).

    artifact_type  → UI / category (Form, Letter, Resolution)
    artifact_code  → ENGINE contract key (FORM_A, BYLAW_DRAFT, etc.)
    """

    ARTIFACT_TYPES = [
        ("FORM", "Form"),
        ("LETTER", "Letter"),
        ("RESOLUTION", "Resolution"),
        ("MINUTES", "Minutes"),
    ]

    legal_obligation = models.ForeignKey(
        "LegalObligation",
        on_delete=models.CASCADE,
        related_name="artifact_templates",
    )

    artifact_type = models.CharField(
        max_length=32,
        choices=ARTIFACT_TYPES,
    )

    # ✅ THIS IS THE MISSING PIECE
    artifact_code = models.CharField(
    max_length=64,
    null=True,
    blank=True,
    db_index=True,   # keep lookup fast
    )


    template_body = models.TextField(
        help_text="Template body with placeholders like {{ society_name }}",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["artifact_code"]

    def __str__(self):
        return f"{self.artifact_code} ({self.get_artifact_type_display()})"


class SocietyLegalProgress(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('OVERRIDDEN', 'Overridden'),
    )

    society = models.ForeignKey(Society, on_delete=models.CASCADE)
    legal_stage = models.ForeignKey(LegalStage, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    started_on = models.DateTimeField(auto_now_add=True)
    completed_on = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.society} - {self.legal_stage}"


class SocietyObligationStatus(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('SKIPPED', 'Skipped'),
    )

    society = models.ForeignKey(Society, on_delete=models.CASCADE)
    legal_obligation = models.ForeignKey(LegalObligation, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    override_reason = models.TextField(blank=True, null=True)
    overridden_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    overridden_on = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.society} - {self.legal_obligation}"
from django.conf import settings

class StatutoryAuditLog(models.Model):
    ACTION_CHOICES = [
        ("STEP_COMPLETED", "Step Completed"),
        ("STEP_STARTED", "Step Started"),
        ("DOCUMENT_UPLOADED", "Document Uploaded"),
        ("SYSTEM", "System Action"),
    ]

    society = models.ForeignKey(
        "society.Society",
        on_delete=models.CASCADE,
        related_name="audit_logs",
    )

    legal_stage = models.ForeignKey(
        "statutory.LegalStage",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.TextField()

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    source = models.CharField(
        max_length=50,
        default="API",  # API / ADMIN / SYSTEM
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.society.name} | {self.action} | {self.created_at}"
from django.db import models
from society.models import Society


class SocietyLegalDocument(models.Model):
    society = models.ForeignKey(
        Society,
        on_delete=models.CASCADE,
        related_name="legal_documents",
    )

    template = models.ForeignKey(
        "LegalArtifactTemplate",
        on_delete=models.PROTECT,
        related_name="uploaded_documents",
    )

    file = models.FileField(upload_to="legal_documents/")

    status = models.CharField(
    max_length=20,
    choices=[
        ("GENERATED", "Generated"),
        ("UPLOADED", "Uploaded"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("SUPERSEDED", "Superseded"),
    ],
    default="GENERATED",
)


    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("society", "template")
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.society.name} – {self.template.artifact_code}"
    
    def save(self, *args, **kwargs):
        is_new_upload = self.pk is None

        super().save(*args, **kwargs)

        if (
            is_new_upload
            and self.status == "Uploaded"
            and self.template.is_mandatory
        ):
            from statutory.services import finalize_society_if_allowed
            finalize_society_if_allowed(self.society)
    # statutory/models.py

from django.conf import settings
from django.utils import timezone
from django.db import models

class ShareOwnership(models.Model):
    society = models.ForeignKey(
        "society.Society",
        on_delete=models.CASCADE,
        related_name="share_ownerships",
    )

    member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="share_ownerships",
    )

    shares = models.PositiveIntegerField(default=1)

    is_active = models.BooleanField(default=True)

    acquired_on = models.DateField(default=timezone.now)
    relinquished_on = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-acquired_on"]
        indexes = [
            models.Index(fields=["society", "is_active"]),
        ]

    def __str__(self):
        status = "ACTIVE" if self.is_active else "HISTORICAL"
        return f"{self.member} – {status}"

class SocietyBylawDecision(models.Model):
    """
    Stores decisions taken by a specific society
    against a by-law decision definition.
    """

    society = models.ForeignKey(
        "society.Society",
        on_delete=models.CASCADE,
        related_name="bylaw_decisions",
    )

    decision = models.ForeignKey(
        "bylaws.BylawDecision",
        on_delete=models.CASCADE,
        related_name="society_values",
    )

    ENFORCEMENT_CHOICES = (
        ("ADVISORY", "Advisory"),
        ("SOFT_BLOCK", "Soft Block"),
        ("HARD_BLOCK", "Hard Block"),
        ("CONDITIONAL", "Conditional"),
    )

    enforcement_level = models.CharField(
        max_length=20,
        choices=ENFORCEMENT_CHOICES,
        default="ADVISORY",
    )   

    value = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("society", "decision")

    def __str__(self):
        return f"{self.society.name} — {self.decision.decision_code}"



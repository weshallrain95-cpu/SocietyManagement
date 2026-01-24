# society/legal/disputes/cases/models/case.py

from django.db import models
import uuid


# ============================
# Legal Case Model
# ============================

class LegalCase(models.Model):
    """
    Represents a legal dispute case.
    Core judicial entity of the platform.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Case Identity
    case_number = models.CharField(max_length=100, unique=True, db_index=True)
    title = models.CharField(max_length=255)

    # Jurisdiction & Authority
    jurisdiction = models.CharField(max_length=255)
    authority = models.CharField(max_length=255)   # governing body / arbitration panel / court

    # Case Type
    case_type = models.CharField(
        max_length=100,
        choices=[
            ("DISPUTE", "Dispute"),
            ("VIOLATION", "Violation"),
            ("APPEAL", "Appeal"),
            ("ARBITRATION", "Arbitration"),
            ("COMPLIANCE", "Compliance"),
            ("GOVERNANCE", "Governance"),
        ],
    )

    # Legal Domain
    legal_domain = models.CharField(max_length=100)

    # Core Status
    status = models.CharField(
        max_length=50,
        choices=[
            ("FILED", "Filed"),
            ("ADMITTED", "Admitted"),
            ("UNDER_REVIEW", "Under Review"),
            ("HEARING", "Hearing"),
            ("ARBITRATION", "Arbitration"),
            ("JUDGEMENT_PENDING", "Judgement Pending"),
            ("DECIDED", "Decided"),
            ("ENFORCED", "Enforced"),
            ("CLOSED", "Closed"),
            ("APPEALED", "Appealed"),
        ],
        default="FILED"
    )

    # Legal Context
    legal_basis = models.JSONField(default=dict)   # laws, bylaws, canon refs
    claims_summary = models.TextField(null=True, blank=True)

    # Governance Binding
    governance_context = models.JSONField(null=True, blank=True)

    # Authority Graph Binding
    authority_chain = models.JSONField(null=True, blank=True)

    # Timestamps
    filed_at = models.DateTimeField(auto_now_add=True)
    admitted_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Legal Case"
        verbose_name_plural = "Legal Cases"
        indexes = [
            models.Index(fields=["case_number"]),
            models.Index(fields=["status"]),
            models.Index(fields=["case_type"]),
            models.Index(fields=["jurisdiction"]),
        ]

    def __str__(self):
        return f"{self.case_number} - {self.title}"

    # ----------------------------
    # Lifecycle Transitions
    # ----------------------------

    def admit(self, time):
        self.status = "ADMITTED"
        self.admitted_at = time
        self.save()

    def move_to_review(self):
        self.status = "UNDER_REVIEW"
        self.save()

    def start_hearing(self):
        self.status = "HEARING"
        self.save()

    def start_arbitration(self):
        self.status = "ARBITRATION"
        self.save()

    def mark_judgement_pending(self):
        self.status = "JUDGEMENT_PENDING"
        self.save()

    def decide(self):
        self.status = "DECIDED"
        self.save()

    def enforce(self):
        self.status = "ENFORCED"
        self.save()

    def appeal(self):
        self.status = "APPEALED"
        self.save()

    def close(self, time):
        self.status = "CLOSED"
        self.closed_at = time
        self.save()

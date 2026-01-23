# society/legal/constitution/models/authority.py

from django.db import models
from django.conf import settings
import uuid


# ============================
# Authority Type Enum (Executable)
# ============================

class AuthorityType(models.TextChoices):
    CONSTITUTIONAL_BODY = "CONSTITUTIONAL_BODY", "Constitutional Body"
    GOVERNING_COUNCIL = "GOVERNING_COUNCIL", "Governing Council"
    EXECUTIVE_AUTHORITY = "EXECUTIVE_AUTHORITY", "Executive Authority"
    JUDICIAL_AUTHORITY = "JUDICIAL_AUTHORITY", "Judicial Authority"
    REGULATORY_AUTHORITY = "REGULATORY_AUTHORITY", "Regulatory Authority"
    ADMIN_AUTHORITY = "ADMIN_AUTHORITY", "Administrative Authority"
    EMERGENCY_AUTHORITY = "EMERGENCY_AUTHORITY", "Emergency Authority"
    EXTERNAL_AUTHORITY = "EXTERNAL_AUTHORITY", "External Authority"


# ============================
# Legal Authority Model
# ============================

class LegalAuthority(models.Model):
    """
    Root model representing a source of legal power in the platform.
    This is NOT a role, user, or permission model.
    This is the source-of-law legitimacy model.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Identity
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    authority_type = models.CharField(
        max_length=50,
        choices=AuthorityType.choices
    )

    # Legal Scope
    jurisdiction = models.CharField(max_length=255)
    scope = models.JSONField(
        default=dict,
        help_text="Spatial, functional, domain scope"
    )
    legal_domain = models.CharField(max_length=100)

    # Power Structure
    supremacy_rank = models.PositiveIntegerField(
        help_text="Lower number = higher authority"
    )

    legal_powers = models.JSONField(
        default=dict,
        help_text="Structured declaration of legal powers"
    )
    delegation_rights = models.JSONField(
        default=dict,
        help_text="Delegable powers and constraints"
    )
    override_rights = models.JSONField(
        default=dict,
        help_text="Override capabilities"
    )

    # Capabilities (fast checks)
    can_create_law = models.BooleanField(default=False)
    can_amend_law = models.BooleanField(default=False)
    can_repeal_law = models.BooleanField(default=False)
    can_interpret_law = models.BooleanField(default=False)
    can_enforce_law = models.BooleanField(default=False)

    # Governance Binding
    governance_binding = models.JSONField(
        default=dict,
        help_text="Governance policy bindings"
    )

    # Validity Window
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField(blank=True, null=True)

    # State
    status = models.CharField(
        max_length=30,
        default="ACTIVE"
    )

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_legal_authorities"
    )

    class Meta:
        ordering = ["supremacy_rank", "-created_at"]
        verbose_name = "Legal Authority"
        verbose_name_plural = "Legal Authorities"

    def __str__(self):
        return f"{self.name} [{self.authority_type}]"

    # ============================
    # Domain Logic
    # ============================

    def is_active(self, at_time=None):
        """Check temporal validity"""
        from django.utils import timezone
        now = at_time or timezone.now()
        if self.valid_until:
            return self.valid_from <= now <= self.valid_until
        return self.valid_from <= now

    def has_power(self, power_key: str) -> bool:
        """
        Structured power check.
        Example power_key: 'create_law', 'amend_law', 'override_law'
        """
        # JSON-declared powers take precedence
        if self.legal_powers.get(power_key):
            return True

        # fallback to boolean flags
        flag_name = f"can_{power_key}"
        return bool(getattr(self, flag_name, False))

    def is_supreme_over(self, other_authority: "LegalAuthority") -> bool:
        """
        Lower supremacy_rank = higher authority
        """
        return self.supremacy_rank < other_authority.supremacy_rank

    def can_exercise(self, action: str) -> bool:
        """
        Unified capability gate
        """
        action_map = {
            "CREATE_LAW": self.can_create_law,
            "AMEND_LAW": self.can_amend_law,
            "REPEAL_LAW": self.can_repeal_law,
            "INTERPRET_LAW": self.can_interpret_law,
            "ENFORCE_LAW": self.can_enforce_law,
        }
        return bool(action_map.get(action, False))

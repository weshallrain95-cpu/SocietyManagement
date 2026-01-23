# society/legal/constitution/models/authority_graph.py

from django.db import models
import uuid
from .authority import LegalAuthority


# ============================
# Authority Relation Types (Executable Enum)
# ============================

class AuthorityRelationType(models.TextChoices):
    SUPERSEDES = "SUPERSEDES", "Supersedes"
    DELEGATES_TO = "DELEGATES_TO", "Delegates To"
    OVERRIDES = "OVERRIDES", "Overrides"
    SUBORDINATE_TO = "SUBORDINATE_TO", "Subordinate To"
    DERIVES_FROM = "DERIVES_FROM", "Derives From"


# ============================
# Authority Graph Edge Model
# ============================

class LegalAuthorityRelation(models.Model):
    """
    Directed edge in the Legal Authority Graph.
    This defines power relationships between authorities.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    from_authority = models.ForeignKey(
        LegalAuthority,
        on_delete=models.CASCADE,
        related_name="outgoing_relations"
    )

    to_authority = models.ForeignKey(
        LegalAuthority,
        on_delete=models.CASCADE,
        related_name="incoming_relations"
    )

    relation_type = models.CharField(
        max_length=50,
        choices=AuthorityRelationType.choices
    )

    # Contextual Constraints
    scope = models.JSONField(
        default=dict,
        help_text="Contextual scope of this relationship"
    )
    conditions = models.JSONField(
        default=dict,
        help_text="Conditional activation rules"
    )

    # Validity Window
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField(blank=True, null=True)

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            "from_authority",
            "to_authority",
            "relation_type"
        )
        verbose_name = "Legal Authority Relation"
        verbose_name_plural = "Legal Authority Relations"

    def __str__(self):
        return f"{self.from_authority} -[{self.relation_type}]-> {self.to_authority}"

    # ============================
    # Domain Logic
    # ============================

    def is_active(self, at_time=None):
        """Check temporal validity of relation"""
        from django.utils import timezone
        now = at_time or timezone.now()
        if self.valid_until:
            return self.valid_from <= now <= self.valid_until
        return self.valid_from <= now

# society/legal/constitution/services/authority_graph.py

from typing import List, Optional
from django.db.models import Q
from django.utils import timezone

from ..models.authority import LegalAuthority
from ..models.authority_graph import (
    LegalAuthorityRelation,
    AuthorityRelationType,
)


# =====================================
# Authority Graph Service
# =====================================

class AuthorityGraphService:
    """
    Service layer for interacting with the Legal Authority Graph.

    This is NOT business logic for bylaws.
    This is power-structure logic:
    - legitimacy
    - supremacy
    - delegation
    - override
    - derivation
    """

    # -----------------------------
    # Basic Capability Checks
    # -----------------------------

    def can_create_law(self, authority: LegalAuthority) -> bool:
        return authority.can_create_law and authority.is_active()

    def can_amend_law(self, authority: LegalAuthority) -> bool:
        return authority.can_amend_law and authority.is_active()

    def can_repeal_law(self, authority: LegalAuthority) -> bool:
        return authority.can_repeal_law and authority.is_active()

    def can_interpret_law(self, authority: LegalAuthority) -> bool:
        return authority.can_interpret_law and authority.is_active()

    def can_enforce_law(self, authority: LegalAuthority) -> bool:
        return authority.can_enforce_law and authority.is_active()

    # -----------------------------
    # Supremacy Resolution
    # -----------------------------

    def resolve_supremacy(
        self,
        authority_a: LegalAuthority,
        authority_b: LegalAuthority
    ) -> LegalAuthority:
        """
        Lower supremacy_rank = higher authority
        """
        return authority_a if authority_a.supremacy_rank < authority_b.supremacy_rank else authority_b

    # -----------------------------
    # Graph Relationship Checks
    # -----------------------------

    def has_relation(
        self,
        source: LegalAuthority,
        target: LegalAuthority,
        relation_type: AuthorityRelationType
    ) -> bool:
        return LegalAuthorityRelation.objects.filter(
            from_authority=source,
            to_authority=target,
            relation_type=relation_type,
            valid_from__lte=timezone.now()
        ).filter(
            Q(valid_until__isnull=True) | Q(valid_until__gte=timezone.now())
        ).exists()

    def has_override_power(
        self,
        source: LegalAuthority,
        target: LegalAuthority
    ) -> bool:
        return self.has_relation(source, target, AuthorityRelationType.OVERRIDES)

    def is_subordinate(
        self,
        source: LegalAuthority,
        target: LegalAuthority
    ) -> bool:
        return self.has_relation(source, target, AuthorityRelationType.SUBORDINATE_TO)

    def derives_from(
        self,
        source: LegalAuthority,
        target: LegalAuthority
    ) -> bool:
        return self.has_relation(source, target, AuthorityRelationType.DERIVES_FROM)

    # -----------------------------
    # Authority Validation Engine
    # -----------------------------

    def validate_authority_action(
        self,
        authority: LegalAuthority,
        action: str,
        context: Optional[dict] = None
    ) -> bool:
        """
        Unified validation gate for legal actions.
        """
        if not authority.is_active():
            return False

        # Direct capability check
        if not authority.can_exercise(action):
            return False

        # Future: context-aware checks (jurisdiction, scope, governance mode, etc.)
        return True

    # -----------------------------
    # Graph Queries
    # -----------------------------

    def get_delegated_authorities(self, authority: LegalAuthority) -> List[LegalAuthority]:
        """
        Authorities this authority has delegated power to
        """
        relations = LegalAuthorityRelation.objects.filter(
            from_authority=authority,
            relation_type=AuthorityRelationType.DELEGATES_TO,
            valid_from__lte=timezone.now()
        ).filter(
            Q(valid_until__isnull=True) | Q(valid_until__gte=timezone.now())
        )

        return [rel.to_authority for rel in relations]

    def get_superior_authorities(self, authority: LegalAuthority) -> List[LegalAuthority]:
        """
        Authorities that have supremacy over this authority
        """
        relations = LegalAuthorityRelation.objects.filter(
            to_authority=authority,
            relation_type=AuthorityRelationType.SUBORDINATE_TO,
            valid_from__lte=timezone.now()
        ).filter(
            Q(valid_until__isnull=True) | Q(valid_until__gte=timezone.now())
        )

        return [rel.from_authority for rel in relations]

    def get_override_sources(self, authority: LegalAuthority) -> List[LegalAuthority]:
        """
        Authorities that can override this authority
        """
        relations = LegalAuthorityRelation.objects.filter(
            to_authority=authority,
            relation_type=AuthorityRelationType.OVERRIDES,
            valid_from__lte=timezone.now()
        ).filter(
            Q(valid_until__isnull=True) | Q(valid_until__gte=timezone.now())
        )

        return [rel.from_authority for rel in relations]

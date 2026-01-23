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

    Power-structure logic:
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
        if not authority.is_active():
            return False

        if not authority.can_exercise(action):
            return False

        return True

    # -----------------------------
    # Graph Queries
    # -----------------------------

    def get_delegated_authorities(self, authority: LegalAuthority) -> List[LegalAuthority]:
        relations = LegalAuthorityRelation.objects.filter(
            from_authority=authority,
            relation_type=AuthorityRelationType.DELEGATES_TO,
            valid_from__lte=timezone.now()
        ).filter(
            Q(valid_until__isnull=True) | Q(valid_until__gte=timezone.now())
        )
        return [rel.to_authority for rel in relations]

    def get_superior_authorities(self, authority: LegalAuthority) -> List[LegalAuthority]:
        relations = LegalAuthorityRelation.objects.filter(
            to_authority=authority,
            relation_type=AuthorityRelationType.SUBORDINATE_TO,
            valid_from__lte=timezone.now()
        ).filter(
            Q(valid_until__isnull=True) | Q(valid_until__gte=timezone.now())
        )
        return [rel.from_authority for rel in relations]

    def get_override_sources(self, authority: LegalAuthority) -> List[LegalAuthority]:
        relations = LegalAuthorityRelation.objects.filter(
            to_authority=authority,
            relation_type=AuthorityRelationType.OVERRIDES,
            valid_from__lte=timezone.now()
        ).filter(
            Q(valid_until__isnull=True) | Q(valid_until__gte=timezone.now())
        )
        return [rel.from_authority for rel in relations]

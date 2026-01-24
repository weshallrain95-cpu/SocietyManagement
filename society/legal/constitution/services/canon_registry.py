# society/legal/constitution/services/canon_registry.py

from typing import List, Optional
from django.utils import timezone

from society.legal.constitution.models.canon import LegalCanonNode, CanonType
from society.legal.constitution.models.authority import LegalAuthority


# ============================
# Canon Registry Service
# ============================

class CanonRegistryService:
    """
    Manages the legal canon hierarchy.
    Responsible for structure of law.
    """

    def create_canon_node(
        self,
        name: str,
        canon_type: CanonType,
        hierarchy_level: int,
        authority: LegalAuthority,
        jurisdiction: str,
        legal_domain: str,
        parent: Optional[LegalCanonNode] = None,
        scope: dict = None,
        governance_binding: dict = None,
        version: str = "1.0.0",
    ) -> LegalCanonNode:

        node = LegalCanonNode.objects.create(
            name=name,
            canon_type=canon_type,
            hierarchy_level=hierarchy_level,
            parent=parent,
            authority_source=authority,
            jurisdiction=jurisdiction,
            legal_domain=legal_domain,
            scope=scope or {},
            governance_binding=governance_binding or {},
            version=version,
            valid_from=timezone.now(),
        )

        return node

    def get_root_nodes(self) -> List[LegalCanonNode]:
        return LegalCanonNode.objects.filter(parent__isnull=True, status="ACTIVE")

    def get_children(self, node: LegalCanonNode) -> List[LegalCanonNode]:
        return list(node.children.filter(status="ACTIVE"))

    def get_tree(self, root: LegalCanonNode) -> dict:
        """
        Returns full canon subtree.
        """

        def build(node):
            return {
                "id": str(node.id),
                "name": node.name,
                "canon_type": node.canon_type,
                "children": [build(child) for child in node.children.all()],
            }

        return build(root)

    def deactivate_node(self, node: LegalCanonNode):
        node.status = "SUSPENDED"
        node.save()

    def repeal_node(self, node: LegalCanonNode):
        node.status = "REPEALED"
        node.save()

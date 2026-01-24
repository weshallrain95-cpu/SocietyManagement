# society/legal/constitution/services/document_registry.py

from typing import List
from django.utils import timezone

from society.legal.constitution.models.document import LegalDocument, DocumentType
from society.legal.constitution.models.canon import LegalCanonNode
from society.legal.constitution.models.authority import LegalAuthority


# ============================
# Legal Document Registry
# ============================

class DocumentRegistryService:
    """
    Manages lifecycle of machine-legible legal documents.
    """

    def register_document(
        self,
        title: str,
        code: str,
        doc_type: DocumentType,
        canon_node: LegalCanonNode,
        authority: LegalAuthority,
        jurisdiction: str,
        legal_domain: str,
        hierarchy_level: int,
        normative_type: str,
        created_by: str,
        scope: dict = None,
        conditions: dict = None,
        rules: list = None,
        obligations: list = None,
        prohibitions: list = None,
        permissions: list = None,
        exceptions: list = None,
        sanctions: list = None,
        governance_binding: dict = None,
        enforcement_bindings: dict = None,
        version: str = "1.0.0",
    ) -> LegalDocument:

        doc = LegalDocument.objects.create(
            title=title,
            code=code,
            doc_type=doc_type,
            canon_node=canon_node,
            authority_source=authority,
            jurisdiction=jurisdiction,
            legal_domain=legal_domain,
            hierarchy_level=hierarchy_level,
            normative_type=normative_type,
            scope=scope or {},
            conditions=conditions or {},
            rules=rules or [],
            obligations=obligations or [],
            prohibitions=prohibitions or [],
            permissions=permissions or [],
            exceptions=exceptions or [],
            sanctions=sanctions or [],
            governance_binding=governance_binding or {},
            enforcement_bindings=enforcement_bindings or {},
            version=version,
            created_by=created_by,
            effective_from=timezone.now(),
        )

        return doc

    def activate_document(self, document: LegalDocument):
        document.status = "ACTIVE"
        document.save()

    def suspend_document(self, document: LegalDocument):
        document.status = "SUSPENDED"
        document.save()

    def repeal_document(self, document: LegalDocument):
        document.status = "REPEALED"
        document.save()

    def get_active_documents(self) -> List[LegalDocument]:
        return LegalDocument.objects.filter(status="ACTIVE")

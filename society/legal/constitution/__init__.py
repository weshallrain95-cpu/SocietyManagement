"""
Legal Constitution Layer
Phase 11 — Legal Platform

This package defines the constitutional layer of the legal platform:
- Legal Authority
- Authority Graph
- Legal Power Structures
- Source-of-law legitimacy
- Legal Canon (hierarchy of law)
- Machine-law schema
- Legal ontology
- Legal execution services
"""

# ============================
# Authority Layer
# ============================

from .models.authority import LegalAuthority, AuthorityType
from .models.authority_graph import LegalAuthorityRelation, AuthorityRelationType
from .services.authority_graph import AuthorityGraphService

# ============================
# Canon Layer
# ============================

from .models.canon import LegalCanonNode, CanonType

# ============================
# Document Layer
# ============================

from .models.document import LegalDocument, DocumentType

# ============================
# Bylaw Layer
# ============================

from .models.bylaw import Bylaw

# ============================
# Ontology Layer
# ============================

from .ontology.normative import NormativeType, Norm
from .ontology.domains import LegalDomain, DOMAIN_DESCRIPTIONS

# ============================
# Services Layer
# ============================

from .services.canon_registry import CanonRegistryService
from .services.document_registry import DocumentRegistryService
from .services.bylaw_engine import BylawEngine

__all__ = [
    # Authority
    "LegalAuthority",
    "AuthorityType",
    "LegalAuthorityRelation",
    "AuthorityRelationType",
    "AuthorityGraphService",

    # Canon
    "LegalCanonNode",
    "CanonType",

    # Document
    "LegalDocument",
    "DocumentType",

    # Bylaw
    "Bylaw",

    # Ontology
    "NormativeType",
    "Norm",
    "LegalDomain",
    "DOMAIN_DESCRIPTIONS",

    # Services
    "CanonRegistryService",
    "DocumentRegistryService",
    "BylawEngine",
]

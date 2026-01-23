
"""
Legal Constitution Layer
Phase 11 — Legal Platform

This package defines the constitutional layer of the legal platform:
- Legal Authority
- Authority Graph
- Legal Power Structures
- Source-of-law legitimacy
"""

from .models.authority import LegalAuthority, AuthorityType
from .models.authority_graph import LegalAuthorityRelation, AuthorityRelationType
from .services.authority_graph import AuthorityGraphService

__all__ = [
    "LegalAuthority",
    "AuthorityType",
    "LegalAuthorityRelation",
    "AuthorityRelationType",
    "AuthorityGraphService",
]

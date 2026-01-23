"""
Legal App Model Aggregator

This file exposes all legal-domain models to Django's app registry.
Deep domain models must be imported here for migrations and ORM discovery.
"""

# Constitution Layer Models
from society.legal.constitution.models.authority import LegalAuthority
from society.legal.constitution.models.authority_graph import LegalAuthorityRelation

__all__ = [
    "LegalAuthority",
    "LegalAuthorityRelation",
]

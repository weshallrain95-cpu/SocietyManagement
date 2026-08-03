"""
===============================================================================
SocietyOS Spend Resolver
-------------------------------------------------------------------------------

Purpose
-------
Provides canonical validation and normalization of Spend
classification selected by the user.

This module is the ONLY canonical resolver for:

    Operational Domain
            ↓
        Spend Item
            ↓
    Canonical Spend Resolution

It deliberately contains:

✓ No ORM
✓ No Django models
✓ No database access
✓ No Posting Engine
✓ No Chart of Accounts
✓ No workflow logic
✓ No accounting decisions

The resolver produces canonical business classification only.

Business workflows, accounting resolution and financial
processing remain the responsibility of their respective
domains.
===============================================================================
"""

from dataclasses import dataclass

from society.domain_services.spend.spend_catalog import (
    get_spend_item,
)


@dataclass(frozen=True)
class SpendResolution:
    """
    Canonical spend classification returned by the
    Spend Resolver.
    """

    operational_domain_code: str
    spend_item_code: str


def resolve_spend(
    *,
    operational_domain_code: str,
    spend_item_code: str,
) -> SpendResolution:
    """
    Resolve and normalize the supplied Spend
    classification.

    Version 1 intentionally trusts the supplied
    Operational Domain.

    Operational Domain validation will be introduced
    once the Spend hierarchy is formally modelled.
    """

    spend_item = get_spend_item(
        spend_item_code,
    )

    return SpendResolution(
        operational_domain_code=operational_domain_code,
        spend_item_code=spend_item.code,
    )
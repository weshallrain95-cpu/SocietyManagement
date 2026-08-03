"""
===============================================================================
Society Spend Catalog
-------------------------------------------------------------------------------

Purpose
-------
Canonical registry of everything a housing society may spend money on.

This catalog represents BUSINESS vocabulary only.

It DOES NOT contain:

- Accounting rules
- Ledger mappings
- Posting logic
- Vendor logic
- Payment logic

It simply answers:

"What is the society paying for?"

Every financial journey within SocietyOS begins here.

Architecture
------------
Society Spend
        │
        ▼
Spend Head
        │
        ▼
Expense Authorization
        │
        ▼
Vendor Bill
        │
        ▼
Vendor Payable
        │
        ▼
Finance Kernel

Future modules (Assets, Inventory, Budgeting etc.) derive their behaviour
from the selected Spend Head.

This file is intentionally business-centric and completely finance-agnostic.
===============================================================================
"""

from dataclasses import dataclass
from typing import Optional
from .exceptions import UnknownSpendItem

@dataclass(frozen=True)
class SpendHead:
    """
    Canonical description of a society spend.
    """

    code: str
    display_name: str

    expense_category: str

    acquisition_type: str

    asset_category: Optional[str] = None

    asset_type: Optional[str] = None

from .acquisition_types import (
    SERVICE,
    CONSUMABLE,
    ASSET,
)

SPEND_CATALOG = {
}

from .spend_items import ALL_SPEND_ITEMS


SPEND_CATALOG = {
    item.code: item
    for item in ALL_SPEND_ITEMS
}

def get_spend_item(code: str):
    """
    Return the SpendItem for the supplied code.

    Raises:
        UnknownSpendItem
            If the supplied code is not registered.
    """
    try:
        return SPEND_CATALOG[code]

    except KeyError as exc:
        raise UnknownSpendItem(
            f"Unknown Spend Item: '{code}'"
        ) from exc
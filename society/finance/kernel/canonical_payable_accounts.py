"""
Canonical Payable Accounting Definitions
========================================

This module is the single source of truth for every canonical
Chart of Account required by the SocietyOS Payables domain.

Purpose
-------
The Payables domain must never hardcode:

- account names
- account codes
- account types
- account categories

Instead, every payable posting engine resolves its accounting
requirements from this module.

This module intentionally contains:

✓ No ORM
✓ No database queries
✓ No business logic
✓ No posting logic
✓ No workflow knowledge

It is a static accounting contract.
"""

CANONICAL_PAYABLE_ACCOUNTS = {

    "VENDOR_PAYABLES": {

        "system_account": "VENDOR_PAYABLES",

        "code": "VENDOR_PAYABLES",

        "name": "Vendor Payables",

        "account_type": "LIABILITY",

        "account_category": "VENDOR",

        "subtype": None,

        "is_postable": True,

        "requires_entity": True,

    },

    "ADVANCES_TO_VENDORS": {

        "system_account": "ADVANCES_TO_VENDORS",

        "code": "ADVANCES_TO_VENDORS",

        "name": "Advances To Vendors",

        "account_type": "ASSET",

        "account_category": "VENDOR",

        "subtype": None,

        "is_postable": True,

        "requires_entity": True,

    },

    "VENDOR_RETENTION_PAYABLE": {

        "system_account": "VENDOR_RETENTION_PAYABLE",

        "code": "VENDOR_RETENTION",

        "name": "Vendor Retention Payable",

        "account_type": "LIABILITY",

        "account_category": "VENDOR",

        "subtype": None,

        "is_postable": True,

        "requires_entity": True,

    },

    "VENDOR_SECURITY_DEPOSIT": {

        "system_account": "VENDOR_SECURITY_DEPOSIT",

        "code": "VENDOR_SECURITY",

        "name": "Vendor Security Deposit",

        "account_type": "LIABILITY",

        "account_category": "VENDOR",

        "subtype": None,

        "is_postable": True,

        "requires_entity": True,

    },

    "TDS_PAYABLE": {

        "system_account": "TDS_PAYABLE",

        "code": "TDS_PAYABLE",

        "name": "TDS Payable",

        "account_type": "LIABILITY",

        "account_category": "GENERAL",

        "subtype": None,

        "is_postable": True,

        "requires_entity": False,

    },

    "GST_INPUT_CREDIT": {

        "system_account": "GST_INPUT_CREDIT",

        "code": "GST_INPUT_CREDIT",

        "name": "GST Input Credit",

        "account_type": "ASSET",

        "account_category": "GENERAL",

        "subtype": None,

        "is_postable": True,

        "requires_entity": False,

    },

}